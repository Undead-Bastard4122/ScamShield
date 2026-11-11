"""Differential comparison of ScamShield's parser with the WHATWG URL
Standard test data (web-platform-tests ``url/resources/urltestdata.json``).

ScamShield is deliberately a strict subset of a browser URL parser. This
module classifies every relevant WPT case so differences are visible and
reviewed, not assumed. It does NOT claim browser equivalence.

Compared for cases both parsers accept: scheme, host (after IDNA), port and
path. Query and fragment are not compared: ScamShield drops them by design.
ScamShield keeps the path as written (no dot-segment resolution, no
percent-encoding); each such difference is classified, and must be fully
explained by those two browser steps or the case is a PATH_MISMATCH.

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

EQUIVALENT = "equivalent"  # scheme, host, port AND path identical to the browser's
# Scheme, host and port identical; ScamShield keeps the path as written while a
# browser normalises it. Intentional: see docs/input-engine.md. The detail names
# the browser step(s) that explain the whole difference.
PATH_DIFFERENCE = "path_difference"
PATH_MISMATCH = "PATH_MISMATCH"  # path differs and the browser steps do not explain it
AGREE_REJECT = "agree_reject"
STRICT_REJECT = "strict_reject"  # browser accepts, ScamShield rejects (by design)
MISMATCH = "MISMATCH"  # both accept but disagree: must never happen
ACCEPTS_BROWSER_FAILURE = "ACCEPTS_BROWSER_FAILURE"  # we accept, browser rejects


_SINGLE_DOT = {".", "%2e"}
_DOUBLE_DOT = {"..", ".%2e", "%2e.", "%2e%2e"}
# WHATWG path percent-encode set (query set + ? ^ ` { }) plus C0 controls and
# everything above U+007E, encoded as UTF-8.
_PATH_ENCODE = set(' "#<>?^`{}')


def resolve_dot_segments(path: str) -> str:
    """Reference WHATWG dot-segment handling for an absolute http(s) path."""
    segments = path[1:].split("/")
    out: list[str] = []
    for position, segment in enumerate(segments):
        last = position == len(segments) - 1
        lowered = segment.lower()
        if lowered in _DOUBLE_DOT:
            if out:
                out.pop()
            if last:
                out.append("")
        elif lowered in _SINGLE_DOT:
            if last:
                out.append("")
        else:
            out.append(segment)
    return "/" + "/".join(out)


def percent_encode_path(path: str) -> str:
    out = []
    for char in path:
        if ord(char) < 0x20 or ord(char) > 0x7E or char in _PATH_ENCODE:
            out.extend(f"%{byte:02X}" for byte in char.encode("utf-8"))
        else:
            out.append(char)
    return "".join(out)


def explain_path_difference(path: str, expected: str) -> str | None:
    """Name the browser step(s) that turn ScamShield's path into ``expected``.

    Returns None if applying dot-segment resolution and percent-encoding does
    not reproduce the browser's pathname exactly (an unexplained difference).
    """
    resolved = resolve_dot_segments(path)
    encoded = percent_encode_path(resolved)
    if encoded != expected:
        return None
    steps = []
    if resolved != path:
        steps.append("dot_segments")
    if encoded != resolved:
        steps.append("percent_encoding")
    return "+".join(steps)


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
    if not same:
        return (MISMATCH, indicator.host)
    # Query and fragment are intentionally dropped by ScamShield, so only the
    # path is compared (WPT ``pathname`` excludes them too).
    if indicator.path == case["pathname"]:
        return (EQUIVALENT, None)
    reason = explain_path_difference(indicator.path, case["pathname"])
    return (PATH_DIFFERENCE, reason) if reason else (PATH_MISMATCH, indicator.path)


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
