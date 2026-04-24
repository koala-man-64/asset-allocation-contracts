from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

PublicationReconcileStatus = Literal["pending", "processed", "error"]


class RegimePublicationModelReference(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    modelName: str = Field(..., min_length=1, max_length=128, validation_alias=AliasChoices("modelName", "model_name"))
    modelVersion: int = Field(..., ge=1, validation_alias=AliasChoices("modelVersion", "model_version"))


class RegimePublicationReconcileMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    publishedAsOfDate: str = Field(..., min_length=10, max_length=10, pattern=r"^\d{4}-\d{2}-\d{2}$")
    inputAsOfDate: str | None = Field(default=None, min_length=10, max_length=10, pattern=r"^\d{4}-\d{2}-\d{2}$")
    historyRows: int = Field(..., ge=0)
    latestRows: int = Field(..., ge=0)
    transitionRows: int = Field(..., ge=0)
    activeModels: list[RegimePublicationModelReference] = Field(default_factory=list, max_length=16)
    domainArtifactPath: str | None = Field(default=None, max_length=512)
    producerJobName: str = Field(default="gold-regime-job", pattern=r"^gold-regime-job$")


class StrategyPublicationReconcileSignalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    jobKey: str = Field(..., min_length=1, max_length=128, pattern=r"^[a-z0-9][a-z0-9-]*$")
    sourceFingerprint: str = Field(..., min_length=1, max_length=128)
    publishedAt: datetime | None = None
    metadata: RegimePublicationReconcileMetadata


class StrategyPublicationReconcileSignalResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    jobKey: str
    sourceFingerprint: str
    status: PublicationReconcileStatus
    created: bool
    createdAt: datetime
    updatedAt: datetime
    processedAt: datetime | None = None
    error: str | None = None
