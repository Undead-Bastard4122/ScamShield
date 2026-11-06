# ScamShield — Phase 0 Checklist

**Phase:** Documentation and technical preparation  
**Status:** In progress  
**Last updated:** 2026-11-05

This checklist tracks preparation only. Application code must not be started until the exit criteria are approved.

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
- [ ] Confirm current terms, quotas, and cost at implementation time.
- [ ] Decide which provider data categories may be shared.
- [ ] Approve user-facing consent wording and interaction.
- [x] Confirm whether consent is per scan or a revocable saved preference (per scan, per provider; D-018).

## E. Data and security design

- [x] No arbitrary destination fetching established as a security boundary.
- [x] External provider requests require consent as the design baseline.
- [x] Raw URL and secret logging prohibited.
- [x] Conceptual data entities documented.
- [x] Approve whether scan history is off by default (off by default, opt-in; D-016).
- [ ] Approve retention period and deletion semantics.
- [ ] Approve final database schema, indexes, and constraints.
- [ ] Review risk classification rules and freshness requirements.
- [ ] Review threat model and remaining risks.

## F. Phase 1 readiness

- [ ] Define the supported runtime and dependency versions.
- [ ] Agree on initial test cases and safe fixtures.
- [ ] Confirm acceptance criteria for the standalone URL/domain engine.
- [ ] Confirm local development and Git branching workflow.
- [ ] Approve Phase 0 exit.

## Phase 0 exit criteria

All items in sections D, E, and F marked as approval tasks must be resolved or explicitly deferred with a documented reason.

**Coding status:** Not started. Do not create application source files during Phase 0.

## Next milestone after sign-off

Phase 1: build and test a standalone URL/domain validation and normalisation engine. It must work without Telegram integration and without contacting the submitted destination.
