# ScamShield — Decision Log

**Document status:** Active  
**Last reviewed:** 2026-11-05

This file records decisions that materially affect product scope, architecture, security, or operations. Revisit a decision only through an explicit change with a reason and impact assessment.

## Locked product decisions

### D-001 — Project name

**Status:** Accepted  
**Decision date:** 2026-10-31  
**Decision:** The project is named ScamShield.  
**Reason:** Clear, memorable name aligned with the defensive purpose.

### D-002 — Product ambition

**Status:** Accepted  
**Decision date:** 2026-10-31  
**Decision:** The initial ambition is a serious public GitHub portfolio project.  
**Reason:** Prioritise demonstrable engineering quality, tests, documentation, and a usable result over premature monetisation.

### D-003 — Privacy model

**Status:** Accepted  
**Decision date:** 2026-10-31  
**Decision:** Privacy-first.  
**Consequences:** Minimise stored data, avoid raw URL logging, disclose third-party data sharing, and do not send submitted indicators externally without explicit consent.

### D-004 — Supported input types

**Status:** Accepted  
**Decision date:** 2026-10-31  
**Decision:** Both complete URLs and bare domain names are supported.  
**Consequences:** The input layer must distinguish URL-level from domain-level analysis. A domain-only scan must not be represented as a full URL check.

### D-005 — Initial interface

**Status:** Accepted  
**Decision date:** 2026-10-31  
**Decision:** Telegram bot only.  
**Consequences:** No web dashboard in the MVP. Initial support is for individual private chats.

## Architecture decisions

### D-006 — Python as primary language

**Status:** Accepted  
**Decision date:** 2026-10-31  
**Decision:** Use Python for the application.  
**Reason:** Suitable for bot development, parsing, API integration, testing, and the project's learning and portfolio goals.

### D-007 — Modular monolith

**Status:** Accepted for MVP  
**Decision date:** 2026-11-05  
**Decision:** Implement one deployable application with separate bot, input/scanner, provider, privacy, risk, report, and persistence modules.  
**Reason:** Keeps deployment simple without creating a single unmaintainable file or premature microservices.

### D-008 — SQLite as initial persistence option

**Status:** Proposed; final schema pending  
**Decision date:** 2026-11-05  
**Decision:** Start with SQLite for a low-volume, single-process MVP if the final schema and hosting model support it.  
**Reason:** Minimal operational overhead. PostgreSQL remains a future option if concurrency or scale requires it.

### D-009 — No arbitrary URL fetching

**Status:** Accepted security boundary  
**Decision date:** 2026-11-05  
**Decision:** The MVP will not open, resolve, or follow user-submitted destinations.  
**Reason:** Prevent SSRF and avoid exposing the host or internal network. Local parsing and fixed-host provider lookups are sufficient for the initial product.

### D-010 — Local-only by default

**Status:** Accepted privacy design baseline  
**Decision date:** 2026-11-05  
**Decision:** Perform local analysis first. External provider queries require clear user consent that names the provider and the data category being disclosed.  
**Reason:** URLs can contain private tokens or internal hostnames. Declining external lookup must still produce a local report.

### D-011 — Provider independence

**Status:** Accepted architecture rule  
**Decision date:** 2026-11-05  
**Decision:** Integrate providers through a shared internal adapter interface.  
**Reason:** Providers can change terms, availability, API versions, costs, and coverage independently.

### D-012 — Evidence-first verdicts

**Status:** Accepted architecture rule  
**Decision date:** 2026-11-05  
**Decision:** The risk engine returns an explainable classification with source provenance and coverage. It does not claim a numeric probability unless a future model is properly calibrated.  
**Reason:** A score without a validated statistical basis would create false precision.

### D-013 — No AI verdict engine in MVP

**Status:** Accepted scope boundary  
**Decision date:** 2026-11-05  
**Decision:** No generative AI is required to make the initial verdict.  
**Reason:** Deterministic evidence and transparent rules are easier to test and explain. AI may be reconsidered later for safe explanation assistance, never as an unsupported source of threat evidence.

### D-014 — Initial deployment approach

**Status:** Proposed for MVP  
**Decision date:** 2026-11-05  
**Decision:** Start with Telegram long polling on a Linux host and one application process.  
**Reason:** Lower operational complexity than a webhook deployment at this scale.

## Decisions intentionally left open

### D-015 — Threat-intelligence providers

**Status:** Candidates approved by owner (2026-11-06). On 2026-11-07 the owner directed that PhishTank stay **disabled**; URLhaus is also disabled. Production enablement pending  
**Decision:** PhishTank and URLhaus are the approved first candidates to evaluate. No provider is yet approved as a production dependency. Each stays disabled until its current terms, quotas, key availability and privacy handling are re-checked, and no provider accounts, keys, or real user indicators are used without further owner approval.  
**Reason:** API coverage, privacy impact, commercial-use rules, rate limits, cost, attribution, and retention must be evaluated. See PROVIDER_EVALUATION.md.

### D-016 — Scan-history retention

**Status:** Baseline approved by owner (2026-11-06); deletion and backup semantics pending  
**Decision:** History is off by default and opt-in, with a 30-day retention period and a user-accessible delete action. Live-database deletion, retention expiry, and backup purge must be specified separately before persistence work; no promise is made that deletion instantly erases backups unless the backup design guarantees it.  
**Reason:** History is not needed for a scan and can reveal user activity.

### D-017 — Final database schema

**Status:** Timing approved by owner (2026-11-07): final schema approval is deferred to the start of Phase 5  
**Decision:** Phases 1 to 4 need no persistence, so the final schema (field types, indexes, constraints, deletion behaviour) is approved at the start of Phase 5, before any database implementation. Conceptual entities remain in ARCHITECTURE.md as the starting point. Until then no database code may be written.

### D-018 — Consent interaction

**Status:** Approved by owner. Model (2026-11-06): per-scan, per-provider, no remembered consent in the MVP. Wording (2026-11-07): revision 3.1, recorded in docs/CONSENT_COPY.md  
**Decision:** The consent flow must show provider name and data category before a lookup. Consent is per scan and per provider, with no remembered consent in the MVP (approved). The approved wording is in docs/CONSENT_COPY.md. It must be rechecked once a hosting environment is chosen and before any provider is enabled.

### D-019 — Risk thresholds and freshness

**Status:** Pending test evidence  
**Decision:** High-risk thresholds and provider freshness requirements will be finalised against documented provider semantics and a labelled test dataset.

### D-020 — `/report` deferred to post-MVP

**Status:** Accepted (owner, 2026-11-06)  
**Decision:** FR-14 and the user-report use case are removed from the MVP and moved to the post-MVP backlog.  
**Reason:** THREAT_MODEL.md T-10 requires a moderation and deletion process before the feature is enabled, and none is defined. Removing it reduces storage, abuse, and personal-data risk.  
**Consequences:** REQUIREMENTS.md updated. T-10 stays in the threat model for when the feature returns.

## Change procedure

For a new decision:

1. Give it the next D-number.
2. State the status and date.
3. Record the decision.
4. Explain the reason and alternatives considered.
5. Record security, privacy, cost, and migration consequences.
6. Update related documents.
