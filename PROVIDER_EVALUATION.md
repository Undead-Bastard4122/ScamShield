# ScamShield — Threat-Intelligence Provider Evaluation

**Review date:** 2026-11-05  
**Status:** Candidate assessment; no production provider selected  
**Purpose:** Inform an MVP provider decision without coupling the product to one vendor.

> Provider APIs, quotas, pricing, and terms change. Re-check the linked official documentation immediately before implementation and before public deployment. This document is a technical comparison, not legal advice.

## 1. Evaluation criteria

Every provider must be evaluated against:

1. Threat coverage: phishing, malware distribution, deceptive sites, or domain reputation.
2. Input support: complete URL, hostname, or registrable domain.
3. Privacy: whether the queried indicator is sent in clear text, hashed, logged, retained, or shared.
4. API access: account, API key, authentication, and onboarding.
5. Rate limits and reliability.
6. Cost and free-tier constraints.
7. Commercial-use and redistribution terms.
8. Attribution requirements.
9. Freshness and expiry semantics.
10. Whether the provider's result can be shown in a public portfolio project.

## 2. Candidate comparison

| Provider | Main coverage | Access and limitations | Privacy considerations | Initial assessment |
|---|---|---|---|---|
| PhishTank | Community-reported phishing URLs | API supports URL checking; an application key improves limits; rate limits apply. Its FAQ says commercial and non-commercial API use is permitted. | Lookup request includes the URL. PhishTank's privacy notice says API user details, action, parameters, and request IP are recorded. | Strong candidate for phishing-specific coverage, subject to consent and rate-limit testing. |
| URLhaus | URLs used for malware distribution | Community API requires an Auth-Key and is subject to fair use. Commercial/for-profit use may require the enhanced commercial API. It is not a phishing database. | Submitted or queried indicators leave ScamShield; account/authentication and applicable provider terms must be reviewed. | Useful as a malware-distribution source, not a phishing verdict source. |
| Google Web Risk | Phishing/social engineering, malware, and other unsafe web resources | Enterprise-oriented product. Lookup and Update APIs have different complexity and cost models. Pricing and quotas must be checked for the planned usage. | Lookup sends the actual URL. Update maintains local hashed threat lists and generally contacts Google only to confirm possible matches, which is more privacy-preserving but more complex. Google says Web Risk information must not be redistributed. | Strong technical candidate for privacy-aware URL checks, but cost, terms, and redistribution rules need review. |
| Google Safe Browsing API v4 | Unsafe URL lists | Google documents the legacy v4 API as deprecated and limits Safe Browsing API use to non-commercial purposes; commercial users should evaluate Web Risk instead. | Lookup sends actual URLs; the older Update approach is more privacy-preserving but should not be selected without checking the migration path. | Do not select legacy v4 for a new production integration. |
| VirusTotal | Aggregated URL/domain intelligence from many security vendors | Community public API has restrictive request quotas and must not be used in commercial products or services. Paid/private access has separate terms and pricing. | Submitted URLs/domains and related data may be shared with examining partners and used to improve services. | Valuable for research and optional, consented evaluation, but not a default production dependency under the public API. |

## 3. Provider-specific findings

### 3.1 PhishTank

Official references:

- API information: https://phishtank.org/api_info.php
- FAQ: https://phishtank.org/faq.php
- Privacy policy: https://phishtank.org/privacy.php

The documented check endpoint accepts a URL in a POST request. The service supports XML, PHP, and JSON response formats. Its API documentation describes rate limits and an optional application key for higher limits. The FAQ states that API use is permitted for both commercial and non-commercial purposes.

Privacy implication: a URL lookup discloses the URL to PhishTank. Its privacy policy describes collection of API-user details, action, parameters, and request IP. It must therefore sit behind the ScamShield consent gate.

Coverage limitation: a PhishTank no-match is not evidence that a URL is safe. It means that the service did not return a known phishing entry for the submitted indicator.

### 3.2 URLhaus

Official references:

- API documentation: https://urlhaus.abuse.ch/api/
- About: https://urlhaus.abuse.ch/about/
- FAQ: https://urlhaus.abuse.ch/faq/

URLhaus focuses on URLs used to distribute malware. Its submission policy explicitly distinguishes phishing from malware and directs phishing reports to other services. Its community API requires an Auth-Key and is governed by fair-use principles. The documentation says commercial or for-profit use may require the enhanced commercial API.

Coverage limitation: do not use a URLhaus no-match to imply that a site is not phishing. It is a malware-URL signal, not a universal malicious-site verdict.

### 3.3 Google Web Risk

Official references:

- Overview: https://docs.cloud.google.com/web-risk/docs/overview
- Lookup API: https://docs.cloud.google.com/web-risk/docs/lookup-api
- Update API: https://docs.cloud.google.com/web-risk/docs/update-api
- Pricing: https://cloud.google.com/web-risk/pricing
- Quotas: https://docs.cloud.google.com/web-risk/quotas

The Lookup API sends the actual URL to Google's service. The Update API is more involved: the client maintains local hashed threat data and sends a hash prefix for server confirmation when a possible match occurs. This is a better privacy fit in principle, but it adds canonicalisation, local feed-update, and cache-management complexity.

Google's documentation says Web Risk information must not be redistributed. The exact permitted presentation and retention of findings must be reviewed before using the service in a public product.

Commercial and pricing implications must be checked against the current pricing and service terms. Do not assume that a free usage allowance means every integration or downstream use is free.

### 3.4 Google Safe Browsing API v4

Official references:

- API overview: https://developers.google.com/safe-browsing/v4
- REST reference: https://developers.google.com/safe-browsing/reference/rest

Google marks the v4 API as deprecated and states that Safe Browsing APIs are for non-commercial use. Google directs commercial users to Web Risk. Do not base a new production integration on a deprecated API without a documented migration justification.

### 3.5 VirusTotal

Official references:

- API overview: https://docs.virustotal.com/docs/api-overview
- Getting started: https://docs.virustotal.com/reference/getting-started
- Public vs. premium API: https://docs.virustotal.com/reference/public-vs-premium-api
- How it works: https://docs.virustotal.com/docs/how-it-works

VirusTotal aggregates analysis from many security vendors and can provide useful investigative context. However, its public API documentation states that the public API must not be used in commercial products or services and documents restrictive request quotas. VirusTotal also explains that submitted URLs and other indicators may be shared with examining partners.

Decision: do not make the public VirusTotal API a default dependency. Any later use requires an appropriate licence, explicit privacy disclosure, and review of data-sharing implications.

## 4. Proposed selection strategy

Do not enable every provider at once.

Recommended evaluation order:

1. Build the provider abstraction and mocked contract tests without selecting a live provider.
2. Evaluate PhishTank for phishing-specific URL lookup, including request privacy and rate limits.
3. Evaluate URLhaus separately for malware-distribution indicators and confirm the applicable community/commercial terms.
4. Evaluate Google Web Risk Update API as a privacy-aware but more complex option; review redistribution conditions and actual cost.
5. Keep VirusTotal as an optional research candidate only unless a suitable paid licence and data-sharing model are approved.

The first MVP should use the smallest provider set that gives meaningful coverage and can be operated lawfully and transparently.

## 5. Consent and disclosure requirements

Before the first external lookup, ScamShield must show:

- The provider name.
- The exact data category to be transmitted.
- Whether the complete URL or only a hostname/domain is sent.
- Whether path or query information is required.
- Relevant provider privacy/terms links.
- A clear decline option.

A provider adapter must not be able to bypass the consent gate.

If a provider requires the complete URL, a domain-only query cannot be represented as equivalent coverage. The report must say what was and was not checked.

## 6. Operational requirements for any selected provider

- Keep API keys outside source control.
- Use HTTPS and fixed provider endpoints.
- Configure request timeouts and bounded concurrency.
- Track quota and rate-limit responses.
- Cache only within provider terms and freshness rules.
- Record provider status and timestamps.
- Treat timeout, error, unsupported, and rate-limited as incomplete checks.
- Review response schema changes.
- Re-check terms, quotas, cost, attribution, and privacy before releases.

## 7. Decision

**No provider is approved for default MVP production use yet.**

PhishTank and URLhaus are the first candidates to test for separate coverage areas. Google Web Risk is the main candidate for a broader URL-checking capability with a more privacy-preserving Update API option. VirusTotal public API and legacy Google Safe Browsing v4 are not suitable as default production dependencies under their documented restrictions.

The final selection requires an explicit decision in DECISIONS.md after the consent flow, data-sharing policy, and expected project usage are agreed.
