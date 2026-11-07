# ScamShield — Privacy and Data Handling

**Document status:** Engineering privacy specification; not a final legal privacy notice  
**Version:** 1.0-draft  
**Last reviewed:** 2026-11-05

## 1. Privacy commitment

ScamShield is designed to minimise the information it collects and shares.

A submitted URL can contain more than a website address. Its path or query may include password-reset tokens, invitation codes, session identifiers, email addresses, customer references, or other private data.

For that reason, ScamShield must not automatically forward every submitted URL to external services.

## 2. Data-flow principles

1. Parse and analyse submitted input locally first.
2. Do not visit, resolve, or follow the submitted destination in the MVP.
3. Do not send an indicator to an external provider until the user has seen the disclosure and consented.
4. Tell the user which provider will receive the data and whether it needs a URL, hostname, or domain.
5. Do not transmit URL username/password fields, fragments, or query parameters by default.
6. Do not persist the complete raw URL by default.
7. Do not place raw input or secrets in application logs.
8. Make scan history optional and deletable.

Declining external lookup must still produce a local-analysis report.

## 3. Data inventory

| Data category | Proposed handling |
|---|---|
| Telegram user identifier | Processed to reply to the user; stored only when needed for opted-in settings or history |
| Message body | Processed for the submitted indicator; not retained as a conversation transcript |
| Raw submitted URL | Kept in memory only for the request where practical; not stored by default |
| URL query and fragment | Treated as sensitive; not sent to providers by default and not logged |
| URL userinfo | Never sent to providers; reject or safely redact before processing |
| Hostname/domain | Used for local analysis; may be sent to a provider only after consent |
| Local heuristic findings | Returned to the user; saved only if history is enabled |
| Provider result | Normalised to the minimum fields needed for the report; saved only if history is enabled |
| Consent preference | Not stored in the MVP: consent applies to one provider and one scan (D-018) |
| Operational logs | Request IDs, timing, status categories, and error classes; no raw indicator |
| API credentials | Stored in deployment secret storage or environment variables; never in the database or repository |

A hostname can itself reveal sensitive information, for example an internal company subdomain. Treat it as user data.

## 4. External provider disclosure

Threat-intelligence providers receive the data necessary to perform a lookup. Their retention, use, and sharing practices are governed by their own terms and privacy policies.

Before external lookup, ScamShield must display a clear notice that states:

- Provider name.
- Data to be sent: complete URL, hostname, or registrable domain.
- Whether path information is included.
- Whether query parameters are excluded or required.
- A link to the provider's privacy/terms information.
- That the user may decline and receive local-only analysis.

If a provider requires a complete URL, the consent flow must make that explicit. If query parameters may contain a secret, the user should be advised not to submit the link or to decline that provider check.

Provider consent must not be hidden inside a general acceptance of the bot's terms.

## 5. Default behaviour

The default is **local-only analysis**.

No external provider request should occur until the user explicitly consents to the relevant data disclosure. No consent preference is remembered in the MVP: consent applies to one provider and one scan (D-018). A saved, revocable preference would need a future scope decision. The approved consent wording is revision 3.1 in `docs/CONSENT_COPY.md`; it must be rechecked (provider data handling, outbound IP wording) before any provider is enabled.

## 6. Scan history and retention

Scan history is not required to perform a scan. It is a convenience feature and should be opt-in.

Owner-approved baseline (D-016), with deletion, expiry and backup semantics still to be written:

- History off by default.
- If a user enables history, store only the minimum indicator and findings needed for the feature.
- Retention period: 30 days (approved baseline).
- Provide a deletion command or equivalent flow.
- Do not store the raw full URL or query string by default.

History off by default, opt-in and 30-day retention are owner-approved baselines (D-016). The 30-day period is not yet a final user-facing commitment until deletion and backup semantics are written. The exact fields and deletion semantics must be approved before database implementation and public launch.

## 7. Logging

Logs must not include:

- Complete URLs.
- Query parameters or fragments.
- Embedded username/password values.
- Telegram message text.
- API keys, bot tokens, or authorization headers.
- Full provider response bodies.
- Unredacted exception text if it may contain an indicator.

Logs may include a random request ID, event type, provider name, status code/category, duration, and exception class.

## 8. User controls

The planned interface should provide:

- /privacy — explain local and external processing.
- A way to decline external checks.
- A way to view current privacy settings.
- A way to disable scan history.
- A way to delete saved history.
- A way to submit a privacy-related request through a documented contact channel.

The precise commands and storage model must be confirmed before implementation.

## 9. Telegram and hosting providers

ScamShield runs through Telegram. Telegram processes messages and bot interactions under its own platform terms and privacy policy. The hosting provider may process operational data such as server logs and network metadata.

The final public privacy notice must identify the actual hosting provider and configured threat-intelligence providers. Do not publish this draft as if all third-party processors are already selected.

## 10. Security safeguards

- Keep credentials outside source control.
- Use HTTPS for external API requests.
- Apply least-privilege access to the application host and database.
- Limit data retention.
- Restrict database and backup file access.
- Use deletion and backup-expiry procedures.
- Review provider terms and privacy notices before enabling an integration.

## 11. Important limitations

A privacy-first design reduces unnecessary disclosure but does not make a Telegram bot anonymous. Telegram, the hosting provider, and any threat-intelligence provider used with consent may process data under their own policies.

This engineering document is not legal advice. Before public release, the operator must review applicable privacy and data-protection obligations and publish an accurate notice for the actual deployment.

## 12. Official platform and provider policy references

- Telegram Privacy Policy: https://telegram.org/privacy
- Telegram Bot API: https://core.telegram.org/bots/api
- VirusTotal API Overview: https://docs.virustotal.com/docs/api-overview
- PhishTank API Information: https://phishtank.org/api_info.php
- PhishTank Privacy Policy: https://phishtank.org/privacy.php
- URLhaus API: https://urlhaus.abuse.ch/api/
- Google Web Risk Overview: https://docs.cloud.google.com/web-risk/docs/overview

These links are starting points for review, not blanket approval to transmit user data. Re-check the applicable terms before enabling any provider.
