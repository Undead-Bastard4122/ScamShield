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

- **Not a browser parser.** This is a strict subset of what browsers accept,
  chosen so that anything ambiguous is rejected. It has not been compared
  against a WHATWG reference implementation; a corpus comparison is a
  follow-up.
- **No registrable domain.** Deriving it needs a pinned public suffix list
  that never downloads at runtime. Not implemented; do not approximate with
  "last two labels". Required before any component needs it.
- **No shortener detection** (Phase 2).
- Lock files have no hashes yet (see README).
