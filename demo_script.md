# Claim-It — 3 Minute Demo Script

*Audience:* Judges (product + tech). *Mode:* Demo (MOCK_MODE=true). *Setup:* Backend + frontend running locally.

## Timing
| Section | Time | Goal |
| --- | --- | --- |
| Hook | 0:00–0:20 | State the problem |
| Voice intake | 0:20–0:50 | Show Hindi narration + transcript |
| Documents | 0:50–1:10 | Load the sample pack, show side-by-side parsing |
| Coverage | 1:10–1:40 | Show line-by-line verdicts, clause citations, gaps |
| Draft & PDF | 1:40–2:10 | Edit form/letter and show “Save as PDF” |
| Spoken reply | 2:10–3:00 | Play summary, show next steps, wrap up | 

## Step by step

### 1) Hook (0:00–0:20)
*"Health and accident insurance claims in India get delayed or rejected over missing documents, unclear clauses, and messy paperwork. Claim-It is a voice-first copilot that speaks your language and turns it all into a claim you can actually send."*

Show the home screen (demo mode badge).

### 2) Voice intake (0:20–0:50)
1. Language = Hindi (or Tamil/Telugu/Bengali/English).
2. Tap **Use sample narration**.
3. Point out the editable **transcript**: “The user can correct OCR/ASR mistakes before moving on.”
4. Click **Next: Upload documents**.

*Note:* In live mode this would use Sarvam Saaras (`saaras:v4`). In demo mode we use the canned transcript.

### 3) Documents (0:50–1:10)
1. Click **Load sample set**. It pulls `policy.pdf`, `bill_printed.png` and `bill_handwritten.png` from `/samples`.
2. Show **side-by-side view**: original document on the left, extracted fields on the right.
3. Scroll the **Policy clauses** (room rent 1%, ICU 2%, consumables excluded, accident cover day-one, 10% co-pay, pre-authorisation).
4. Scroll **bill lines** (11 items). Call out the **handwritten pharmacy bill** matching with lower confidence (a real-world edge case).
5. Click **Check coverage**.

### 4) Coverage (1:10–1:40)
Show the totals:
- Billed ₹1,54,700 → Likely covered ₹1,21,230 → You may pay ₹33,470

Open **Line-by-line verdicts**:
- **Partly covered:** Room rent (cited Clause C1 — 1% daily cap) → ₹20,000 payable of ₹30,000.
- **Covered:** Surgery, ICU, diagnostics (Clause C5).
- **Not covered:** Consumables/dressings (Clause C3).
- **Needs review:** Calcium/vitamin D supplements (needs prescription).

Show **Document gaps & next steps** (sorted by priority): discharge summary, pre-authorisation, name mismatch (`Sunita Sharma` vs `Sunita S.`), prescription, ID proof.

### 5) Draft & PDF (1:40–2:10)
1. Click **Draft the claim**.
2. Show the pre-filled **Claim details** (editable). Amount defaults to billed total.
3. Read a snippet of the **Hindi claim letter**. Edit one line to show human-in-the-loop.
4. Click **Save as PDF** (browser print dialog) — show Hindi text rendering correctly.
5. Click **Hear the summary**.

### 6) Spoken reply (2:10–3:00)
1. Click **Play the summary & next steps**.
2. In demo mode it falls back to the browser voice with a localised summary; in live mode Sarvam Bulbul speaks it.
3. Read the **What to do next** checklist.
4. Click **Start a new claim** to show it resets cleanly.

## Demo tips
- **Keep it in Hindi** for maximum impact, or switch languages to show i18n.
- **Show editing** — change a clause or a bill line amount and see that the UI keeps it editable.
- **Point to the disclaimer** — “not legal, medical, or financial advice”.
- **Mention mock mode** — the same UI runs against real Sarvam with `MOCK_MODE=false`.
- **Show the sample pack** — `samples/` contains the PDF and both images.
