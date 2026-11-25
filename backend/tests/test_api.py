"""HTTP-level tests for the FastAPI endpoints in mock mode."""
import pytest

from app import mock_data


def test_health_reports_mock_mode(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["mode"] == "mock"
    assert body["mock_flag"] is True
    assert body["models"]["stt"] == "saaras:v4"
    assert body["models"]["chat"] == "sarvam-105b-conversations"
    assert body["models"]["tts"] == "bulbul:v4-flash"


@pytest.mark.parametrize(
    "language,expected_key",
    [
        ("hi-IN", "मेरी माँ"),
        ("en-IN", "My mother"),
        ("ta-IN", "என்"),
        ("te-IN", "మా"),
        ("bn-IN", "আমার"),
    ],
)
def test_transcribe_returns_canned_transcript(client, language, expected_key):
    res = client.post(
        "/api/transcribe",
        files={"file": ("narration.wav", b"fake audio", "audio/wav")},
        data={"language": language},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["mode"] == "mock"
    assert body["language_code"] == language
    assert expected_key in body["transcript"]
    assert body["warning"] == ""


def test_transcribe_validates_input(client):
    empty = client.post(
        "/api/transcribe",
        files={"file": ("narration.wav", b"", "audio/wav")},
        data={"language": "hi-IN"},
    )
    assert empty.status_code == 400
    assert "empty" in empty.json()["detail"].lower()

    bad_lang = client.post(
        "/api/transcribe",
        files={"file": ("narration.wav", b"audio", "audio/wav")},
        data={"language": "fr-FR"},
    )
    assert bad_lang.status_code == 400
    assert "fr-FR" in bad_lang.json()["detail"]

    too_big = client.post(
        "/api/transcribe",
        files={"file": ("narration.wav", b"a" * (15 * 1024 * 1024 + 1), "audio/wav")},
        data={"language": "hi-IN"},
    )
    assert too_big.status_code == 413


def test_parse_sample_pack(client, sample_uploads):
    res = client.post(
        "/api/parse",
        files=sample_uploads,
        data={"kinds": "policy,bill,bill", "language": "hi-IN"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["mode"] == "mock"
    assert body["policy"]["policy_number"] == "BSG-HS-2025-88421"
    assert body["policy"]["insured_name"] == "Sunita Sharma"
    assert len(body["policy"]["clauses"]) == 9
    assert body["bill"]["patient_name"] == "Sunita Sharma"
    assert len(body["bill"]["line_items"]) == 11
    assert body["bill"]["total_amount"] == 154700.0
    assert {line["id"] for line in body["bill"]["line_items"]} == {
        f"B{i}" for i in range(1, 12)
    }


@pytest.mark.parametrize(
    "files,kinds,expected_status,detail_hint",
    [
        (
            [("files", ("policy.txt", b"x", "text/plain"))],
            "policy",
            415,
            "unsupported file type",
        ),
        (
            [("files", ("policy.pdf", b"%PDF-1.4 fake", "application/pdf"))],
            "policy,bill",
            400,
            "each file must be tagged",
        ),
        (
            [("files", ("policy.pdf", b"%PDF-1.4 fake", "application/pdf"))],
            "claim",
            400,
            "unknown document type",
        ),
        (
            [("files", ("bill.png", b"fake", "image/png"))],
            "bill",
            422,
            "no policy document",
        ),
    ],
)
def test_parse_validation(client, files, kinds, expected_status, detail_hint):
    res = client.post("/api/parse", files=files, data={"kinds": kinds, "language": "en-IN"})
    assert res.status_code == expected_status
    assert detail_hint in res.json()["detail"].lower()


def test_analyze_canonical_scenario(client):
    policy = mock_data.policy().model_dump()
    bill = mock_data.bill().model_dump()
    res = client.post(
        "/api/analyze",
        json={
            "narration": mock_data.TRANSCRIPTS["hi-IN"],
            "language": "hi-IN",
            "policy": policy,
            "bill": bill,
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["mode"] == "mock"
    assert len(body["verdicts"]) == 11
    assert len(body["gaps"]) == 6
    assert body["totals"] == {
        "billed": 154700.0,
        "admissible": 134700.0,
        "copay_percent": 10.0,
        "copay_amount": 13470.0,
        "covered": 121230.0,
        "patient_pay": 33470.0,
    }
    assert {v["verdict"] for v in body["verdicts"]} <= {
        "covered",
        "partially_covered",
        "not_covered",
        "unclear",
    }
    assert all(v["clause_id"] and v["clause_text"] for v in body["verdicts"])
    gap_titles = " ".join(g["title"] for g in body["gaps"]).lower()
    assert "discharge summary" in gap_titles
    assert "pre-authorisation" in gap_titles
    assert "not legal, medical, or financial advice" in body["disclaimer"].lower()


def test_analyze_rejects_empty_narration(client):
    policy = mock_data.policy().model_dump()
    bill = mock_data.bill().model_dump()
    res = client.post(
        "/api/analyze",
        json={"narration": "   ", "language": "hi-IN", "policy": policy, "bill": bill},
    )
    assert res.status_code == 400
    assert "narration" in res.json()["detail"].lower()


@pytest.mark.parametrize("language", ["hi-IN", "en-IN", "ta-IN", "te-IN", "bn-IN"])
def test_draft_letter_in_every_supported_language(client, language):
    res = client.post(
        "/api/draft",
        json={
            "language": language,
            "form": {
                "policy_number": "BSG-HS-2025-88421",
                "insurer": "Bharat Suraksha General Insurance",
                "patient_name": "Sunita Sharma",
                "hospital_name": "CityCare Hospital, Jaipur",
                "claim_amount": 154700,
                "phone": "9876543210",
                "address": "Jaipur",
            },
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["language"] == language
    assert body["mode"] == "mock"
    assert "BSG-HS-2025-88421" in body["letter"]
    assert "Sunita Sharma" in body["letter"]
    assert len(body["letter"]) > 120


def test_draft_requires_patient(client):
    res = client.post("/api/draft", json={"language": "hi-IN", "form": {}})
    assert res.status_code == 400
    assert "patient name" in res.json()["detail"].lower()


def test_speak_mock_returns_empty_audio_with_header(client):
    res = client.post(
        "/api/speak",
        json={"text": "आपका दावा तैयार है।", "language": "hi-IN"},
    )
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("audio/wav")
    assert res.headers["x-claimit-mock"] == "true"
    assert res.content == b""

    empty = client.post("/api/speak", json={"text": "  ", "language": "hi-IN"})
    assert empty.status_code == 400

    bad_lang = client.post("/api/speak", json={"text": "hello", "language": "fr-FR"})
    assert bad_lang.status_code == 400


def test_sample_files_are_served(client):
    for name in ("policy.pdf", "bill_printed.png", "bill_handwritten.png", "narration_hi.txt"):
        res = client.get(f"/samples/{name}")
        assert res.status_code == 200
        assert len(res.content) > 0
