# AGENTS.md instructions for C:\Users\rdpro\Projects\asset-allocation-contracts

## Source of Truth

Repo-local agents live under `.codex/skills`. Use that directory as the authoritative repo-local agent inventory for this repository.

## Service and Process Defaults

Do not add feature flags, enable/disable toggles, kill switches, dry-run gates, rollout flags, or env-controlled process gates unless the user explicitly requests that control.

Services, jobs, workers, routes, integrations, and shared contracts for operational processes are enabled by default when added. Missing credentials, identity, endpoints, roles, or provider configuration should fail fast instead of silently disabling behavior.

If temporary rollout control is explicitly requested, include a named owner, expiry or removal condition, tests, and documentation in the same change.

Do not remove UI component disabled states, React Query execution options, validation booleans, or domain business-rule `enabled` fields unless they are actually service or process gates.

## Cross-Repo Contract Ownership

This repo owns shared cross-repo data contract authoring for the asset-allocation repo family.

A change counts as shared contract authoring when it adds, removes, renames, retypes, or changes validation, serialization, or schema semantics for:

- shared API request and response payloads
- serialization keys or schema-backed shapes consumed across repos
- types exported through `asset-allocation-contracts` or `@asset-allocation/contracts`

This rule does not apply to:

- repo-local build, release, or documentation metadata
- implementation-only helpers not exported as shared contracts
- consumer-repo adoption code, adapters, or migrations

Required routing:

- Author shared contract shape changes in this repo first.
- Use `docs/architecture/master-design.md` as the contract process reference.
- Consumer repos should only plan adoption, adapters, migration, or version-bump work until this repo's contract work item exists and the target version is planned or published.
- When removing platform, service, process, or runtime enablement fields, update Python models, TypeScript models, generated schemas, examples, and consumer adoption work together.

Required planning decision:

- State either `This is a contracts-authoring change.` or `This is local-only and does not require consumer adoption.`

Default:

- If the shape may be shared and ownership is unclear after checking local evidence, keep the authoring work in this repo and create consumer-repo adoption work separately.

## How to Use Agents

- Discovery: repo-local agents live under `.codex/skills`.
- Trigger rules: if the user names an agent or the task clearly matches one, use the minimal set that covers the request.
- Coordination: for planning and workflow decisions, treat `delivery-orchestrator-agent` as the authoritative routing surface and `gateway-bookkeeper` as the Azure DevOps tracking surface.
- Safety: do not mark consumer adoption done until the relevant contract version is planned or published.
