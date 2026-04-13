from __future__ import annotations

import importlib.util
import json
import sys
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


def test_compute_release_version_reads_committed_manifest_version(tmp_path: Path) -> None:
    module = load_module("compute_release_version", "scripts/compute_release_version.py")
    write_release_manifests(tmp_path)

    version = module.resolve_release_version(tmp_path)

    assert version == "0.1.2"
    module.validate_release_version(version)


def test_compute_release_version_requires_python_and_typescript_parity(tmp_path: Path) -> None:
    module = load_module("compute_release_version_mismatch", "scripts/compute_release_version.py")
    write_release_manifests(tmp_path)
    (tmp_path / "ts" / "package.json").write_text(
        json.dumps(
            {
                "name": "@asset-allocation/contracts",
                "version": "0.1.3",
                "type": "module",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="must match before release"):
        module.resolve_release_version(tmp_path)


def test_compute_release_version_requires_stable_semver(tmp_path: Path) -> None:
    module = load_module("compute_release_version_invalid", "scripts/compute_release_version.py")
    write_release_manifests(tmp_path)
    (tmp_path / "python" / "pyproject.toml").write_text(
        "\n".join(
            [
                "[build-system]",
                'requires = ["setuptools>=69", "wheel"]',
                'build-backend = "setuptools.build_meta"',
                "",
                "[project]",
                'name = "asset-allocation-contracts"',
                'version = "2026.4.13-dev.1001"',
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "ts" / "package.json").write_text(
        json.dumps(
            {
                "name": "@asset-allocation/contracts",
                "version": "2026.4.13-dev.1001",
                "type": "module",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="stable semver"):
        module.resolve_release_version(tmp_path)


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


def test_release_workflow_is_manual_and_uses_committed_manifest_version() -> None:
    release_workflow = (repo_root() / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")

    assert "workflow_dispatch:" in release_workflow
    assert "push:" not in release_workflow
    assert "Resolve release version" in release_workflow
    assert "python scripts/compute_release_version.py --repo-root ." in release_workflow
    assert "Stage generated release version" not in release_workflow
    assert "python scripts/stage_release_version.py" not in release_workflow
