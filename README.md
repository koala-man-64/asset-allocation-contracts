# Asset Allocation Contracts

Shared cross-repo contracts for the runtime-split Asset Allocation system.

This repository owns:
- Python contract models under `python/asset_allocation_contracts`
- TypeScript contract types under `ts/src`
- JSON schema artifacts under `schemas`
- Cross-repo smoke gate under `scripts/compatibility_gate.ps1`

Documentation:

- `docs/architecture/configuration-examples.md` contains valid examples for the shared configuration contract surfaces.
- `docs/ops/env-contract.md` and `docs/ops/env-contract.csv` document the repo bootstrap env contract used for release and dispatch automation.

Downstream repos consume published package versions. Normal CI and release flows should not install contracts from a sibling checkout, and `contracts_released` dispatches carry the exact published version for downstream auto-adoption.

It does not own runtime IO, storage, Postgres, Delta, monitoring, or orchestration helpers.

## Operations

Canonical workflows live under `.github/workflows/`.

- `ci.yml` is the required validation path for PRs and `main`.
- `security.yml` runs dependency and supply-chain checks.
- `release.yml` is a manual workflow that computes a fresh UTC prerelease version, stages it into the runner workspace manifests, publishes TypeScript to npm under the `dev` dist-tag, emits `release-manifest.json`, and dispatches `contracts_released` to downstream repos.
- `scripts/setup-env.ps1` builds repo-local `.env.web` for registry and dispatch configuration, including loading `DISPATCH_APP_PRIVATE_KEY` from a PEM file.
- `scripts/sync-all-to-github.ps1` syncs the `.env.web` surface into repo vars and secrets.
- Deployment guidance and required registry credentials live in `DEPLOYMENT_SETUP.md`.
