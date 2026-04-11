from __future__ import annotations

import csv
import re
import subprocess
from pathlib import Path


WORKFLOW_VAR_PATTERN = re.compile(r"\bvars\.([A-Z][A-Z0-9_]+)\b")
WORKFLOW_SECRET_PATTERN = re.compile(r"\bsecrets\.([A-Z][A-Z0-9_]+)\b")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def contract_rows() -> list[dict[str, str]]:
    path = repo_root() / "docs" / "ops" / "env-contract.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def contract_map() -> dict[str, dict[str, str]]:
    return {row["name"]: row for row in contract_rows()}


def env_keys(path: Path) -> set[str]:
    keys: set[str] = set()
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        keys.add(line.split("=", 1)[0].strip())
    return keys


def workflow_refs(pattern: re.Pattern[str]) -> set[str]:
    refs: set[str] = set()
    for path in (repo_root() / ".github" / "workflows").glob("*.yml"):
        refs.update(pattern.findall(path.read_text(encoding="utf-8")))
    return refs


def powershell_exe() -> str:
    for candidate in ("pwsh", "powershell"):
        try:
            subprocess.run([candidate, "-NoProfile", "-Command", "$PSVersionTable.PSVersion.ToString()"], check=True, capture_output=True, text=True)
            return candidate
        except Exception:
            continue
    raise AssertionError("PowerShell executable not found for setup-env dry-run test")


def test_template_matches_contract_surface() -> None:
    assert env_keys(repo_root() / ".env.template") == set(contract_map())


def test_workflow_refs_are_documented() -> None:
    contract = contract_map()
    for name in workflow_refs(WORKFLOW_VAR_PATTERN):
        assert name in contract
        assert contract[name]["github_storage"] == "var"

    for name in workflow_refs(WORKFLOW_SECRET_PATTERN):
        assert name in contract
        assert contract[name]["github_storage"] == "secret"


def test_contracts_repo_has_bootstrap_scripts_and_no_azure_provisioner() -> None:
    scripts_dir = repo_root() / "scripts"
    assert (scripts_dir / "setup-env.ps1").exists()
    assert (scripts_dir / "sync-all-to-github.ps1").exists()
    assert not (scripts_dir / "provision_azure.ps1").exists()


def test_setup_env_dry_run_reports_sources_without_prompting(tmp_path: Path) -> None:
    script = repo_root() / "scripts" / "setup-env.ps1"
    env_path = tmp_path / ".env.web"
    completed = subprocess.run(
        [
            powershell_exe(),
            "-NoProfile",
            "-File",
            str(script),
            "-EnvFilePath",
            str(env_path),
            "-DryRun",
        ],
        cwd=repo_root(),
        check=True,
        capture_output=True,
        text=True,
    )
    stdout = completed.stdout
    assert "source=git" in stdout or "source=default" in stdout
    assert "prompt_required=" in stdout


def test_setup_env_reads_dispatch_private_key_from_file(tmp_path: Path) -> None:
    script = repo_root() / "scripts" / "setup-env.ps1"
    env_path = tmp_path / ".env.web"
    env_path.write_text(
        "\n".join(
            [
                "CONTROL_PLANE_REPOSITORY=owner/asset-allocation-control-plane",
                "JOBS_REPOSITORY=owner/asset-allocation-jobs",
                "UI_REPOSITORY=owner/asset-allocation-ui",
                "DISPATCH_APP_ID=123456",
                "PYTHON_PUBLISH_REPOSITORY_URL=https://upload.pypi.org/legacy/",
                "DISPATCH_APP_PRIVATE_KEY=",
                "PYTHON_PUBLISH_USERNAME=__token__",
                "PYTHON_PUBLISH_PASSWORD=test-password",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    private_key_path = tmp_path / "dispatch-app.pem"
    private_key_path.write_text(
        "-----BEGIN RSA PRIVATE KEY-----\nkey-line\n-----END RSA PRIVATE KEY-----\n",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            powershell_exe(),
            "-NoProfile",
            "-File",
            str(script),
            "-EnvFilePath",
            str(env_path),
            "-DispatchAppPrivateKeyPath",
            str(private_key_path),
        ],
        cwd=repo_root(),
        check=True,
        capture_output=True,
        text=True,
    )

    assert "source=file" in completed.stdout
    env_contents = env_path.read_text(encoding="utf-8")
    assert (
        "DISPATCH_APP_PRIVATE_KEY=-----BEGIN RSA PRIVATE KEY-----\\nkey-line\\n-----END RSA PRIVATE KEY-----"
        in env_contents
    )
