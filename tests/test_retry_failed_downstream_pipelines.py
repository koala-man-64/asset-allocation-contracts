from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "retry_failed_downstream_pipelines.py"


spec = importlib.util.spec_from_file_location("retry_failed_downstream_pipelines", SCRIPT_PATH)
assert spec is not None
retry_module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = retry_module
spec.loader.exec_module(retry_module)


class FakeClient:
    def __init__(self) -> None:
        self.definitions = {
            "failed-ci": 1,
            "succeeded-security": 2,
            "running-quality": 3,
            "empty-ci": 4,
        }
        self.runs: dict[int, dict[str, Any] | None] = {
            1: {"id": 101, "status": "completed", "result": "failed"},
            2: {"id": 202, "status": "completed", "result": "succeeded"},
            3: {"id": 303, "status": "inProgress", "result": None},
            4: None,
        }
        self.queued: list[dict[str, Any]] = []

    def get_definition_id(self, pipeline_name: str) -> int:
        return self.definitions[pipeline_name]

    def get_latest_run(self, definition_id: int, branch: str) -> dict[str, Any] | None:
        assert branch == "refs/heads/main"
        return self.runs[definition_id]

    def queue_run(
        self,
        *,
        definition_id: int,
        branch: str,
        variables: dict[str, str],
    ) -> dict[str, Any]:
        self.queued.append(
            {"definition_id": definition_id, "branch": branch, "variables": variables}
        )
        return {"id": 9000 + definition_id}


def test_retries_only_failed_latest_main_runs() -> None:
    client = FakeClient()

    decisions = retry_module.retry_failed_pipelines(
        client=client,
        pipeline_names=[
            "failed-ci",
            "succeeded-security",
            "running-quality",
            "empty-ci",
        ],
        branch="refs/heads/main",
        release_build_id="1857",
        release_build_number="contracts-release-20260515.6",
        release_source_version="abc123",
    )

    assert [decision.action for decision in decisions] == [
        "queued",
        "skipped",
        "skipped",
        "skipped",
    ]
    assert client.queued == [
        {
            "definition_id": 1,
            "branch": "refs/heads/main",
            "variables": {
                "RETRIED_BY_CONTRACTS_RELEASE_BUILD_ID": "1857",
                "RETRIED_BY_CONTRACTS_RELEASE_BUILD_NUMBER": "contracts-release-20260515.6",
                "RETRIED_BY_CONTRACTS_RELEASE_SOURCE_VERSION": "abc123",
                "RETRIED_FAILED_RUN_ID": "101",
            },
        }
    ]


def test_release_pipeline_runs_retry_stage_after_release_without_waiting() -> None:
    release = (REPO_ROOT / "azure-pipelines" / "release.yml").read_text(encoding="utf-8")

    assert "- stage: RetryFailedDownstreamValidation" in release
    assert "dependsOn: Release" in release
    assert "condition: succeeded('Release')" in release
    assert "python scripts/retry_failed_downstream_pipelines.py" in release
    assert "SYSTEM_ACCESSTOKEN: $(System.AccessToken)" in release
    assert "asset-allocation-runtime-common-ci" in release
    assert "asset-allocation-jobs-quality" in release
    assert "asset-allocation-ui-contracts-compat" in release
    assert "az pipelines runs show" not in release
