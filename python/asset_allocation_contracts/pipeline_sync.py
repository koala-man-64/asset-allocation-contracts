from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


PipelineSyncViewStatus = Literal["available", "partial", "unavailable", "error"]
PipelineSyncResult = Literal[
    "healthy",
    "attention",
    "blocked",
    "running",
    "unknown",
    "unavailable",
    "error",
]
PipelineDefinitionType = Literal[
    "ci",
    "security",
    "release",
    "deploy",
    "rollback",
    "compatibility",
    "governance",
    "other",
]
PipelineRunLifecycleStatus = Literal[
    "notStarted",
    "inProgress",
    "completed",
    "cancelling",
    "postponed",
    "unknown",
]
PipelineRunResult = Literal[
    "succeeded",
    "partiallySucceeded",
    "failed",
    "canceled",
    "skipped",
    "unknown",
]
PipelineStageLifecycleStatus = Literal[
    "succeeded",
    "failed",
    "canceled",
    "skipped",
    "running",
    "pending",
    "unknown",
]
PipelineApprovalStatus = Literal["pending", "approved", "rejected", "skipped", "unknown"]
PipelineSyncActionKind = Literal[
    "queue",
    "cancel",
    "retry-run",
    "retry-stage",
    "approve-check",
    "open",
]
PipelineActionResponseStatus = Literal["accepted", "completed"]


class PipelineSyncLink(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str = Field(min_length=1, max_length=96)
    href: str = Field(min_length=1, max_length=2048)


class PipelineSyncAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: PipelineSyncActionKind
    label: str = Field(min_length=1, max_length=96)
    href: str | None = Field(default=None, min_length=1, max_length=2048)
    disabledReason: str | None = Field(default=None, min_length=1, max_length=512)
    pipelineId: int | None = Field(default=None, ge=1)
    runId: int | None = Field(default=None, ge=1)
    stageName: str | None = Field(default=None, min_length=1, max_length=160)
    approvalId: str | None = Field(default=None, min_length=1, max_length=128)
    links: list[PipelineSyncLink] = Field(default_factory=list)


class PipelineApproval(BaseModel):
    model_config = ConfigDict(extra="forbid")

    approvalId: str = Field(min_length=1, max_length=128)
    status: PipelineApprovalStatus = "unknown"
    approverDisplayName: str | None = Field(default=None, min_length=1, max_length=160)
    approverUniqueName: str | None = Field(default=None, min_length=1, max_length=320)
    instructions: str | None = Field(default=None, min_length=1, max_length=512)
    reason: str | None = Field(default=None, min_length=1, max_length=512)
    action: PipelineSyncAction | None = None
    links: list[PipelineSyncLink] = Field(default_factory=list)


class PipelineStageSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=160)
    status: PipelineStageLifecycleStatus = "unknown"
    result: PipelineStageLifecycleStatus | None = None
    runId: int | None = Field(default=None, ge=1)
    runName: str | None = Field(default=None, min_length=1, max_length=160)
    pipelineName: str | None = Field(default=None, min_length=1, max_length=160)
    approval: PipelineApproval | None = None
    action: PipelineSyncAction | None = None
    links: list[PipelineSyncLink] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class PipelineSyncRunSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pipelineId: int | None = Field(default=None, ge=1)
    pipelineName: str = Field(min_length=1, max_length=160)
    runId: int | None = Field(default=None, ge=1)
    runNumber: str | None = Field(default=None, min_length=1, max_length=160)
    status: PipelineRunLifecycleStatus = "unknown"
    result: PipelineRunResult = "unknown"
    reason: str | None = Field(default=None, min_length=1, max_length=80)
    sourceSha: str | None = Field(
        default=None,
        min_length=7,
        max_length=64,
        pattern=r"^[0-9a-fA-F]+$",
    )
    sourceBranch: str | None = Field(default=None, min_length=1, max_length=256)
    queuedAt: datetime | None = None
    startedAt: datetime | None = None
    finishedAt: datetime | None = None
    links: list[PipelineSyncLink] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class PipelineSyncRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    repo: str = Field(min_length=1, max_length=160)
    pipelineId: int | None = Field(default=None, ge=1)
    pipelineName: str = Field(min_length=1, max_length=160)
    pipelineType: PipelineDefinitionType = "other"
    definitionPath: str | None = Field(default=None, min_length=1, max_length=512)
    defaultBranch: str | None = Field(default=None, min_length=1, max_length=256)
    latestRun: PipelineSyncRunSummary | None = None
    activeRuns: list[PipelineSyncRunSummary] = Field(default_factory=list)
    failedStages: list[PipelineStageSummary] = Field(default_factory=list)
    pendingApprovals: list[PipelineApproval] = Field(default_factory=list)
    actions: list[PipelineSyncAction] = Field(default_factory=list)
    links: list[PipelineSyncLink] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class PipelineSyncSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    totalPipelines: int = Field(ge=0)
    healthy: int = Field(default=0, ge=0)
    running: int = Field(default=0, ge=0)
    failed: int = Field(default=0, ge=0)
    pendingApprovals: int = Field(default=0, ge=0)
    blocked: int = Field(default=0, ge=0)
    unknown: int = Field(default=0, ge=0)
    unavailable: int = Field(default=0, ge=0)
    error: int = Field(default=0, ge=0)


class PipelineSyncView(BaseModel):
    model_config = ConfigDict(extra="forbid")

    checkedAt: datetime
    status: PipelineSyncViewStatus
    result: PipelineSyncResult
    summary: PipelineSyncSummary
    pipelines: list[PipelineSyncRow] = Field(default_factory=list)
    links: list[PipelineSyncLink] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class PipelineQueueActionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pipelineId: int = Field(ge=1)
    sourceBranch: str | None = Field(default=None, min_length=1, max_length=256)


class PipelineRunActionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pipelineId: int = Field(ge=1)
    runId: int = Field(ge=1)


class PipelineStageRetryActionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pipelineId: int = Field(ge=1)
    runId: int = Field(ge=1)
    stageName: str | None = Field(default=None, min_length=1, max_length=160)


class PipelineApprovalActionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pipelineId: int = Field(ge=1)
    runId: int = Field(ge=1)
    approvalId: str = Field(min_length=1, max_length=128)
    comment: str | None = Field(default=None, min_length=1, max_length=512)


class PipelineActionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pipelineId: int = Field(ge=1)
    pipelineName: str | None = Field(default=None, min_length=1, max_length=160)
    action: PipelineSyncActionKind
    status: PipelineActionResponseStatus = "completed"
    message: str = Field(min_length=1, max_length=512)
    runId: int | None = Field(default=None, ge=1)
    runName: str | None = Field(default=None, min_length=1, max_length=160)
    stageName: str | None = Field(default=None, min_length=1, max_length=160)
    approvalId: str | None = Field(default=None, min_length=1, max_length=128)
    approvalStatus: PipelineApprovalStatus | None = None
    details: dict[str, Any] = Field(default_factory=dict)
    links: list[PipelineSyncLink] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
