"""Differential comparison of ScamShield's parser with the WHATWG URL
Standard test data (web-platform-tests ``url/resources/urltestdata.json``).

ScamShield is deliberately a strict subset of a browser URL parser. This
module classifies every relevant WPT case so differences are visible and
reviewed, not assumed. It does NOT claim browser equivalence.

Run ``python tests/wpt_differential.py`` to regenerate the golden file after
an intentional parser change, then review the diff.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

DATA = Path(__file__).parent / "data" / "wpt"
CORPUS = DATA / "urltestdata.json"
GOLDEN = DATA / "expected_outcomes.json"

_HTTPISH = re.compile(r"^[\x00-\x20]*https?:", re.IGNORECASE)

EQUIVALENT = "equivalent"
AGREE_REJECT = "agree_reject"
STRICT_REJECT = "strict_reject"  # browser accepts, ScamShield rejects (by design)
MISMATCH = "MISMATCH"  # both accept but disagree: must never happen
ACCEPTS_BROWSER_FAILURE = "ACCEPTS_BROWSER_FAILURE"  # we accept, browser rejects


def load_cases() -> list[dict]:
    raw = json.loads(CORPUS.read_text("utf-8"))
    return [item for item in raw if isinstance(item, dict)]


def classify(case: dict) -> tuple[str, str | None] | None:
    """Return (outcome, detail) or None if the case is out of scope.

    In scope: absolute inputs (no base) that a browser parses to an http(s)
    URL, and absolute http(s)-looking inputs that a browser rejects.
    """
    from app.scanner import InvalidIndicator, parse_indicator

    if case.get("base") is not None:
        return None
    browser_ok = not case.get("failure")
    if browser_ok and case["protocol"] not in ("http:", "https:"):
        return None
    if not browser_ok and not _HTTPISH.match(case["input"]):
        return None

    try:
        indicator = parse_indicator(case["input"])
    except InvalidIndicator as exc:
        return (STRICT_REJECT if browser_ok else AGREE_REJECT, exc.reason.value)

    if not browser_ok:
        return (ACCEPTS_BROWSER_FAILURE, None)

    expected_host = case["hostname"].strip("[]")
    expected_port = int(case["port"]) if case["port"] else None
    same = (
        indicator.scheme == case["protocol"][:-1]
        and indicator.host == expected_host
        and indicator.port == expected_port
    )
    return (EQUIVALENT, None) if same else (MISMATCH, indicator.host)


def build_report() -> list[dict]:
    report = []
    for index, case in enumerate(load_cases()):
        result = classify(case)
        if result is None:
            continue
        outcome, detail = result
        report.append(
            {
                "index": index,
                "input": case["input"],
                "outcome": outcome,
                "detail": detail,
            }
        )
    return report


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    GOLDEN.write_text(
        json.dumps(build_report(), indent=1, ensure_ascii=False) + "\n", "utf-8"
    )
    print(f"wrote {GOLDEN}")
