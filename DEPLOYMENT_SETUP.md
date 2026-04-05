# Deployment Setup

## Recommendation

Do not deploy this repo into `AssetAllocationRG`.

This repo should publish versioned contract artifacts only:

- a Python package from `python/`
- a TypeScript package from `ts/`
- JSON schemas from `schemas/`

The runtime repos should pin a contracts version and deploy against that version.

## Same Resource Group?

No. This repo should not own an Azure Container App, Container Apps Job, storage account, or database.

## Current State

- This repo has no `.github/workflows/` directory yet.
- Python package metadata exists in `python/pyproject.toml`.
- TypeScript package metadata exists in `ts/package.json`.
- Shared JSON schemas already exist under `schemas/`.
- Cross-repo verification already exists in `scripts/compatibility_gate.ps1`.

## What To Provision

Provision package distribution, not Azure runtime infrastructure:

1. Pick a Python package registry.
2. Pick a TypeScript package registry.
3. Add publishing credentials as GitHub repository secrets.
4. Add a release workflow that builds, tests, and publishes both packages from the same tag.

Good first-cut options:

- Python: PyPI, GitHub Packages, or Azure Artifacts
- TypeScript: npm, GitHub Packages, or Azure Artifacts

## Deploy

This repo has no Azure deployment target.

The operational path is:

1. run `.github/workflows/ci.yml`
2. run `.github/workflows/security.yml`
3. publish with `.github/workflows/release.yml`

`release.yml` emits `artifacts/release-manifest.json` and dispatches `contracts_released` to the control-plane and UI repos.

## Operate

- Keep the Python and TypeScript package versions identical.
- Keep `schemas/` regenerated from source by running `python python/scripts/export_schemas.py`.
- Use `scripts/compatibility_gate.ps1` as the cross-repo smoke check before publishing a breaking contract change.

## Release Steps

1. Update the version in `python/pyproject.toml`.
2. Update the version in `ts/package.json`.
3. Run the contract validation steps:
   - `python -m pytest tests/python/test_contract_models.py -q`
   - `cd ts && corepack pnpm typecheck`
   - `powershell -ExecutionPolicy Bypass -File scripts/compatibility_gate.ps1`
4. Build and publish the Python package.
5. Build and publish the TypeScript package.
6. Update version pins in the control-plane, jobs, and UI repos.

## Rollback

- Re-publish or re-tag the previous known-good contracts version.
- Re-run the downstream compatibility workflows against that version.
- Revert any consumer repo updates that pinned the bad version.

## Troubleshoot

- If `ci.yml` fails on schema drift, regenerate `schemas/` from `python/scripts/export_schemas.py` and commit the result.
- If `release.yml` fails before publish, check the package version mismatch between `python/pyproject.toml` and `ts/package.json`.
- If publish fails, verify `PYTHON_PUBLISH_REPOSITORY_URL`, `PYTHON_PUBLISH_USERNAME`, `PYTHON_PUBLISH_PASSWORD`, `NPM_REGISTRY_URL`, and `NPM_TOKEN`.
- If downstream dispatch fails, verify `DISPATCH_APP_ID`, `DISPATCH_APP_PRIVATE_KEY`, and the target repo variables `CONTROL_PLANE_REPOSITORY` and `UI_REPOSITORY`.

## Dependencies

- GitHub App credentials for `contracts_released` dispatches
- Python package registry credentials
- TypeScript package registry credentials
- Downstream repos: `asset-allocation-control-plane` and `asset-allocation-ui`

## GitHub Setup

Add repository secrets for the registries you choose. At minimum:

- `PYPI_TOKEN` or the equivalent registry token for Python
- `NPM_TOKEN` or the equivalent registry token for TypeScript

Add a workflow that:

1. runs the Python tests
2. runs the TypeScript typecheck
3. runs `scripts/compatibility_gate.ps1`
4. publishes both packages from the same release

## What This Repo Owns

- Pydantic models under `python/asset_allocation_contracts/`
- TypeScript contract exports under `ts/src/`
- exported JSON schemas under `schemas/`

It should not own:

- FastAPI deployment
- Azure Container Apps Jobs
- Azure storage access
- Postgres access

## Evidence

- `python/pyproject.toml`
- `ts/package.json`
- `schemas/`
- `scripts/compatibility_gate.ps1`
- `README.md`
