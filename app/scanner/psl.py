"""Public Suffix List lookup against a vendored, immutable snapshot.

This module only reads the snapshot shipped in ``app/scanner/data``. It never
downloads anything, never resolves a name, and never guesses a registrable
domain from "the last two labels". See ``data/PSL_SOURCE.md`` for provenance.

It implements the published PSL algorithm: the prevailing rule is an
exception rule if one matches, otherwise the matching rule with the most
labels, otherwise the default rule ``*`` (the last label alone).
"""

from __future__ import annotations

import functools
from dataclasses import dataclass, field
from importlib import resources

import idna

_DATA_FILE = "data/public_suffix_list.dat"
_SECTION_MARKERS = {
    "// ===BEGIN ICANN DOMAINS===": ("icann", True),
    "// ===END ICANN DOMAINS===": ("icann", False),
    "// ===BEGIN PRIVATE DOMAINS===": ("private", True),
    "// ===END PRIVATE DOMAINS===": ("private", False),
}


class PublicSuffixError(RuntimeError):
    """The vendored snapshot is missing or malformed. Fails closed."""


@dataclass(frozen=True)
class SuffixInfo:
    """Result of a public suffix lookup for an ASCII (punycode) hostname.

    ``listed`` is False when no rule matched and the default rule applied:
    the suffix is then only the last label, and callers should treat the
    result with caution.
    ``section`` is ``"icann"`` or ``"private"`` for a listed suffix and
    ``None`` when unlisted.
    ``registrable_domain`` is ``None`` when the host is itself a public
    suffix (nothing is registrable under it).
    """

    public_suffix: str = field(repr=False)
    registrable_domain: str | None = field(repr=False)
    section: str | None
    listed: bool


@dataclass(frozen=True)
class _Rules:
    exact: dict[str, str]  # suffix -> section
    wildcard: dict[str, str]  # parent of "*.parent" -> section
    exception: dict[str, str]  # suffix -> section


def _to_ascii(rule: str) -> str:
    try:
        return idna.encode(rule).decode("ascii")
    except (idna.IDNAError, UnicodeError) as exc:
        raise PublicSuffixError("snapshot contains an unusable rule") from exc


def parse_rules(text: str) -> _Rules:
    """Parse PSL text. Raises :class:`PublicSuffixError` if it is malformed."""
    exact: dict[str, str] = {}
    wildcard: dict[str, str] = {}
    exception: dict[str, str] = {}
    section: str | None = None
    seen = {"icann": 0, "private": 0}

    for raw_line in text.splitlines():
        line = raw_line.strip()
        marker = _SECTION_MARKERS.get(line)
        if marker is not None:
            name, opening = marker
            if opening and section is not None:
                raise PublicSuffixError("nested sections in snapshot")
            if not opening and section != name:
                raise PublicSuffixError("mismatched section end in snapshot")
            section = name if opening else None
            continue
        if not line or line.startswith("//"):
            continue
        if section is None:
            raise PublicSuffixError("rule outside a known section")

        rule = line.split()[0].lower()
        if rule.startswith("!"):
            exception[_to_ascii(rule[1:])] = section
        elif rule.startswith("*."):
            wildcard[_to_ascii(rule[2:])] = section
        elif "*" in rule:
            raise PublicSuffixError("unsupported wildcard form in snapshot")
        else:
            exact[_to_ascii(rule)] = section
        seen[section] += 1

    if section is not None or not all(seen.values()):
        raise PublicSuffixError("snapshot is missing a section or is empty")
    return _Rules(exact=exact, wildcard=wildcard, exception=exception)


@functools.lru_cache(maxsize=1)
def _load() -> _Rules:
    try:
        text = resources.files("app.scanner").joinpath(_DATA_FILE).read_text("utf-8")
    except (OSError, ModuleNotFoundError) as exc:
        raise PublicSuffixError("vendored snapshot is unavailable") from exc
    return parse_rules(text)


def lookup(host: str, rules: _Rules | None = None) -> SuffixInfo | None:
    """Return suffix information for ``host``, or ``None`` if it is unusable.

    ``host`` must already be normalised ASCII (lowercase, punycode, no
    trailing dot). Empty labels (``".com"``, ``"a..b"``) return ``None``.
    ``rules`` exists for tests; production code uses the vendored snapshot.
    """
    if not host or host != host.lower():
        return None
    labels = host.split(".")
    if any(not label for label in labels):
        return None
    table = _load() if rules is None else rules

    best_len = 0
    best_section: str | None = None
    exception_len = 0
    exception_section: str | None = None

    for n in range(1, len(labels) + 1):
        suffix = ".".join(labels[-n:])
        if suffix in table.exception:
            exception_len, exception_section = n, table.exception[suffix]
        if suffix in table.exact:
            best_len, best_section = n, table.exact[suffix]
        elif n >= 2:
            parent = ".".join(labels[-n + 1 :])
            if parent in table.wildcard:
                best_len, best_section = n, table.wildcard[parent]

    if exception_len:
        suffix_len = exception_len - 1  # an exception drops its leftmost label
        section: str | None = exception_section
        listed = True
    elif best_len:
        suffix_len, section, listed = best_len, best_section, True
    else:
        suffix_len, section, listed = 1, None, False  # default "*" rule

    public_suffix = ".".join(labels[-suffix_len:])
    registrable = (
        ".".join(labels[-suffix_len - 1 :]) if len(labels) > suffix_len else None
    )
    return SuffixInfo(
        public_suffix=public_suffix,
        registrable_domain=registrable,
        section=section,
        listed=listed,
    )
