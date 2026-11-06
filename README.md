# ScamShield

**Detect the danger before you click.**

ScamShield is a planned, privacy-first Telegram cybersecurity bot for investigating suspicious URLs and domain names. It is designed to combine local indicator analysis with carefully selected threat-intelligence sources and return an evidence-based report that explains what was checked, what was found, and what remains unknown.

> **Project status: early development.** Phase 0 (planning) is largely complete and Phase 1 (the offline URL/domain input engine) is in progress. ScamShield is not yet a working bot and must not be relied on to assess real links.

## Product principles

- **Privacy first:** analyse locally before any external lookup. A provider must not receive a submitted URL or domain until the user has seen the disclosure and consented.
- **No arbitrary browsing:** the MVP will not open submitted links, follow redirects, resolve user-supplied destinations, or download files.
- **Evidence, not guesses:** results must show supporting findings and provider coverage. A failed provider is not a clean result.
- **Honest classifications:** no known threat detected does not mean a website is guaranteed safe.
- **Modular engineering:** Telegram interaction, parsing, analysis, provider adapters, risk rules, reports, and persistence have separate responsibilities.

## Planned MVP

- Telegram private-chat interface.
- Accept one complete HTTP/HTTPS URL or one bare domain per scan.
- Validate and normalise the submitted indicator.
- Perform local heuristic analysis without visiting the destination.
- Query approved threat-intelligence providers only after informed consent.
- Return an explainable classification: **HIGH RISK**, **SUSPICIOUS**, **NO KNOWN THREAT DETECTED**, or **UNKNOWN / INCOMPLETE**.
- Optional, privacy-conscious scan history after its retention and deletion rules are approved.

Telegram group monitoring, a web dashboard, file analysis, live page inspection, and AI-generated verdicts are outside the initial MVP.

## Documentation

| Document | Purpose |
|---|---|
| [REQUIREMENTS.md](REQUIREMENTS.md) | Product scope, functional requirements, and acceptance criteria |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Components, data flow, trust boundaries, and proposed repository layout |
| [THREAT_MODEL.md](THREAT_MODEL.md) | Threats, mitigations, abuse cases, and release security checklist |
| [PRIVACY.md](PRIVACY.md) | Data minimisation, external disclosure, retention, and user controls |
| [PROVIDER_EVALUATION.md](PROVIDER_EVALUATION.md) | Official-source review of threat-intelligence candidates |
| [DECISIONS.md](DECISIONS.md) | Locked product choices and pending architecture decisions |
| [ROADMAP.md](ROADMAP.md) | Milestone-based development plan |
| [PHASE_0_CHECKLIST.md](PHASE_0_CHECKLIST.md) | Planning tasks and Phase 0 exit criteria |

## Proposed technology

- **Language:** Python
- **Telegram integration:** Telegram Bot API, with a Python bot library selected during Phase 1
- **Persistence:** SQLite for the initial low-volume deployment, subject to final schema approval
- **Deployment:** Linux host, initially using Telegram long polling
- **Testing:** automated unit and integration tests

Dependencies and exact runtime versions will be selected and pinned when implementation begins.

## Development status

| Milestone | Status |
|---|---|
| Product direction and core decisions | Locked |
| Initial requirements | Documented |
| Architecture baseline | Documented |
| Threat model | Drafted |
| Privacy specification | Drafted |
| Provider evaluation | Candidate review completed; provider selection pending |
| Database schema and retention | Pending approval |
| Phase 0 sign-off | Pending |
| Phase 1: input engine and configuration | In progress (awaiting review) |
| Telegram bot, providers, persistence | Not started |

## Development

Supported: Python 3.12 or newer. Development and tests use the exact version in `.python-version` (3.13.18). The input engine makes no network requests.

```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.lock
pip install -e . --no-deps
ruff check . && ruff format --check .
pytest
```

`requirements.lock` and `requirements-dev.lock` pin exact versions but do not yet include hashes, because they were generated without network access. Add hashes (see the comment at the top of each file) before any release.

## Safety notice

ScamShield is intended as a defensive information tool. Threat-intelligence databases are incomplete and can be delayed or incorrect. A clean result cannot prove that a URL or domain is safe. Users should not enter passwords, one-time codes, payment details, or other sensitive information into a site solely because a scanner found no known threat.

## Contributing and project workflow

The project is being developed in documented phases. Before code is added, Phase 0 decisions must be approved. Meaningful architecture changes are recorded in [DECISIONS.md](DECISIONS.md). Do not commit bot tokens, provider keys, private URLs, or personal data.

## License

The repository currently includes an MIT License. That license applies to this project's code and documentation; it does not override third-party API terms, provider data licences, or trademark rights.
