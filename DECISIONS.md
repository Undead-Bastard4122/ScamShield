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

**Status:** Pending evaluation  
**Decision:** No provider is yet approved as a default production dependency.  
**Reason:** API coverage, privacy impact, commercial-use rules, rate limits, cost, attribution, and retention must be evaluated. See PROVIDER_EVALUATION.md.

### D-016 — Scan-history retention

**Status:** Pending user/product approval  
**Decision:** History should be optional. A 30-day retention period is a planning proposal, not a final commitment.  
**Reason:** History is not needed for a scan and can reveal user activity.

### D-017 — Final database schema

**Status:** Pending  
**Decision:** Conceptual entities are documented in ARCHITECTURE.md. Field types, indexes, and deletion behaviour are not approved yet.

### D-018 — Consent interaction

**Status:** Pending  
**Decision:** The consent flow must show provider name and data category before a lookup. Exact wording, whether consent is per-scan or saved as a revocable setting, and handling of sensitive query parameters remain to be approved.

### D-019 — Risk thresholds and freshness

**Status:** Pending test evidence  
**Decision:** High-risk thresholds and provider freshness requirements will be finalised against documented provider semantics and a labelled test dataset.

## Change procedure

For a new decision:

1. Give it the next D-number.
2. State the status and date.
3. Record the decision.
4. Explain the reason and alternatives considered.
5. Record security, privacy, cost, and migration consequences.
6. Update related documents.
