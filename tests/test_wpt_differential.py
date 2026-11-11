"""ScamShield vs the WHATWG URL test data. See wpt_differential.py."""

import hashlib
import json
from collections import Counter

import pytest
import wpt_differential as wd

from app.scanner import InvalidIndicator, parse_indicator

CORPUS_SHA256 = "e9f53c341d498e64f8c4df212439ba9cffe55ac1c4fb566d27691ef71199d143"
LICENSE_SHA256 = "5fac07febb0e2a97fb0d7b0def149ec08b642e1ba4b9c345283ab1cbd2af6570"
UPSTREAM_COMMIT = "96769025acfcbe4a510461b98b65d2f3bd8760f7"

# Every way a browser-valid input may be rejected by ScamShield, with why.
# A new reason showing up here must be added deliberately.
DOCUMENTED_STRICT_REASONS = {
    "embedded_credentials": "username/password in the URL: rejected, not redacted",
    "invalid_host": "hosts browsers tolerate but DNS rules or IDNA reject",
    "missing_scheme": "http:example.com forms without //: not guessed",
    "control_characters": "tabs/newlines/zero-width characters browsers strip",
    "multiple_indicators": "inner whitespace browsers strip",
    "obfuscated_ip": "decimal, hex, octal or short IPv4 forms",
    "ambiguous_syntax": "backslashes that browsers treat as slashes",
}


@pytest.fixture(scope="module")
def report():
    return wd.build_report()


def test_corpus_is_the_pinned_upstream_file():
    assert hashlib.sha256(wd.CORPUS.read_bytes()).hexdigest() == CORPUS_SHA256
    licence = (wd.DATA / "WPT_LICENSE.md").read_bytes()
    assert hashlib.sha256(licence).hexdigest() == LICENSE_SHA256
    source = (wd.DATA / "SOURCE.md").read_text("utf-8")
    for pinned in (CORPUS_SHA256, LICENSE_SHA256, UPSTREAM_COMMIT):
        assert pinned in source


def test_enough_cases_are_in_scope(report):
    counts = Counter(item["outcome"] for item in report)
    assert len(report) >= 250
    assert counts[wd.EQUIVALENT] + counts[wd.PATH_DIFFERENCE] >= 60
    assert counts[wd.EQUIVALENT] >= 40
    assert counts[wd.AGREE_REJECT] >= 100


def test_no_case_where_both_accept_but_disagree(report):
    bad = [item for item in report if item["outcome"] == wd.MISMATCH]
    assert not bad, bad[:5]


def test_every_path_difference_is_fully_explained(report):
    bad = [item for item in report if item["outcome"] == wd.PATH_MISMATCH]
    assert not bad, bad[:5]


def test_path_differences_are_only_the_documented_browser_steps(report):
    details = {
        item["detail"] for item in report if item["outcome"] == wd.PATH_DIFFERENCE
    }
    assert details
    allowed = {"dot_segments", "percent_encoding", "dot_segments+percent_encoding"}
    assert details <= allowed


def test_path_comparison_uses_the_path_the_parser_retains():
    # ScamShield keeps the path as written; a browser normalises it.
    kept = parse_indicator("http://example.com/a/../b")
    assert kept.path == "/a/../b"
    assert wd.explain_path_difference(kept.path, "/b") == "dot_segments"
    assert wd.explain_path_difference("/你", "/%E4%BD%A0") == "percent_encoding"
    assert wd.explain_path_difference("/a/../你", "/%E4%BD%A0") == (
        "dot_segments+percent_encoding"
    )


def test_explainer_rejects_differences_it_cannot_account_for():
    assert wd.explain_path_difference("/a/b", "/a/c") is None
    assert wd.explain_path_difference("/a/b", "/A/b") is None


def test_reference_dot_segment_and_encoding_steps():
    for raw, expected in [
        ("/./a", "/a"),
        ("/a/.", "/a/"),
        ("/a/b/../c", "/a/c"),
        ("/a/%2E%2e/c", "/c"),
        ("/../../x", "/x"),
        ("/a/..", "/"),
        ("////../..", "//"),
    ]:
        assert wd.resolve_dot_segments(raw) == expected, raw
    assert wd.percent_encode_path('/a b"c') == "/a%20b%22c"
    assert wd.percent_encode_path("/\u00e9") == "/%C3%A9"


def test_never_accepts_what_browsers_reject(report):
    bad = [item for item in report if item["outcome"] == wd.ACCEPTS_BROWSER_FAILURE]
    assert not bad, bad[:5]


def test_every_strict_rejection_has_a_documented_reason(report):
    reasons = {item["detail"] for item in report if item["outcome"] == wd.STRICT_REJECT}
    assert reasons <= set(DOCUMENTED_STRICT_REASONS), reasons


def test_outcomes_match_the_reviewed_golden_file(report):
    golden = json.loads(wd.GOLDEN.read_text("utf-8"))
    assert report == golden, (
        "Parser behaviour changed on the WPT corpus. If intentional, run "
        "`python tests/wpt_differential.py` and review the diff."
    )


def test_equivalent_cases_agree_on_scheme_host_port_and_path():
    # Spot-check the comparison itself on a few known WPT shapes.
    for raw, host, port in [
        ("https://example.com:8443/a", "example.com", 8443),
        ("HTTP://EXAMPLE.COM:80/", "example.com", None),
        ("http://[::1]:3000/", "::1", 3000),
    ]:
        indicator = parse_indicator(raw)
        assert (indicator.host, indicator.port) == (host, port)


def test_scope_excludes_other_schemes_and_relative_cases():
    scoped = {item["index"] for item in wd.build_report()}
    cases = wd.load_cases()
    for index in scoped:
        case = cases[index]
        assert case["base"] is None
        if not case.get("failure"):
            assert case["protocol"] in ("http:", "https:")


def test_http_without_slashes_is_not_called_an_unsupported_scheme():
    for raw in ("http:example.com/", "https:/example.com/"):
        with pytest.raises(InvalidIndicator) as info:
            parse_indicator(raw)
        assert info.value.reason.value == "missing_scheme"
