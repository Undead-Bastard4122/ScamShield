"""Data types for the input engine.

Pure data only: nothing in this module performs I/O or touches the network.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class IndicatorType(StrEnum):
    URL = "url"
    DOMAIN = "domain"


class HostKind(StrEnum):
    DNS_NAME = "dns_name"
    IPV4 = "ipv4"
    IPV6 = "ipv6"


class RejectReason(StrEnum):
    """Stable machine-readable rejection codes."""

    EMPTY = "empty"
    TOO_LONG = "too_long"
    MULTIPLE_INDICATORS = "multiple_indicators"
    CONTROL_CHARACTERS = "control_characters"
    AMBIGUOUS_SYNTAX = "ambiguous_syntax"
    UNSUPPORTED_SCHEME = "unsupported_scheme"
    MISSING_SCHEME = "missing_scheme"
    EMBEDDED_CREDENTIALS = "embedded_credentials"
    INVALID_HOST = "invalid_host"
    INVALID_PORT = "invalid_port"
    OBFUSCATED_IP = "obfuscated_ip"
    IP_NOT_DOMAIN = "ip_not_domain"


# User-safe messages. They must never echo the submitted text: submitted
# values can contain secrets and must not reach logs or error reports.
REJECT_MESSAGES: dict[RejectReason, str] = {
    RejectReason.EMPTY: "Send one link or domain name to check.",
    RejectReason.TOO_LONG: "That input is too long to check.",
    RejectReason.MULTIPLE_INDICATORS: ("Please send one link or domain at a time."),
    RejectReason.CONTROL_CHARACTERS: (
        "That input contains hidden or control characters."
    ),
    RejectReason.AMBIGUOUS_SYNTAX: (
        "That link uses syntax that different programs read differently, "
        "so it cannot be checked safely."
    ),
    RejectReason.UNSUPPORTED_SCHEME: ("Only http:// and https:// links are supported."),
    RejectReason.MISSING_SCHEME: (
        "Send a full link starting with http:// or https://, "
        "or only a domain name such as example.com."
    ),
    RejectReason.EMBEDDED_CREDENTIALS: (
        "That link contains a username or password. It was not checked "
        "or stored. Do not share links containing credentials."
    ),
    RejectReason.INVALID_HOST: "That is not a valid host name.",
    RejectReason.INVALID_PORT: "That link has an invalid port number.",
    RejectReason.OBFUSCATED_IP: (
        "That host is written as a disguised IP address, which "
        "cannot be checked safely."
    ),
    RejectReason.IP_NOT_DOMAIN: (
        "That is an IP address, not a domain name. To check an IP address, "
        "send it inside a full http:// or https:// link."
    ),
}


class InvalidIndicator(ValueError):
    """Raised when input cannot be accepted as a URL or domain.

    The message is fixed per reason and never contains the submitted text.
    """

    def __init__(self, reason: RejectReason) -> None:
        self.reason = reason
        super().__init__(REJECT_MESSAGES[reason])


@dataclass(frozen=True)
class HostInfo:
    """A normalised host."""

    ascii: str
    unicode: str | None
    kind: HostKind
    is_idn: bool
    lookup_blocked_reason: str | None


@dataclass(frozen=True)
class Indicator:
    """A validated, normalised URL or domain.

    ``display_value`` is safe to show to the user: it never contains
    credentials, and the query string and fragment are replaced by markers.

    ``url_without_query`` is the most a provider could ever be offered for a
    URL: no userinfo, query, or fragment. It still includes the path, which
    can hold private tokens, so the consent gate (Phase 3) decides whether
    to use it. It is ``None`` for domain-only input.

    ``lookup_blocked_reason`` is set for hosts that must never be sent to an
    external provider (private or reserved IPs, single-label or internal
    names). Hostnames can themselves be private (see PRIVACY.md).
    """

    indicator_type: IndicatorType
    scheme: str | None
    host: str
    host_unicode: str | None
    host_kind: HostKind
    is_idn: bool
    port: int | None
    path: str
    has_query: bool
    has_fragment: bool
    display_value: str
    url_without_query: str | None
    lookup_blocked_reason: str | None
