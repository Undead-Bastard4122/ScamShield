"""Host normalisation: IDNA, IP-literal handling, and lookup eligibility.

Pure functions. No DNS resolution, sockets, or any other I/O: a hostname is
only ever parsed as text, never resolved.
"""

from __future__ import annotations

import ipaddress
import re

import idna

from app.scanner.models import HostInfo, HostKind, InvalidIndicator, RejectReason

_LDH_LABEL = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
# Browsers treat a host whose last label is numeric as an IPv4 address, even
# in decimal ("2130706433"), hex ("0x7f.1") or octal ("0177.0.0.1") forms.
_NUMERIC_LABEL = re.compile(r"^(?:0[xX][0-9a-fA-F]*|[0-9]+)$")
_MAX_HOST_LENGTH = 253

# A limited, conservative heuristic: names that only make sense on a private
# network, or that are reserved and never resolve publicly. These are never
# offered to external providers. This list is NOT exhaustive and is not
# derived from the IANA special-use registry; do not treat a name that is
# absent from it as public.
_NON_PUBLIC_SUFFIXES = frozenset(
    {
        "localhost",
        "local",
        "internal",
        "intranet",
        "lan",
        "home",
        "corp",
        "home.arpa",
        "test",
        "example",
        "invalid",
        "onion",
    }
)


def _ip_blocked_reason(
    ip: ipaddress.IPv4Address | ipaddress.IPv6Address,
) -> str | None:
    candidates = [ip]
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
        candidates.append(ip.ipv4_mapped)
    if all(candidate.is_global for candidate in candidates):
        return None
    return "non-public IP address"


def _dns_blocked_reason(ascii_host: str) -> str | None:
    labels = ascii_host.split(".")
    if len(labels) == 1:
        return "single-label host name"
    for size in (2, 1):
        if len(labels) >= size and ".".join(labels[-size:]) in _NON_PUBLIC_SUFFIXES:
            return "private or reserved name"
    return None


def normalize_host(raw_host: str, *, bracketed: bool = False) -> HostInfo:
    """Normalise a host taken from a URL authority or a bare domain.

    ``bracketed`` means the text came from ``[...]`` and must be IPv6.
    Raises :class:`InvalidIndicator` for anything unsafe or ambiguous.
    """
    if "%" in raw_host:
        # Percent-encoded hosts and IPv6 zone IDs are read differently by
        # different programs.
        raise InvalidIndicator(RejectReason.INVALID_HOST)

    if bracketed:
        try:
            ip6 = ipaddress.IPv6Address(raw_host)
        except ValueError:
            raise InvalidIndicator(RejectReason.INVALID_HOST) from None
        return HostInfo(
            ascii=ip6.compressed,
            unicode=None,
            kind=HostKind.IPV6,
            is_idn=False,
            lookup_blocked_reason=_ip_blocked_reason(ip6),
        )

    try:
        ascii_host = idna.encode(raw_host, uts46=True).decode("ascii")
    except (idna.IDNAError, UnicodeError):
        raise InvalidIndicator(RejectReason.INVALID_HOST) from None
    if ascii_host.endswith("."):
        ascii_host = ascii_host[:-1]
    if not ascii_host or len(ascii_host) > _MAX_HOST_LENGTH:
        raise InvalidIndicator(RejectReason.INVALID_HOST)

    labels = ascii_host.split(".")
    if _NUMERIC_LABEL.match(labels[-1]):
        try:
            ip4 = ipaddress.IPv4Address(ascii_host)
        except ValueError:
            raise InvalidIndicator(RejectReason.OBFUSCATED_IP) from None
        return HostInfo(
            ascii=str(ip4),
            unicode=None,
            kind=HostKind.IPV4,
            is_idn=False,
            lookup_blocked_reason=_ip_blocked_reason(ip4),
        )

    if not all(_LDH_LABEL.match(label) for label in labels):
        raise InvalidIndicator(RejectReason.INVALID_HOST)

    is_idn = any(label.startswith("xn--") for label in labels)
    unicode_host: str | None = None
    if is_idn:
        try:
            decoded = idna.decode(ascii_host)
        except (idna.IDNAError, UnicodeError):
            raise InvalidIndicator(RejectReason.INVALID_HOST) from None
        if decoded != ascii_host:
            unicode_host = decoded

    return HostInfo(
        ascii=ascii_host,
        unicode=unicode_host,
        kind=HostKind.DNS_NAME,
        is_idn=is_idn,
        lookup_blocked_reason=_dns_blocked_reason(ascii_host),
    )
