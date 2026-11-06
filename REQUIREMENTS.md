# ScamShield — Product Requirements

**Document status:** Phase 0 specification  
**Version:** 1.0-draft  
**Last reviewed:** 2026-11-05  
**Product type:** Defensive cybersecurity tool  
**Primary interface:** Telegram bot

## 1. Purpose

ScamShield is a privacy-first Telegram bot that helps an individual investigate a suspicious URL or domain. It combines local, non-networked URL analysis with selected threat-intelligence lookups and returns an evidence-based explanation in plain language.

The product is an aid to decision-making. It is not a guarantee that a website is safe, and it is not a replacement for endpoint protection, browser protection, or professional incident response.

## 2. Locked product decisions

| Decision | Approved value |
|---|---|
| Project name | ScamShield |
| Primary ambition | Public software-engineering portfolio project |
| Privacy model | Privacy-first |
| Supported input | Both URLs and domain names |
| Initial interface | Telegram bot only |
| Primary language | Python |
| Initial persistence option | SQLite, subject to final schema review |
| Initial audience | Individual Telegram users |
| Initial deployment model | One Linux-hosted bot process using long polling |

The product must not expand into a web dashboard or group-moderation system during the MVP without a documented scope change.

## 3. Problem statement

People receive links through messaging apps, email, SMS, and social platforms. They may not be able to distinguish a legitimate destination from a phishing page, malware distribution URL, impersonation domain, or an unknown site.

ScamShield provides a simple workflow: submit one URL or domain, review the available evidence, and receive practical safety guidance.

## 4. Users and use cases

### Primary user

An individual Telegram user who wants to check a link or domain before interacting with it.

### MVP use cases

1. A user sends a complete HTTP or HTTPS URL and requests an assessment.
2. A user sends a bare domain name and requests an assessment.
3. A user views the findings, checks performed, data-sharing status, and limitations.
4. A user views saved scan history if history is enabled.
5. A user reads the privacy notice and requests deletion of saved history.

## 5. Scope

### 5.1 MVP — required

- Telegram onboarding and help.
- Accept one URL or one domain per scan.
- Validate and normalise supported inputs.
- Reject unsupported schemes and malformed input.
- Perform local URL/domain heuristic analysis without visiting the submitted destination.
- Support replaceable threat-intelligence provider adapters.
- Request explicit user consent before sending an indicator to an external provider.
- Preserve provider-specific result states, timestamps, and source attribution.
- Produce an explainable classification.
- Clearly distinguish no match from provider failure or incomplete coverage.
- Provide scan history only under an approved opt-in and retention design.
- Provide privacy information and a way to delete saved history.
- Apply user-level and global rate limits.
- Log operational events without raw submitted URLs, query strings, credentials, or API keys.
- Include automated tests and user-facing limitations.

### 5.2 Explicitly out of scope for MVP

- Telegram group monitoring or automatic moderation.
- Web dashboard or public web application.
- Automatic browsing, redirect following, crawling, or screenshotting of submitted URLs.
- File downloading, malware execution, or sandbox detonation.
- Port scanning, exploitation, credential collection, or offensive security features.
- AI-generated verdicts.
- A /report flow and any storage or moderation of user-submitted scam reports (deferred to post-MVP, see D-020).
- Automatic publication of user reports to third-party feeds.
- Claims that a website is safe or guaranteed legitimate.
- A numeric probability of maliciousness without a validated and calibrated model.

## 6. Input requirements

### FR-INPUT-01 — URL input

The bot must accept a single absolute URL using HTTP or HTTPS.

### FR-INPUT-02 — Domain input

The bot must accept a bare DNS domain name. Normalisation must not silently imply that every path or subdomain on the domain has been checked.

### FR-INPUT-03 — Input size

The initial implementation should enforce a documented maximum input length of 4,096 characters. The limit may be adjusted after test evidence.

### FR-INPUT-04 — Unsupported schemes

Reject schemes such as file, data, javascript, ftp, and other schemes that are not explicitly supported.

### FR-INPUT-05 — User information

Detect URLs containing embedded username or password fields. Do not send these credentials to a provider or persist them. The scan should be rejected or safely redacted according to a reviewed rule.

### FR-INPUT-06 — Internationalised domains

Handle internationalised domain names using a standards-compliant IDNA implementation. Display the ASCII/Punycode form and a safely rendered Unicode form where appropriate. Do not assume that Unicode display means a domain is trustworthy.

### FR-INPUT-07 — Multiple links

The MVP should ask the user to submit one indicator at a time. It must not guess which link in a long message the user intended to scan.

### FR-INPUT-08 — Shortened links

The MVP must not resolve or follow a shortener. It may identify a known shortening service and explain that the final destination was not inspected.

## 7. Functional requirements

| ID | Requirement |
|---|---|
| FR-01 | Provide /start onboarding and explain the bot's purpose. |
| FR-02 | Provide /help instructions and supported input rules. |
| FR-03 | Provide /scan or accept a single URL/domain sent directly. |
| FR-04 | Provide /about with project and limitation information. |
| FR-05 | Provide /privacy with data handling and provider-sharing information. |
| FR-06 | Validate and normalise submitted URL/domain input. |
| FR-07 | Run local heuristic analysis without visiting the destination. |
| FR-08 | Query only approved, configured provider endpoints and only after the required consent. |
| FR-09 | Preserve provider outcome states such as match, no match, unsupported, timeout, rate-limited, stale, and error. |
| FR-10 | Aggregate findings without treating a failed provider as a clean result. |
| FR-11 | Return a classification, evidence explanations, sources, timestamps, and coverage limitations. |
| FR-12 | Provide /history only if history storage is enabled by the user. |
| FR-13 | Provide a deletion command or equivalent flow for saved history. |
| FR-14 | *Deferred to post-MVP (D-020).* A /report flow requires a defined moderation and deletion process first. |
| FR-15 | Apply per-user and global request limits. |
| FR-16 | Handle malformed input, Telegram errors, provider outages, and database failures safely. |

## 8. Classification requirements

The MVP uses four user-facing outcomes:

| Outcome | Meaning |
|---|---|
| **HIGH RISK** | Strong, sufficiently fresh malicious evidence was returned by an approved source or by a reviewed combination of evidence. The report must identify the evidence and source. |
| **SUSPICIOUS** | Heuristics or weaker/unverified evidence indicate caution, but there is not enough evidence to make a stronger claim. |
| **NO KNOWN THREAT DETECTED** | The configured checks completed and returned no known match. This is not a safety guarantee. |
| **UNKNOWN / INCOMPLETE** | Evidence is unavailable, checks failed, the input is unsupported by providers, or coverage is too limited to provide a meaningful conclusion. |

The risk engine must not interpret provider timeout, quota exhaustion, unsupported input, or missing credentials as a no-match result.

A numeric score, if introduced later, must be documented as a rule score rather than a probability unless separately calibrated against a representative labelled dataset.

## 9. Report requirements

Every report must show:

- Submitted indicator type: URL or domain.
- A safely redacted display value.
- Overall classification.
- Individual findings and why they matter.
- Threat-intelligence providers actually queried.
- Provider result state and result freshness where available.
- Whether any external provider received the URL or domain.
- Checks that were skipped or failed.
- A concise recommended action.
- A warning that no detection is not proof of safety.

A domain-only assessment must disclose that path-specific threats may not have been checked.

## 10. Privacy requirements

- External sharing is disabled by default until a clear consent flow is implemented and accepted.
- Before consent, show which provider will receive which data category: full URL, hostname, or domain.
- Do not transmit URL credentials, fragments, or query parameters by default.
- If a provider requires the full URL, explain that requirement before transmission and let the user decline.
- Do not persist the complete submitted URL by default.
- Do not log raw URLs, query parameters, secrets, or API credentials.
- Scan history must be opt-in; retention period remains a Phase 0 decision.
- Provide a deletion path for saved history.
- Keep provider API keys in environment-based secret storage, never in source control.

## 11. Non-functional requirements

| Area | Requirement |
|---|---|
| Security | No unrestricted outbound requests to user-supplied destinations. |
| Privacy | Data minimisation, explicit provider-sharing consent, and limited retention. |
| Reliability | Provider outages must produce partial/incomplete results, not false clean results. |
| Maintainability | Modular monolith with clear component boundaries. |
| Testability | Unit tests for parsing, heuristics, aggregation, and privacy rules. |
| Performance | Asynchronous external I/O with bounded concurrency and timeouts where beneficial. |
| Usability | Plain-language explanations for non-expert users. |
| Portability | Deployable on a supported Linux environment. |
| Observability | Structured logs and operational metrics without sensitive indicator content. |
| Extensibility | Provider adapters can be added or removed without rewriting the bot or risk engine. |

## 12. Acceptance criteria for MVP

The MVP is acceptable only when:

1. A valid URL and a bare domain are both accepted.
2. Unsupported schemes and malformed inputs are rejected safely.
3. The submitted destination is never fetched by the application.
4. No external provider request occurs before the applicable consent.
5. Provider failures remain distinguishable from no-match results.
6. Every classification includes its supporting evidence and coverage.
7. Secrets and raw sensitive URL components are absent from logs and Git history.
8. Scan history follows the approved opt-in, retention, and deletion rules.
9. Automated tests cover benign, suspicious, invalid, provider failure, and conflicting-result cases.
10. Installation, configuration, limitations, and security boundaries are documented.

## 13. Open decisions before implementation

- Which one or two providers will be enabled in the MVP?
- What exact consent wording and data preview will be shown?
- Will history be disabled by default or offered as an opt-in setting?
- What retention period will apply to opted-in history?
- What final database schema and deletion behaviour will be used?
- What minimum provider evidence and freshness rules qualify for HIGH RISK?
- Which runtime and dependency versions will be pinned?

These decisions must be resolved before the affected components are implemented.
