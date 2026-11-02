"""Generate the synthetic Claim-It demo pack.

Run from the repo root:  python samples/generate_samples.py
Outputs:
  samples/policy.pdf
  samples/bill_printed.png
  samples/bill_handwritten.png
  samples/narration_{hi,en,ta,te,bn}.txt
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.mock_data import BILL_LINES, CLAUSES, TRANSCRIPTS

SAMPLES = ROOT / "samples"
SAMPLES.mkdir(parents=True, exist_ok=True)

FONT_DIR = Path("C:/Windows/Fonts")


def font(name: str, size: int):
    path = FONT_DIR / name
    if not path.exists():
        return ImageFont.load_default()
    return ImageFont.truetype(str(path), size)


# --------------------------------------------------------------------------
# 1. Policy PDF
# --------------------------------------------------------------------------


def build_policy() -> None:
    out = SAMPLES / "policy.pdf"
    doc = SimpleDocTemplate(
        str(out),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="Family Health Shield - Policy Schedule",
        author="Bharat Suraksha General Insurance",
    )

    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.2,
        leading=13,
        textColor=colors.HexColor("#23312e"),
        alignment=TA_LEFT,
        spaceAfter=5,
    )
    small = ParagraphStyle("Small", parent=body, fontSize=7.6, leading=10)
    h1 = ParagraphStyle(
        "H1",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=21,
        textColor=colors.white,
        spaceAfter=2,
    )
    h2 = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11.5,
        leading=14,
        textColor=colors.HexColor("#0f766e"),
        spaceBefore=10,
        spaceAfter=5,
    )
    clause_title = ParagraphStyle(
        "ClauseTitle",
        parent=body,
        fontName="Helvetica-Bold",
        fontSize=8.8,
        leading=11,
        spaceAfter=1,
    )
    label = ParagraphStyle(
        "Label",
        parent=small,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#5c6d68"),
    )
    value = ParagraphStyle("Value", parent=body, fontSize=9.4, leading=12, spaceAfter=0)

    def banner(canvas, _doc):
        canvas.saveState()
        canvas.setFillColor(colors.HexColor("#0f766e"))
        canvas.rect(0, A4[1] - 30 * mm, A4[0], 30 * mm, stroke=0, fill=1)
        canvas.setFillColor(colors.HexColor("#99f6e4"))
        canvas.setFont("Helvetica-Bold", 8)
        canvas.drawString(18 * mm, A4[1] - 13 * mm, "BHARAT SURAKSHA GENERAL INSURANCE")
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 15)
        canvas.drawString(18 * mm, A4[1] - 21 * mm, "Family Health Shield")
        canvas.setFont("Helvetica", 8.5)
        canvas.drawString(18 * mm, A4[1] - 26 * mm, "Policy schedule and coverage conditions")
        canvas.setFillColor(colors.HexColor("#ccfbf1"))
        canvas.setFont("Helvetica", 7)
        canvas.drawRightString(A4[0] - 18 * mm, A4[1] - 13 * mm, "Policy No. BSG-HS-2025-88421")
        canvas.restoreState()

    def footer(canvas, _doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#d7e0dc"))
        canvas.line(18 * mm, 13 * mm, A4[0] - 18 * mm, 13 * mm)
        canvas.setFillColor(colors.HexColor("#6b7c77"))
        canvas.setFont("Helvetica", 7)
        canvas.drawString(
            18 * mm,
            9 * mm,
            "Bharat Suraksha General Insurance Ltd. | IRDAI Reg. No. 144 | This is a synthetic demo document.",
        )
        canvas.drawRightString(A4[0] - 18 * mm, 9 * mm, f"Page {doc.page}")
        canvas.restoreState()

    story = []
    story.append(Spacer(1, 22 * mm))

    details = [
        [Paragraph("Policy number", label), Paragraph("BSG-HS-2025-88421", value),
         Paragraph("Sum insured", label), Paragraph("Rs. 5,00,000", value)],
        [Paragraph("Insured name", label), Paragraph("Sunita Sharma", value),
         Paragraph("Policy period", label), Paragraph("01 Apr 2025 - 31 Mar 2026", value)],
        [Paragraph("Plan", label), Paragraph("Family Health Shield - Silver", value),
         Paragraph("Hospital network", label), Paragraph("Non-network cashless / reimbursement", value)],
        [Paragraph("Insured age", label), Paragraph("54 years", value),
         Paragraph("Customers", label), Paragraph("Self + spouse + two children", value)],
    ]
    table = Table(details, colWidths=[30 * mm, 47 * mm, 27 * mm, 55 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f4f9f7")),
                ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#cfe3de")),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#dcebe7")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("Coverage summary", h2))
    story.append(
        Paragraph(
            "This policy covers medically necessary hospitalisation for accident and illness, subject to the "
            "sum insured, sub-limits, exclusions, waiting periods and co-payment conditions below. Accidental "
            "injury is covered from day one. All claims require the documents listed in Clause C8.",
            body,
        )
    )

    story.append(Paragraph("Policy clauses and conditions", h2))
    for clause in CLAUSES:
        story.append(
            KeepTogether(
                [
                    Paragraph(f"{clause.id}. {clause.title}", clause_title),
                    Paragraph(clause.text, body),
                ]
            )
        )

    story.append(Spacer(1, 8))
    story.append(Paragraph("How to claim", h2))
    story.append(
        Paragraph(
            "For cashless treatment at a network hospital, show this policy at the insurance desk and obtain "
            "pre-authorisation. For reimbursement, pay the hospital, collect the itemised bill, discharge summary, "
            "prescriptions, investigation reports and government ID, then submit the claim within 30 days of "
            "discharge through the insurer portal or TPA helpline.",
            body,
        )
    )
    story.append(Spacer(1, 5))
    story.append(
        Paragraph(
            "<b>Important:</b> This is a synthetic document created for the Claim-It hackathon demo. It is not a "
            "real insurance contract and creates no coverage rights.",
            small,
        )
    )

    doc.build(story, onFirstPage=banner, onLaterPages=banner)
    print(f"wrote {out}")


# --------------------------------------------------------------------------
# 2. Printed hospital bill
# --------------------------------------------------------------------------


def build_printed_bill() -> None:
    W, H = 1000, 1414
    img = Image.new("RGB", (W, H), "#ffffff")
    draw = ImageDraw.Draw(img)

    ink = "#1f2d2a"
    muted = "#5f706b"
    brand = "#0f766e"

    draw.rectangle([0, 0, W, 8], fill=brand)
    draw.text((70, 45), "CITYCARE", font=font("segoeuib.ttf", 44), fill=brand)
    draw.text((70, 98), "MULTISPECIALITY HOSPITAL", font=font("segoeuib.ttf", 19), fill=ink)
    draw.text(
        (70, 128),
        "Plot 14, Malviya Nagar, Jaipur, Rajasthan 302017  |  GSTIN 08AABCU9603R1ZX",
        font=font("segoeui.ttf", 14),
        fill=muted,
    )
    draw.text((70, 150), "Tel: 0141-400-2200  |  billing@citycare.example", font=font("segoeui.ttf", 14), fill=muted)

    draw.line([(70, 185), (W - 70, 185)], fill="#c9d6d2", width=2)
    draw.text((70, 205), "INPATIENT BILL / CASH MEMO", font=font("segoeuib.ttf", 25), fill=ink)
    draw.text((W - 70, 212), "ORIGINAL FOR INSURER", font=font("segoeui.ttf", 12), fill=muted, anchor="ra")

    rows = [
        ("Patient name", "Sunita Sharma"),
        ("Age / Sex", "54 / Female"),
        ("UHID", "CC-OPD-88214"),
        ("Bill number", "CC-2026-10427"),
        ("Admission", "24 Oct 2026, 22:10"),
        ("Discharge", "27 Oct 2026, 11:40"),
        ("Consultant", "Dr. A. Mehta, Orthopaedics"),
        ("Payment", "Self pay (reimbursement)"),
    ]
    y = 252
    for i, (key, val) in enumerate(rows):
        col = 70 if i % 2 == 0 else 530
        row = i // 2
        yy = y + row * 34
        draw.text((col, yy), f"{key}:", font=font("segoeuib.ttf", 14), fill=muted)
        draw.text((col + 118, yy), val, font=font("segoeui.ttf", 14), fill=ink)

    top = y + 4 * 34 + 30
    draw.rectangle([70, top, W - 70, top + 36], fill="#eaf4f1")
    draw.text((86, top + 9), "DESCRIPTION", font=font("segoeuib.ttf", 13), fill=ink)
    draw.text((W - 86, top + 9), "AMOUNT (Rs.)", font=font("segoeuib.ttf", 13), fill=ink, anchor="ra")

    yy = top + 36
    for index, line in enumerate(BILL_LINES):
        if index % 2 == 0:
            draw.rectangle([70, yy, W - 70, yy + 34], fill="#fafcfb")
        draw.text((86, yy + 8), line.description, font=font("segoeui.ttf", 14), fill=ink)
        draw.text((W - 86, yy + 8), f"{line.amount:,.0f}", font=font("segoeui.ttf", 14), fill=ink, anchor="ra")
        yy += 34

    draw.line([(70, yy), (W - 70, yy)], fill="#c9d6d2", width=2)
    yy += 16
    subtotal = sum(line.amount for line in BILL_LINES)
    draw.text((W - 360, yy), "Subtotal", font=font("segoeui.ttf", 14), fill=muted)
    draw.text((W - 86, yy), f"{subtotal:,.0f}", font=font("segoeui.ttf", 14), fill=ink, anchor="ra")
    yy += 28
    draw.text((W - 360, yy), "Discount / concession", font=font("segoeui.ttf", 14), fill=muted)
    draw.text((W - 86, yy), "0", font=font("segoeui.ttf", 14), fill=ink, anchor="ra")
    yy += 34
    draw.rectangle([560, yy, W - 70, yy + 46], fill=brand)
    draw.text((576, yy + 13), "TOTAL PAYABLE", font=font("segoeuib.ttf", 16), fill="#ffffff")
    draw.text((W - 86, yy + 12), f"Rs. {subtotal:,.0f}", font=font("segoeuib.ttf", 19), fill="#ffffff", anchor="ra")

    yy += 74
    draw.text((70, yy), "Amount in words: One lakh fifty-four thousand seven hundred rupees only.", font=font("segoeuii.ttf", 13), fill=muted)
    yy += 34
    draw.text(
        (70, yy),
        "Includes room, ICU, surgery, anaesthesia, medicines, diagnostics, physiotherapy and consumables.",
        font=font("segoeui.ttf", 12.5),
        fill=muted,
    )

    # Paid stamp
    draw.ellipse([W - 320, H - 330, W - 80, H - 160], outline="#b91c1c", width=5)
    draw.text((W - 200, H - 278), "PAID", font=font("segoeuib.ttf", 40), fill="#b91c1c", anchor="mm")
    draw.text((W - 200, H - 232), "27 OCT 2026", font=font("segoeui.ttf", 15), fill="#b91c1c", anchor="mm")

    draw.line([(70, H - 130), (W - 70, H - 130)], fill="#c9d6d2", width=1)
    draw.text(
        (70, H - 110),
        "Computer-generated bill. Please retain this original for insurance submission.",
        font=font("segoeui.ttf", 11.5),
        fill=muted,
    )
    draw.text((W - 70, H - 110), "Page 1 of 1", font=font("segoeui.ttf", 11.5), fill=muted, anchor="ra")

    out = SAMPLES / "bill_printed.png"
    img.save(out, "PNG", optimize=True)
    print(f"wrote {out}")


# --------------------------------------------------------------------------
# 3. Handwritten pharmacy bill
# --------------------------------------------------------------------------


def build_handwritten_bill() -> None:
    W, H = 1000, 1250
    img = Image.new("RGB", (W, H), "#fffdf5")
    draw = ImageDraw.Draw(img)

    # Ruled notebook paper
    for y in range(150, H - 60, 46):
        draw.line([(60, y), (W - 50, y)], fill="#dbe7f3", width=1)
    draw.line([(105, 60), (105, H - 60)], fill="#f0b4b4", width=2)

    title_font = font("segoesc.ttf", 44)
    hand = font("segoesc.ttf", 27)
    hand_small = font("segoesc.ttf", 22)
    ink = "#1e3a8a"

    draw.text((140, 52), "CityCare Pharmacy", font=title_font, fill=ink)
    draw.text((143, 108), "Inside CityCare Hospital, Malviya Nagar, Jaipur", font=hand_small, fill="#3b5a9a")
    draw.text((143, 142), "Ph: 0141-400-2211    GSTIN: 08AAACC1234D1Z2", font=hand_small, fill="#3b5a9a")

    draw.text((620, 200), "Date: 27/10/2026", font=hand, fill=ink)
    draw.text((620, 238), "Bill No: PH-4471", font=hand, fill=ink)
    draw.text((143, 200), "Patient: Sunita S.", font=hand, fill=ink)
    draw.text((143, 238), "Hospital bill: CC-2026-10427", font=hand_small, fill=ink)

    draw.text((143, 300), "Qty        Item", font=hand, fill=ink)
    draw.text((760, 300), "Amount", font=hand, fill=ink)
    draw.line([(140, 338), (860, 338)], fill="#3b5a9a", width=2)

    items = [
        ("1", "Painkillers + antibiotics (IV)", "3,200"),
        ("1", "Calcium + Vitamin D supplements", "1,800"),
        ("2", "Bandage + crepe roll", "700"),
    ]
    y = 360
    for qty, desc, amount in items:
        draw.text((143, y), qty, font=hand, fill=ink)
        draw.text((215, y), desc, font=hand, fill=ink)
        draw.text((885, y), amount, font=hand, fill=ink, anchor="ra")
        y += 54

    draw.line([(140, y + 6), (860, y + 6)], fill="#3b5a9a", width=2)
    draw.text((560, y + 24), "Total", font=font("segoescb.ttf", 31), fill=ink)
    draw.text((885, y + 24), "5,700", font=font("segoescb.ttf", 31), fill=ink, anchor="ra")

    draw.text((143, y + 100), "Rupees five thousand seven hundred only.", font=hand_small, fill="#3b5a9a")
    draw.text((143, y + 150), "For CityCare Pharmacy", font=hand_small, fill="#3b5a9a")
    draw.text((640, y + 170), "R. Nair", font=font("segoesc.ttf", 34), fill=ink)
    draw.line([(640, y + 214), (860, y + 214)], fill="#3b5a9a", width=1)
    draw.text((640, y + 220), "Pharmacist", font=hand_small, fill="#3b5a9a")

    # Small handwriting wobble on a few strokes is hard to do well; a light paper texture is enough.
    for i in range(0, W, 3):
        for j in range(0, H, 3):
            if (i * 7 + j * 13) % 97 == 0:
                draw.point((i, j), fill="#f4efe2")

    out = SAMPLES / "bill_handwritten.png"
    img.save(out, "PNG", optimize=True)
    print(f"wrote {out}")


# --------------------------------------------------------------------------
# 4. Narration scripts
# --------------------------------------------------------------------------


def write_narrations() -> None:
    names = {"hi-IN": "hi", "en-IN": "en", "ta-IN": "ta", "te-IN": "te", "bn-IN": "bn"}
    for code, suffix in names.items():
        out = SAMPLES / f"narration_{suffix}.txt"
        out.write_text(TRANSCRIPTS[code] + "\n", encoding="utf-8")
        print(f"wrote {out}")


if __name__ == "__main__":
    build_policy()
    build_printed_bill()
    build_handwritten_bill()
    write_narrations()
    print("Sample pack ready.")
