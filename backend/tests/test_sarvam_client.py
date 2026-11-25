"""Tests for the single Sarvam integration module, without live API calls."""
import json
from types import SimpleNamespace

from app import mock_data
from app.sarvam_client import SarvamClient, _loads_json_object


class _FakeChat:
    def __init__(self, content: str):
        self.content = content
        self.kwargs = None

    def completions(self, **kwargs):
        self.kwargs = kwargs
        message = SimpleNamespace(content=self.content)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def test_mock_client_never_needs_a_key():
    client = SarvamClient()
    assert client.mode == "mock"
    assert client.client is None

    stt = client.transcribe(b"audio", "narration.webm", "hi-IN")
    assert stt["mode"] == "mock"
    assert stt["transcript"] == mock_data.TRANSCRIPTS["hi-IN"]

    policy = client.parse_document(b"pdf", "policy.pdf", "policy")
    bill = client.parse_document(b"png", "bill.png", "bill")
    assert policy["policy"]["policy_number"] == "BSG-HS-2025-88421"
    assert bill["policy"] is None
    assert len(bill["bill"]["line_items"]) == 11

    analysis = client.reason("narration", "hi-IN", policy["policy"], bill["bill"])
    assert len(analysis["verdicts"]) == 11
    assert client.speak("hello", "hi-IN") == b""


def test_json_loader_accepts_fences_and_surrounding_text():
    payload = {"verdicts": [{"line_id": "B1"}], "summary": "ok"}
    assert _loads_json_object(json.dumps(payload)) == payload
    assert _loads_json_object(f"```json\n{json.dumps(payload)}\n```") == payload
    assert _loads_json_object(f"Here you go: {json.dumps(payload)} thanks") == payload
    assert _loads_json_object("not json") == {}


def test_reason_uses_demo_safe_chat_settings_and_maps_alternate_schema():
    content = json.dumps(
        {
            "line_items_verdict": [
                {
                    "line_id": "B1",
                    "verdict": "partially_covered",
                    "covered_amount": 20000,
                    "confidence": 0.9,
                    "clause_id": "C1",
                    "clause_text": "Room rent sub-limit",
                    "reasoning": "1% daily cap",
                }
            ],
            "gaps": [],
        }
    )
    chat = _FakeChat(content)
    client = object.__new__(SarvamClient)
    client.mode = "live"
    client.client = SimpleNamespace(chat=chat)

    data = client.reason(
        "narration",
        "hi-IN",
        mock_data.policy().model_dump(),
        mock_data.bill().model_dump(),
    )

    assert len(data["verdicts"]) == 1
    assert data["verdicts"][0]["line_id"] == "B1"
    assert data["mode"] == "live"
    assert "disclaimer" in data
    assert chat.kwargs["model"] == "sarvam-105b-conversations"
    assert chat.kwargs["max_tokens"] == 4096
    assert chat.kwargs["response_format"] == {"type": "json_object"}
    assert "reasoning_effort" not in chat.kwargs
    system = chat.kwargs["messages"][0]["content"]
    assert '"verdicts"' in system and '"clause_id"' in system and '"covered_amount"' in system
