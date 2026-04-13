from __future__ import annotations

import importlib.util
import json
import sys
from datetime import date
from pathlib import Path

import pytest


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_module(module_name: str, relative_path: str):
    script_path = repo_root() / relative_path
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_release_manifests(root: Path) -> None:
    python_dir = root / "python"
    ts_dir = root / "ts"
    python_dir.mkdir(parents=True)
    ts_dir.mkdir(parents=True)
    (python_dir / "pyproject.toml").write_text(
        "\n".join(
            [
                "[build-system]",
                'requires = ["setuptools>=69", "wheel"]',
                'build-backend = "setuptools.build_meta"',
                "",
                "[project]",
                'name = "asset-allocation-contracts"',
                'version = "0.1.2"',
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (ts_dir / "package.json").write_text(
        json.dumps(
            {
                "name": "@asset-allocation/contracts",
                "version": "0.1.2",
                "type": "module",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def test_compute_release_version_uses_expected_shape() -> None:
    module = load_module("compute_release_version", "scripts/compute_release_version.py")

    version = module.compute_release_version(date(2026, 4, 12), 157, 1)

    assert version == "2026.4.12-dev.157001"
    module.validate_release_version(version)


def test_compute_release_version_is_deterministic_for_same_inputs() -> None:
    module = load_module("compute_release_version_same_inputs", "scripts/compute_release_version.py")

    first = module.compute_release_version(date(2026, 4, 12), 157, 2)
    second = module.compute_release_version(date(2026, 4, 12), 157, 2)

    assert first == second == "2026.4.12-dev.157002"


def test_compute_release_version_changes_with_run_attempt() -> None:
    module = load_module("compute_release_version_attempts", "scripts/compute_release_version.py")

    first_attempt = module.compute_release_version(date(2026, 4, 12), 157, 1)
    second_attempt = module.compute_release_version(date(2026, 4, 12), 157, 2)

    assert first_attempt == "2026.4.12-dev.157001"
    assert second_attempt == "2026.4.12-dev.157002"
    assert first_attempt != second_attempt


def test_stage_release_version_updates_both_manifests(tmp_path: Path) -> None:
    module = load_module("stage_release_version", "scripts/stage_release_version.py")
    write_release_manifests(tmp_path)

    module.stage_release_version(tmp_path, "2026.4.12-dev.157001")

    pyproject_text = (tmp_path / "python" / "pyproject.toml").read_text(encoding="utf-8")
    package_json = json.loads((tmp_path / "ts" / "package.json").read_text(encoding="utf-8"))
    assert 'version = "2026.4.12-dev.157001"' in pyproject_text
    assert package_json["version"] == "2026.4.12-dev.157001"


def test_stage_release_version_fails_when_project_version_is_not_unique(tmp_path: Path) -> None:
    module = load_module("stage_release_version_invalid", "scripts/stage_release_version.py")
    python_dir = tmp_path / "python"
    ts_dir = tmp_path / "ts"
    python_dir.mkdir(parents=True)
    ts_dir.mkdir(parents=True)
    (python_dir / "pyproject.toml").write_text(
        "\n".join(
            [
                "[project]",
                'name = "asset-allocation-contracts"',
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (ts_dir / "package.json").write_text(
        json.dumps({"name": "@asset-allocation/contracts", "version": "0.1.2"}, indent=2) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Expected exactly one \\[project\\] version entry"):
        module.stage_release_version(tmp_path, "2026.4.12-dev.157001")


def test_release_workflow_is_manual_and_stages_generated_version() -> None:
    release_workflow = (repo_root() / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")

    assert "workflow_dispatch:" in release_workflow
    assert "push:" not in release_workflow
    assert "Compute release version" in release_workflow
    assert "python scripts/compute_release_version.py" in release_workflow
    assert "Stage generated release version" in release_workflow
    assert 'python scripts/stage_release_version.py --repo-root . --version "${CONTRACTS_VERSION}"' in release_workflow
    assert "Resolve contracts version" not in release_workflow
