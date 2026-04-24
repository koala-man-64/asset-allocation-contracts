from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


JobCategory = Literal["data-pipeline", "strategy-compute", "operational-support"]
JobMetadataSource = Literal["tags", "legacy-catalog", "unknown"]
JobMetadataStatus = Literal["valid", "fallback", "invalid"]


class RuntimeJobMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    jobCategory: JobCategory
    jobKey: str = Field(min_length=1, max_length=128, pattern=r"^[a-z0-9][a-z0-9-]*$")
    jobRole: str = Field(min_length=1, max_length=64, pattern=r"^[a-z0-9][a-z0-9-]*$")
    triggerOwner: str = Field(min_length=1, max_length=64, pattern=r"^[a-z0-9][a-z0-9-]*$")
    metadataSource: JobMetadataSource
    metadataStatus: JobMetadataStatus
