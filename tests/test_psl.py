import hashlib
import socket
from importlib import resources
from pathlib import Path

import idna
import pytest

from app.scanner import psl
from app.scanner.psl import PublicSuffixError, SuffixInfo, lookup, parse_rules

VECTORS = Path(__file__).parent / "data" / "psl_official_tests.txt"
EXPECTED_SHA256 = "762b6cbdd2dacc597b398fcd7860e2184b684125a58aa177dbdf54916a1f3430"


def _ascii(value: str) -> str:
    return idna.encode(value, uts46=True).decode("ascii")


# --- snapshot integrity ---------------------------------------------------


def test_snapshot_is_the_recorded_immutable_file():
    data = (
        resources.files("app.scanner")
        .joinpath("data/public_suffix_list.dat")
        .read_bytes()
    )
    assert hashlib.sha256(data).hexdigest() == EXPECTED_SHA256
    source = resources.files("app.scanner").joinpath("data/PSL_SOURCE.md")
    assert EXPECTED_SHA256 in source.read_text("utf-8")


def test_licence_notice_is_vendored_with_the_snapshot():
    base = resources.files("app.scanner").joinpath("data")
    assert "Mozilla Public License" in base.joinpath(
        "PSL_LICENSE_MPL-2.0.txt"
    ).read_text("utf-8")
    assert "Mozilla Public" in base.joinpath("public_suffix_list.dat").read_text(
        "utf-8"
    )


# --- official test vectors ------------------------------------------------


def _vectors():
    for line in VECTORS.read_text("utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("//"):
            continue
        given, expected = line.split()
        yield given, expected


def test_official_vectors_are_present():
    assert len(list(_vectors())) == 78


@pytest.mark.parametrize(("given", "expected"), list(_vectors()))
def test_official_vector(given, expected):
    if given == "null":
        assert lookup("") is None
        return
    # Mirror what the input engine hands to lookup(): lowercase punycode.
    host = given.lower() if given.startswith(".") else _ascii(given)
    info = lookup(host)
    got = info.registrable_domain if info else None
    # Expected values are written in Unicode; the engine works in punycode.
    assert got == (None if expected == "null" else _ascii(expected))


# --- behaviour the engine relies on --------------------------------------


@pytest.mark.parametrize(
    ("host", "suffix", "registrable", "section"),
    [
        ("example.com", "com", "example.com", "icann"),
        ("a.b.example.co.uk", "co.uk", "example.co.uk", "icann"),
        ("foo.github.io", "github.io", "foo.github.io", "private"),
        ("x.foo.github.io", "github.io", "foo.github.io", "private"),
        ("www.ck", "ck", "www.ck", "icann"),  # exception rule !www.ck
        ("b.www.ck", "ck", "www.ck", "icann"),
        ("a.test.ck", "test.ck", "a.test.ck", "icann"),  # wildcard *.ck
    ],
)
def test_listed_suffixes(host, suffix, registrable, section):
    info = lookup(host)
    assert info is not None and info.listed
    assert (info.public_suffix, info.registrable_domain, info.section) == (
        suffix,
        registrable,
        section,
    )


@pytest.mark.parametrize("host", ["com", "co.uk", "github.io", "test.ck"])
def test_a_public_suffix_has_no_registrable_domain(host):
    info = lookup(host)
    assert info is not None
    assert info.registrable_domain is None
    assert info.public_suffix == host


def test_unlisted_suffix_is_flagged_not_guessed():
    info = lookup("a.b.notarealtld")
    assert info == SuffixInfo("notarealtld", "b.notarealtld", None, False)
    # The "last two labels" shortcut would be wrong here for listed suffixes;
    # prove we use the list, not a shortcut.
    assert lookup("example.co.uk").registrable_domain != "co.uk"


def test_idn_suffix_is_matched_in_punycode():
    info = lookup(_ascii("shop.公司.cn"))
    assert info is not None and info.listed
    assert info.registrable_domain == _ascii("shop.公司.cn")


@pytest.mark.parametrize("host", ["", ".", ".com", "a..b", "a.com.", "EXAMPLE.com"])
def test_unusable_hosts_return_none(host):
    assert lookup(host) is None


def test_lookup_makes_no_network_calls(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError("network access attempted")

    psl._load.cache_clear()
    for name in ("socket", "create_connection", "getaddrinfo", "gethostbyname"):
        monkeypatch.setattr(socket, name, blocked)
    assert lookup("example.co.uk").registrable_domain == "example.co.uk"
    psl._load.cache_clear()


def test_info_repr_hides_hostname_parts():
    assert "secret" not in repr(lookup("secret.example.com"))


# --- fail-closed parsing --------------------------------------------------

GOOD = (
    "// ===BEGIN ICANN DOMAINS===\ncom\n// ===END ICANN DOMAINS===\n"
    "// ===BEGIN PRIVATE DOMAINS===\nblogspot.com\n// ===END PRIVATE DOMAINS===\n"
)


def test_parse_accepts_minimal_valid_snapshot():
    rules = parse_rules(GOOD)
    assert lookup("a.blogspot.com", rules).section == "private"
    assert lookup("a.example.com", rules).section == "icann"


@pytest.mark.parametrize(
    "text",
    [
        "",
        "com\n",  # rule outside a section
        "// ===BEGIN ICANN DOMAINS===\ncom\n",  # unterminated
        "// ===BEGIN ICANN DOMAINS===\n// ===END ICANN DOMAINS===\n",  # empty
        GOOD.replace("com\n// ===END ICANN", "a*b\n// ===END ICANN", 1),
        GOOD + "// ===BEGIN ICANN DOMAINS===\nx\n",
    ],
)
def test_malformed_snapshot_fails_closed(text):
    with pytest.raises(PublicSuffixError):
        parse_rules(text)
