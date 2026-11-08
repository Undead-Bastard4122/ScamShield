# ScamShield — Development Roadmap

**Document status:** Planning baseline  
**Version:** 1.0-draft  
**Last reviewed:** 2026-11-05

The roadmap is milestone-based. A phase is complete only when its deliverables and acceptance criteria are met. The existence of a file or a successful bot response is not, by itself, proof that a milestone is complete.

## Phase 0 — Project documentation and technical preparation

**Status:** Approved by the project owner on 2026-11-08

Deliverables:

- [x] Confirm product name and core direction.
- [x] Lock privacy-first approach, both input types, and Telegram-only interface.
- [x] Draft functional and non-functional requirements.
- [x] Draft modular-monolith architecture.
- [x] Draft privacy and threat-model baselines.
- [x] Review candidate threat-intelligence providers.
- [x] Approve the first provider set and its permitted use (candidates only: PhishTank and URLhaus, both disabled; terms and data handling are a Phase 3 entry gate).
- [x] Approve scan-history and retention behaviour (baseline: off by default, opt-in, 30 days; deletion and backup semantics still to be written).
- [x] Approve the consent flow (per scan, per provider; wording revision 3.1 in docs/CONSENT_COPY.md).
- [x] Decide database schema timing: final schema approval deferred to the start of Phase 5 (D-017).
- [x] Complete Phase 0 sign-off (owner, 2026-11-08).

**Exit condition:** Product scope, provider policy, privacy controls, schema timing, and Phase 1 acceptance tests are approved. Items explicitly deferred to a later phase entry are listed in PHASE_0_CHECKLIST.md. No application code is required in this phase.

## Phase 1 — Project foundation and input engine

Deliverables:

- Establish the Python project and reproducible development environment.
- Add configuration validation and secret-loading rules.
- Implement URL/domain validation and normalisation.
- Handle IDNA and safe display.
- Reject unsupported schemes and embedded credentials.
- Add unit tests for valid, invalid, and adversarial inputs.
- Establish linting, formatting, and test commands.

**Exit condition:** A standalone, tested input engine works without Telegram or external provider calls.

## Phase 2 — Local heuristic analysis

**Entry gate (owner-approved 2026-11-08):** review the local-only risk rules before implementation. A local heuristic alone must not produce HIGH RISK or NO KNOWN THREAT DETECTED; those outcomes need approved evidence rules (D-019).


Deliverables:

- Define documented heuristic identifiers.
- Implement domain and URL structure checks.
- Add lookalike and suspicious-hostname signals with conservative rules.
- Identify shorteners without resolving them.
- Generate structured local findings.
- Test benign and suspicious fixtures.

**Exit condition:** Local analysis returns deterministic evidence and does not make network requests.

## Phase 3 — Threat-intelligence integration

**Entry gate (owner-approved 2026-11-08):** before any adapter is enabled or any provider account, key, or request is used, re-verify the provider's current terms, quotas, cost, and data handling, and re-check `docs/CONSENT_COPY.md`. Review provider evidence and freshness rules (D-019).


Deliverables:

- Implement the shared provider interface.
- Add the approved provider adapters.
- Add the consent gate and provider-specific data preview.
- Handle timeouts, rate limits, stale results, and provider errors.
- Add safe caching based on provider semantics.
- Preserve source provenance and partial coverage.
- Test provider adapters with mocked responses.

**Exit condition:** Approved lookups work only after consent, and provider failures cannot become false clean results.

## Phase 4 — Telegram bot interface

Deliverables:

- Connect the Telegram Bot API.
- Implement onboarding, help, scan, about, and privacy flows.
- Accept URL and domain inputs.
- Add consent interactions.
- Format evidence-based reports.
- Add user-level rate limits and graceful errors.

**Exit condition:** A user can complete the full private-chat scan workflow with correct privacy and error behaviour.

## Phase 5 — Persistence and user controls

**Entry gate (owner-approved 2026-11-08; the approvals themselves are still required before any database code):** final schema, indexes and constraints; live-database deletion, retention expiry and backup-purge semantics (D-016, D-017).

Deliverables:

- Implement approved database schema.
- Add optional scan history.
- Enforce per-user ownership checks.
- Implement retention and deletion rules.
- Add migration/backup documentation.
- Test database failures and cross-user access.

**Exit condition:** Opted-in records persist, expire, and can be deleted without cross-user access.

## Phase 6 — Testing and security hardening

Deliverables:

- Unit and integration test suite.
- Labelled benign/suspicious/known-threat fixtures.
- False-positive and false-negative evaluation.
- Rate-limit and abuse tests.
- Secret and logging audit.
- Dependency review.
- Threat-model review.
- Release checklist.

**Exit condition:** Release candidate satisfies the documented MVP acceptance criteria and known limitations are published.

## Phase 7 — Deployment and portfolio release

Deliverables:

- Deploy to a suitable Linux host.
- Configure production secrets.
- Configure process restart, monitoring, and redacted logs.
- Verify persistent storage and backup/restore.
- Publish installation and operator instructions.
- Add screenshots or a short demonstration using safe test data.
- Tag the first release.

**Exit condition:** The public repository can be installed from documentation, the bot is operational, and the release status is accurately represented.

## Phase 8 — Post-MVP evaluation

Potential improvements, not commitments:

- Telegram group moderation.
- More threat-intelligence providers.
- Local threat-feed cache.
- Web dashboard.
- PostgreSQL.
- Webhook deployment.
- Abuse-report moderation queue.
- Additional languages and accessibility improvements.

Every post-MVP feature must be justified by user need and reviewed for privacy/security impact.

## Engineering workflow

- Work on small, named tasks.
- Use focused commits that explain intent.
- Write tests alongside implementation.
- Keep main branch in a working state.
- Document meaningful architecture changes in DECISIONS.md.
- Do not add dependencies without a reason.
- Never place real credentials or sensitive URLs in issues, commits, screenshots, or examples.
