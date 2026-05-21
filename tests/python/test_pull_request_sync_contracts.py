from __future__ import annotations

import pytest

from asset_allocation_contracts.pull_request_sync import (
    PullRequestActionResponse,
    PullRequestApprovalActionRequest,
    PullRequestPipelineApprovalActionRequest,
    PullRequestRetryStageActionRequest,
    PullRequestSyncRow,
    PullRequestSyncSummary,
)


def test_pull_request_sync_contract_accepts_approval_and_retry_fields() -> None:
    row = PullRequestSyncRow(
        repo="asset-allocation-ui",
        repositoryId="repo-ui",
        pullRequestId=280,
        title="AB#996 Add inline PR controls",
        status="active",
        isDraft=False,
        sourceRefName="refs/heads/feature/system-status-pr-actions",
        targetRefName="refs/heads/main",
        mergeStatus="failure",
        result="error",
        approval={
            "requiresUserApproval": True,
            "reviewerDisplayName": "Rudy Prokes",
            "reviewerUniqueName": "rdprokes@example.com",
            "vote": "not-voted",
            "reason": "Minimum reviewer policy is waiting on your vote.",
            "action": {
                "kind": "approve",
                "label": "Approve pull request",
                "href": "https://dev.azure.com/example/_git/asset-allocation-ui/pullrequest/280",
            },
        },
        stages=[
            {
                "name": "asset-allocation-ui-ci",
                "status": "failed",
                "result": "failed",
                "runId": 1958,
                "runName": "ui-ci-20260517.1",
                "pipelineName": "asset-allocation-ui-ci",
                "action": {
                    "kind": "retry-stage",
                    "label": "Retry validation run",
                },
                "warnings": ["Typecheck failed."],
            },
            {
                "name": "deploy approval",
                "status": "pending",
                "result": "pending",
                "runId": 1960,
                "runName": "ui-deploy-20260517.3",
                "pipelineName": "asset-allocation-ui-deploy",
                "approval": {
                    "approvalId": "b2d2ab90-b959-4cc1-a63b-663965c445d2",
                    "status": "pending",
                    "approverDisplayName": "Rudy Prokes",
                    "approverUniqueName": "rdprokes@example.com",
                    "instructions": "Approve the environment gate.",
                    "reason": "Deploy validation is waiting for owner approval.",
                    "action": {
                        "kind": "approve-check",
                        "label": "Approve pipeline gate",
                    },
                },
                "action": {
                    "kind": "approve-check",
                    "label": "Approve pipeline gate",
                },
            }
        ],
    )
    summary = PullRequestSyncSummary(
        totalPullRequests=1,
        drafts=0,
        ready=1,
        synced=0,
        targetStale=0,
        sourceStale=0,
        conflicts=0,
        unknown=0,
        unavailable=0,
        error=1,
        approvalRequired=1,
        failedStages=1,
        pendingApprovals=1,
    )

    assert row.approval is not None
    assert row.approval.action is not None
    assert row.approval.action.kind == "approve"
    assert row.stages is not None
    assert row.stages[0].runId == 1958
    assert row.stages[0].action is not None
    assert row.stages[0].action.kind == "retry-stage"
    assert row.stages[1].approval is not None
    assert row.stages[1].approval.approvalId == "b2d2ab90-b959-4cc1-a63b-663965c445d2"
    assert row.stages[1].approval.action is not None
    assert row.stages[1].approval.action.kind == "approve-check"
    assert row.stages[1].action is not None
    assert row.stages[1].action.kind == "approve-check"
    assert summary.approvalRequired == 1
    assert summary.failedStages == 1
    assert summary.pendingApprovals == 1


def test_pull_request_action_contracts_capture_approve_retry_and_check_requests() -> None:
    approve = PullRequestApprovalActionRequest(
        repositoryId="repo-ui",
        pullRequestId=280,
        reviewerUniqueName="rdprokes@example.com",
    )
    retry = PullRequestRetryStageActionRequest(
        repositoryId="repo-ui",
        pullRequestId=280,
        runId=1958,
    )
    approve_check = PullRequestPipelineApprovalActionRequest(
        repositoryId="repo-ui",
        pullRequestId=280,
        runId=1960,
        approvalId="b2d2ab90-b959-4cc1-a63b-663965c445d2",
        comment="Approved from System Status.",
    )
    response = PullRequestActionResponse(
        repositoryId="repo-ui",
        pullRequestId=280,
        action="approve-check",
        status="accepted",
        message="Approved the pipeline gate.",
        runId=1960,
        runName="asset-allocation-ui-ci-20260517.3",
        approvalId="b2d2ab90-b959-4cc1-a63b-663965c445d2",
        approvalStatus="approved",
    )

    assert approve.reviewerUniqueName == "rdprokes@example.com"
    assert retry.runId == 1958
    assert approve_check.approvalId == "b2d2ab90-b959-4cc1-a63b-663965c445d2"
    assert approve_check.comment == "Approved from System Status."
    assert response.action == "approve-check"
    assert response.status == "accepted"
    assert response.runId == 1960
    assert response.approvalId == "b2d2ab90-b959-4cc1-a63b-663965c445d2"
    assert response.approvalStatus == "approved"


def test_pull_request_action_contracts_forbid_unknown_fields() -> None:
    with pytest.raises(Exception) as exc_info:
        PullRequestApprovalActionRequest.model_validate(
            {
                "repositoryId": "repo-ui",
                "pullRequestId": 280,
                "unexpected": True,
            }
        )

    assert "unexpected" in str(exc_info.value)
