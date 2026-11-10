# Input engine: accepted grammar and boundaries

Applies to `app/scanner` (Phase 1). The engine only parses text. It never
resolves a name, opens a socket, or fetches anything (D-009).

## Accepted input

One of:

1. **URL:** `http://` or `https://` (scheme case-insensitive), then a host,
   an optional `:port`, then an optional path, `?query`, `#fragment`.
2. **Bare domain:** a DNS name with no scheme, port, path, or `@`.

Input is at most 4,096 characters (checked first) and is trimmed of outer
whitespace.

## Normalisation

- Host: UTS #46 mapping and IDNA to ASCII (punycode). Display is always the
  ASCII form; the Unicode form is exposed separately and is never trusted.
- One trailing dot is removed. Default ports (80 for http, 443 for https) are
  dropped. An empty path becomes `/`.
- The path is kept as submitted. It is not percent-decoded and dot segments
  are not resolved.
- The query and fragment are never kept, only flagged (`has_query`,
  `has_fragment`). `display_value` shows `?[hidden]` and `#[hidden]`.
- `url_without_query` is scheme + host + port + path. The path can still hold
  private tokens, so the consent gate (Phase 3) decides whether to send it.

## Output safety

`display_value` is privacy-redacted but **not** safe to paste into a message.
It can contain user-controlled path text, including characters that are
special in Telegram HTML or MarkdownV2. Whoever renders it (Phase 4) must
escape it for the chosen parse mode, or send it as plain text.

## Rejected (not guessed)

| Reason | Examples |
|---|---|
| empty / too long | empty, over 4,096 characters |
| multiple indicators | any inner whitespace |
| control characters | control, zero-width, bidi, lone surrogates |
| ambiguous syntax | any backslash |
| unsupported scheme | `javascript:`, `data:`, `file:`, `ftp:`, `mailto:` |
| missing scheme | `example.com/path`, `example.com:80`, `a@b.com`, `//host` |
| embedded credentials | any `@` in the authority |
| invalid host | bad labels, `%` in host, bad brackets, overlong names |
| invalid port | not 1-65535, empty, non-ASCII digits |
| obfuscated IP | `2130706433`, `0x7f.0.0.1`, `127.1`, numeric last label |
| IP as domain | bare `8.8.8.8` (send it inside a URL instead) |

## Lookup eligibility

`lookup_blocked_reason` is set for non-public IPs (via `ipaddress.is_global`,
including IPv4-mapped IPv6), single-label names, and a small list of private
or reserved suffixes (`localhost`, `local`, `internal`, `lan`, `home.arpa`,
`onion`, and a few more). **This list is a limited heuristic, not the IANA
special-use registry.** A name missing from it must not be assumed public.

## Known limits

- **Not a browser parser, and not claimed to be.** This is a strict subset of
  what browsers accept, chosen so that anything ambiguous is rejected. It is
  compared against the WHATWG URL test data (see below); that comparison is
  evidence about differences, not a promise of browser equivalence.
- **Registrable domain comes from a vendored, dated Public Suffix List
  snapshot** (`app/scanner/data/`, provenance and licence in `PSL_SOURCE.md`
  and `PSL_LICENSE_MPL-2.0.txt`). It is never downloaded, never updated at
  runtime, and never approximated with "last two labels". The lookup passes
  the official PSL test vectors (78 cases) and fails closed if the snapshot
  is missing or malformed.
  - `registrable_domain`, `public_suffix`, `suffix_section` (`icann` or
    `private`) and `suffix_listed` are set only for public-looking DNS names.
    They are `None` for IP addresses and for single-label or private/reserved
    names, even where the PSL default rule would give an answer.
  - A suffix that is not in the list gets the PSL default rule (the last
    label) and `suffix_listed = False`. Treat that result with caution.
  - A host that is itself a public suffix (for example `github.io`) has no
    registrable domain.
  - The snapshot ages. It was taken on 2026-11-08 and must be refreshed in a
    reviewed change before release. It was not compared with the copy on
    publicsuffix.org (that site was unreachable when it was taken).
- **No shortener detection** (Phase 2).
- Lock files have no hashes yet (see README).

## Differential testing against the WHATWG URL test data

`tests/test_wpt_differential.py` runs ScamShield over the web-platform-tests
`urltestdata.json` (pinned to upstream commit `96769025`, BSD-3-Clause; see
`tests/data/wpt/SOURCE.md`). In scope are absolute inputs that a browser
parses to an `http(s)` URL, plus absolute `http(s)`-looking inputs that a
browser rejects. Result on the pinned data: **283 cases**.

| Outcome | Cases | Meaning |
|---|---|---|
| equivalent | 69 | Both accept; scheme, host (after IDNA) and port agree. |
| agree_reject | 149 | Browser rejects and so do we. |
| strict_reject | 65 | Browser accepts, we reject on purpose (reasons below). |
| MISMATCH | 0 | Both accept but disagree. The test fails if this is ever not 0. |
| ACCEPTS_BROWSER_FAILURE | 0 | We accept what a browser rejects. The test fails if this is ever not 0. |

Strict rejections by reason: embedded credentials 15, invalid host 13,
`http:example.com`-style missing `//` 12, control characters 9, inner
whitespace 8, disguised IPv4 5, backslashes 3.

Every outcome is recorded in `tests/data/wpt/expected_outcomes.json`. Any
change to parser behaviour shows up as a diff there and must be reviewed.

**What this does not cover:** path, query and fragment normalisation (we keep
the path as submitted and discard query and fragment, so they are not
compared); relative URLs; non-http(s) schemes; the IDNA conformance data;
and the JavaScript-only test file. Only the pinned snapshot was compared, so
browsers that change later are not tracked.
