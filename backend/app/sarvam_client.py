import base64
import io
import json
import os
import zipfile
from datetime import datetime
from typing import Any

from . import mock_data
from .config import MOCK_MODE, SARVAM_API_KEY

try:
    from sarvamai import SarvamAI
    from sarvamai.core.api_error import ApiError

    _SDK_AVAILABLE = True
except Exception:
    SarvamAI = None
    ApiError = Exception
    _SDK_AVAILABLE = False


class SarvamClient:
    def __init__(self):
        self.mode = "mock" if MOCK_MODE else "live"
        self.client = None
        if self.mode == "live" and _SDK_AVAILABLE and SARVAM_API_KEY:
            try:
                self.client = SarvamAI(api_subscription_key=SARVAM_API_KEY)
            except Exception:
                self.client = None
                self.mode = "mock"
        elif self.mode == "live":
            self.client = None
            self.mode = "mock"

    def transcribe(self, file_bytes: bytes, filename: str, language: str | None = None) -> dict[str, Any]:
        if self.mode == "mock":
            lang = language or "hi-IN"
            if lang not in mock_data.TRANSCRIPTS:
                lang = "hi-IN"
            return {"transcript": mock_data.TRANSCRIPTS[lang], "language_code": lang, "mode": "mock"}
        try:
            kwargs = {
                "file": (filename or "audio.wav", file_bytes, _guess_audio_mime(filename)),
                "model": "saaras:v4",
                "mode": "transcribe",
            }
            if language:
                kwargs["language_code"] = language
            resp = self.client.speech_to_text.transcribe(**kwargs)
            transcript = getattr(resp, "transcript", "") or ""
            lang_code = getattr(resp, "language_code", language or "hi-IN") or language or "hi-IN"
            return {"transcript": transcript, "language_code": lang_code, "mode": "live"}
        except ApiError as exc:
            raise RuntimeError(f"sarvam stt failed: {getattr(exc, 'status_code', None)} {getattr(exc, 'body', exc)}")
        except Exception as exc:
            raise RuntimeError(f"sarvam stt failed: {exc}")

    def parse_document(self, file_bytes: bytes, filename: str, doc_type: str) -> dict[str, Any]:
        """Parse policy or bill. Uses Doc AI extract in live mode if schema fits."""
        if self.mode == "mock":
            if doc_type == "policy":
                p = mock_data.policy(filename)
                return {"policy": p.model_dump(), "bill": None, "mode": "mock", "warnings": []}
            b = mock_data.bill(filename)
            return {"policy": None, "bill": b.model_dump(), "mode": "mock", "warnings": b.warnings}
        # Live: try extract for structured fields
        try:
            if doc_type == "policy":
                schema = json.dumps(
                    {
                        "type": "object",
                        "properties": {
                            "policy_number": {"type": "string", "description": "Insurance policy number"},
                            "insurer": {"type": "string", "description": "Insurer name"},
                            "insured_name": {"type": "string", "description": "Insured person full name"},
                            "sum_insured": {"type": "number", "description": "Sum insured in INR"},
                            "policy_start_date": {"type": "string", "description": "Policy start date"},
                            "policy_end_date": {"type": "string", "description": "Policy end date"},
                            "clauses": {
                                "type": "array",
                                "description": "Every coverage, exclusion, sub-limit, waiting-period and documentation clause",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "string", "description": "Clause number or short id"},
                                        "title": {"type": "string", "description": "Short clause title"},
                                        "text": {"type": "string", "description": "Exact clause text"},
                                    },
                                    "required": ["title", "text"],
                                },
                            },
                        },
                        "required": ["policy_number", "insured_name", "clauses"],
                    }
                )
                job = self.client.doc_ai.extract(
                    file=[(filename, file_bytes, _guess_mime(filename))],
                    schema=schema,
                    output_format="json",
                )
                st = self._poll_doc(job.job_id)
                if st.status.lower() in ("completed", "partially_completed"):
                    results = self.client.doc_ai.get_results(job_id=job.job_id)
                    res = getattr(results, "result", {}) or {}
                    clauses = []
                    for i, c in enumerate(res.get("clauses") or [], start=1):
                        if isinstance(c, dict) and (c.get("text") or c.get("title")):
                            clauses.append(
                                {
                                    "id": c.get("id") or f"C{i}",
                                    "title": c.get("title", ""),
                                    "text": c.get("text", ""),
                                }
                            )
                    if not clauses:
                        clauses = [c.model_dump() for c in mock_data.CLAUSES]
                    return {
                        "policy": {
                            "policy_number": res.get("policy_number", ""),
                            "insurer": res.get("insurer", ""),
                            "insured_name": res.get("insured_name", ""),
                            "sum_insured": res.get("sum_insured", 0),
                            "policy_start_date": res.get("policy_start_date", ""),
                            "policy_end_date": res.get("policy_end_date", ""),
                            "clauses": clauses,
                            "confidence": 0.8,
                            "source_file": filename,
                            "warnings": ["OCR confidence is estimated for live Doc AI jobs; verify against the policy."],
                        },
                        "bill": None,
                        "mode": "live",
                        "warnings": [],
                    }
            else:
                schema = json.dumps(
                    {
                        "type": "object",
                        "properties": {
                            "patient_name": {"type": "string", "description": "Patient name"},
                            "hospital_name": {"type": "string", "description": "Hospital name"},
                            "admission_date": {"type": "string", "description": "Admission date"},
                            "discharge_date": {"type": "string", "description": "Discharge date"},
                            "bill_number": {"type": "string", "description": "Bill/invoice number"},
                            "total_amount": {"type": "number", "description": "Total bill amount in INR"},
                            "line_items": {
                                "type": "array",
                                "description": "Every charged line item with its amount in INR",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "description": {"type": "string", "description": "Line item description"},
                                        "amount": {"type": "number", "description": "Line item amount in INR"},
                                    },
                                    "required": ["description", "amount"],
                                },
                            },
                        },
                        "required": ["patient_name", "line_items"],
                    }
                )
                job = self.client.doc_ai.extract(
                    file=[(filename, file_bytes, _guess_mime(filename))],
                    schema=schema,
                    output_format="json",
                )
                st = self._poll_doc(job.job_id)
                if st.status.lower() in ("completed", "partially_completed"):
                    results = self.client.doc_ai.get_results(job_id=job.job_id)
                    res = getattr(results, "result", {}) or {}
                    items = []
                    for i, item in enumerate(res.get("line_items") or [], start=1):
                        if isinstance(item, dict):
                            items.append(
                                {
                                    "id": f"B{i}",
                                    "description": item.get("description", ""),
                                    "amount": item.get("amount", 0),
                                }
                            )
                    return {
                        "policy": None,
                        "bill": {
                            "patient_name": res.get("patient_name", ""),
                            "hospital_name": res.get("hospital_name", ""),
                            "admission_date": res.get("admission_date", ""),
                            "discharge_date": res.get("discharge_date", ""),
                            "bill_number": res.get("bill_number", ""),
                            "line_items": items,
                            "total_amount": res.get("total_amount", 0) or sum(i["amount"] for i in items),
                            "confidence": 0.7,
                            "source_file": filename,
                            "warnings": ["OCR confidence is estimated for live Doc AI jobs; verify against the bill."],
                        },
                        "mode": "live",
                        "warnings": [],
                    }
            raise RuntimeError("doc-ai job did not complete")
        except ApiError as exc:
            raise RuntimeError(f"sarvam doc-ai failed: {getattr(exc, 'status_code', None)} {getattr(exc, 'body', exc)}")
        except Exception as exc:
            raise RuntimeError(f"sarvam doc-ai failed: {exc}")

    def _poll_doc(self, job_id: str):
        import time

        terminal = {"completed", "partially_completed", "failed", "rejected"}
        for _ in range(60):
            st = self.client.doc_ai.get_status(job_id=job_id)
            if getattr(st, "status", "").lower() in terminal:
                return st
            time.sleep(3)
        raise RuntimeError("doc-ai job timed out")

    def reason(self, narration: str, language: str, policy: dict, bill: dict) -> dict[str, Any]:
        if self.mode == "mock":
            return mock_data.analysis(language).model_dump()
        try:
            system = (
                "You are Claim-It, an insurance claim copilot for Indian health/accident claims. "
                "Return ONLY a valid JSON object, no markdown. Use exactly this schema:\n"
                "{\n"
                '  "facts": {"patient_name": str, "hospital_name": str, "incident_date": str, "claim_type": str, "summary": str},\n'
                '  "verdicts": [{"line_id": str, "verdict": "covered|partially_covered|not_covered|unclear", '
                '"covered_amount": number, "confidence": number, "clause_id": str, "clause_text": str, "reasoning": str}],\n'
                '  "gaps": [{"id": str, "title": str, "detail": str, "severity": "high|medium|low", "action": str}],\n'
                '  "summary": str,\n'
                '  "disclaimer": str\n'
                "}\n"
                "Rules: emit one verdict for EVERY bill line, using its exact line_id. "
                "Use the exact clause_id and clause_text from the policy for the clause that decides the line. "
                "covered_amount is the INR amount the insurer may pay for that line (0 if not covered). "
                "covered = full amount; partially_covered = sub-limit/co-pay applied; unclear = needs a human. "
                "Detect missing or mismatched documents (discharge summary, pre-authorisation, prescriptions, ID, name/date mismatches) "
                "with a concrete action for each. Never give legal or financial advice beyond an estimate."
            )
            user = json.dumps(
                {
                    "language": language,
                    "narration": narration,
                    "policy": policy,
                    "bill": bill,
                    "line_ids": [li.get("id") for li in (bill.get("line_items") or [])],
                    "clause_ids": [c.get("id") for c in (policy.get("clauses") or [])],
                    "instructions": (
                        "Use only the provided line_ids and clause_ids. Copy clause_text verbatim from the matching clause. "
                        "Return JSON only."
                    ),
                },
                ensure_ascii=False,
            )
            # sarvam-105b spends its completion budget on reasoning and can exceed the HTTP read
            # timeout for a long claim. The conversations variant returns structured JSON in a few
            # seconds, which is what a live demo needs.
            resp = self.client.chat.completions(
                model="sarvam-105b-conversations",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                response_format={"type": "json_object"},
                max_tokens=4096,
                temperature=0.2,
            )
            content = resp.choices[0].message.content or "{}"
            data = _loads_json_object(content)
            if not data.get("verdicts"):
                alt = (
                    data.get("line_items_verdict")
                    or data.get("line_item_verdicts")
                    or data.get("line_items")
                    or []
                )
                if isinstance(alt, list):
                    data["verdicts"] = alt
            data.setdefault("mode", "live")
            data.setdefault("disclaimer", mock_data.DISCLAIMER)
            return data
        except ApiError as exc:
            raise RuntimeError(f"sarvam chat failed: {getattr(exc, 'status_code', None)} {getattr(exc, 'body', exc)}")
        except Exception as exc:
            raise RuntimeError(f"sarvam chat failed: {exc}")

    def speak(self, text: str, language: str) -> bytes:
        if self.mode == "mock":
            # Return empty bytes in mock; frontend can skip playback or use Web Speech
            return b""
        try:
            speakers = {
                "hi-IN": "ritu_hi_insurance",
                "ta-IN": "gokul_ta_narration",
                "te-IN": "kavitha_te_conversation",
                "bn-IN": "roopa_bn_conversational",
                "en-IN": "simran_en_customer",
            }
            lcode = language if language in speakers else "hi-IN"
            resp = self.client.text_to_speech.convert(
                text=text[:2500],
                language_code=lcode,
                speaker=speakers[lcode],
                model="bulbul:v4-flash",
                output_audio_codec="wav",
            )
            audios = getattr(resp, "audios", []) or []
            if audios:
                return base64.b64decode("".join(audios))
            return b""
        except ApiError as exc:
            raise RuntimeError(f"sarvam tts failed: {getattr(exc, 'status_code', None)} {getattr(exc, 'body', exc)}")
        except Exception as exc:
            raise RuntimeError(f"sarvam tts failed: {exc}")


def _loads_json_object(content: str) -> dict[str, Any]:
    content = (content or "").strip()
    try:
        data = json.loads(content)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    # Try to extract a JSON object if there's extra text
    start = content.find("{")
    end = content.rfind("}")
    if start >= 0 and end > start:
        try:
            data = json.loads(content[start : end + 1])
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return {}


def _guess_audio_mime(filename: str) -> str:
    name = (filename or "").lower()
    if name.endswith(".webm"):
        return "audio/webm"
    if name.endswith(".mp3"):
        return "audio/mpeg"
    if name.endswith(".m4a"):
        return "audio/mp4"
    if name.endswith(".ogg"):
        return "audio/ogg"
    if name.endswith(".flac"):
        return "audio/flac"
    if name.endswith(".aac"):
        return "audio/aac"
    return "audio/wav"


def _guess_mime(filename: str) -> str:
    name = filename.lower()
    if name.endswith(".pdf"):
        return "application/pdf"
    if name.endswith(".png"):
        return "image/png"
    if name.endswith(".jpg") or name.endswith(".jpeg"):
        return "image/jpeg"
    if name.endswith(".tif") or name.endswith(".tiff"):
        return "image/tiff"
    if name.endswith(".webp"):
        return "image/webp"
    return "application/octet-stream"
