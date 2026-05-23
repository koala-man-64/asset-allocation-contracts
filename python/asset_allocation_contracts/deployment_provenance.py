from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ConsistencyStatus = Literal[
    "consistent",
    "stale",
    "mismatch",
    "running",
    "unknown",
    "unavailable",
    "error",
]
DeploymentProvenanceStatus = Literal["available", "partial", "unavailable", "error"]
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


class DeploymentProvenanceLink(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str = Field(min_length=1, max_length=96)
    href: str = Field(min_length=1, max_length=2048)


class PipelineRunSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pipelineId: int | None = Field(default=None, ge=1)
    pipelineName: str = Field(min_length=1, max_length=160)
    runId: int | None = Field(default=None, ge=1)
    runNumber: str | None = Field(default=None, min_length=1, max_length=160)
    status: PipelineRunLifecycleStatus = "unknown"
    result: PipelineRunResult = "unknown"
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
    links: list[DeploymentProvenanceLink] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class DeploymentVersionMatrix(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contracts: str | None = Field(default=None, min_length=1, max_length=80)
    runtimeCommon: str | None = Field(default=None, min_length=1, max_length=80)
    controlPlane: str | None = Field(default=None, min_length=1, max_length=80)
    jobs: str | None = Field(default=None, min_length=1, max_length=80)
    ui: str | None = Field(default=None, min_length=1, max_length=80)


class DeploymentPackageVersion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    repo: str = Field(min_length=1, max_length=160)
    packageName: str = Field(min_length=1, max_length=160)
    version: str | None = Field(default=None, min_length=1, max_length=80)
    versionMatrix: DeploymentVersionMatrix | None = None
    releaseRun: PipelineRunSummary | None = None
    checkedAt: datetime
    links: list[DeploymentProvenanceLink] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ResourceDeploymentVersion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    resourceName: str = Field(min_length=1, max_length=160)
    resourceType: str = Field(min_length=1, max_length=160)
    environment: str = Field(min_length=1, max_length=80)
    repo: str = Field(min_length=1, max_length=160)
    packageVersion: str | None = Field(default=None, min_length=1, max_length=80)
    versionMatrix: DeploymentVersionMatrix | None = None
    artifactDigest: str | None = Field(default=None, min_length=1, max_length=256)
    sourceSha: str | None = Field(
        default=None,
        min_length=7,
        max_length=64,
        pattern=r"^[0-9a-fA-F]+$",
    )
    releaseRun: PipelineRunSummary | None = None
    deployRun: PipelineRunSummary | None = None
    latestSuccessfulRun: PipelineRunSummary | None = None
    status: DeploymentProvenanceStatus = "available"
    result: ConsistencyStatus
    checkedAt: datetime
    links: list[DeploymentProvenanceLink] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class DeploymentProvenanceSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    totalResources: int = Field(ge=0)
    consistent: int = Field(default=0, ge=0)
    stale: int = Field(default=0, ge=0)
    mismatch: int = Field(default=0, ge=0)
    running: int = Field(default=0, ge=0)
    unknown: int = Field(default=0, ge=0)
    unavailable: int = Field(default=0, ge=0)
    error: int = Field(default=0, ge=0)


class DeploymentProvenanceView(BaseModel):
    model_config = ConfigDict(extra="forbid")

    checkedAt: datetime
    status: DeploymentProvenanceStatus
    result: ConsistencyStatus
    summary: DeploymentProvenanceSummary
    latestPackages: list[DeploymentPackageVersion] = Field(default_factory=list)
    resources: list[ResourceDeploymentVersion] = Field(default_factory=list)
    links: list[DeploymentProvenanceLink] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
