# Azure DevOps CI/CD

This repo now publishes contract packages through Azure Pipelines and Azure Artifacts.

## Pipelines

- `azure-pipelines/ci.yml`: PR and `main` validation for Python contracts, schema drift, TypeScript typecheck, and package packing.
- `azure-pipelines/security.yml`: PR, `main`, and weekly dependency audits.
- `azure-pipelines/release.yml`: gated manual release to the `prod-package-release` environment.

## Package Feed

Use the project-scoped feed `asset-allocation-packages`.

- npm registry: `https://pkgs.dev.azure.com/rdprokes/AdaptiveAssetAllocation/_packaging/asset-allocation-packages/npm/registry/`
- PyPI feed: `AdaptiveAssetAllocation/asset-allocation-packages`

The pipelines authenticate with `npmAuthenticate@0` and `TwineAuthenticate@1`. Do not add `NPMRC`, `PYTHON_PUBLISH_USERNAME`, `PYTHON_PUBLISH_PASSWORD`, or `npm.pkg.github.com` secrets for Azure DevOps.

## Release Manifest

The release pipeline publishes `contracts-release` with `release-manifest.json`, Python distributions, and the TypeScript tarball. Retain the pipeline artifact for at least 90 days in Azure DevOps pipeline settings.
