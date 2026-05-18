from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


PullRequestSyncViewStatus = Literal["available", "partial", "unavailable", "error"]
PullRequestSyncStatus = Literal[
    "synced",
    "target-stale",
    "source-stale",
    "conflict",
    "unknown",
    "unavailable",
    "error",
]
PullRequestLifecycleStatus = Literal["active", "abandoned", "completed", "unknown"]
PullRequestMergeStatus = Literal[
    "notSet",
    "queued",
    "conflicts",
    "succeeded",
    "rejectedByPolicy",
    "failure",
    "unknown",
]
PullRequestSyncActionKind = Literal["approve", "retry-stage", "open"]
PullRequestApprovalVote = Literal[
    "approved",
    "approved-with-suggestions",
    "rejected",
    "waiting",
    "not-voted",
    "unknown",
]
PullRequestStageLifecycleStatus = Literal[
    "succeeded",
    "failed",
    "canceled",
    "skipped",
    "running",
    "pending",
    "unknown",
]
PullRequestActionResponseStatus = Literal["accepted", "completed"]


class PullRequestSyncLink(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str = Field(min_length=1, max_length=96)
    href: str = Field(min_length=1, max_length=2048)


class PullRequestWorkItemRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int = Field(ge=1)
    title: str | None = Field(default=None, min_length=1, max_length=256)
    workItemType: str | None = Field(default=None, min_length=1, max_length=96)
    state: str | None = Field(default=None, min_length=1, max_length=80)
    links: list[PullRequestSyncLink] = Field(default_factory=list)


class PullRequestCommitSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    commitId: str = Field(min_length=7, max_length=64, pattern=r"^[0-9a-fA-F]+$")
    comment: str | None = Field(default=None, min_length=1, max_length=512)
    authorName: str | None = Field(default=None, min_length=1, max_length=160)
    authorEmail: str | None = Field(default=None, min_length=1, max_length=320)
    authoredAt: datetime | None = None
    links: list[PullRequestSyncLink] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class PullRequestSyncAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: PullRequestSyncActionKind
    label: str = Field(min_length=1, max_length=96)
    href: str | None = Field(default=None, min_length=1, max_length=2048)
    disabledReason: str | None = Field(default=None, min_length=1, max_length=512)
    links: list[PullRequestSyncLink] = Field(default_factory=list)


class PullRequestApprovalStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requiresUserApproval: bool = False
    reviewerDisplayName: str | None = Field(default=None, min_length=1, max_length=160)
    reviewerUniqueName: str | None = Field(default=None, min_length=1, max_length=320)
    vote: PullRequestApprovalVote | None = None
    reason: str | None = Field(default=None, min_length=1, max_length=512)
    action: PullRequestSyncAction | None = None
    links: list[PullRequestSyncLink] = Field(default_factory=list)


class PullRequestPipelineStage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=160)
    status: PullRequestStageLifecycleStatus = "unknown"
    result: PullRequestStageLifecycleStatus | None = None
    runId: int | None = Field(default=None, ge=1)
    runName: str | None = Field(default=None, min_length=1, max_length=160)
    pipelineName: str | None = Field(default=None, min_length=1, max_length=160)
    action: PullRequestSyncAction | None = None
    links: list[PullRequestSyncLink] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class PullRequestSyncRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    repo: str = Field(min_length=1, max_length=160)
    repositoryId: str | None = Field(default=None, min_length=1, max_length=128)
    pullRequestId: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=512)
    status: PullRequestLifecycleStatus = "unknown"
    isDraft: bool = False
    createdByDisplayName: str | None = Field(default=None, min_length=1, max_length=160)
    sourceRefName: str = Field(min_length=1, max_length=256)
    targetRefName: str = Field(min_length=1, max_length=256)
    sourceHeadSha: str | None = Field(default=None, min_length=7, max_length=64, pattern=r"^[0-9a-fA-F]+$")
    targetHeadSha: str | None = Field(default=None, min_length=7, max_length=64, pattern=r"^[0-9a-fA-F]+$")
    lastMergeSourceCommit: str | None = Field(default=None, min_length=7, max_length=64, pattern=r"^[0-9a-fA-F]+$")
    lastMergeTargetCommit: str | None = Field(default=None, min_length=7, max_length=64, pattern=r"^[0-9a-fA-F]+$")
    lastMergeCommit: str | None = Field(default=None, min_length=7, max_length=64, pattern=r"^[0-9a-fA-F]+$")
    mergeStatus: PullRequestMergeStatus = "unknown"
    result: PullRequestSyncStatus
    createdAt: datetime | None = None
    updatedAt: datetime | None = None
    workItems: list[PullRequestWorkItemRef] = Field(default_factory=list)
    commits: list[PullRequestCommitSummary] = Field(default_factory=list)
    approval: PullRequestApprovalStatus | None = None
    stages: list[PullRequestPipelineStage] | None = None
    links: list[PullRequestSyncLink] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class PullRequestSyncSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    totalPullRequests: int = Field(ge=0)
    drafts: int = Field(default=0, ge=0)
    ready: int = Field(default=0, ge=0)
    synced: int = Field(default=0, ge=0)
    targetStale: int = Field(default=0, ge=0)
    sourceStale: int = Field(default=0, ge=0)
    conflicts: int = Field(default=0, ge=0)
    unknown: int = Field(default=0, ge=0)
    unavailable: int = Field(default=0, ge=0)
    error: int = Field(default=0, ge=0)
    approvalRequired: int | None = Field(default=None, ge=0)
    failedStages: int | None = Field(default=None, ge=0)


class PullRequestSyncView(BaseModel):
    model_config = ConfigDict(extra="forbid")

    checkedAt: datetime
    status: PullRequestSyncViewStatus
    result: PullRequestSyncStatus
    summary: PullRequestSyncSummary
    pullRequests: list[PullRequestSyncRow] = Field(default_factory=list)
    links: list[PullRequestSyncLink] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class PullRequestApprovalActionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    repositoryId: str = Field(min_length=1, max_length=128)
    pullRequestId: int = Field(ge=1)
    reviewerUniqueName: str | None = Field(default=None, min_length=1, max_length=320)


class PullRequestRetryStageActionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    repositoryId: str = Field(min_length=1, max_length=128)
    pullRequestId: int = Field(ge=1)
    runId: int = Field(ge=1)


class PullRequestActionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    repositoryId: str = Field(min_length=1, max_length=128)
    pullRequestId: int = Field(ge=1)
    action: PullRequestSyncActionKind
    status: PullRequestActionResponseStatus = "completed"
    message: str = Field(min_length=1, max_length=512)
    reviewerUniqueName: str | None = Field(default=None, min_length=1, max_length=320)
    runId: int | None = Field(default=None, ge=1)
    runName: str | None = Field(default=None, min_length=1, max_length=160)
    links: list[PullRequestSyncLink] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
