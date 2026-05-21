from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timezone
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
            "old-failed-release": 5,
        }
        self.runs: dict[int, list[dict[str, Any]]] = {
            1: [{"id": 101, "status": "completed", "result": "failed"}],
            2: [{"id": 202, "status": "completed", "result": "succeeded"}],
            3: [
                {"id": 303, "status": "inProgress", "result": None},
                {"id": 302, "status": "completed", "result": "failed"},
            ],
            4: [],
            5: [],
        }
        self.queries: list[dict[str, Any]] = []
        self.queued: list[dict[str, Any]] = []

    def get_definition_id(self, pipeline_name: str) -> int:
        return self.definitions[pipeline_name]

    def get_recent_runs(
        self,
        definition_id: int,
        branch: str,
        min_time: datetime,
        top: int,
    ) -> list[dict[str, Any]]:
        assert branch == "refs/heads/main"
        self.queries.append(
            {
                "definition_id": definition_id,
                "branch": branch,
                "min_time": min_time,
                "top": top,
            }
        )
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


def test_retries_only_recent_failed_latest_main_runs() -> None:
    client = FakeClient()
    current_time = datetime(2026, 5, 21, 18, 0, tzinfo=timezone.utc)

    decisions = retry_module.retry_failed_pipelines(
        client=client,
        pipeline_names=[
            "failed-ci",
            "succeeded-security",
            "running-quality",
            "empty-ci",
            "old-failed-release",
        ],
        branch="refs/heads/main",
        release_build_id="1857",
        release_build_number="contracts-release-20260515.6",
        release_source_version="abc123",
        lookback_hours=24,
        max_runs_per_pipeline=10,
        current_time=current_time,
    )

    assert [decision.action for decision in decisions] == [
        "queued",
        "skipped",
        "skipped",
        "skipped",
        "skipped",
    ]
    assert client.queries == [
        {
            "definition_id": 1,
            "branch": "refs/heads/main",
            "min_time": datetime(2026, 5, 20, 18, 0, tzinfo=timezone.utc),
            "top": 10,
        },
        {
            "definition_id": 2,
            "branch": "refs/heads/main",
            "min_time": datetime(2026, 5, 20, 18, 0, tzinfo=timezone.utc),
            "top": 10,
        },
        {
            "definition_id": 3,
            "branch": "refs/heads/main",
            "min_time": datetime(2026, 5, 20, 18, 0, tzinfo=timezone.utc),
            "top": 10,
        },
        {
            "definition_id": 4,
            "branch": "refs/heads/main",
            "min_time": datetime(2026, 5, 20, 18, 0, tzinfo=timezone.utc),
            "top": 10,
        },
        {
            "definition_id": 5,
            "branch": "refs/heads/main",
            "min_time": datetime(2026, 5, 20, 18, 0, tzinfo=timezone.utc),
            "top": 10,
        },
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
    assert "--lookback-hours 24" in release
    assert "--max-runs-per-pipeline 10" in release
    assert "SYSTEM_ACCESSTOKEN: $(System.AccessToken)" in release
    assert "asset-allocation-runtime-common-ci" in release
    assert "asset-allocation-runtime-common-release" in release
    assert "asset-allocation-control-plane-release" in release
    assert "asset-allocation-jobs-quality" in release
    assert "asset-allocation-jobs-release" in release
    assert "asset-allocation-ui-contracts-compat" in release
    assert "asset-allocation-ui-release" in release
    assert "asset-allocation-ui-deploy-prod" not in release
    assert "az pipelines runs show" not in release
