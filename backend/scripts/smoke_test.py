"""Repeatable end-to-end smoke test against a running Claim-It backend.

Usage:
    python scripts/smoke_test.py
    python scripts/smoke_test.py --base-url http://127.0.0.1:8001

Works in both mock and live mode. In live mode it consumes Sarvam credits.
"""
import argparse
import json
import os
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
SAMPLES = ROOT / "samples"


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def close(a, b, tol=0.02) -> bool:
    return abs(float(a or 0) - float(b or 0)) <= tol


def main() -> int:
    parser = argparse.ArgumentParser(description="Claim-It end-to-end smoke test")
    parser.add_argument(
        "--base-url",
        default=os.getenv("CLAIMIT_BASE_URL", "http://127.0.0.1:8000"),
        help="Backend base URL (default: http://127.0.0.1:8000)",
    )
    args = parser.parse_args()

    files = [
        ("files", ("policy.pdf", (SAMPLES / "policy.pdf").read_bytes(), "application/pdf")),
        ("files", ("bill_printed.png", (SAMPLES / "bill_printed.png").read_bytes(), "image/png")),
        ("files", ("bill_handwritten.png", (SAMPLES / "bill_handwritten.png").read_bytes(), "image/png")),
    ]
    result = {"base_url": args.base_url}

    try:
        with httpx.Client(base_url=args.base_url, timeout=180) as client:
            health = client.get("/api/health")
            check(health.status_code == 200, f"health failed: {health.status_code}")
            mode = health.json()["mode"]
            result["mode"] = mode
            print(f"health: {health.json()['status']} / {mode}")

            stt = client.post(
                "/api/transcribe",
                files={"file": ("narration.wav", b"demo-audio", "audio/wav")},
                data={"language": "hi-IN"},
            )
            check(stt.status_code == 200, f"transcribe failed: {stt.status_code}")
            transcript = stt.json()["transcript"]
            check(bool(transcript.strip()), "transcribe returned an empty transcript")
            result["transcript_chars"] = len(transcript)
            print(f"transcribe: {len(transcript)} chars")

            parsed = client.post(
                "/api/parse",
                files=files,
                data={"kinds": "policy,bill,bill", "language": "hi-IN"},
            )
            check(parsed.status_code == 200, f"parse failed: {parsed.status_code} {parsed.text[:200]}")
            parsed_data = parsed.json()
            policy, bill = parsed_data["policy"], parsed_data["bill"]
            check(bool(policy["policy_number"]), "parse returned no policy number")
            check(bool(policy["clauses"]), "parse returned no policy clauses")
            check(bool(bill["line_items"]), "parse returned no bill line items")
            result["policy_number"] = policy["policy_number"]
            result["line_items"] = len(bill["line_items"])
            print(f"parse: {policy['policy_number']} | {len(bill['line_items'])} lines")

            analyzed = client.post(
                "/api/analyze",
                json={
                    "narration": transcript,
                    "language": "hi-IN",
                    "policy": policy,
                    "bill": bill,
                },
            )
            check(analyzed.status_code == 200, f"analyze failed: {analyzed.status_code} {analyzed.text[:200]}")
            analysis = analyzed.json()
            verdicts, gaps, totals = analysis["verdicts"], analysis["gaps"], analysis["totals"]
            check(len(verdicts) == len(bill["line_items"]), "verdict count does not match bill lines")
            check(bool(gaps), "analysis returned no document gaps")
            check(all(v["verdict"] in {"covered", "partially_covered", "not_covered", "unclear"} for v in verdicts),
                  "unexpected verdict value")
            check(all(v["clause_id"] and v["clause_text"] for v in verdicts), "verdict missing clause citation")
            check(close(totals["covered"], totals["admissible"] - totals["copay_amount"]),
                  "covered does not match admissible minus co-pay")
            check(close(totals["patient_pay"], totals["billed"] - totals["covered"]),
                  "patient_pay does not match billed minus covered")
            if mode == "mock":
                check(totals["billed"] == 154700.0, f"unexpected mock billed: {totals['billed']}")
                check(totals["covered"] == 121230.0, f"unexpected mock covered: {totals['covered']}")
                check(len(gaps) == 6, f"unexpected mock gap count: {len(gaps)}")
            result["verdicts"] = len(verdicts)
            result["gaps"] = len(gaps)
            result["covered"] = totals["covered"]
            print(f"analyze: {len(verdicts)} verdicts | {len(gaps)} gaps | covered {totals['covered']:,.0f}")

            drafted = client.post(
                "/api/draft",
                json={
                    "language": "hi-IN",
                    "form": {
                        "policy_number": policy["policy_number"],
                        "insurer": policy["insurer"],
                        "patient_name": bill["patient_name"],
                        "hospital_name": bill["hospital_name"],
                        "claim_amount": bill["total_amount"],
                        "phone": "9876543210",
                        "address": "Jaipur",
                    },
                },
            )
            check(drafted.status_code == 200, f"draft failed: {drafted.status_code}")
            letter = drafted.json()["letter"]
            check(policy["policy_number"] in letter, "letter is missing the policy number")
            check(bill["patient_name"] in letter, "letter is missing the patient name")
            result["letter_chars"] = len(letter)
            print(f"draft: {len(letter)} chars")

            spoken = client.post(
                "/api/speak",
                json={"text": "आपका दावा तैयार है।", "language": "hi-IN"},
            )
            check(spoken.status_code == 200, f"speak failed: {spoken.status_code}")
            if mode == "mock":
                check(spoken.headers.get("x-claimit-mock") == "true", "mock speak header missing")
                check(spoken.content == b"", "mock speak should return empty audio")
            else:
                check(spoken.content.startswith(b"RIFF"), "live speak did not return a WAV")
            result["speak_bytes"] = len(spoken.content)
            print(f"speak: {len(spoken.content)} bytes")
    except (httpx.HTTPError, AssertionError, OSError) as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1

    print("SMOKE PASS")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
