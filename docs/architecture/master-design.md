# Asset Allocation Contracts Master Design Document

This document is the canonical design and governance reference for `asset-allocation-contracts`.

It is intentionally normative, not just descriptive. It defines what this repo is supposed to own, how changes are supposed to flow through it, which interfaces are public, and which invariants future agents must preserve. It does not replace file-level sources of truth; it tells future maintainers which files are authoritative for each contract surface and what must be updated together.

Use [original-monolith-and-five-repo-map.md](./original-monolith-and-five-repo-map.md) for lineage and system-split context. Use this document for current intended design, operational contract boundaries, and repo update rules.

Verified against the current worktree on 2026-04-25.

## 1. Purpose and Non-Goals

### Purpose

`asset-allocation-contracts` exists to publish the shared contract layer for the split Asset Allocation system.

It owns:

- Shared Python contract models under `python/asset_allocation_contracts/`
- Shared TypeScript contract types under `ts/src/`
- Generated JSON Schema artifacts under `schemas/`
- Release automation that publishes both packages and notifies downstream repos
- Repo-level env/config contract used to drive release and retained legacy dispatch automation
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
- `azure-pipelines/ci.yml`
- `azure-pipelines/security.yml`
- `azure-pipelines/release.yml`
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
5. Release automation emits `release-manifest.json` so downstream automation can react to the exact published version.

### Primary Evidence

- `README.md`
- `docs/architecture/original-monolith-and-five-repo-map.md`
- `scripts/compatibility_gate.ps1`
- `azure-pipelines/release.yml`

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

- Azure Pipelines inputs and behavior under `azure-pipelines/`
- Repo env/config contract under `docs/ops/env-contract.csv`
- Bootstrap and sync scripts under `scripts/setup-env.ps1` and `scripts/sync-all-to-azure-devops.ps1`
- Local release-prep script under `scripts/prepare-release.ps1`
- Release artifact and downstream version-handoff shapes

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
- `python/asset_allocation_contracts/regime.py`
- `schemas/strategy-config.schema.json`
- `schemas/universe-definition.schema.json`
- `schemas/*-config.schema.json`
- `schemas/*-revision.schema.json`
- `ts/src/contracts.ts`

Purpose:

- Define strategy runtime configuration
- Define universe selection structure
- Define the plaintext-to-universe draft-generation request/response envelope consumed by control-plane and UI
- Define exit-rule configuration semantics
- Define reusable versioned configuration library contracts for regime policies, risk policies, and exit rule sets
- Define exact revision pin fields that let strategy assembly reference reusable library objects by name and version
- Define `StrategyConfig.regimeGates`, the strategy-level weighted regime playbook that maps named regime predicates to saved strategy revision allocations
- Preserve temporary compatibility behavior such as legacy toggle stripping at the API boundary

Key design note:

`StrategyConfig` currently strips legacy `enabled` toggles from `regimePolicy` and `exits` before final validation. That is compatibility behavior, not a new canonical modeling direction, and it should remain explicit if retained.

Reusable strategy configuration libraries are database-backed and revisioned outside the strategy document. Strategy assembly pins exact revisions with `universeConfigVersion`, `rankingSchemaVersion`, `regimePolicyConfigVersion`, `riskPolicyVersion`, and `exitRuleSetVersion`; execution continues to read resolved snapshots such as `regimePolicy`, `strategyRiskPolicy`, `intrabarConflictPolicy`, and `exits` from immutable strategy revisions. No runtime should resolve "latest by name" during execution.

Weighted regime routing is strategy-level, not ranking-schema-level. `StrategyConfig.regimeGates` is a dictionary keyed by gate name; each entry contains a regime predicate and one or more saved strategy revision allocations with positive relative weights. Runtimes normalize active allocation weights at evaluation time. If no gate is active, execution should target zero rather than carrying forward a prior strategy. Ranking schemas remain pure scoring and universe-selection definitions.

Plaintext-to-universe generation is a draft-only contract family. `UniverseConfigDraftGenerationRequest` carries the user's plaintext intent and optional editor hints; `UniverseConfigDraftGenerationResponse` returns a candidate `UniverseConfigPreset`, explanation, assumptions, warnings, fields used, and optional preview. The generated universe is not a saved reusable config. Control-plane owns prompt construction, Azure OpenAI calls, validation, preview, and persistence separation; this repo owns only the shared envelope and embedded `UniverseDefinition` semantics.

Plaintext-to-ranking generation follows the same draft-only boundary. `RankingSchemaDraftGenerationRequest` carries the user's ranking intent plus optional naming, universe, and preview hints; `RankingSchemaDraftGenerationResponse` returns a candidate `RankingSchemaPreset`, explanation, assumptions, warnings, factor field references, unmapped signals, and optional ranking preview. The generated ranking schema is not persisted by this contract; control-plane owns prompt construction, Azure OpenAI calls, catalog validation, preview execution, and save separation.

Trader agent profile overlays are contracts-repo-first and deterministic. `AgentProfileConfig` stores bounded behavioral traits, relative worldview weights, evidence policy, and regime preferences; `AgentStrategyBinding` pins an exact profile revision and exact base strategy revision while carrying explicit governed component maps and clamp bounds. Compilers must produce an immutable resolved `StrategyConfig` artifact outside the profile document, record structured `AgentAppliedConfigChange` provenance, and block on missing mappings or refs instead of silently selecting defaults. V1 agent profiles are limited to research, recommendation, and paper-preview workflows and must not model live-submit authority.

### 4.2 Ranking Contracts

Owned by:

- `python/asset_allocation_contracts/ranking.py`
- `schemas/ranking-schema.schema.json`
- `ts/src/contracts.ts`

Purpose:

- Define ranking factors, groups, transforms, and output-summary shapes
- Enforce naming, transform-parameter, and uniqueness rules centrally
- Exclude regime routing. New ranking schema documents must not author regime gates; legacy rows with ranking-level gates are compatibility input for downstream adapters only.

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
- Define the active-portfolio allocation model used by account-scoped orchestration, including v1 `percent` and `notional_base_ccy` sleeve allocation modes
- Encode the current v1 operating boundary explicitly: internal-only, model-managed accounts with position-level accounting and strategy-native sleeve cadence

Key design note:

These contracts intentionally stop short of broker or custody-grade accounting. They support internal ledger truth, pinned strategy revisions, dual-mode sleeve budgeting, and derived monitoring surfaces, but they do not imply external execution, lot accounting, settlement, or reconciliation ownership in this repo.

### 4.6 Broker Account Operations Contracts

Owned by:

- `python/asset_allocation_contracts/broker_accounts.py`
- `python/asset_allocation_contracts/trade_desk.py`
- `schemas/broker-account-*.schema.json`
- `schemas/trade-account-*.schema.json`
- `schemas/trade-order-*.schema.json`
- `ts/src/contracts.ts`

Purpose:

- Define broker-account trading policy, effective policy, configuration versioning, edit capabilities, and append-only audit payloads shared by control-plane and UI
- Define account-scoped strategy allocation summaries and update requests that orchestrate active-portfolio changes without introducing a second source of truth on the account
- Define trade-desk preview and submit confirmation fields such as `policyVersion`, `confirmationRequired`, `orderHash`, `confirmationToken`, and `expiresAt`

Key design note:

Broker-account contracts own account-level hard controls and operator-facing configuration state. They do not move portfolio construction ownership away from the active portfolio. Account allocation edits are orchestrated through broker-account commands, but the active portfolio remains the canonical source for sleeve definitions and allocation rows.

### 4.6.1 Options Strategy and Backtest Contracts

Owned by:

- `python/asset_allocation_contracts/options.py`
- `python/asset_allocation_contracts/backtest.py`
- `python/asset_allocation_contracts/trade_desk.py`
- `schemas/option-*.schema.json`
- `schemas/backtest-*.schema.json`
- `schemas/trade-*.schema.json`
- `ts/src/contracts.ts`

Purpose:

- Define canonical option contract identity, option legs, leg groups, strategy templates, payoff profiles, quote/Greeks snapshots, lifecycle events, broker capability profiles, risk gates, and option backtest result/event envelopes
- Publish the full options ladder taxonomy while keeping v1 research-only through explicit `researchBacktestSupported`, `brokerPreviewSupported`, and `liveSubmitSupported` flags
- Carry option-specific backtest observability fields such as quote/Greeks missing counts, chain staleness, assignment/exercise/expiry counts, research-only blocks, and model-quality status
- Represent Alpaca as the first broker capability profile without making Alpaca the canonical strategy model

Key design note:

Options are a contracts-repo-first capability. Consumer repos must not invent divergent option payloads for strategies, broker previews, chain snapshots, lifecycle events, or payoff/risk evaluation. V1 does not support live option submission: every canonical strategy template and broker constraint profile must keep `liveSubmitSupported=false`. Runtime-common may add pure payoff and normalization helpers after consuming a published contracts version, but API state, saved configuration, provider ingestion, and UI workflows remain owned by their respective consumer repos.

### 4.7 Notification And Trade Approval Contracts

Owned by:

- `python/asset_allocation_contracts/notifications.py`
- `schemas/notification-*.schema.json`
- `ts/src/contracts.ts`

Purpose:

- Define control-plane-owned notification request, delivery, polling-status, magic-link detail, and decision payloads shared by internal callers and UI consumers
- Support one-way message delivery and trade approval requests without duplicating the existing trade-desk order-intent contract
- Preserve the boundary that notification contracts define payload semantics only; runtime delivery, token storage, audit persistence, and trade release logic belong to `asset-allocation-control-plane`

Key design note:

Trade approval payloads carry an existing `TradeOrderPreviewRequest` plus release identifiers such as `previewId`, `orderHash`, and `placeIdempotencyKey`. Approval does not bypass trade-desk controls; the control plane remains responsible for revalidating freshness, kill switches, policy, and idempotency before releasing a trade.

### 4.8 Job Metadata and Strategy Publication Contracts

Owned by:

- `python/asset_allocation_contracts/job_metadata.py`
- `python/asset_allocation_contracts/results.py`
- `python/asset_allocation_contracts/strategy_publication.py`
- `schemas/runtime-job-metadata.schema.json`
- `schemas/results-reconcile-request.schema.json`
- `schemas/results-reconcile-response.schema.json`
- `schemas/strategy-publication-reconcile-signal-request.schema.json`
- `schemas/strategy-publication-reconcile-signal-response.schema.json`
- `ts/src/contracts.ts`

Purpose:

- Define the additive system-health taxonomy fields `jobCategory`, `jobKey`, `jobRole`, `triggerOwner`, `metadataSource`, and `metadataStatus`
- Keep strategy-compute jobs, medallion data-pipeline jobs, and operational-support jobs distinct without relying on job-name substring inference
- Define the strict results reconcile request and response shared by `results-reconcile-job`, runtime-common, and the control-plane internal API
- Define the durable regime publication reconcile signal request and response shared between jobs and the control-plane internal API
- Preserve server ownership of reconcile signal state: producers send typed publication metadata, while the control plane assigns `pending`, `processed`, or `error`

Key design note:

`strategy-compute` is a workflow category, not a medallion layer. `gold-regime-job` remains the ACA resource name and may write gold outputs, but its contract category is `strategy-compute`. `platinum-rankings-job` follows the same rule for platinum outputs.

### 4.8 UI Runtime Config Contract

Owned by:

- `python/asset_allocation_contracts/ui_config.py`
- `schemas/ui-runtime-config.schema.json`
- `ts/src/contracts.ts`

Purpose:

- Define the browser bootstrap/runtime config surface for API base URL and OIDC/auth settings, including the derived post-logout completion URI
- Normalize scope/audience list handling

### 4.9 Auth Session Contract

Owned by:

- `python/asset_allocation_contracts/ui_config.py`
- `schemas/auth-session-status.schema.json`
- `ts/src/contracts.ts`

Purpose:

- Define the shared response payload for the control-plane `GET /api/auth/session` surface
- Give the UI a typed auth/authz probe that is distinct from general system-health data
- Keep the control-plane, UI, and any future non-browser consumer aligned on the same minimal session summary fields

### 4.10 Shared Finance and Path Constants

Owned by:

- `python/asset_allocation_contracts/finance.py`
- `python/asset_allocation_contracts/paths.py`
- `python/asset_allocation_contracts/market_history.py`

Purpose:

- Provide stable shared constants and path-construction rules used across runtime repos
- Keep storage/domain naming conventions and finance subdomain mappings from drifting between consumers

These are still contract surfaces even though they are constants rather than large object models.

### 4.11 Stock Screener Contracts

Owned by:

- `python/asset_allocation_contracts/stock_screener.py`
- `schemas/stock-screener-*.schema.json`
- `ts/src/contracts.ts`

Purpose:

- Define the shared request and response payload for the control-plane stock screener API consumed by the UI
- Keep server-side filtering, sort keys, coverage flags, facets, and active filter echo aligned across control-plane and browser consumers
- Preserve the read-only research boundary: these contracts describe screening data and metadata, not trading actions or watchlist mutation commands

### 4.11.1 Intraday And Live Currency Contracts

Owned by:

- `python/asset_allocation_contracts/intraday.py`
- `schemas/currency-intraday-*.schema.json`
- `schemas/live-currency-price-*.schema.json`
- `ts/src/contracts.ts`

Purpose:

- Define shared currency intraday bar payloads and live currency price payloads consumed by control-plane and UI.
- Normalize supported BTC/USD symbol forms to canonical `BTCUSD` while preserving provider diagnostics such as `providerPair` and `providerChannel`.
- Keep the live stream display boundary explicit: `LiveCurrencyPriceTick`, `LiveCurrencyPriceSnapshot`, and `LiveMarketPriceStatus` describe display/monitoring state only, not persistence, strategy triggers, order routing, or medallion ingestion.

### 4.12 Deployment Provenance Contracts

Owned by:

- `python/asset_allocation_contracts/deployment_provenance.py`
- `schemas/deployment-provenance-view.schema.json`
- `ts/src/contracts.ts`

Purpose:

- Define the shared `/api/system/status-view` deployment provenance payload consumed by UI and produced by control-plane.
- Carry live Azure resource deployment evidence, including resource name/type, environment, repo, image digest, source SHA, release run, deploy run, latest successful run, checked time, links, warnings, and error state.
- Keep deployed-version consistency semantics explicit with `consistent`, `stale`, `mismatch`, `running`, `unknown`, `unavailable`, and `error`.
- Preserve the operational source-of-truth rule: live Azure resource provenance is authoritative; Azure DevOps pipeline runs are comparison evidence.

### 4.13 Release and Env/Config Surfaces

Owned by:

- `azure-pipelines/ci.yml`
- `azure-pipelines/security.yml`
- `azure-pipelines/release.yml`
- `.env.template`
- `docs/ops/env-contract.csv`
- `docs/ops/env-contract.md`
- `scripts/setup-env.ps1`
- `scripts/sync-all-to-azure-devops.ps1`

Purpose:

- Define what makes the repo safe to build, publish, and operate
- Define which Azure DevOps variables, feeds, and environment gates are required
- Define how local env bootstrap becomes Azure DevOps configuration
- Define downstream release-manifest handoff behavior after release

### Primary Evidence

- `python/asset_allocation_contracts/strategy.py`
- `python/asset_allocation_contracts/ranking.py`
- `python/asset_allocation_contracts/regime.py`
- `python/asset_allocation_contracts/backtest.py`
- `python/asset_allocation_contracts/broker_accounts.py`
- `python/asset_allocation_contracts/options.py`
- `python/asset_allocation_contracts/job_metadata.py`
- `python/asset_allocation_contracts/strategy_publication.py`
- `python/asset_allocation_contracts/trade_desk.py`
- `python/asset_allocation_contracts/ui_config.py`
- `python/asset_allocation_contracts/deployment_provenance.py`
- `python/asset_allocation_contracts/stock_screener.py`
- `python/asset_allocation_contracts/intraday.py`
- `python/asset_allocation_contracts/finance.py`
- `python/asset_allocation_contracts/paths.py`
- `python/asset_allocation_contracts/market_history.py`
- `ts/src/contracts.ts`
- `schemas/deployment-provenance-view.schema.json`
- `schemas/live-currency-price-tick.schema.json`
- `schemas/live-currency-price-snapshot.schema.json`
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

`azure-pipelines/ci.yml` is the required validation path.

It enforces:

- Python and TypeScript version parity
- Schema export with no drift in `schemas/`
- Python contract tests
- Python distribution build
- TypeScript typecheck and package pack

It runs on the self-hosted `local-docker-agents` pool and requires the Linux contracts toolchain capabilities documented in `docs/ops/azure-devops-ci-cd.md`.

### 5.3 Scheduled Security Audit

`azure-pipelines/security.yml` runs on pull requests, `main`, and a weekly schedule.

It audits:

- Python dependencies using `pip-audit`
- TypeScript dependencies using `pnpm audit`

Artifacts from those audits are uploaded for review.

### 5.4 Release by Manual Dispatch

`azure-pipelines/release.yml` runs manually against `main` and is gated by the `prod-package-release` environment.

The release workflow reads the committed stable semver from `python/pyproject.toml` and `ts/package.json`, verifies that both manifests match exactly, and publishes that same version for both package ecosystems.

It performs:

1. Version parity and stable semver validation
2. Schema export with no drift
3. Python contract tests
4. Python package build
5. TypeScript typecheck and package tarball build
6. Python package publish to Azure Artifacts
7. TypeScript package publish to Azure Artifacts
8. Release manifest generation
9. Retained `contracts-release` artifact publication

Release intentionally stays on Microsoft-hosted `ubuntu-latest` until the local Docker agent pool has proven uptime, patching, monitoring, and repeatability.

### 5.5 Release Manifest Interface

`release.yml` writes `artifacts/release-manifest.json` with this shape:

```json
{
  "schema_version": 1,
  "ci_provider": "azure-devops",
  "repo": "asset-allocation-contracts",
  "source_repo": "<Azure Repos repository name>",
  "source_sha": "<release commit sha>",
  "build_id": "<Azure Pipelines build id>",
  "pipeline_definition_id": "<Azure Pipelines definition id>",
  "run_id": "<Azure Pipelines run id>",
  "run_attempt": "<Azure Pipelines build number>",
  "artifact_uri": "<Azure Pipelines artifact URL>",
  "artifact_kind": "contracts",
  "artifact_ref": ["<artifact path>"],
  "artifact_hashes": {
    "<artifact path>": "<sha256>"
  },
  "package_version": "<shared version>",
  "version_matrix": {
    "contracts": "<shared version>",
    "runtime_common": null,
    "control_plane": null,
    "jobs": null,
    "ui": null
  }
}
```

This is a public operational artifact and must remain intentional if changed.

### 5.6 Downstream Version Handoff

The release workflow publishes the retained `contracts-release` artifact. Downstream automation should consume the exact `package_version`, `source_sha`, and artifact hashes from `release-manifest.json`.

Current downstream consumers remain:

- Jobs
- UI

Any change to the manifest shape or target consumer list is a release-contract change and must be documented and coordinated with consumers.

### 5.7 Cross-Repo Compatibility Gate

`scripts/compatibility_gate.ps1` is the smoke gate for breaking or risky contract changes.

It validates this repo locally, then shells into sibling repos and runs selected control-plane, jobs, and UI validations. That makes compatibility a first-class design concern even though most of the checks run outside this repo.

### Primary Evidence

- `azure-pipelines/ci.yml`
- `azure-pipelines/security.yml`
- `azure-pipelines/release.yml`
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

### 6.4 Release and Handoff Invariants

- Release artifacts must include both Python and TypeScript outputs.
- Python and TypeScript releases publish to Azure Artifacts from Azure Pipelines.
- `release-manifest.json` shape is part of the public operating contract.
- Downstream version-handoff semantics and target consumer set are part of the public operating contract.

### 6.5 Env/Config Invariants

- Workflow variable and secret references must be documented in `docs/ops/env-contract.csv`.
- `.env.template`, `docs/ops/env-contract.csv`, `scripts/setup-env.ps1`, `scripts/sync-all-to-azure-devops.ps1`, and workflow references must stay synchronized.
- `.env.web` carries Python registry and retained legacy dispatch credentials only; TypeScript publish auth is not stored there.
- `DISPATCH_APP_PRIVATE_KEY` is retained for the legacy GitHub workflow surface and is loaded from a PEM file path with literal `\n` escapes.

### 6.6 Scope Invariants

- Do not expand this repo into a runtime or deployment repo.
- Keep runtime-specific behavior in consumer repos unless it is truly shared contract logic.
- Shared compatibility shims are allowed only when they are explicit, intentional, and documented.

### Primary Evidence

- `python/pyproject.toml`
- `ts/package.json`
- `azure-pipelines/ci.yml`
- `azure-pipelines/security.yml`
- `azure-pipelines/release.yml`
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

- Cross-repo compatibility is not enforced by Azure Pipelines in this repo
- TypeScript-to-Python semantic parity is not automatically diffed
- Release manifest and downstream handoff shapes are not directly unit-tested as standalone contracts

### Primary Evidence

- `azure-pipelines/ci.yml`
- `azure-pipelines/security.yml`
- `tests/python/test_contract_models.py`
- `tests/test_env_contract.py`
- `scripts/compatibility_gate.ps1`

## 8. Governance Rules

Future agents must treat the following files as one governance unit:

- `azure-pipelines/*.yml`
- `.env.template`
- `docs/ops/env-contract.csv`
- `docs/ops/env-contract.md`
- `scripts/setup-env.ps1`
- `scripts/sync-all-to-azure-devops.ps1`
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
- `azure-pipelines/release.yml`
- `docs/ops/env-contract.csv`
- `scripts/setup-env.ps1`
- `scripts/sync-all-to-azure-devops.ps1`

## 9. Known Current Drift

This section records current mismatches observed during verification. It exists so future agents do not mistake repo drift for intended design.

### 9.1 Committed Release Version Source

Observed:

- `azure-pipelines/release.yml` reads the committed version from `python/pyproject.toml` and `ts/package.json`
- the committed version must be stable semver and identical across Python and TypeScript
- Azure Artifacts is the current Python and TypeScript package publication target

Interpretation:

The steady-state contracts release path is committed-manifest semver publishing. Future agents should treat the checked-in Python and TypeScript versions as both CI alignment state and the publish artifact state for manual releases.

### 9.2 Off-Repo Compatibility Gate

Observed:

- `scripts/compatibility_gate.ps1` is an important release-safety mechanism
- It depends on sibling repos and local checkout layout
- It is not currently enforced inside Azure Pipelines for this repo

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

- `azure-pipelines/release.yml`
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
- The downstream version-handoff shape or target-repo list changes
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
- `python/asset_allocation_contracts/stock_screener.py`
- `python/asset_allocation_contracts/deployment_provenance.py`
- `python/asset_allocation_contracts/strategy.py`
- `python/asset_allocation_contracts/ui_config.py`
- `python/scripts/export_schemas.py`
- `ts/package.json`
- `ts/src/contracts.ts`
- `ts/src/index.ts`
- `schemas/deployment-provenance-view.schema.json`
- `azure-pipelines/ci.yml`
- `azure-pipelines/security.yml`
- `azure-pipelines/release.yml`
- `azure-pipelines/*.yml` (legacy surface; not canonical)
- `scripts/compatibility_gate.ps1`
- `scripts/setup-env.ps1`
- `scripts/sync-all-to-azure-devops.ps1`
- `docs/ops/env-contract.csv`
- `docs/ops/env-contract.md`
- `tests/python/test_contract_models.py`
- `tests/test_env_contract.py`
- `CODEOWNERS`
- `.github/CODEOWNERS`
