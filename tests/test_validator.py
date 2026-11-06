import pytest

from app.scanner import (
    HostKind,
    IndicatorType,
    InvalidIndicator,
    RejectReason,
    parse_indicator,
)


def reason(raw: str, **kwargs) -> RejectReason:
    with pytest.raises(InvalidIndicator) as info:
        parse_indicator(raw, **kwargs)
    return info.value.reason


# --- accepted URLs ---------------------------------------------------------


def test_basic_https_url():
    ind = parse_indicator("https://example.com/a/b")
    assert ind.indicator_type is IndicatorType.URL
    assert ind.scheme == "https"
    assert ind.host == "example.com"
    assert ind.path == "/a/b"
    assert ind.url_without_query == "https://example.com/a/b"
    assert ind.lookup_blocked_reason is None


def test_scheme_and_host_are_lowercased_path_case_is_kept():
    ind = parse_indicator("HTTPS://ExAmPle.COM/CaSe")
    assert ind.scheme == "https"
    assert ind.host == "example.com"
    assert ind.path == "/CaSe"


def test_empty_path_becomes_slash():
    assert parse_indicator("http://example.com").path == "/"


def test_surrounding_whitespace_is_stripped():
    assert parse_indicator("  https://example.com \n").host == "example.com"


def test_default_ports_are_dropped_others_kept():
    assert parse_indicator("https://example.com:443/").port is None
    assert parse_indicator("http://example.com:80/").port is None
    ind = parse_indicator("https://example.com:8443/x")
    assert ind.port == 8443
    assert ind.url_without_query == "https://example.com:8443/x"


def test_trailing_dot_is_removed():
    assert parse_indicator("https://example.com./").host == "example.com"


def test_query_and_fragment_are_never_in_display_or_provider_url():
    ind = parse_indicator("https://example.com/reset?token=SECRET123#frag-SECRET")
    assert ind.has_query and ind.has_fragment
    assert "SECRET" not in ind.display_value
    assert "SECRET" not in (ind.url_without_query or "")
    assert ind.display_value == "https://example.com/reset?[hidden]#[hidden]"


def test_bare_question_mark_and_fragment_still_flagged():
    ind = parse_indicator("https://example.com/?#")
    assert ind.has_query and ind.has_fragment


def test_long_path_is_truncated_for_display_only():
    ind = parse_indicator("https://example.com/" + "a" * 200)
    assert len(ind.display_value) < 100
    assert ind.path == "/" + "a" * 200


def test_percent_encoding_in_path_is_not_decoded():
    assert parse_indicator("https://example.com/a%2Fb").path == "/a%2Fb"


# --- bare domains ----------------------------------------------------------


def test_bare_domain():
    ind = parse_indicator("Example.COM")
    assert ind.indicator_type is IndicatorType.DOMAIN
    assert ind.host == "example.com"
    assert ind.url_without_query is None
    assert ind.path == ""
    assert ind.scheme is None


@pytest.mark.parametrize(
    "raw",
    ["example.com/login", "example.com:8080", "user@example.com", "//example.com"],
)
def test_bare_inputs_with_extra_parts_are_not_guessed(raw):
    assert reason(raw) is RejectReason.MISSING_SCHEME


@pytest.mark.parametrize("raw", ["192.0.2.1", "8.8.8.8"])
def test_bare_ip_is_not_a_domain(raw):
    assert reason(raw) is RejectReason.IP_NOT_DOMAIN


# --- rejected input --------------------------------------------------------


@pytest.mark.parametrize("raw", ["", "   ", "\n\t"])
def test_empty(raw):
    assert reason(raw) is RejectReason.EMPTY


def test_non_string_is_rejected():
    assert reason(None) is RejectReason.EMPTY  # type: ignore[arg-type]


def test_length_limit():
    assert reason("https://example.com/" + "a" * 4100) is RejectReason.TOO_LONG
    ok = "https://example.com/" + "a" * (4096 - len("https://example.com/"))
    assert len(ok) == 4096
    parse_indicator(ok)
    assert reason("x" * 11, max_length=10) is RejectReason.TOO_LONG


@pytest.mark.parametrize(
    "raw",
    [
        "javascript:alert(1)",
        "data:text/html,<script>1</script>",
        "file:///etc/passwd",
        "ftp://example.com/",
        "mailto:a@example.com",
        "tel:+2348012345678",
        "HTTP-ish://example.com",
        "ws://example.com/",
    ],
)
def test_unsupported_schemes(raw):
    # tel:+234... is not a port form, so it is unsupported rather than guessed.
    assert reason(raw) is RejectReason.UNSUPPORTED_SCHEME


@pytest.mark.parametrize(
    "raw",
    [
        "https://user@example.com/",
        "https://user:pass@example.com/",
        "https://paypal.com@evil.example/",
        "https://:pass@example.com/",
        "https://@example.com/",
    ],
)
def test_embedded_credentials_rejected(raw):
    assert reason(raw) is RejectReason.EMBEDDED_CREDENTIALS


def test_at_sign_in_path_or_query_is_not_credentials():
    ind = parse_indicator("https://example.com/a@b?x=y@z")
    assert ind.host == "example.com"


@pytest.mark.parametrize(
    "raw",
    ["https://a.com https://b.com", "a.com b.com", "see https://a.com now"],
)
def test_multiple_indicators(raw):
    assert reason(raw) is RejectReason.MULTIPLE_INDICATORS


@pytest.mark.parametrize(
    "raw",
    ["https://exa​mple.com/", "https://example.com/‮x", "ex\x00ample.com"],
)
def test_hidden_characters(raw):
    assert reason(raw) is RejectReason.CONTROL_CHARACTERS


@pytest.mark.parametrize(
    "raw", ["http://evil.com\\@good.com/", "https://example.com\\path"]
)
def test_backslash_is_ambiguous(raw):
    assert reason(raw) is RejectReason.AMBIGUOUS_SYNTAX


@pytest.mark.parametrize(
    "raw",
    [
        "https://",
        "https:///path",
        "https://-bad.example/",
        "https://bad-.example/",
        "https://exa_mple.com/",
        "https://a..b.com/",
        "https://.example.com/",
        "https://exa%6Dple.com/",
        "https://[::1/",
        "https://[::1]x/",
        "https://[not-an-ip]/",
        "https://a:b:c/",
        "https://" + "a" * 64 + ".com/",
        "https://" + ".".join(["abcdefghi"] * 30) + "/",
        "https://xn--bad-.com/",
        "https://[fe80::1%25eth0]/",
        "https://example.com,evil.com/",
    ],
)
def test_invalid_hosts(raw):
    assert reason(raw) is RejectReason.INVALID_HOST


@pytest.mark.parametrize(
    "raw",
    [
        "https://example.com:0/",
        "https://example.com:65536/",
        "https://example.com:abc/",
        "https://example.com:/",
        "https://example.com:-1/",
        "https://example.com:١٢/",
    ],
)
def test_invalid_ports(raw):
    assert reason(raw) is RejectReason.INVALID_PORT


@pytest.mark.parametrize(
    "raw",
    [
        "http://2130706433/",
        "http://0x7f.0.0.1/",
        "http://0177.0.0.1/",
        "http://127.1/",
        "http://127.0.0/",
        "http://1.2.3.4.5/",
        "http://１２７.0.0.1.5/",
        "https://example.123/",
        "https://example.0x1/",
    ],
)
def test_obfuscated_ips_rejected(raw):
    assert reason(raw) is RejectReason.OBFUSCATED_IP


# --- IP literals -----------------------------------------------------------


@pytest.mark.parametrize(
    "raw",
    [
        "http://127.0.0.1/",
        "http://10.0.0.5/admin",
        "http://192.168.1.1/",
        "http://169.254.169.254/latest/meta-data",
        "http://100.64.0.1/",
        "http://0.0.0.0/",
        "http://[::1]/",
        "http://[fe80::1]/",
        "http://[::ffff:127.0.0.1]/",
        "http://[fc00::1]/",
    ],
)
def test_non_public_ips_parse_but_are_blocked_from_lookup(raw):
    ind = parse_indicator(raw)
    assert ind.host_kind in {HostKind.IPV4, HostKind.IPV6}
    assert ind.lookup_blocked_reason == "non-public IP address"


def test_public_ip_is_allowed():
    ind = parse_indicator("http://8.8.8.8/")
    assert ind.host_kind is HostKind.IPV4
    assert ind.lookup_blocked_reason is None


def test_ipv6_display_and_port():
    ind = parse_indicator("http://[2001:4860:4860::8888]:8080/x")
    assert ind.host_kind is HostKind.IPV6
    assert ind.display_value == "http://[2001:4860:4860::8888]:8080/x"
    assert ind.lookup_blocked_reason is None


# --- private-looking names -------------------------------------------------


@pytest.mark.parametrize(
    "raw",
    [
        "http://localhost/",
        "http://intranet/",
        "https://printer.local/",
        "https://db.internal/",
        "https://router.home.arpa/",
        "https://nas.lan/",
        "intranet",
        "app.corp",
    ],
)
def test_private_names_are_blocked_from_lookup(raw):
    assert parse_indicator(raw).lookup_blocked_reason is not None


# --- IDN -------------------------------------------------------------------


def test_idn_is_converted_to_punycode_and_displayed_as_ascii():
    ind = parse_indicator("https://bücher.example/")
    assert ind.host == "xn--bcher-kva.example"
    assert ind.is_idn
    assert ind.host_unicode == "bücher.example"
    assert "ü" not in ind.display_value


def test_idn_lookalike_is_not_treated_as_the_ascii_name():
    ind = parse_indicator("https://аpple.com/")  # Cyrillic a
    assert ind.host != "apple.com"
    assert ind.host.startswith("xn--")


def test_uts46_case_and_width_mapping():
    assert parse_indicator("https://Ｅxample.com/").host == "example.com"


def test_ideographic_full_stop_is_a_dot():
    assert parse_indicator("example。com").host == "example.com"


def test_unicode_bare_domain():
    ind = parse_indicator("bücher.de")
    assert ind.host == "xn--bcher-kva.de"
    assert ind.indicator_type is IndicatorType.DOMAIN


# --- safety properties -----------------------------------------------------


def test_error_messages_never_echo_input():
    secret = "SUPERSECRET-TOKEN"
    for raw in [
        f"https://user:{secret}@example.com/",
        f"javascript:{secret}",
        f"https://example.com:{secret}/",
        f"https://{secret}%/",
        f"https://a.com/{secret} b",
    ]:
        with pytest.raises(InvalidIndicator) as info:
            parse_indicator(raw)
        assert secret not in str(info.value)
        assert secret not in repr(info.value)


def test_parse_makes_no_network_calls(monkeypatch):
    import socket

    def blocked(*args, **kwargs):
        raise AssertionError("network access attempted during parsing")

    for name in (
        "socket",
        "create_connection",
        "getaddrinfo",
        "gethostbyname",
        "gethostbyname_ex",
        "gethostbyaddr",
    ):
        monkeypatch.setattr(socket, name, blocked)

    samples = [
        "https://example.com/a?b=c#d",
        "example.org",
        "http://[::1]:8080/",
        "http://127.0.0.1/",
        "http://localhost/",
        "https://bücher.example/",
        "http://169.254.169.254/",
        "https://bit.ly/abc",
    ]
    for raw in samples:
        parse_indicator(raw)
