# Asset Allocation Contracts

Shared cross-repo contracts for the runtime-split Asset Allocation system.

This repository owns:
- Python contract models under `python/asset_allocation_contracts`
- TypeScript contract types under `ts/src`
- JSON schema artifacts under `schemas`
- Cross-repo smoke gate under `scripts/compatibility_gate.ps1`

Documentation:

- `docs/architecture/configuration-examples.md` contains valid examples for the shared configuration contract surfaces.
- `docs/ops/env-contract.md` and `docs/ops/env-contract.csv` document the repo bootstrap env contract used for release and retained legacy dispatch automation.

Downstream repos consume published package versions. Normal CI and release flows should not install contracts from a sibling checkout, and the retained release manifest carries the exact published version for downstream automation.

It does not own runtime IO, storage, Postgres, Delta, monitoring, or orchestration helpers.

## Operations

Canonical workflows live under `azure-pipelines/`.

- `azure-pipelines/ci.yml` is the required validation path for PRs and `main`; it runs on the self-hosted `local-docker-agents` pool with the baked contracts toolchain.
- `azure-pipelines/security.yml` runs dependency and supply-chain checks on the same local pool.
- `azure-pipelines/release.yml` is a gated manual pipeline that publishes the committed stable semver from `python/pyproject.toml` and `ts/package.json` to Azure Artifacts and emits `release-manifest.json`.
- `azure-pipelines/` is retained as a legacy surface from the previous operating model; do not treat it as the canonical CI/CD path.
- `scripts/setup-env.ps1` builds repo-local `.env.web` for registry and retained legacy dispatch configuration, including loading `DISPATCH_APP_PRIVATE_KEY` from a PEM file.
- `scripts/sync-all-to-azure-devops.ps1` syncs the `.env.web` surface into repo vars and secrets.
- Deployment guidance and required registry credentials live in `DEPLOYMENT_SETUP.md`.

## Versioning

- Public contracts releases use stable semver only: `MAJOR.MINOR.PATCH`.
- `python/pyproject.toml` and `ts/package.json` are the release version source of truth and must stay identical.
- Legacy `0.1.x` and `YYYY.M.D-dev.*` artifacts remain in registries for history only and are unsupported for new consumer pins.
