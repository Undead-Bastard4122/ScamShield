"""Validate and normalise one submitted URL or domain.

This module only parses text. It never resolves a name, opens a socket, or
fetches anything (D-009). Parsing is deliberately strict: anything that
different programs could read differently is rejected, not guessed at.
"""

from __future__ import annotations

import re
import unicodedata

from app.scanner.models import (
    HostKind,
    Indicator,
    IndicatorType,
    InvalidIndicator,
    RejectReason,
)
from app.scanner.normalizer import normalize_host

DEFAULT_MAX_LENGTH = 4096
_MAX_DISPLAY_PATH = 60
_ALLOWED_SCHEMES = frozenset({"http", "https"})
_DEFAULT_PORTS = {"http": 80, "https": 443}
_SCHEME = re.compile(r"^([A-Za-z][A-Za-z0-9+.\-]*):")
_LOOKS_LIKE_PORT = re.compile(r"^[0-9]{1,5}(?:[/?#]|$)")


def parse_indicator(raw: str, *, max_length: int = DEFAULT_MAX_LENGTH) -> Indicator:
    """Parse ``raw`` as a single http(s) URL or bare domain name.

    Raises :class:`InvalidIndicator`; its message never echoes ``raw``.
    """
    if not isinstance(raw, str):
        raise InvalidIndicator(RejectReason.EMPTY)
    # Length is checked before any other work so oversized input stays cheap.
    if len(raw) > max_length:
        raise InvalidIndicator(RejectReason.TOO_LONG)

    text = raw.strip()
    if not text:
        raise InvalidIndicator(RejectReason.EMPTY)
    if any(ch.isspace() for ch in text):
        raise InvalidIndicator(RejectReason.MULTIPLE_INDICATORS)
    # Cc control, Cf format (zero-width, bidi), Cs lone surrogates.
    if any(unicodedata.category(ch) in {"Cc", "Cf", "Cs"} for ch in text):
        raise InvalidIndicator(RejectReason.CONTROL_CHARACTERS)
    if "\\" in text:
        # Browsers read "\" as "/" in http URLs, which enables spoofing.
        raise InvalidIndicator(RejectReason.AMBIGUOUS_SYNTAX)
    if text.startswith("//"):
        raise InvalidIndicator(RejectReason.MISSING_SCHEME)

    match = _SCHEME.match(text)
    if match is not None:
        after_colon = text[match.end() :]
        if after_colon.startswith("//"):
            scheme = match.group(1).lower()
            if scheme not in _ALLOWED_SCHEMES:
                raise InvalidIndicator(RejectReason.UNSUPPORTED_SCHEME)
            return _parse_url(scheme, after_colon[2:])
        if not _LOOKS_LIKE_PORT.match(after_colon):
            # javascript:, data:, mailto:, and similar.
            raise InvalidIndicator(RejectReason.UNSUPPORTED_SCHEME)
        # "host:8080" falls through to the bare-domain rule below.

    return _parse_domain(text)


def _parse_domain(text: str) -> Indicator:
    if any(ch in text for ch in "/?#@:[]"):
        # A path, port, email address, or similar: not a bare domain, and
        # we do not guess which part the user meant.
        raise InvalidIndicator(RejectReason.MISSING_SCHEME)
    host = normalize_host(text)
    if host.kind is not HostKind.DNS_NAME:
        raise InvalidIndicator(RejectReason.IP_NOT_DOMAIN)
    return Indicator(
        indicator_type=IndicatorType.DOMAIN,
        scheme=None,
        host=host.ascii,
        host_unicode=host.unicode,
        host_kind=host.kind,
        is_idn=host.is_idn,
        port=None,
        path="",
        has_query=False,
        has_fragment=False,
        display_value=host.ascii,
        url_without_query=None,
        lookup_blocked_reason=host.lookup_blocked_reason,
    )


def _parse_url(scheme: str, rest: str) -> Indicator:
    end = len(rest)
    for marker in "/?#":
        index = rest.find(marker)
        if index != -1:
            end = min(end, index)
    authority, remainder = rest[:end], rest[end:]

    if "@" in authority:
        raise InvalidIndicator(RejectReason.EMBEDDED_CREDENTIALS)
    if not authority:
        raise InvalidIndicator(RejectReason.INVALID_HOST)

    bracketed = authority.startswith("[")
    if bracketed:
        close = authority.find("]")
        if close == -1:
            raise InvalidIndicator(RejectReason.INVALID_HOST)
        host_text = authority[1:close]
        tail = authority[close + 1 :]
        if tail and not tail.startswith(":"):
            raise InvalidIndicator(RejectReason.INVALID_HOST)
        has_port, port_text = bool(tail), tail[1:]
    else:
        if authority.count(":") > 1:
            raise InvalidIndicator(RejectReason.INVALID_HOST)
        host_text, colon, port_text = authority.partition(":")
        has_port = bool(colon)

    port = _parse_port(port_text) if has_port else None
    host = normalize_host(host_text, bracketed=bracketed)

    before_fragment, hash_mark, _fragment = remainder.partition("#")
    path, question_mark, _query = before_fragment.partition("?")
    path = path or "/"
    has_query, has_fragment = bool(question_mark), bool(hash_mark)

    if port == _DEFAULT_PORTS[scheme]:
        port = None
    host_part = f"[{host.ascii}]" if host.kind is HostKind.IPV6 else host.ascii
    origin = f"{scheme}://{host_part}" + (f":{port}" if port is not None else "")

    shown_path = path
    if len(shown_path) > _MAX_DISPLAY_PATH:
        shown_path = shown_path[:_MAX_DISPLAY_PATH] + "…"
    display = origin + shown_path
    if has_query:
        display += "?[hidden]"
    if has_fragment:
        display += "#[hidden]"

    return Indicator(
        indicator_type=IndicatorType.URL,
        scheme=scheme,
        host=host.ascii,
        host_unicode=host.unicode,
        host_kind=host.kind,
        is_idn=host.is_idn,
        port=port,
        path=path,
        has_query=has_query,
        has_fragment=has_fragment,
        display_value=display,
        url_without_query=origin + path,
        lookup_blocked_reason=host.lookup_blocked_reason,
    )


def _parse_port(port_text: str) -> int:
    if not (port_text.isascii() and port_text.isdigit()):
        raise InvalidIndicator(RejectReason.INVALID_PORT)
    port = int(port_text)
    if not 1 <= port <= 65535:
        raise InvalidIndicator(RejectReason.INVALID_PORT)
    return port
