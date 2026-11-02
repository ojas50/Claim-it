# Claim-It

**Voice-first insurance claim copilot for Indian policyholders.**

Claim-It turns a spoken accident/hospitalisation story and photos of messy paperwork into a clear coverage check, a list of missing documents, and a ready-to-send claim letter — in the user's own language.

> Hackathon demo. Not legal, medical, or financial advice. Every coverage outcome is an estimate and must be verified with the insurer.

---

## Why it matters

Health and accident claims in India are delayed or rejected because of missing documents, unclear policy clauses, and forms that assume English. Claim-It lets a user explain the situation in Hindi, Tamil, Telugu, Bengali or English, then does the paperwork work for them:

- **Voice intake** with Sarvam Saaras (`saaras:v4`).
- **Policy + bill reading** with Sarvam Vision Document AI extract, including handwritten bills.
- **Line-by-line coverage reasoning** with Sarvam-105B, citing the exact policy clause and a confidence score.
- **Gap detection** for missing discharge summaries, pre-authorisation, name/date mismatches, prescriptions and ID proof.
- **Editable claim form + plain-language letter**, printable to PDF.
- **Spoken summary** with Sarvam Bulbul (`bulbul:v4-flash`).
- **Mock mode** so the whole demo works with no network or API key.

---

## Demo scenario

The repo ships one coherent synthetic scenario:

| Field | Value |
| --- | --- |
| Patient | Sunita Sharma, 54 |
| Incident | Fall from stairs, fractured right wrist |
| Hospital | CityCare Multispeciality Hospital, Jaipur |
| Dates | 24–27 October 2026 |
| Policy | `BSG-HS-2025-88421`, Bharat Suraksha General Insurance |
| Sum insured | ₹5,00,000 |
| Billed | ₹1,54,700 |
| Admissible after exclusions/sub-limits | ₹1,34,700 |
| 10% non-network co-pay | ₹13,470 |
| Estimated covered | **₹1,21,230** |
| Estimated patient share | **₹33,470** |
| Gaps | Discharge summary, pre-authorisation, name mismatch, pharmacy prescription, ID proof |

Generated samples live in [`samples/`](samples/):

- `policy.pdf` — 9 clauses (room/ICU sub-limits, consumables exclusion, accident cover, co-pay, pre-auth, documents, pharmacy).
- `bill_printed.png` — itemised hospital bill, 11 lines, ₹1,54,700.
- `bill_handwritten.png` — pharmacy bill with `Sunita S.` (intentional name mismatch), ₹5,700.
- `narration_hi.txt` (plus `en`, `ta`, `te`, `bn`) — the spoken narration script.

Regenerate the pack at any time:

```bash
python samples/generate_samples.py
```

---

## Architecture

```text
React + Vite (mobile-first 5-step wizard)
        │  JSON / multipart
        ▼
FastAPI backend
        │
        ▼
backend/app/sarvam_client.py   ← the only place that calls Sarvam
   ├── transcribe()       Saaras v4        /speech-to-text
   ├── parse_document()   Sarvam Vision    /doc-ai/v1/job/extract
   ├── reason()           Sarvam-105B      /v1/chat/completions
   └── speak()            Bulbul v4 Flash  /text-to-speech
```

`MOCK_MODE=true` short-circuits all four functions with canned data. If the key or SDK is missing, the backend automatically falls back to mock mode.

### File tree

```text
claim-it/
├─ backend/
│  ├─ app/
│  │  ├─ main.py             FastAPI routes, normalization, totals, gap rules
│  │  ├─ models.py           Pydantic response/request models
│  │  ├─ config.py           .env loader, MOCK_MODE, language list, paths
│  │  ├─ sarvam_client.py    single Sarvam integration module
│  │  ├─ mock_data.py        canonical demo scenario and canned responses
│  │  └─ letters.py          multilingual claim-letter templates
│  └─ requirements.txt
├─ frontend/
│  ├─ src/
│  │  ├─ App.jsx             wizard state, step gating, print area
│  │  ├─ api.js              typed-ish fetch wrappers
│  │  ├─ i18n.js             languages, sample narration, speech fallback
│  │  ├─ styles.css          mobile-first design + print styles
│  │  └─ components/         Voice, Documents, Coverage, Claim, Final
│  ├─ vite.config.js         proxies /api and /samples to FastAPI
│  └─ package.json
├─ samples/                  policy PDF, two bill images, narration scripts
├─ .env.example
├─ demo_script.md
└─ pitch.md
```

---

## Quickstart (mock mode, recommended for the demo)

**1. Backend**

```bash
cd backend
python -m pip install -r requirements.txt
```

Create `.env` in the repo root:

```bash
copy .env.example .env      # Windows
# cp .env.example .env      # macOS / Linux
```

Leave `MOCK_MODE=true` and run:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**2. Frontend** (second terminal)

```bash
cd frontend
npm install
npm run dev
```

Open <http://127.0.0.1:5173>.

**3. Demo path**

1. **Narrate** → “Use sample narration” → Next.
2. **Documents** → “Load sample set” → wait for extraction → “Check coverage”.
3. **Coverage** → review verdicts, clause quotes, confidence and gaps.
4. **Claim** → edit fields/letter → “Save as PDF” (browser print dialog).
5. **Reply** → “Play the summary” (browser voice in mock mode).

### One-command production demo (optional)

```bash
cd frontend
npm run build
cd ../backend
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

FastAPI serves `frontend/dist` at <http://127.0.0.1:8000> if the build exists.

---

## Live Sarvam mode

> **Cost note:** live mode sends real audio, documents and text to Sarvam and consumes credits. Test with the sample pack first.

1. Put your key in `.env`:

   ```dotenv
   MOCK_MODE=false
   SARVAM_API_KEY=your_key_here
   ```

2. Restart the backend. `GET /api/health` should report `"mode": "live"`.

3. Record real narration (or use the sample script) and upload the sample files.

### Verified Sarvam endpoints and models

Checked against the official docs during the build:

| Capability | Model / endpoint | Notes |
| --- | --- | --- |
| Speech-to-text | `saaras:v4`, `POST /speech-to-text` | Uses `mode="transcribe"`; language auto-detected when not supplied. |
| Text-to-speech | `bulbul:v4-flash`, `POST /text-to-speech` | Response is an `audios` array of **base64** WAV strings; decoded server-side. |
| Document extraction | Sarvam Vision 2.1, `POST /doc-ai/v1/job/extract` | Async job: submit → poll status → fetch results. |
| Reasoning | `sarvam-105b-conversations`, `POST /v1/chat/completions` | Uses `response_format={"type":"json_object"}` and `max_tokens=4096`. The full `sarvam-105b` reasoning model is available but spends its completion budget on reasoning tokens; with a large claim payload it can exceed the HTTP read timeout, so the conversations variant is the demo-safe default. |

**Uncertainty / discrepancy:** the Doc AI extract docs list a `language` parameter, but the installed `sarvamai 0.1.42` SDK does not expose it on `doc_ai.extract()`. Claim-It omits it and relies on auto-detection. If you upgrade the SDK, pass `language` there if supported.

**Deterministic post-processing:** the backend re-checks every model verdict. It clamps confidence, recomputes covered amounts from the bill lines, parses the co-pay percentage from the policy text, recalculates totals, and adds rule-based gaps. The LLM cannot drift the final arithmetic.

### Speakers used

| Language | Speaker |
| --- | --- |
| Hindi | `ritu_hi_insurance` |
| Tamil | `gokul_ta_narration` |
| Telugu | `kavitha_te_conversation` |
| Bengali | `roopa_bn_conversational` |
| English | `simran_en_customer` |

---

## API

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Mode, key presence, model names. |
| `POST` | `/api/transcribe` | Multipart `file` (audio) + `language`. |
| `POST` | `/api/parse` | Multipart repeated `files` + `kinds="policy,bill,bill"` + `language`. |
| `POST` | `/api/analyze` | JSON narration + language + parsed policy/bill. |
| `POST` | `/api/draft` | JSON language + editable claim form. |
| `POST` | `/api/speak` | JSON text + language; returns WAV or an empty mock body. |
| `GET` | `/samples/*` | Static sample pack. |

Mock `/api/speak` returns HTTP 200, `X-Claimit-Mock: true` and zero bytes. The frontend detects this and falls back to the browser’s `speechSynthesis` with a localised summary.

---

## Error handling

- Unsupported language → HTTP 400 with the supported list.
- Empty/unreadable upload → HTTP 400; wrong file type → HTTP 415; over 20 MB → HTTP 413.
- Low OCR confidence → warning banner and an explicit “check every field” gap.
- Sarvam failure → HTTP 502 with a retry hint; the UI shows the error and keeps the user’s data.
- Empty transcript → warning to retry or type the narration.
- Name/date mismatches → automatic gap with a concrete action.
- Missing clauses or line items → warning plus manual editing before analysis.
- Every extracted field and letter is editable (human-in-the-loop).

---

## Tests run

```bash
# Backend syntax
cd backend
python -m py_compile app/*.py

# Frontend production build
cd ../frontend
npm run build
```

Mock API smoke test (happy path):

```text
health: ok mock
transcribe: मेरी माँ सुनीता शर्मा ... | lang: hi-IN
parse: BSG-HS-2025-88421 | lines: 11 | total: 154700.0
analyze: verdicts 11 | gaps 6 | covered 121230.0 | patient_pay 33470.0
draft: सेवा में, | chars: 757
speak: 200 | mock header: true | bytes: 0
```

Live Sarvam smoke test (real key, sample pack):

```text
health: live | chat: sarvam-105b-conversations
tts: 200 | audio/wav RIFF | 148220 bytes | 1.0s
stt: 200 | Hindi transcript | 0.6s
parse: BSG-HS-2025-88421 | clauses 9 | line items 14 | total 160400.0 | 16.1s
analyze: 14 verdicts | 4 gaps | covered 105030.0 | patient_pay 55370.0 | 7.7s
draft: 727 chars | 0.1s
```

Live extraction can legitimately differ from the canned scenario (for example, it itemises the handwritten pharmacy bill into extra lines). Mock mode remains the deterministic demo path.

---

## Limitations and next steps

- Doc AI extract is polled; a live job can take longer than the demo window. Mock mode is the stage-safe path.
- The live bill schema asks for line items, but real-world OCR may still need manual correction — this is why every field is editable.
- PDF export uses the browser print dialog so Indic scripts render with the device’s fonts. No server-side PDF font embedding.
- Coverage verdicts are estimates, not a claim decision. The disclaimer is shown in the UI and in the letter.
- Next: WhatsApp bot, insurer/TPA APIs, hospital network lookup, claim-status tracking, audit trail for edits.

---

## Environment variables

| Name | Default | Meaning |
| --- | --- | --- |
| `MOCK_MODE` | `true` | `true` = canned responses, no Sarvam calls. |
| `SARVAM_API_KEY` | empty | Required only when `MOCK_MODE=false`. Never commit `.env`. |

Optional frontend override: `VITE_API_BASE` (e.g. a deployed backend URL). Leave empty for the Vite proxy.

---

## Key features at a glance

- 🎙️ Multilingual voice intake — Hindi, Tamil, Telugu, Bengali, English.
- 📄 Reads printed **and** handwritten bills; flags low-confidence fields.
- 🔍 Side-by-side view: original document next to editable extracted fields.
- 📎 Every verdict cites the clause, the bill line, and a confidence score.
- ✏️ Human-in-the-loop: all fields and the letter are editable before export.
- 🧪 Mock mode so the demo works offline or if an API fails.

## License / disclaimer

MIT License. Built for a hackathon. Synthetic data only. Not affiliated with any insurer. Not legal, medical, or financial advice.
