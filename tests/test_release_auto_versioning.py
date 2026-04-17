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
    release_workflow = (repo_root() / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")

    assert "workflow_dispatch:" in release_workflow
    assert "push:" not in release_workflow
    assert "Resolve committed release version" in release_workflow
    assert "Compute release version" not in release_workflow
    assert "Stage generated release version" not in release_workflow
    assert "scripts/compute_release_version.py" not in release_workflow
    assert "scripts/stage_release_version.py" not in release_workflow
    assert 'npm publish "${tarballs[0]}" --access public --provenance' in release_workflow
    assert "--tag dev" not in release_workflow


def test_release_workflow_checks_both_registries_before_publish() -> None:
    release_workflow = (repo_root() / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")

    assert "Check npm version availability" in release_workflow
    assert "Check Python version availability" in release_workflow
    assert "vars.PYTHON_PACKAGE_INDEX_URL" in release_workflow
    assert "Bump python/pyproject.toml and ts/package.json before rerunning release.yml." in release_workflow
