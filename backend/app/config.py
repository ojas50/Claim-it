import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load_env() -> None:
    """Load .env without adding a python-dotenv dependency."""
    for path in (ROOT / ".env", Path.cwd() / ".env"):
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, value = line.split("=", 1)
            os.environ.setdefault(name.strip(), value.strip().strip('"').strip("'"))


_load_env()

MOCK_MODE = os.getenv("MOCK_MODE", "true").strip().lower() in {"1", "true", "yes", "on"}
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "").strip()
SAMPLES_DIR = ROOT / "samples"

SUPPORTED_LANGUAGES = ["hi-IN", "ta-IN", "te-IN", "bn-IN", "en-IN"]
LANGUAGE_NAMES = {
    "hi-IN": "Hindi",
    "ta-IN": "Tamil",
    "te-IN": "Telugu",
    "bn-IN": "Bengali",
    "en-IN": "English",
}
