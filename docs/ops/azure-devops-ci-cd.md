# Azure DevOps CI/CD

This repo now publishes contract packages through Azure Pipelines and Azure Artifacts.

## Pipelines

- `azure-pipelines/ci.yml`: PR and `main` validation for Python contracts, schema drift, TypeScript typecheck, and package packing. Runs on `local-docker-agents`.
- `azure-pipelines/security.yml`: PR, `main`, and weekly dependency audits. Runs on `local-docker-agents`.
- `azure-pipelines/release.yml`: gated manual release to the `prod-package-release` environment. Stays on Microsoft-hosted `ubuntu-latest`.

## Agent Pools

CI and security require the self-hosted `local-docker-agents` pool with a Linux contracts toolchain image. The agent image must advertise these capabilities:

- `CONTRACTS_TOOLCHAIN=true`
- `CONTRACTS_PYTHON=3.14`
- `CONTRACTS_NODE=20`
- `CONTRACTS_PNPM=10.28.1`

The release pipeline intentionally stays hosted because package publication should not depend on a local workstation runner until the local pool has proven uptime, patching, monitoring, and repeatability.

Do not mount the host Docker socket for PR or `main` validation. Docker socket mode gives pipeline code control over the host daemon and should be reserved for explicitly trusted pipelines.

## Package Feed

Use the project-scoped feed `asset-allocation-packages`.

- npm registry: `https://pkgs.dev.azure.com/rdprokes/AdaptiveAssetAllocation/_packaging/asset-allocation-packages/npm/registry/`
- PyPI feed: `AdaptiveAssetAllocation/asset-allocation-packages`

The pipelines authenticate with `npmAuthenticate@0` and `TwineAuthenticate@1`. Do not add `NPMRC`, `PYTHON_PUBLISH_USERNAME`, `PYTHON_PUBLISH_PASSWORD`, or `npm.pkg.github.com` secrets for Azure DevOps.

## Release Manifest

The release pipeline publishes `contracts-release` with `release-manifest.json`, Python distributions, and the TypeScript tarball. Retain the pipeline artifact for at least 90 days in Azure DevOps pipeline settings.
