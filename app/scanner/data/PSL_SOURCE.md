# Public Suffix List snapshot: provenance

- **File:** `public_suffix_list.dat` (unmodified copy)
- **Upstream repository:** https://github.com/publicsuffix/list
- **Upstream commit:** `94ec5df7273926560d91e77c002000ba1a53fec4` (committed 2026-11-06T10:01:36+01:00)
- **Retrieved:** 2026-11-08, by `git clone --depth 1`
- **SHA-256:** `762b6cbdd2dacc597b398fcd7860e2184b684125a58aa177dbdf54916a1f3430`
- **Licence:** Mozilla Public License 2.0, copy in `PSL_LICENSE_MPL-2.0.txt`. The file carries its own MPL notice header, which is kept. The file is not modified, so MPL source-availability obligations are met by distributing it as-is.
- **Official test vectors:** `tests/data/psl_official_tests.txt`, from the same commit (`tests/tests.txt`, dedicated to the public domain under CC0 per its header).

## Provenance caveat (read this)

The file's header asks that the list be pulled "from, and only from" https://publicsuffix.org/list/public_suffix_list.dat. That URL was **not reachable** from the environment where this snapshot was taken (the network proxy refused the connection), so the snapshot comes from the official `publicsuffix/list` repository instead. It has **not** been compared byte-for-byte against the publicsuffix.org copy. Whoever refreshes the snapshot with normal network access should fetch from publicsuffix.org, compare, and record the result here.

## Rules for this file

- **Never downloaded at runtime.** The application reads only this vendored copy. There is no auto-update and no fallback.
- **Refreshing is a reviewed change:** replace the file, update every value above, run the tests (they check the SHA-256 and the official vectors), and open a pull request. Never edit the list by hand.
- The list is community-maintained and changes often. A stale snapshot can misjudge new suffixes; this is acceptable for Phase 1 and must be revisited before release.
