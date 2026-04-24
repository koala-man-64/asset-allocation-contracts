# Asset Allocation Contracts Master Design Document

This document is the canonical design and governance reference for `asset-allocation-contracts`.

It is intentionally normative, not just descriptive. It defines what this repo is supposed to own, how changes are supposed to flow through it, which interfaces are public, and which invariants future agents must preserve. It does not replace file-level sources of truth; it tells future maintainers which files are authoritative for each contract surface and what must be updated together.

Use [original-monolith-and-five-repo-map.md](./original-monolith-and-five-repo-map.md) for lineage and system-split context. Use this document for current intended design, operational contract boundaries, and repo update rules.

Verified against the current worktree on 2026-04-24.

## 1. Purpose and Non-Goals

### Purpose

`asset-allocation-contracts` exists to publish the shared contract layer for the split Asset Allocation system.

It owns:

- Shared Python contract models under `python/asset_allocation_contracts/`
- Shared TypeScript contract types under `ts/src/`
- Generated JSON Schema artifacts under `schemas/`
- Release automation that publishes both packages and notifies downstream repos
- Repo-level env/config contract used to drive release and dispatch automation
- Cross-repo compatibility validation expectations for contract changes

This repo exists because the Asset Allocation platform was split into separate control-plane, jobs, UI, runtime-common, and contracts repos. After the split, shared shapes had to become explicit, versioned artifacts instead of implicit cross-repo source imports.

### Non-Goals

This repo does not own:

- Runtime IO
- FastAPI or browser runtime behavior
- Storage systems such as Postgres, Delta, or ADLS
- Azure deployment or provisioning
- Job orchestration or control-plane orchestration logic
- Consumer-specific business logic outside shared contract semantics

If a change requires owning runtime behavior instead of shared interfaces, it likely belongs in a consumer repo rather than here.

### Primary Evidence

- `README.md`
- `python/pyproject.toml`
- `ts/package.json`
- `.github/workflows/ci.yml`
- `.github/workflows/release.yml`
- `DEPLOYMENT_SETUP.md`

## 2. System Context

This repo is one part of a five-repo system:

- `asset-allocation-contracts`: shared contracts and publication boundary
- `asset-allocation-runtime-common`: shared backend helper layer
- `asset-allocation-control-plane`: API and operator-state owner
- `asset-allocation-jobs`: ETL, provider integration, and backtesting runtime
- `asset-allocation-ui`: browser-based operator console

The intended dependency model is published-artifact consumption:

- Python consumers install the published `asset-allocation-contracts` package
- TypeScript consumers install the published `@asset-allocation/contracts` package
- Language-neutral consumers can use the generated `schemas/*.schema.json`

Normal CI and release flows are not supposed to install contracts from a sibling checkout. This repo is designed to be a packaging and compatibility boundary, not a shared source tree.

### How the Repo Fits the System

At a high level:

1. Engineers change shared contract models in Python and keep the TypeScript mirror aligned.
2. JSON Schemas are regenerated from the Python models.
3. CI validates version parity, schema drift, tests, and package builds.
4. Release automation publishes Python and TypeScript artifacts.
5. Release automation emits `release-manifest.json` and dispatches `contracts_released` to downstream repos so they can react to the new contract version.

### Primary Evidence

- `README.md`
- `docs/architecture/original-monolith-and-five-repo-map.md`
- `scripts/compatibility_gate.ps1`
- `.github/workflows/release.yml`

## 3. Source-of-Truth Hierarchy

This repo has multiple contract representations. Their intended authority is not equal.

### 3.1 Canonical Data Contract Source

Python Pydantic models in `python/asset_allocation_contracts/` are the canonical contract source for shared data shapes and validation semantics.

That includes:

- Allowed fields
- Required vs optional fields
- Validation constraints
- Normalization behavior
- Compatibility shims that still exist at the model boundary

If a change affects shared contract meaning, the Python models are the first place that should change.

### 3.2 Derived Artifact Layer

JSON Schemas in `schemas/` are derived artifacts generated from the Python models by `python/scripts/export_schemas.py`.

These files must not be treated as hand-authored source. They exist to make the Python contract surface consumable outside Python and to make drift observable in CI.

### 3.3 Maintained Mirror Layer

TypeScript types in `ts/src/contracts.ts` are a maintained mirror of the shared contract surface for frontend and TS consumers.

They are public and important, but they are not schema-generated today. They must be kept in sync intentionally when the Python contract source changes.

### 3.4 Operational Contract Surfaces

This repo also has operational interfaces that are part of its architecture:

- GitHub workflow inputs and behavior under `.github/workflows/`
- Repo env/config contract under `docs/ops/env-contract.csv`
- Bootstrap and sync scripts under `scripts/setup-env.ps1` and `scripts/sync-all-to-github.ps1`
- Local release-prep script under `scripts/prepare-release.ps1`
- Release artifact and downstream dispatch payload shapes

These are not secondary implementation details. They are part of the repo's public operating contract.

### Source-of-Truth Rule

If a contract change touches multiple surfaces, update them in this order:

1. Python models
2. TypeScript mirror
3. Generated schemas
4. Tests
5. Workflow/docs/env surfaces if the release or operating contract changed
6. This design document

### Primary Evidence

- `python/asset_allocation_contracts/__init__.py`
- `python/scripts/export_schemas.py`
- `ts/src/contracts.ts`
- `tests/python/test_contract_models.py`
- `tests/test_env_contract.py`

## 4. Contract Inventory

This section lists the public contract families this repo owns and why each exists.

### 4.1 Strategy and Universe Contracts

Owned by:

- `python/asset_allocation_contracts/strategy.py`
- `schemas/strategy-config.schema.json`
- `schemas/universe-definition.schema.json`
- `ts/src/contracts.ts`

Purpose:

- Define strategy runtime configuration
- Define universe selection structure
- Define exit-rule configuration semantics
- Preserve temporary compatibility behavior such as legacy toggle stripping at the API boundary

Key design note:

`StrategyConfig` currently strips legacy `enabled` toggles from `regimePolicy` and `exits` before final validation. That is compatibility behavior, not a new canonical modeling direction, and it should remain explicit if retained.

### 4.2 Ranking Contracts

Owned by:

- `python/asset_allocation_contracts/ranking.py`
- `schemas/ranking-schema.schema.json`
- `ts/src/contracts.ts`

Purpose:

- Define ranking factors, groups, transforms, and output-summary shapes
- Enforce naming, transform-parameter, and uniqueness rules centrally

### 4.3 Regime Contracts

Owned by:

- `python/asset_allocation_contracts/regime.py`
- `schemas/regime-*.schema.json`
- `ts/src/contracts.ts`

Purpose:

- Define regime policy, model config, snapshots, transitions, and model revision payloads
- Preserve default regime model behavior and operational thresholds in a shared form

### 4.4 Backtest Contracts

Owned by:

- `python/asset_allocation_contracts/backtest.py`
- `schemas/backtest-*.schema.json`
- `ts/src/contracts.ts`

Purpose:

- Define request/response payloads for backtest claim, start, complete, fail, listing, summary, timeseries, rolling metrics, and trade outputs
- Carry additive backtest result metadata for v2 semantics on timeseries and rolling metrics responses without removing legacy field names
- Preserve compatibility shims where the runtime still emits or accepts old payload keys such as `daily_return` and `window_days`

### 4.5 Portfolio Workspace Contracts

Owned by:

- `python/asset_allocation_contracts/portfolio.py`
- `schemas/portfolio-*.schema.json`
- `ts/src/contracts.ts`

Purpose:

- Define internal portfolio-account and reusable portfolio-definition contracts for the portfolio workspace feature
- Define immutable ledger-event, assignment, rebalance-proposal, snapshot, history, position, attribution, and alert payloads shared across control-plane, jobs, and UI
- Encode the current v1 operating boundary explicitly: internal-only, model-managed accounts with position-level accounting and strategy-native sleeve cadence

Key design note:

These contracts intentionally stop short of broker or custody-grade accounting. They support internal ledger truth, pinned strategy revisions, and derived monitoring surfaces, but they do not imply external execution, lot accounting, settlement, or reconciliation ownership in this repo.

### 4.6 Job Metadata and Strategy Publication Contracts

Owned by:

- `python/asset_allocation_contracts/job_metadata.py`
- `python/asset_allocation_contracts/strategy_publication.py`
- `schemas/runtime-job-metadata.schema.json`
- `schemas/strategy-publication-reconcile-signal-request.schema.json`
- `schemas/strategy-publication-reconcile-signal-response.schema.json`
- `ts/src/contracts.ts`

Purpose:

- Define the additive system-health taxonomy fields `jobCategory`, `jobKey`, `jobRole`, `triggerOwner`, `metadataSource`, and `metadataStatus`
- Keep strategy-compute jobs, medallion data-pipeline jobs, and operational-support jobs distinct without relying on job-name substring inference
- Define the durable regime publication reconcile signal request and response shared between jobs and the control-plane internal API
- Preserve server ownership of reconcile signal state: producers send typed publication metadata, while the control plane assigns `pending`, `processed`, or `error`

Key design note:

`strategy-compute` is a workflow category, not a medallion layer. `gold-regime-job` remains the ACA resource name and may write gold outputs, but its contract category is `strategy-compute`. `platinum-rankings-job` follows the same rule for platinum outputs.

### 4.7 UI Runtime Config Contract

Owned by:

- `python/asset_allocation_contracts/ui_config.py`
- `schemas/ui-runtime-config.schema.json`
- `ts/src/contracts.ts`

Purpose:

- Define the browser bootstrap/runtime config surface for API base URL and OIDC/auth settings, including the derived post-logout completion URI
- Normalize scope/audience list handling

### 4.8 Auth Session Contract

Owned by:

- `python/asset_allocation_contracts/ui_config.py`
- `schemas/auth-session-status.schema.json`
- `ts/src/contracts.ts`

Purpose:

- Define the shared response payload for the control-plane `GET /api/auth/session` surface
- Give the UI a typed auth/authz probe that is distinct from general system-health data
- Keep the control-plane, UI, and any future non-browser consumer aligned on the same minimal session summary fields

### 4.9 Shared Finance and Path Constants

Owned by:

- `python/asset_allocation_contracts/finance.py`
- `python/asset_allocation_contracts/paths.py`
- `python/asset_allocation_contracts/market_history.py`

Purpose:

- Provide stable shared constants and path-construction rules used across runtime repos
- Keep storage/domain naming conventions and finance subdomain mappings from drifting between consumers

These are still contract surfaces even though they are constants rather than large object models.

### 4.10 Release and Env/Config Surfaces

Owned by:

- `.github/workflows/ci.yml`
- `.github/workflows/security.yml`
- `.github/workflows/release.yml`
- `.env.template`
- `docs/ops/env-contract.csv`
- `docs/ops/env-contract.md`
- `scripts/setup-env.ps1`
- `scripts/sync-all-to-github.ps1`

Purpose:

- Define what makes the repo safe to build, publish, and operate
- Define which GitHub variables and secrets are required
- Define how local env bootstrap becomes GitHub configuration
- Define downstream dispatch behavior after release

### Primary Evidence

- `python/asset_allocation_contracts/strategy.py`
- `python/asset_allocation_contracts/ranking.py`
- `python/asset_allocation_contracts/regime.py`
- `python/asset_allocation_contracts/backtest.py`
- `python/asset_allocation_contracts/job_metadata.py`
- `python/asset_allocation_contracts/strategy_publication.py`
- `python/asset_allocation_contracts/ui_config.py`
- `python/asset_allocation_contracts/finance.py`
- `python/asset_allocation_contracts/paths.py`
- `python/asset_allocation_contracts/market_history.py`
- `ts/src/contracts.ts`
- `schemas/`

## 5. Execution Lifecycle

This repo is mostly dormant until humans change contracts or automation triggers run. Its important behavior is packaging, validation, and release.

### 5.1 Authoring and Schema Generation

Shared contract changes start in Python model code. JSON Schemas are regenerated via:

```powershell
python python/scripts/export_schemas.py
```

CI treats schema drift as a failure. That means the checked-in `schemas/` directory is expected to match the current Python contract source exactly.

### 5.2 CI on Pull Requests and `main`

`.github/workflows/ci.yml` is the required validation path.

It enforces:

- Workflow linting with `actionlint`
- Python and TypeScript version parity
- Schema export with no drift in `schemas/`
- Python contract tests
- Python distribution build
- TypeScript typecheck and package pack

### 5.3 Scheduled Security Audit

`.github/workflows/security.yml` runs on pull requests, `main`, manual dispatch, and a weekly schedule.

It audits:

- Python dependencies using `pip-audit`
- TypeScript dependencies using `pnpm audit`

Artifacts from those audits are uploaded for review.

### 5.4 Release by Manual Dispatch

`.github/workflows/release.yml` runs by manual dispatch.

The release workflow reads the committed stable semver from `python/pyproject.toml` and `ts/package.json`, verifies that both manifests match exactly, and publishes that same version for both package ecosystems.

It performs:

1. Version parity and stable semver validation
2. npm version availability check
3. Python registry version availability check
4. Python package build
5. TypeScript package tarball build
6. TypeScript package publish to public npm from a GitHub-hosted runner using npm trusted publishing
7. Python package publish
8. Release manifest generation
9. GitHub App token creation
10. Downstream `contracts_released` dispatch
11. Release summary write-out

Normal steady-state releases do not use a long-lived npm publish token. The first publish of a brand-new npm package remains a one-time bootstrap exception handled outside the normal env-contract surface.

### 5.5 Release Manifest Interface

`release.yml` writes `artifacts/release-manifest.json` with this shape:

```json
{
  "repo": "<github repository slug>",
  "git_sha": "<release commit sha>",
  "artifact_kind": "contracts",
  "artifact_ref": {
    "python": ["<python artifact names>"],
    "typescript": ["<typescript artifact names>"]
  },
  "contracts_version": "<shared version>"
}
```

This is a public operational artifact and must remain intentional if changed.

### 5.6 Downstream Dispatch Interface

The release workflow dispatches the GitHub repository event `contracts_released` to downstream repos.

Current workflow behavior targets:

- Jobs
- UI

Current payload shape:

```json
{
  "event_type": "contracts_released",
  "client_payload": {
    "contracts_version": "<shared version>",
    "contracts_ref": "<git ref name>",
    "contracts_sha": "<git sha>",
    "manifest_path": "release-manifest.json"
  }
}
```

Any change to this payload or target-repo list is a release-contract change and must be documented and coordinated with consumers.

### 5.7 Cross-Repo Compatibility Gate

`scripts/compatibility_gate.ps1` is the smoke gate for breaking or risky contract changes.

It validates this repo locally, then shells into sibling repos and runs selected control-plane, jobs, and UI validations. That makes compatibility a first-class design concern even though most of the checks run outside this repo.

### Primary Evidence

- `.github/workflows/ci.yml`
- `.github/workflows/security.yml`
- `.github/workflows/release.yml`
- `scripts/compatibility_gate.ps1`
- `scripts/prepare-release.ps1`
- `python/scripts/export_schemas.py`

## 6. Public Interfaces and Invariants

The following rules are mandatory design invariants.

### 6.1 Package and Version Invariants

- Python and TypeScript package versions must stay identical.
- Version mismatch is release-blocking and CI-blocking.
- Consumer repos are expected to pin published versions, not rely on sibling source.

### 6.2 Schema Invariants

- `schemas/` must be reproducible from Python models.
- Schema files are derived artifacts and must not be hand-edited as the primary change path.
- Any intended schema change must be explainable by a corresponding Python model change.

### 6.3 Mirror-Surface Invariants

- TypeScript types must stay semantically aligned with the Python contract source.
- Because alignment is maintained manually today, agents must treat TS updates as required companion work for shared-contract changes.

### 6.4 Release and Dispatch Invariants

- Release artifacts must include both Python and TypeScript outputs.
- TypeScript releases publish to public npm from GitHub Actions using npm trusted publishing.
- `release-manifest.json` shape is part of the public operating contract.
- `contracts_released` payload shape and target-repo set are part of the public operating contract.

### 6.5 Env/Config Invariants

- Workflow variable and secret references must be documented in `docs/ops/env-contract.csv`.
- `.env.template`, `docs/ops/env-contract.csv`, `scripts/setup-env.ps1`, `scripts/sync-all-to-github.ps1`, and workflow references must stay synchronized.
- `.env.web` carries Python registry and dispatch credentials only; TypeScript publish auth is not stored there.
- `DISPATCH_APP_PRIVATE_KEY` is expected to be loaded from a PEM file path and stored in `.env.web` with literal `\n` escapes.

### 6.6 Scope Invariants

- Do not expand this repo into a runtime or deployment repo.
- Keep runtime-specific behavior in consumer repos unless it is truly shared contract logic.
- Shared compatibility shims are allowed only when they are explicit, intentional, and documented.

### Primary Evidence

- `python/pyproject.toml`
- `ts/package.json`
- `.github/workflows/ci.yml`
- `.github/workflows/release.yml`
- `docs/ops/env-contract.csv`
- `scripts/setup-env.ps1`

## 7. Validation Model

The question for this repo is not only “do the tests pass?” but “is the contract release-safe?”

### Safe-to-Release Definition

This repo is safe to release only when all of the following are true:

- Python and TypeScript versions match
- Python models, TypeScript mirror, and generated schemas are aligned
- `schemas/` shows no unintended drift
- Python contract tests pass
- TypeScript typecheck passes
- Package builds succeed
- Release env/config surfaces are internally consistent
- Downstream impact has been considered for any breaking or high-risk change

### Required Local and CI Evidence

Core validation commands:

```powershell
python -m pytest tests/python/test_contract_models.py tests/test_env_contract.py -q
```

```powershell
cd ts
corepack pnpm typecheck
```

Optional but expected for risky changes:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/compatibility_gate.ps1
```

### What Each Gate Proves

- `tests/python/test_contract_models.py`
  - shared model validation and normalization still behave as intended
- `tests/test_env_contract.py`
  - workflow vars/secrets, env template, and env docs remain synchronized
- `ci.yml`
  - required repo-local build and drift checks pass
- `security.yml`
  - dependency audit posture is acceptable at current thresholds
- `compatibility_gate.ps1`
  - likely downstream consumers still tolerate the contract change

### Known Limits of the Current Validation Model

- Cross-repo compatibility is not enforced by GitHub Actions in this repo
- TypeScript-to-Python semantic parity is not automatically diffed
- Release manifest and dispatch payload shapes are not directly unit-tested as standalone contracts

### Primary Evidence

- `.github/workflows/ci.yml`
- `.github/workflows/security.yml`
- `tests/python/test_contract_models.py`
- `tests/test_env_contract.py`
- `scripts/compatibility_gate.ps1`

## 8. Governance Rules

Future agents must treat the following files as one governance unit:

- `.github/workflows/*.yml`
- `.env.template`
- `docs/ops/env-contract.csv`
- `docs/ops/env-contract.md`
- `scripts/setup-env.ps1`
- `scripts/sync-all-to-github.ps1`
- `tests/test_env_contract.py`
- this document

Do not change one of these surfaces in isolation when the effective release or env contract changes.

### What Must Change Together

#### Contract-model changes

When changing shared data contract behavior:

- update Python model source
- update TypeScript mirror types
- regenerate schemas
- update or add tests
- update this document if public behavior, invariants, or update rules changed
- run compatibility validation when the change may affect consumers

#### Workflow or env-contract changes

When adding or changing workflow variables, secrets, release steps, dispatch behavior, or manifest behavior:

- update the workflow
- update `docs/ops/env-contract.csv`
- update `.env.template` if the bootstrap surface changed
- update bootstrap/sync scripts if needed
- update `tests/test_env_contract.py`
- update this document

#### Breaking or compatibility-sensitive changes

When changing payload shape, removing fields, changing validation rules, or altering release payloads:

- document the compatibility impact explicitly
- run or revise the cross-repo compatibility gate
- coordinate with downstream repos
- make the versioning intent explicit in the release

### Primary Evidence

- `tests/test_env_contract.py`
- `.github/workflows/release.yml`
- `docs/ops/env-contract.csv`
- `scripts/setup-env.ps1`
- `scripts/sync-all-to-github.ps1`

## 9. Known Current Drift

This section records current mismatches observed during verification. It exists so future agents do not mistake repo drift for intended design.

### 9.1 Committed Release Version Source

Observed:

- `release.yml` reads the committed version from `python/pyproject.toml` and `ts/package.json`
- the committed version must be stable semver and identical across Python and TypeScript
- npm and Python registry preflight checks block republishing an existing contracts version

Interpretation:

The steady-state contracts release path is committed-manifest semver publishing. Future agents should treat the checked-in Python and TypeScript versions as both CI alignment state and the publish artifact state for manual releases.

### 9.2 Off-Repo Compatibility Gate

Observed:

- `scripts/compatibility_gate.ps1` is an important release-safety mechanism
- It depends on sibling repos and local checkout layout
- It is not currently enforced inside GitHub Actions for this repo

Interpretation:

The most meaningful compatibility check is operationally important but partly externalized. Future agents should not mistake repo-local CI success for full downstream compatibility confidence.

### 9.3 TypeScript Mirror Drift Risk

Observed:

- Python is treated as the schema-generation source
- TypeScript is maintained manually
- No automated semantic parity check compares the TS surface against Python models or JSON Schemas

Interpretation:

TS alignment depends on disciplined companion edits. This is a manageable design tradeoff, but it is a real drift risk.

### 9.4 Governance Ambiguity in the Current Worktree

Observed:

- The committed repo contains `CODEOWNERS` at the repo root
- The current worktree also contains an untracked `.github/CODEOWNERS` with different ownership rules

Interpretation:

This may represent an in-flight governance change rather than committed repo behavior. Treat it as `Unverified / Needs confirmation` until the repo settles on one documented source of ownership truth.

### Primary Evidence

- `.github/workflows/release.yml`
- `docs/ops/env-contract.csv`
- `.env.template`
- `tests/test_env_contract.py`
- `scripts/compatibility_gate.ps1`
- `CODEOWNERS`
- `.github/CODEOWNERS`

## 10. Future-Agent Update Protocol

Update this document in the same change when any of the following happens:

- A new contract model or exported type is added
- A field is added, removed, renamed, retyped, or given new validation semantics
- A new schema artifact is introduced or a contract family is renamed
- A compatibility shim is added, changed, deprecated, or removed
- A workflow variable or secret is added, removed, or repurposed
- The release manifest shape changes
- The downstream dispatch payload or target-repo list changes
- The compatibility gate scope changes
- A validation gate changes what “safe to release” means
- Repo scope changes in a way that affects ownership boundaries

### Update Checklist

When updating this document:

1. Confirm which file is authoritative for the changed surface.
2. Update the code, workflow, or env source first.
3. Update related derived or mirrored artifacts.
4. Update tests and validation references.
5. Update this document's affected sections and the known-drift section if the repo is temporarily inconsistent.
6. Re-run the relevant validation commands.

### What Not To Do

- Do not edit schemas first and backfill Python later.
- Do not change workflow vars or secrets without reconciling env docs and tests.
- Do not hide compatibility shims or drift in prose.
- Do not expand repo scope casually because it creates ownership confusion across the five-repo system.

## 11. Evidence Index

Primary files used to verify this document:

- `README.md`
- `DEPLOYMENT_SETUP.md`
- `docs/architecture/original-monolith-and-five-repo-map.md`
- `python/pyproject.toml`
- `python/asset_allocation_contracts/__init__.py`
- `python/asset_allocation_contracts/backtest.py`
- `python/asset_allocation_contracts/finance.py`
- `python/asset_allocation_contracts/market_history.py`
- `python/asset_allocation_contracts/paths.py`
- `python/asset_allocation_contracts/ranking.py`
- `python/asset_allocation_contracts/regime.py`
- `python/asset_allocation_contracts/strategy.py`
- `python/asset_allocation_contracts/ui_config.py`
- `python/scripts/export_schemas.py`
- `ts/package.json`
- `ts/src/contracts.ts`
- `ts/src/index.ts`
- `.github/workflows/ci.yml`
- `.github/workflows/security.yml`
- `.github/workflows/release.yml`
- `scripts/compatibility_gate.ps1`
- `scripts/setup-env.ps1`
- `scripts/sync-all-to-github.ps1`
- `docs/ops/env-contract.csv`
- `docs/ops/env-contract.md`
- `tests/python/test_contract_models.py`
- `tests/test_env_contract.py`
- `CODEOWNERS`
- `.github/CODEOWNERS`
