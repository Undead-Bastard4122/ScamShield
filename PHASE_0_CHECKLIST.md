# ScamShield — Phase 0 Checklist

**Phase:** Documentation and technical preparation  
**Status:** Approved by the project owner on 2026-11-08  
**Last updated:** 2026-11-05

This checklist tracks preparation only. Phase 0 was approved on 2026-11-08 (see Coding status below).

## A. Repository baseline

- [x] Confirm GitHub repository access.
- [x] Confirm repository name and owner.
- [x] Confirm public visibility and main branch.
- [x] Inspect the existing README.
- [x] Confirm the Python .gitignore exists and excludes environment files.
- [x] Confirm the MIT LICENSE exists.
- [x] Keep existing license and ignore files intact.

Repository: https://github.com/Undead-Bastard4122/ScamShield

## B. Product definition

- [x] Project name: ScamShield.
- [x] Portfolio ambition recorded.
- [x] Privacy-first requirement recorded.
- [x] URL and domain input support recorded.
- [x] Telegram-only interface recorded.
- [x] MVP scope and non-goals documented.
- [x] Four outcome categories documented.
- [x] No-AI-verdict and no-URL-fetch boundaries documented.

## C. Technical documentation

- [x] README.md updated.
- [x] REQUIREMENTS.md created.
- [x] ARCHITECTURE.md created.
- [x] THREAT_MODEL.md created.
- [x] PRIVACY.md created.
- [x] DECISIONS.md created.
- [x] ROADMAP.md created.
- [x] PROVIDER_EVALUATION.md created.
- [x] Phase 0 checklist created.

## D. Provider and privacy review

- [x] Candidate provider capabilities and limitations researched.
- [x] Commercial-use restrictions recorded where applicable.
- [x] Provider-specific privacy concerns recorded.
- [x] Select the first provider or providers for the MVP (candidates: PhishTank, URLhaus; enablement pending term checks, D-015).
- [x] Confirm current terms, quotas, and cost at implementation time: **deferred to the Phase 3 entry gate** (owner-approved, 2026-11-08). No provider may be enabled, and no provider account, key, or request used, before this is done.
- [x] Decide which provider data categories may be shared (a URL without userinfo, query string and fragment, path included; bare domains are not sent to PhishTank; see docs/CONSENT_COPY.md).
- [x] Approve user-facing consent wording and interaction (owner, 2026-11-07: revision 3.1).
- [x] Confirm whether consent is per scan or a revocable saved preference (per scan, per provider; D-018).

## E. Data and security design

- [x] No arbitrary destination fetching established as a security boundary.
- [x] External provider requests require consent as the design baseline.
- [x] Raw URL and secret logging prohibited.
- [x] Conceptual data entities documented.
- [x] Approve whether scan history is off by default (off by default, opt-in; D-016).
- [x] 30-day retention baseline approved (D-016).
- [x] Approve live-database deletion, retention expiry, and backup-purge semantics: **deferred to the Phase 5 entry gate** with the schema (owner-approved, 2026-11-08). No database code before then.
- [x] Approve final database schema, indexes, and constraints: **deferred by the owner to the start of Phase 5** (D-017, 2026-11-07).
- [x] Review risk classification rules and freshness requirements: **deferred** (owner-approved, 2026-11-08). Local-only rules are reviewed at the Phase 2 entry and provider evidence and freshness rules at the Phase 3 entry (D-019). A local heuristic alone must not produce HIGH RISK or NO KNOWN THREAT DETECTED.
- [x] Review threat model and remaining risks (accepted by the owner on 2026-11-08 as the Phase 0 planning baseline; this is not production security approval).

## F. Phase 1 readiness

- [x] Define the supported runtime and dependency versions (Python 3.13.18; exact pins in interim lock files without hashes; delivered in the Phase 1 pull request).
- [x] Agree on initial test cases and safe fixtures (tests/test_validator.py and tests/test_config.py; synthetic data only; delivered in the Phase 1 pull request).
- [x] Confirm acceptance criteria for the standalone URL/domain engine (docs/input-engine.md and its test suite).
- [x] Confirm local development and Git branching workflow (CONTRIBUTING.md).
- [x] Approve Phase 0 exit (owner, 2026-11-08).

## Phase 0 exit criteria

All items in sections D, E, and F marked as approval tasks must be resolved or explicitly deferred with a documented reason.

**Coding status:** Phase 0 was approved by the owner on 2026-11-08. The standalone Phase 1 input engine and configuration loader exist. Phase 1 as a whole is not complete (see ROADMAP.md). Phase 2 and later have not started and each begins only on the owner's instruction, subject to the entry gates in ROADMAP.md. Items deferred to those gates (provider terms and cost, deletion and backup semantics, final schema, risk rules) stay open until then.

## Next milestone after sign-off

Phase 1: build and test a standalone URL/domain validation and normalisation engine. It must work without Telegram integration and without contacting the submitted destination.
