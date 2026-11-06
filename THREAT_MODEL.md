# ScamShield — Threat Model

**Document status:** Phase 0 baseline  
**Version:** 1.0-draft  
**Last reviewed:** 2026-11-05  
**Method:** Asset, trust-boundary, and STRIDE-style review

## 1. Purpose

This document identifies the main threats to ScamShield, its users, and its infrastructure. It defines MVP security controls and residual risks.

The model must be reviewed when the architecture, providers, data retention, or deployment environment changes.

## 2. Security objectives

1. Do not expose the bot host or internal network to user-controlled URL requests.
2. Protect Telegram bot tokens and provider API credentials.
3. Do not disclose submitted indicators to third parties without clear user consent.
4. Prevent one user from reading or deleting another user's records.
5. Preserve the distinction between malicious evidence, no-match results, and unavailable checks.
6. Resist message flooding, parser abuse, and provider quota exhaustion.
7. Avoid misleading users with unsupported safety claims.

## 3. Assets

| Asset | Why it matters |
|---|---|
| Telegram bot token | Allows control of the bot |
| Provider API keys | Allow use of paid or quota-limited services |
| Submitted URLs/domains | May contain private account, reset, invitation, or tracking tokens |
| User identifiers and settings | Can identify users and their preferences |
| Scan history and findings | May reveal browsing or security concerns |
| Database | Holds user settings and any opted-in history |
| Risk rules | Determine user-facing security outcomes |
| Logs and backups | May unintentionally retain sensitive information |
| Provider reputation/usage quota | Needed for reliable operation |

## 4. Trust boundaries

1. Telegram user to Telegram platform.
2. Telegram platform to ScamShield application.
3. Application to external threat-intelligence providers.
4. Application process to local database and logs.
5. Deployment host to secrets and backup storage.

Data crossing a boundary must be validated, minimised, and handled under the relevant consent and access rules.

## 5. Threats and mitigations

### T-01 — Server-Side Request Forgery (SSRF)

**Scenario:** A user submits a URL targeting localhost, a private network, cloud metadata, or an internal administrative service. The application fetches it and exposes internal resources.

**Controls:**
- Do not fetch submitted URLs in the MVP.
- Do not follow redirects from submitted destinations.
- Do not perform arbitrary DNS resolution or socket connections based on user input.
- Provider requests must use fixed, allowlisted API hosts.
- Keep provider endpoint configuration out of user input.
- Add regression tests proving that parsing and scanning do not initiate requests to the submitted host.

**Residual risk:** A future redirect-expansion or live-inspection feature would materially change this threat model and must not be added without isolation and a separate security review.

### T-02 — Credential or secret leakage

**Scenario:** A bot token, provider key, database secret, or URL token is committed, logged, or exposed in a report.

**Controls:**
- Load secrets from environment-based secret storage.
- Keep local environment files out of Git.
- Provide a placeholder-only environment example when needed.
- Redact URL userinfo, query strings, and fragments.
- Never log API authorization headers or full provider request URLs.
- Rotate any secret suspected of exposure.

### T-03 — Third-party disclosure without consent

**Scenario:** A private reset link, invitation URL, or internal domain is automatically submitted to a reputation provider.

**Controls:**
- Local-only analysis is the default.
- Require an explicit consent step before external queries.
- Show the provider and data category that will be disclosed.
- Do not send query strings or credentials by default.
- Let the user decline external lookups.
- Document each provider's handling and terms.
- Do not assume a domain-only lookup is equivalent to checking a full URL.

### T-04 — Malformed input and parser denial of service

**Scenario:** Extremely long, deeply encoded, malformed, or ambiguous input consumes excessive CPU or memory or exploits parsing edge cases.

**Controls:**
- Enforce a maximum input length.
- Accept one indicator at a time.
- Use standards-compliant parsing and IDNA libraries.
- Reject unsupported schemes and malformed values.
- Bound parsing work and response sizes.
- Test Unicode, percent-encoding, IPv4/IPv6 literals, and unusual delimiters.

### T-05 — Message flooding and quota exhaustion

**Scenario:** A user or attacker sends repeated requests to exhaust provider quotas or overload the bot.

**Controls:**
- Per-user and global rate limits.
- Bounded concurrent provider calls.
- Provider-specific quota tracking.
- Short, finite timeouts and backoff.
- Cache eligible results using provider freshness/expiry rules.
- Do not retry non-idempotent requests blindly.

### T-06 — Cross-user access to history

**Scenario:** A user guesses or manipulates a scan identifier to retrieve another user's data.

**Controls:**
- Bind every saved scan to an internal user record.
- Enforce ownership in the repository/query layer.
- Never trust user-supplied scan identifiers alone.
- Test cross-user read and delete attempts.
- Use parameterised queries and database constraints.

### T-07 — False or misleading classification

**Scenario:** A provider outage is interpreted as no threat, stale intelligence is treated as current, or weak heuristics trigger an unjustified high-risk label.

**Controls:**
- Use explicit provider outcome states.
- Require evidence and freshness rules for HIGH RISK.
- Preserve provenance and provider disagreement.
- Report incomplete coverage.
- Keep weak indicators from becoming decisive alone.
- Do not publish confidence percentages without calibration.
- Evaluate false positives and false negatives against a labelled dataset.

### T-08 — Provider API compromise, policy change, or outage

**Scenario:** A provider becomes unavailable, changes API behaviour, changes price, or changes usage terms.

**Controls:**
- Provider adapters are replaceable.
- Validate and parse provider responses defensively.
- Keep a provider disabled when credentials or terms are invalid.
- Re-check documentation and terms before release.
- Do not treat provider outage as a clean result.
- Keep provider use and costs observable without logging indicators.

### T-09 — Database or backup disclosure

**Scenario:** A local database or backup is copied or exposed and reveals user scan history.

**Controls:**
- Minimise stored data.
- Make history opt-in.
- Restrict file permissions on the deployment host.
- Store backups securely and define deletion/expiry.
- Do not include database files in Git.
- Review encryption-at-rest needs for the selected host.

### T-10 — Malicious or misleading report submissions

**Status:** The report workflow is deferred to post-MVP (D-020); this threat applies when it returns.

**Scenario:** Users submit fabricated reports, spam, personal data, or malicious URLs in the report workflow.

**Controls:**
- Do not automatically publish reports to a provider.
- Rate-limit and validate submissions.
- Store minimal information.
- Do not treat an unverified user report as confirmed threat intelligence.
- Define a moderation and deletion process before enabling the feature.

## 6. Abuse cases to test

- URL contains username and password fields.
- URL query contains a fake password-reset token.
- Domain is an IP literal for loopback, private, link-local, or reserved ranges.
- Hostname uses Unicode confusables or Punycode.
- Input uses unsupported schemes such as file or javascript.
- URL contains multiple ambiguous links.
- URL is a known shortener.
- Provider returns timeout, 429/rate limit, malformed JSON, stale result, or conflicting result.
- User attempts to access another user's scan history.
- User floods scan requests.
- API key is absent or invalid.
- Database is unavailable or read-only.

These tests should use safe fixtures. Do not open or execute live malicious URLs as part of ordinary unit testing.

## 7. Security classification and residual risk

The MVP is a defensive indicator-checking tool. It does not verify the actual content or behaviour of a live website.

Residual risks include:

- Newly created or unreported malicious sites.
- Compromised legitimate websites.
- Provider false negatives and false positives.
- Threats hidden in redirects that are not followed.
- URL-specific threats not visible from a domain-only check.
- Incomplete provider coverage.
- User misunderstanding of a no-known-threat result.

The report must communicate these limitations.

## 8. Release security checklist

Before public release:

- [ ] No arbitrary user URL fetching exists.
- [ ] Provider destinations are fixed and allowlisted.
- [ ] External disclosure requires informed consent.
- [ ] Bot token and provider keys are not present in repository history.
- [ ] Raw URLs and secrets are not logged.
- [ ] Rate limits and timeouts are active.
- [ ] Database ownership checks are tested.
- [ ] Provider failure and stale-result cases are tested.
- [ ] Dependency vulnerabilities are reviewed.
- [ ] Backup and retention procedures are documented.
- [ ] A security contact/reporting channel is documented.
