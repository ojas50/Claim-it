"""Shared fixtures for the Claim-It backend tests.

Tests always run in mock mode: no Sarvam key, network call, or credit is needed.
Set the flag before importing the app so app.config sees it.
"""
import os
import sys
from pathlib import Path

os.environ["MOCK_MODE"] = "true"

BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = BACKEND_DIR.parent
SAMPLES_DIR = ROOT_DIR / "samples"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def samples():
    return SAMPLES_DIR


@pytest.fixture(scope="session")
def sample_uploads(samples):
    """Multipart payload for the canonical policy + printed + handwritten demo pack."""
    return [
        ("files", ("policy.pdf", (samples / "policy.pdf").read_bytes(), "application/pdf")),
        ("files", ("bill_printed.png", (samples / "bill_printed.png").read_bytes(), "image/png")),
        (
            "files",
            ("bill_handwritten.png", (samples / "bill_handwritten.png").read_bytes(), "image/png"),
        ),
    ]
