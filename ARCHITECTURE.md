# ScamShield — System Architecture

**Document status:** Phase 0 architecture baseline  
**Version:** 1.0-draft  
**Last reviewed:** 2026-11-05

## 1. Architecture goals

ScamShield will begin as a **modular monolith**: one deployable Python application separated into components with explicit responsibilities.

This is preferable to microservices for the MVP. It keeps deployment and debugging manageable while preserving boundaries that make later growth possible.

The architecture must:

1. Keep Telegram interaction separate from security analysis.
2. Keep provider integrations replaceable.
3. Separate evidence collection from final classification.
4. Make privacy and external data sharing explicit.
5. Never browse arbitrary user-submitted destinations.
6. Make provider failures and incomplete coverage visible.
7. Support automated tests without requiring a running Telegram bot.

## 2. Logical request flow

Telegram user  
→ Telegram Bot API  
→ Bot handler  
→ Input validation and normalisation  
→ Local analysis  
→ Consent gate  
→ Approved threat-intelligence adapters  
→ Evidence aggregation  
→ Risk classification  
→ Report generation  
→ Telegram response

The database is accessed only through a persistence/repository layer. Operational logging is separate and must not include raw indicators.

## 3. Component responsibilities

### 3.1 Telegram interface

Responsibilities:

- Receive private messages and commands.
- Validate the message shape and user context.
- Ask for one URL or domain at a time.
- Display consent notices before external sharing.
- Return formatted findings.
- Expose onboarding, help, privacy, history, and deletion flows.

MVP operation is private-chat-only. Group support is deferred.

### 3.2 Input and normalisation layer

Responsibilities:

- Enforce input length and supported schemes.
- Parse URL components without making a network request.
- Reject unsupported schemes and malformed values.
- Detect embedded credentials.
- Convert internationalised hostnames using a standards-compliant IDNA implementation.
- Separate the hostname, registrable domain, path, query, and fragment.
- Produce a redacted display value and provider-specific indicator only after policy checks.

A public suffix list implementation should be used when registrable-domain boundaries are required. Do not build a naïve rule that assumes the last two hostname labels always form the registrable domain.

### 3.3 Local heuristic analyzer

Responsibilities:

- Examine URL and hostname structure.
- Identify IP-literal hosts, unusual hostname patterns, suspicious encodings, misleading subdomains, lookalike indicators, and other documented signals.
- Record each signal with a stable identifier, explanation, and evidence strength.
- Avoid treating weak features such as URL length or HTTPS presence as decisive evidence.

This component is deterministic and does not access the network.

### 3.4 Threat-intelligence adapters

Each provider adapter implements a common internal contract.

Conceptual input:

- Indicator type: URL or domain.
- Normalised indicator approved for disclosure.
- Provider-specific configuration.
- Request timeout and correlation identifier.

Conceptual output:

- Provider identifier.
- Outcome state: match, no match, unsupported, stale, timeout, rate-limited, or error.
- Threat category, if returned.
- Provider timestamp or expiry, if available.
- Minimal normalised evidence.
- Safe attribution text and source reference.

Adapters must not expose provider-specific response objects to the risk engine. Raw responses should remain transient and must not be logged.

Use a fixed allowlist of provider API hosts. Never accept a provider base URL from a Telegram user. Enforce HTTPS, bounded response sizes, finite timeouts, and controlled redirect behaviour for provider endpoints.

### 3.5 Consent and privacy gate

This component decides whether an external lookup is permitted.

Before a provider request, it must know:

- Which provider will receive the data.
- Whether the provider needs the full URL, hostname, or registrable domain.
- Whether path or query data is required.
- Whether the user has consented to that data category and provider.
- Whether provider terms permit the proposed use.

No adapter may be called directly by a Telegram handler while bypassing this gate.

Default behaviour is local-only analysis until the user explicitly consents to the relevant external lookup. Declining consent must not prevent the local analysis report from being returned.

### 3.6 Evidence aggregator

Responsibilities:

- Combine local findings and provider results.
- Preserve source identity and freshness.
- Detect disagreement and incomplete coverage.
- Deduplicate equivalent findings without erasing source provenance.
- Distinguish a no-match response from a failed or unsupported check.

Provider outage is not evidence of safety.

### 3.7 Risk engine

Responsibilities:

- Apply documented deterministic rules to the evidence.
- Produce HIGH RISK, SUSPICIOUS, NO KNOWN THREAT DETECTED, or UNKNOWN / INCOMPLETE.
- Include the reasons for the outcome.
- Avoid fabricated confidence percentages.
- Apply a conservative outcome when evidence is stale, conflicting, or insufficient.

Rules and thresholds must be versioned and tested.

### 3.8 Report generator

Responsibilities:

- Convert the structured result into a Telegram-readable report.
- Show what was checked and what was not checked.
- Show provider names and timestamps where allowed.
- Display privacy/data-sharing status.
- Include practical advice and the no-guarantee warning.

### 3.9 Persistence layer

Responsibilities:

- Store only approved user settings and minimal scan history.
- Enforce ownership checks for user history.
- Apply retention and deletion rules.
- Keep SQL and storage details out of bot handlers and scanner logic.

SQLite is the initial storage choice, subject to schema approval. PostgreSQL may be considered if deployment concurrency or scale later requires it.

### 3.10 Logging and monitoring

Log operational facts such as request ID, handler name, elapsed time, provider name, status category, and exception class.

Do not log:

- Full submitted URLs.
- URL query strings or fragments.
- Embedded URL credentials.
- Telegram message bodies.
- API keys, bot tokens, or consent tokens.
- Provider response bodies that may contain submitted indicators.

## 4. Data flow and network boundaries

### Allowed outbound network destinations

- Telegram Bot API endpoints.
- Explicitly approved threat-intelligence provider API endpoints.
- Operational monitoring endpoints, only if added and documented.

### Forbidden in the MVP

- Fetching a user-supplied URL.
- Following user-supplied redirects.
- Resolving a submitted domain merely to inspect its destination.
- Connecting to arbitrary hostnames or IP addresses supplied by users.
- Downloading files or rendering submitted pages.

The scanner must remain a parser and evidence client, not a browser.

## 5. Provider independence

The bot, scanner, evidence aggregator, and risk engine must depend on the internal provider interface rather than a specific provider SDK.

A provider can be disabled because of an outage, changed terms, quota exhaustion, or cost without changing the other components.

A provider may return unsupported for a domain-only request if it requires a complete URL. The system must not fabricate a URL-level match from a domain-only lookup.

## 6. Conceptual data model

The final schema is not approved yet. The following entities are proposed:

### User settings

- Internal user record identifier.
- Telegram user identifier.
- External lookup consent setting(s).
- Scan-history setting.
- Creation and update timestamps.

### Scan

- Scan identifier.
- Owning user identifier.
- Indicator type: URL or domain.
- Minimised display indicator.
- Classification.
- Rule-set version.
- Created timestamp.
- Deletion/retention metadata.

### Finding

- Finding identifier.
- Scan identifier.
- Source type: local heuristic or provider.
- Source identifier.
- Finding category.
- Evidence strength.
- Outcome state.
- Safe description.
- Observed/checked/expiry timestamps when available.

Do not store a full raw URL, query string, fragment, or embedded credentials by default. Storing even a hostname can reveal user activity; history must therefore be opt-in and subject to a retention decision.

## 7. Proposed repository layout

The initial application layout, to be created during implementation, is:

    app/
      main.py
      config.py
      bot/
        commands.py
        handlers.py
        keyboards.py
      scanner/
        validator.py
        normalizer.py
        analyzer.py
        risk_engine.py
      intelligence/
        base.py
        providers/
      privacy/
        consent.py
        redaction.py
      database/
        connection.py
        models.py
        repository.py
      reports/
        generator.py
    tests/
    docs/

This is a target layout, not a statement that application code already exists. The top-level project documentation remains in the repository root.

## 8. Runtime and deployment

Initial deployment proposal:

- One Python process.
- Telegram long polling.
- SQLite on persistent local storage.
- Environment-based secrets.
- A managed process restart policy.
- Structured, redacted logs.
- A documented backup and restore procedure.

Long polling is selected for operational simplicity. Webhooks and PostgreSQL can be evaluated when scale or hosting requirements justify them.

## 9. Architecture quality attributes

| Attribute | Architectural response |
|---|---|
| Privacy | Consent gate, data minimisation, local analysis first |
| Security | No arbitrary URL fetching; provider host allowlist |
| Reliability | Explicit provider states and partial-result reporting |
| Maintainability | Modular monolith and provider interface |
| Testability | Pure functions for parsing, heuristics, and aggregation |
| Extensibility | Provider adapters and versioned risk rules |
| Portability | Python application with Linux deployment target |

## 10. Architecture decisions still open

- Exact Python and dependency versions.
- Final provider list and permitted use cases.
- Exact consent and data preview interaction.
- Final database schema.
- History opt-in and retention period.
- Whether a local threat-feed cache is practical for the MVP.
- Hosting and backup provider.

Changes to these decisions should be recorded in DECISIONS.md before implementation.
