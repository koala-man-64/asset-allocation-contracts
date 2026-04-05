# Asset Allocation Contracts

Shared cross-repo contracts for the runtime-split Asset Allocation system.

This repository owns:
- Python contract models under `python/asset_allocation_contracts`
- TypeScript contract types under `ts/src`
- JSON schema artifacts under `schemas`
- Cross-repo smoke gate under `scripts/compatibility_gate.ps1`

It does not own runtime IO, storage, Postgres, Delta, monitoring, or orchestration helpers.

## Operations

Canonical workflows live under `.github/workflows/`.

- `ci.yml` is the required validation path for PRs and `main`.
- `security.yml` runs dependency and supply-chain checks.
- `release.yml` publishes the Python and TypeScript packages, emits `release-manifest.json`, and dispatches `contracts_released` to downstream repos.
- Deployment guidance and required registry credentials live in `DEPLOYMENT_SETUP.md`.
