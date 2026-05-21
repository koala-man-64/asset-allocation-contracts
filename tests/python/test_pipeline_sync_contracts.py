from __future__ import annotations

import pytest

from asset_allocation_contracts.pipeline_sync import (
    PipelineActionResponse,
    PipelineApprovalActionRequest,
    PipelineQueueActionRequest,
    PipelineRunActionRequest,
    PipelineStageRetryActionRequest,
    PipelineSyncRow,
    PipelineSyncSummary,
    PipelineSyncView,
)


def test_pipeline_sync_contract_accepts_runs_stages_approvals_and_actions() -> None:
    row = PipelineSyncRow(
        repo="asset-allocation-ui",
        pipelineId=18,
        pipelineName="asset-allocation-ui-deploy-prod",
        pipelineType="deploy",
        definitionPath="azure-pipelines/deploy-prod.yml",
        defaultBranch="refs/heads/main",
        latestRun={
            "pipelineId": 18,
            "pipelineName": "asset-allocation-ui-deploy-prod",
            "runId": 5132,
            "runNumber": "ui-deploy-20260521.1",
            "status": "completed",
            "result": "failed",
            "reason": "resourceTrigger",
            "sourceSha": "abcdef1234567890abcdef1234567890abcdef12",
            "sourceBranch": "refs/heads/main",
            "links": [
                {
                    "label": "Pipeline run",
                    "href": "https://dev.azure.com/example/_build/results?buildId=5132",
                }
            ],
        },
        activeRuns=[
            {
                "pipelineId": 18,
                "pipelineName": "asset-allocation-ui-deploy-prod",
                "runId": 5133,
                "runNumber": "ui-deploy-20260521.2",
                "status": "inProgress",
                "result": "unknown",
                "sourceBranch": "refs/heads/main",
            }
        ],
        failedStages=[
            {
                "name": "Deploy / Verify",
                "status": "failed",
                "result": "failed",
                "runId": 5132,
                "runName": "ui-deploy-20260521.1",
                "pipelineName": "asset-allocation-ui-deploy-prod",
                "action": {
                    "kind": "retry-stage",
                    "label": "Retry Deploy / Verify",
                    "pipelineId": 18,
                    "runId": 5132,
                    "stageName": "Deploy / Verify",
                },
                "warnings": ["Smoke verification failed."],
            }
        ],
        pendingApprovals=[
            {
                "approvalId": "approval-1",
                "status": "pending",
                "approverDisplayName": "Rudy Prokes",
                "approverUniqueName": "rdprokes@example.com",
                "instructions": "Approve production deploy.",
                "action": {
                    "kind": "approve-check",
                    "label": "Approve deploy gate",
                    "pipelineId": 18,
                    "runId": 5133,
                    "approvalId": "approval-1",
                },
            }
        ],
        actions=[
            {"kind": "queue", "label": "Queue pipeline", "pipelineId": 18},
            {"kind": "cancel", "label": "Cancel active run", "pipelineId": 18, "runId": 5133},
        ],
    )
    view = PipelineSyncView(
        checkedAt="2026-05-21T12:00:00Z",
        status="available",
        result="attention",
        summary=PipelineSyncSummary(
            totalPipelines=1,
            healthy=0,
            running=1,
            failed=1,
            pendingApprovals=1,
        ),
        pipelines=[row],
    )

    assert view.pipelines[0].latestRun is not None
    assert view.pipelines[0].latestRun.runId == 5132
    assert view.pipelines[0].activeRuns[0].status == "inProgress"
    assert view.pipelines[0].failedStages[0].action is not None
    assert view.pipelines[0].failedStages[0].action.kind == "retry-stage"
    assert view.pipelines[0].pendingApprovals[0].action is not None
    assert view.pipelines[0].pendingApprovals[0].action.kind == "approve-check"


def test_pipeline_action_contracts_capture_full_control_requests() -> None:
    queue = PipelineQueueActionRequest(pipelineId=18, sourceBranch="refs/heads/main")
    cancel = PipelineRunActionRequest(pipelineId=18, runId=5133)
    retry_stage = PipelineStageRetryActionRequest(
        pipelineId=18,
        runId=5132,
        stageName="Deploy / Verify",
    )
    approve_check = PipelineApprovalActionRequest(
        pipelineId=18,
        runId=5133,
        approvalId="approval-1",
        comment="Approved from System Status.",
    )
    response = PipelineActionResponse(
        pipelineId=18,
        pipelineName="asset-allocation-ui-deploy-prod",
        action="approve-check",
        status="completed",
        message="Approved pipeline gate.",
        runId=5133,
        runName="ui-deploy-20260521.2",
        approvalId="approval-1",
        approvalStatus="approved",
    )

    assert queue.sourceBranch == "refs/heads/main"
    assert cancel.runId == 5133
    assert retry_stage.stageName == "Deploy / Verify"
    assert approve_check.comment == "Approved from System Status."
    assert response.action == "approve-check"
    assert response.approvalStatus == "approved"


def test_pipeline_sync_contracts_forbid_unknown_fields() -> None:
    with pytest.raises(Exception) as exc_info:
        PipelineQueueActionRequest.model_validate(
            {
                "pipelineId": 18,
                "variables": {"unsafe": "not accepted"},
            }
        )

    assert "variables" in str(exc_info.value)
