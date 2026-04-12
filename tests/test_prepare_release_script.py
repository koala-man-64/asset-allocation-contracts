from __future__ import annotations

import subprocess
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def powershell_exe() -> str:
    for candidate in ("pwsh", "powershell"):
        try:
            subprocess.run(
                [candidate, "-NoProfile", "-Command", "$PSVersionTable.PSVersion.ToString()"],
                check=True,
                capture_output=True,
                text=True,
            )
            return candidate
        except Exception:
            continue
    raise AssertionError("PowerShell executable not found for prepare-release script test")


def write_release_files(root: Path) -> None:
    python_dir = root / "python"
    ts_dir = root / "ts"
    python_dir.mkdir()
    ts_dir.mkdir()
    (python_dir / "pyproject.toml").write_text(
        "\n".join(
            [
                "[project]",
                'name = "asset-allocation-contracts"',
                'version = "0.1.0"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    (ts_dir / "package.json").write_text(
        "\n".join(
            [
                "{",
                '  "name": "@asset-allocation/contracts",',
                '  "version": "0.1.0"',
                "}",
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_prepare_release_updates_both_version_files(tmp_path: Path) -> None:
    write_release_files(tmp_path)
    script = repo_root() / "scripts" / "prepare-release.ps1"
    completed = subprocess.run(
        [
            powershell_exe(),
            "-NoProfile",
            "-File",
            str(script),
            "-RepoRoot",
            str(tmp_path),
            "-Version",
            "1.2.3",
        ],
        cwd=repo_root(),
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Updated release version to 1.2.3" in completed.stdout
    assert 'version = "1.2.3"' in (tmp_path / "python" / "pyproject.toml").read_text(encoding="utf-8")
    assert '"version": "1.2.3"' in (tmp_path / "ts" / "package.json").read_text(encoding="utf-8")


def test_prepare_release_dry_run_does_not_modify_files(tmp_path: Path) -> None:
    write_release_files(tmp_path)
    script = repo_root() / "scripts" / "prepare-release.ps1"
    completed = subprocess.run(
        [
            powershell_exe(),
            "-NoProfile",
            "-File",
            str(script),
            "-RepoRoot",
            str(tmp_path),
            "-Version",
            "2.0.0",
            "-DryRun",
        ],
        cwd=repo_root(),
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Dry run: no files were changed." in completed.stdout
    assert 'version = "0.1.0"' in (tmp_path / "python" / "pyproject.toml").read_text(encoding="utf-8")
    assert '"version": "0.1.0"' in (tmp_path / "ts" / "package.json").read_text(encoding="utf-8")
