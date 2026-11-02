import re
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

from . import config, letters
from .models import (
    AnalyzeRequest,
    AnalysisResponse,
    BillFields,
    ClaimForm,
    DraftRequest,
    DraftResponse,
    Facts,
    Gap,
    LineItem,
    ParseResponse,
    PolicyFields,
    SpeakRequest,
    TranscribeResponse,
    Verdict,
)
from .sarvam_client import SarvamClient

app = FastAPI(title="Claim-It API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sarvam = SarvamClient()

if config.SAMPLES_DIR.exists():
    app.mount("/samples", StaticFiles(directory=str(config.SAMPLES_DIR)), name="samples")


def _check_language(language: str) -> str:
    if language not in config.SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language '{language}'. Choose one of: {', '.join(config.SUPPORTED_LANGUAGES)}.",
        )
    return language


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "mode": sarvam.mode,
        "mock_flag": config.MOCK_MODE,
        "has_key": bool(config.SARVAM_API_KEY),
        "models": {
            "stt": "saaras:v4",
            "chat": "sarvam-105b",
            "tts": "bulbul:v4-flash",
            "documents": "Sarvam Vision 2.1 / doc-ai extract",
        },
    }


@app.post("/api/transcribe", response_model=TranscribeResponse)
async def transcribe(file: UploadFile = File(...), language: str = Form("hi-IN")):
    _check_language(language)
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="The audio file is empty. Record again and retry.")
    if len(data) > 15 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Audio is too large. Keep the narration under 30 seconds.")
    try:
        result = sarvam.transcribe(data, file.filename or "narration.webm", language)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=f"Speech-to-text failed. Retry, or set MOCK_MODE=true. ({exc})")
    transcript = (result.get("transcript") or "").strip()
    warning = ""
    if not transcript:
        warning = "No speech was detected. Try again in a quieter room or type the narration."
    return TranscribeResponse(
        transcript=transcript,
        language_code=result.get("language_code") or language,
        mode=result.get("mode", sarvam.mode),
        warning=warning,
    )


@app.post("/api/parse", response_model=ParseResponse)
async def parse_documents(
    files: list[UploadFile] = File(...),
    kinds: str = Form(...),
    language: str = Form("en-IN"),
):
    _check_language(language)
    kind_list = [k.strip() for k in kinds.split(",") if k.strip()]
    if not files:
        raise HTTPException(status_code=400, detail="Upload the policy and at least one bill.")
    if len(files) != len(kind_list):
        raise HTTPException(status_code=400, detail="Each file must be tagged as policy or bill.")
    if len(files) > 6:
        raise HTTPException(status_code=400, detail="Upload at most 6 documents at a time.")

    allowed = {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}
    parsed_policy = None
    bill_parts: list[dict] = []
    warnings: list[str] = []

    for upload, kind in zip(files, kind_list):
        if kind not in {"policy", "bill"}:
            raise HTTPException(status_code=400, detail=f"Unknown document type '{kind}'.")
        suffix = Path(upload.filename or "").suffix.lower()
        if suffix not in allowed:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported file type '{suffix or 'unknown'}'. Use PDF, PNG, JPG, WEBP, or TIFF.",
            )
        data = await upload.read()
        if not data:
            raise HTTPException(status_code=400, detail=f"'{upload.filename}' is empty or unreadable.")
        if len(data) > 20 * 1024 * 1024:
            raise HTTPException(status_code=413, detail=f"'{upload.filename}' is larger than 20 MB.")
        if config.MOCK_MODE and (parsed_policy and bill_parts):
            continue
        try:
            result = sarvam.parse_document(data, upload.filename or "document", kind)
        except RuntimeError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Could not read '{upload.filename}'. Try a clearer photo, or set MOCK_MODE=true. ({exc})",
            )
        warnings.extend(result.get("warnings") or [])
        if kind == "policy":
            parsed_policy = result.get("policy")
        elif result.get("bill"):
            bill_parts.append(result["bill"])

    if not parsed_policy:
        raise HTTPException(status_code=422, detail="No policy document could be read. Upload a clear policy PDF/photo.")
    if not bill_parts:
        raise HTTPException(status_code=422, detail="No bill could be read. Upload a hospital or pharmacy bill.")

    policy = PolicyFields(**parsed_policy)
    bill = _merge_bills(bill_parts)
    if not policy.clauses:
        warnings.append("No policy clauses were extracted. Add them manually before the coverage check.")
    if not bill.line_items:
        warnings.append("No bill line items were extracted. Add them manually before the coverage check.")
    return ParseResponse(policy=policy, bill=bill, mode=sarvam.mode, warnings=_unique(warnings))


def _merge_bills(parts: list[dict]) -> BillFields:
    if len(parts) == 1:
        return BillFields(**parts[0])
    first = parts[0]
    items: list[LineItem] = []
    warnings: list[str] = []
    total = 0.0
    for part in parts:
        for raw in part.get("line_items") or []:
            items.append(LineItem(id=f"B{len(items) + 1}", **{k: raw.get(k, "") for k in ("description", "amount")}))
        total += float(part.get("total_amount") or 0)
        warnings.extend(part.get("warnings") or [])
    return BillFields(
        patient_name=first.get("patient_name", ""),
        hospital_name=first.get("hospital_name", ""),
        admission_date=first.get("admission_date", ""),
        discharge_date=first.get("discharge_date", ""),
        bill_number=first.get("bill_number", ""),
        line_items=items,
        total_amount=total or sum(i.amount for i in items),
        confidence=min(float(p.get("confidence") or 0) for p in parts),
        source_file=", ".join(p.get("source_file", "") for p in parts),
        warnings=_unique(warnings),
    )


@app.post("/api/analyze", response_model=AnalysisResponse)
def analyze(req: AnalyzeRequest):
    _check_language(req.language)
    if not req.narration.strip():
        raise HTTPException(status_code=400, detail="Add or record the narration before checking coverage.")
    try:
        raw = sarvam.reason(
            req.narration,
            req.language,
            req.policy.model_dump(),
            req.bill.model_dump(),
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=f"Coverage analysis failed. Retry, or set MOCK_MODE=true. ({exc})")
    return _normalize_analysis(raw, req)


def _normalize_analysis(raw: dict, req: AnalyzeRequest) -> AnalysisResponse:
    policy, bill = req.policy, req.bill
    clauses = {c.id: c for c in policy.clauses}
    line_map = {li.id: li for li in bill.line_items}
    raw_verdicts = raw.get("verdicts") or []
    verdicts: list[Verdict] = []

    for index, item in enumerate(raw_verdicts):
        line = line_map.get(str(item.get("line_id") or ""))
        if line is None and index < len(bill.line_items):
            line = bill.line_items[index]
        if line is None:
            continue
        verdict = str(item.get("verdict") or "unclear").lower().replace(" ", "_").replace("-", "_")
        if verdict not in {"covered", "partially_covered", "not_covered", "unclear"}:
            verdict = "unclear"
        clause = clauses.get(str(item.get("clause_id") or ""))
        clause_text = clause.text if clause else ""
        clause_id = clause.id if clause else ""
        if clause is None:
            wanted = (item.get("clause_text") or "").strip().lower()
            if wanted:
                for candidate in policy.clauses:
                    if wanted[:60] and wanted[:60] in candidate.text.lower():
                        clause, clause_text, clause_id = candidate, candidate.text, candidate.id
                        break
        if clause is None and verdict in {"covered", "partially_covered"}:
            verdict = "unclear"
        confidence = _clamp(item.get("confidence", 0.5))
        amount = float(line.amount or 0)
        covered_amount = 0.0 if verdict in {"not_covered", "unclear"} else _clamp_amount(item.get("covered_amount", amount), amount)
        if verdict == "covered":
            covered_amount = amount
        verdicts.append(
            Verdict(
                line_id=line.id,
                line_description=line.description,
                amount=amount,
                verdict=verdict,
                covered_amount=covered_amount,
                confidence=confidence,
                clause_id=clause_id,
                clause_text=clause_text or "No exact policy clause matched. Manual review needed.",
                reasoning=str(item.get("reasoning") or item.get("explanation") or ""),
            )
        )

    seen = {v.line_id for v in verdicts}
    for line in bill.line_items:
        if line.id not in seen:
            verdicts.append(
                Verdict(
                    line_id=line.id,
                    line_description=line.description,
                    amount=float(line.amount or 0),
                    verdict="unclear",
                    covered_amount=0,
                    confidence=0.35,
                    clause_id="",
                    clause_text="No exact policy clause matched. Manual review needed.",
                    reasoning="The model did not return a verdict for this line, so it needs manual review.",
                )
            )

    facts_raw = raw.get("facts") or {}
    facts = Facts(
        patient_name=str(facts_raw.get("patient_name") or bill.patient_name or policy.insured_name),
        hospital_name=str(facts_raw.get("hospital_name") or bill.hospital_name),
        incident_date=str(facts_raw.get("incident_date") or bill.admission_date),
        claim_type=str(facts_raw.get("claim_type") or "Hospitalisation claim"),
        summary=str(facts_raw.get("summary") or ""),
    )

    totals = _totals(bill, verdicts, policy)
    raw_gaps = []
    for g in raw.get("gaps") or []:
        if isinstance(g, dict) and (g.get("title") or g.get("detail")):
            severity = str(g.get("severity") or "medium").lower()
            raw_gaps.append(
                Gap(
                    id=str(g.get("id") or ""),
                    title=str(g.get("title") or "Document issue"),
                    detail=str(g.get("detail") or ""),
                    severity=severity if severity in {"high", "medium", "low"} else "medium",
                    action=str(g.get("action") or ""),
                )
            )
    gaps = _dedupe_gaps(raw_gaps + _rule_gaps(policy, bill, verdicts, req.narration))

    summary = str(raw.get("summary") or "").strip() or (
        f"{len([v for v in verdicts if v.verdict == 'covered'])} of {len(verdicts)} line items are covered. "
        f"Estimated payable amount is Rs. {totals.covered:,.0f}; the patient may need to pay about Rs. {totals.patient_pay:,.0f}. "
        f"{len(gaps)} document issue(s) need attention before submission."
    )
    return AnalysisResponse(
        facts=facts,
        verdicts=verdicts,
        gaps=gaps,
        totals=totals,
        summary=summary,
        mode=sarvam.mode,
        disclaimer=str(raw.get("disclaimer") or "Claim-It is an assistive demo, not legal or financial advice. Verify with your insurer."),
    )


def _rule_gaps(policy: PolicyFields, bill: BillFields, verdicts: list[Verdict], narration: str) -> list[Gap]:
    gaps: list[Gap] = []
    clauses_text = " ".join(c.text.lower() for c in policy.clauses)

    if "discharge summary" in clauses_text:
        gaps.append(
            Gap(
                id="AUTO-DISCHARGE",
                title="Discharge summary is missing",
                detail="A discharge summary is required with the claim and was not uploaded.",
                severity="high",
                action="Request the discharge summary and final itemised bill from the hospital records desk.",
            )
        )
    if "pre-authoris" in clauses_text or "pre-authoriz" in clauses_text or "pre authoris" in clauses_text:
        gaps.append(
            Gap(
                id="AUTO-PREAUTH",
                title="Pre-authorisation not obtained",
                detail="The policy requires emergency admission to be notified within 24 hours or pre-authorised before planned admission.",
                severity="high",
                action="Call the insurer/TPA helpline now, share the admission details, and ask about late notification.",
            )
        )
    a = _name_key(policy.insured_name)
    b = _name_key(bill.patient_name)
    if a and b and a != b:
        gaps.append(
            Gap(
                id="AUTO-NAME",
                title="Patient name mismatch",
                detail=f"Policy name '{policy.insured_name}' does not match bill name '{bill.patient_name}'.",
                severity="medium",
                action="Get the bill corrected, or attach ID/affidavit that links both names.",
            )
        )
    gaps.append(
        Gap(
            id="AUTO-ID",
            title="Government ID proof not uploaded",
            detail="A government ID is listed as a required claim document.",
            severity="low",
            action="Attach Aadhaar, PAN, or passport with the name matching the policy.",
        )
    )
    if bill.confidence and bill.confidence < 0.7:
        gaps.append(
            Gap(
                id="AUTO-OCR",
                title="Low-confidence document read",
                detail="At least one uploaded document was read with low confidence. Numbers or names may be wrong.",
                severity="medium",
                action="Check every extracted field against the original document and correct it before submitting.",
            )
        )
    unclear = [v for v in verdicts if v.verdict == "unclear"]
    if unclear:
        gaps.append(
            Gap(
                id="AUTO-UNCLEAR",
                title=f"{len(unclear)} bill line(s) need manual review",
                detail="The policy does not clearly cover: " + "; ".join(v.line_description for v in unclear[:3]),
                severity="medium",
                action="Ask the insurer/TPA to confirm these items in writing before submission.",
            )
        )
    if any(word in narration.lower() for word in ("accident", "दुर्घटना", "விபத்து", "ప్రమాద", "দুর্ঘটনা", "fell", "गिर")):
        # Accident claims are covered from day one; no waiting-period gap.
        pass
    return gaps


def _dedupe_gaps(gaps: list[Gap]) -> list[Gap]:
    keys = {
        "discharge": "discharge",
        "pre-auth": "preauth",
        "preauth": "preauth",
        "pre author": "preauth",
        "name": "name",
        "id proof": "id",
        "government id": "id",
        "prescription": "prescription",
        "low-confidence": "ocr",
        "low confidence": "ocr",
        "unclear": "unclear",
        "manual review": "unclear",
    }
    seen: set[str] = set()
    out: list[Gap] = []
    for gap in gaps:
        hay = f"{gap.id} {gap.title} {gap.detail}".lower()
        key = next((value for needle, value in keys.items() if needle in hay), gap.title.lower())
        if key in seen:
            continue
        seen.add(key)
        out.append(gap)
    order = {"high": 0, "medium": 1, "low": 2}
    out.sort(key=lambda g: order.get(g.severity, 3))
    return out


def _totals(bill: BillFields, verdicts: list[Verdict], policy: PolicyFields) -> dict:
    billed = sum(float(li.amount or 0) for li in bill.line_items) or float(bill.total_amount or 0)
    admissible = sum(float(v.covered_amount or 0) for v in verdicts)
    copay_percent = 0.0
    for clause in policy.clauses:
        text = f"{clause.title} {clause.text}".lower()
        if "co-pay" in text or "copay" in text or "co-payment" in text:
            match = re.search(r"(\d+(?:\.\d+)?)\s*%", text)
            if match:
                copay_percent = float(match.group(1))
                break
    copay_amount = admissible * copay_percent / 100
    covered = max(0.0, admissible - copay_amount)
    return {
        "billed": round(billed, 2),
        "admissible": round(admissible, 2),
        "copay_percent": copay_percent,
        "copay_amount": round(copay_amount, 2),
        "covered": round(covered, 2),
        "patient_pay": round(max(0.0, billed - covered), 2),
    }


def _clamp(value, default: float = 0.5) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return default


def _clamp_amount(value, maximum: float) -> float:
    try:
        return max(0.0, min(float(maximum), float(value)))
    except (TypeError, ValueError):
        return 0.0


def _name_key(name: str) -> str:
    return re.sub(r"[^a-z\u0900-\u097f\u0b80-\u0c7f\u0980-\u09ff]", "", (name or "").lower())


def _unique(values: list[str]) -> list[str]:
    out: list[str] = []
    for value in values:
        if value and value not in out:
            out.append(value)
    return out


@app.post("/api/draft", response_model=DraftResponse)
def draft(req: DraftRequest):
    _check_language(req.language)
    if not req.form.patient_name.strip():
        raise HTTPException(status_code=400, detail="Patient name is required for the claim letter.")
    letter = letters.draft_letter(req.language, req.form)
    return DraftResponse(letter=letter, language=req.language, mode=sarvam.mode)


@app.post("/api/speak")
def speak(req: SpeakRequest):
    _check_language(req.language)
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Nothing to speak. Run the coverage check first.")
    try:
        audio = sarvam.speak(text, req.language)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=f"Text-to-speech failed. Retry, or set MOCK_MODE=true. ({exc})")
    if not audio and not config.MOCK_MODE:
        raise HTTPException(status_code=502, detail="Text-to-speech returned no audio. Retry in a moment.")
    headers = {"X-Claimit-Mock": "true" if config.MOCK_MODE else "false"}
    return Response(content=audio, media_type="audio/wav", headers=headers)


# Serve the built frontend for a one-command demo, if it exists.
_DIST = config.ROOT / "frontend" / "dist"
if _DIST.exists():
    app.mount("/", StaticFiles(directory=str(_DIST), html=True), name="frontend")
