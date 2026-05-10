from __future__ import annotations

import json
import re
from pathlib import Path

import tomllib


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_contracts_manifests_use_identical_stable_semver() -> None:
    pyproject = tomllib.loads((repo_root() / "python" / "pyproject.toml").read_text(encoding="utf-8"))
    package_json = json.loads((repo_root() / "ts" / "package.json").read_text(encoding="utf-8"))

    py_version = pyproject["project"]["version"]
    ts_version = package_json["version"]

    assert py_version == ts_version
    assert re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", py_version)


def test_release_workflow_is_manual_and_uses_committed_manifest_version() -> None:
    release_workflow = (repo_root() / "azure-pipelines" / "release.yml").read_text(encoding="utf-8")

    assert "trigger: none" in release_workflow
    assert "pr: none" in release_workflow
    assert "condition: eq(variables['Build.SourceBranch'], 'refs/heads/main')" in release_workflow
    assert "Resolve committed release version" in release_workflow
    assert "Compute release version" not in release_workflow
    assert "Stage generated release version" not in release_workflow
    assert "scripts/compute_release_version.py" not in release_workflow
    assert "scripts/stage_release_version.py" not in release_workflow
    assert 'npm publish "${tarballs[0]}" --registry "$(NPM_FEED_REGISTRY_URL)" --userconfig "${npm_config}"' in release_workflow
    assert "--tag dev" not in release_workflow


def test_release_workflow_checks_both_registries_before_publish() -> None:
    release_workflow = (repo_root() / "azure-pipelines" / "release.yml").read_text(encoding="utf-8")

    assert "TwineAuthenticate@1" in release_workflow
    assert 'npm view "@asset-allocation/contracts@${version}" version' in release_workflow
    assert "already exists in Azure Artifacts; skipping" in release_workflow


def test_release_workflow_no_longer_dispatches_github_consumers() -> None:
    release_workflow = (repo_root() / "azure-pipelines" / "release.yml").read_text(encoding="utf-8")

    assert "CONTROL_" "PLANE_REPOSITORY" not in release_workflow
    assert "repository_dispatch" not in release_workflow
    assert "contracts_released" not in release_workflow
    assert "artifact: contracts-release" in release_workflow
