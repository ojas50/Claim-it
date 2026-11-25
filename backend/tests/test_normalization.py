"""Unit tests for the deterministic layer that keeps model output honest."""
from app import mock_data
from app.main import _dedupe_gaps, _merge_bills, _normalize_analysis, _totals
from app.models import AnalyzeRequest, Gap, PolicyFields


def _request():
    return AnalyzeRequest(
        narration=mock_data.TRANSCRIPTS["hi-IN"],
        language="hi-IN",
        policy=mock_data.policy(),
        bill=mock_data.bill(),
    )


def test_normalization_clamps_amounts_and_rejects_unknown_clauses():
    req = _request()
    raw = {
        "verdicts": [
            {
                "line_id": "B1",
                "verdict": "covered",
                "covered_amount": 999999,
                "confidence": 5,
                "clause_id": "C-NOPE",
                "clause_text": "",
            },
            {
                "line_id": "B2",
                "verdict": "partially_covered",
                "covered_amount": 20000,
                "confidence": -2,
                "clause_id": "C1",
            },
        ],
        "gaps": [
            {
                "title": "Discharge summary is missing",
                "detail": "from the model",
                "severity": "critical",
                "action": "Ask the hospital",
            },
            {
                "title": "Discharge summary not uploaded",
                "detail": "duplicate from the model",
                "severity": "high",
            },
        ],
        "facts": {"patient_name": "Sunita Sharma"},
        "summary": "",
    }

    result = _normalize_analysis(raw, req)

    # Every bill line must have a verdict; the invented line ID is ignored.
    assert len(result.verdicts) == 11
    by_id = {v.line_id: v for v in result.verdicts}

    first = by_id["B1"]
    assert first.verdict == "unclear"  # covered verdict without a real clause is downgraded
    assert first.covered_amount == 0
    assert first.confidence == 1.0  # clamped from 5
    assert "Manual review needed" in first.clause_text

    second = by_id["B2"]
    assert second.verdict == "partially_covered"
    assert second.covered_amount == 18000.0  # clamped to the line amount
    assert second.confidence == 0.0  # clamped from -2
    assert second.clause_id == "C1"
    assert second.clause_text == req.policy.clauses[0].text

    assert by_id["B3"].verdict == "unclear"  # missing verdicts are filled in
    assert by_id["B3"].confidence == 0.35

    discharge_gaps = [g for g in result.gaps if "discharge summary" in g.title.lower()]
    assert len(discharge_gaps) == 1  # duplicates are collapsed
    assert all(g.severity in {"high", "medium", "low"} for g in result.gaps)

    assert result.facts.patient_name == "Sunita Sharma"
    assert "line items are covered" in result.summary  # generated when the model omits it


def test_totals_recompute_copay_and_patient_share():
    req = _request()
    verdicts = mock_data.analysis().verdicts
    totals = _totals(req.bill, verdicts, req.policy)

    assert totals["billed"] == 154700.0
    assert totals["admissible"] == 134700.0
    assert totals["copay_percent"] == 10.0
    assert totals["copay_amount"] == 13470.0
    assert totals["covered"] == 121230.0
    assert totals["patient_pay"] == 33470.0

    no_copay_policy = PolicyFields(
        clauses=[{"id": "C1", "title": "Surgery", "text": "Surgery is covered."}]
    )
    no_copay = _totals(req.bill, verdicts, no_copay_policy)
    assert no_copay["copay_percent"] == 0.0
    assert no_copay["covered"] == no_copay["admissible"]
    assert no_copay["patient_pay"] == round(no_copay["billed"] - no_copay["admissible"], 2)


def test_merge_bills_renumbers_lines_and_sums_totals():
    first = mock_data.bill("bill_printed.png").model_dump()
    second = {
        "patient_name": "Sunita S.",
        "hospital_name": "CityCare Pharmacy",
        "line_items": [
            {"id": "X1", "description": "Painkillers", "amount": 3200},
            {"id": "X2", "description": "Bandage", "amount": 2500},
        ],
        "total_amount": 5700,
        "confidence": 0.6,
        "source_file": "bill_handwritten.png",
        "warnings": ["Handwritten bill matched with lower confidence."],
    }
    merged = _merge_bills([first, second])

    assert len(merged.line_items) == 13
    assert [line.id for line in merged.line_items] == [f"B{i}" for i in range(1, 14)]
    assert merged.total_amount == 160400.0
    assert merged.patient_name == "Sunita Sharma"
    assert merged.confidence == 0.6
    assert merged.source_file == "bill_printed.png, bill_handwritten.png"


def test_dedupe_gaps_collapses_synonyms_and_sorts_by_severity():
    gaps = _dedupe_gaps(
        [
            Gap(title="Low priority thing", detail="", severity="low"),
            Gap(title="Discharge summary is missing", detail="", severity="high"),
            Gap(title="Discharge summary not uploaded", detail="", severity="high"),
            Gap(title="Unclear line needs manual review", detail="", severity="medium"),
        ]
    )
    assert [g.severity for g in gaps] == ["high", "medium", "low"]
    assert len(gaps) == 3
