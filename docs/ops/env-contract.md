# Contracts Env Contract

This repo treats `.env.web` as the sync surface for GitHub variables and secrets.

Flow:

1. Review `docs/ops/env-contract.csv`.
2. Run `powershell -ExecutionPolicy Bypass -File scripts/setup-env.ps1 -DispatchAppPrivateKeyPath C:\path\to\dispatch-app.pem`.
3. Inspect the preview or generated `.env.web`.
4. Run `powershell -ExecutionPolicy Bypass -File scripts/sync-all-to-github.ps1`.

Rules:

- `scripts/setup-env.ps1` only walks keys documented in `env-contract.csv`.
- Repo slugs for control-plane, jobs, and ui are derived from git where possible.
- The Python publish URL falls back to the checked-in template default.
- TypeScript publish auth is handled by npm trusted publishing from GitHub Actions and is not stored in `.env.web`.
- Existing `.env.web` files must not retain retired `NPM_TOKEN` or `NPM_REGISTRY_URL` keys.
- `DISPATCH_APP_PRIVATE_KEY` is read from a PEM file path and written into `.env.web` with literal `\n` escapes.
- This repo never provisions Azure runtime infrastructure.
