# Contributing to ScamShield

## Workflow

- Work on a branch named `agent/<short-task>` (or `feature/<short-task>`), never directly on `main`.
- Open a pull request. Keep it small and describe what changed and what is still unverified.
- A pull request is merged only after review and the project owner's approval.
- Run the checks before pushing: `ruff check .`, `ruff format --check .`, `pytest` (see README, Development).

## Rules that do not bend

- Never commit bot tokens, provider API keys, private URLs, real user data, or real suspicious links from users.
- The application must never fetch a submitted URL (D-009).
- No provider request may be made without the consent flow in `docs/CONSENT_COPY.md`.
- Tests use synthetic data only.
- Changes to locked decisions go through `DECISIONS.md`, not through a pull request alone.
- Be explicit about uncertainty. Do not describe something as verified unless it was.
