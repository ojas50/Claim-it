# Claim-It 🩺🗣️
**Insurance Claim Copilot for India: speak your story, snap your bills, get your claim ready.**

Claim-It helps policyholders file health and accident insurance claims in their own language. Narrate what happened by voice, upload photos of your policy and hospital bills (even crumpled, handwritten ones), and Claim-It checks coverage, finds missing documents, and drafts the claim for you.

---

## The Problem
Many insurance claims in India are delayed or rejected because of:
- Missing or mismatched documents
- Policy clauses that are hard to understand
- Paperwork and forms that are only in English
- Handwritten or poor-quality bills

## The Solution
A voice-first, vision-powered copilot that walks the user from "what happened" to "claim ready to submit".

| Step | What happens | Powered by |
|------|--------------|------------|
| 1. Voice intake | User narrates the event in their language | Sarvam **Saaras** (speech-to-text) |
| 2. Document parsing | Policy and bills (printed or handwritten) are read into structured data | Sarvam **Vision** |
| 3. Coverage check | Each bill line item is matched to policy clauses (covered / partial / not covered / unclear) with the exact clause cited and a confidence score | Sarvam **105B** |
| 4. Gap detection | Missing or inconsistent documents are listed with next steps | Sarvam **105B** |
| 5. Claim draft | Pre-filled, editable form and claim letter in the user's language, exportable as PDF | Sarvam **105B** |
| 6. Spoken reply | Summary and next steps read aloud | Sarvam **Bulbul** (text-to-speech) |

## Key Features
- 🎙️ Multilingual voice input (Hindi, Tamil, Telugu, Bengali and more)
- 📄 Handles crumpled and handwritten bills
- 🔍 Side-by-side view: original document crop next to extracted fields, so users can verify
- 📎 Every verdict cites the clause and the bill line it came from
- ✏️ Human-in-the-loop: all extracted fields are editable before submission
- 🧪 Mock mode so the demo works offline or if an API fails

## Tech Stack
- **Frontend:** Next.js (React), mobile-first UI
- **Backend:** FastAPI (Python)
- **AI:** Sarvam APIs (Saaras, Vision, 105B, Bulbul)
- **Export:** PDF generation for the claim letter and form

## Project Structure
```
claim-it/
├── frontend/            # Next.js app
├── backend/
│   ├── main.py          # FastAPI app
│   ├── sarvam_client.py # transcribe(), parse_document(), reason(), speak()
│   ├── coverage.py      # clause matching and gap detection
│   └── pdf_export.py
├── samples/             # synthetic policy, bills, Hindi narration script
├── .env.example
└── README.md
```

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.10+
- A Sarvam API key

### Setup
```bash
# 1. Clone
git clone <your-repo-url>
cd claim-it

# 2. Configure environment
cp .env.example .env
# add SARVAM_API_KEY=your_key_here
# set MOCK_MODE=true to run without API calls

# 3. Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# 4. Frontend (new terminal)
cd frontend
npm install
npm run dev
```
Open http://localhost:3000.

### Environment Variables
| Variable | Description |
|----------|-------------|
| `SARVAM_API_KEY` | Your Sarvam API key |
| `MOCK_MODE` | `true` returns canned responses for demos |

## Demo Scenario (3 minutes)
1. Open the app and tap the mic. Narrate a hospitalisation in Hindi (script in `samples/`).
2. Upload the sample policy PDF and the two bills (one printed, one handwritten).
3. Watch Claim-It extract the fields and show original crop vs. extracted data.
4. See the coverage verdicts: most items covered, one partially covered, one missing document flagged.
5. Edit a field, then generate the claim letter and download the PDF.
6. Tap play to hear the summary and next steps in Hindi.

## Responsible Use
Claim-It is an assistant, not legal or financial advice. Users review and edit all extracted data before submitting. Low-confidence results are flagged for manual checking.

## Roadmap
- WhatsApp and phone-call interface
- Direct integration with insurer and TPA portals
- Cashless pre-authorisation support
- More Indian languages and offline-friendly mode

## License
MIT
