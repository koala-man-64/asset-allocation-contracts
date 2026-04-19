from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


SymbolCleanupStatus = Literal["queued", "running", "completed", "failed"]
SymbolWorkStatus = Literal["queued", "claimed", "completed", "failed"]
SymbolSourceKind = Literal["provider", "ai", "derived", "override"]
SymbolValidationStatus = Literal["accepted", "rejected", "pending", "locked"]
SymbolOverwriteMode = Literal["fill_missing", "full_reconcile"]
SymbolEnrichmentField = Literal[
    "security_type_norm",
    "exchange_mic",
    "country_of_risk",
    "sector_norm",
    "industry_group_norm",
    "industry_norm",
    "is_adr",
    "is_etf",
    "is_cef",
    "is_preferred",
    "share_class",
    "listing_status_norm",
    "issuer_summary_short",
]


class SymbolProviderFacts(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol: str = Field(min_length=1, max_length=32)
    name: str | None = Field(default=None, max_length=512)
    description: str | None = None
    sector: str | None = Field(default=None, max_length=255)
    industry: str | None = Field(default=None, max_length=255)
    industry2: str | None = Field(default=None, max_length=255)
    country: str | None = Field(default=None, max_length=64)
    exchange: str | None = Field(default=None, max_length=64)
    assetType: str | None = Field(default=None, max_length=64)
    ipoDate: str | None = Field(default=None, max_length=32)
    delistingDate: str | None = Field(default=None, max_length=32)
    status: str | None = Field(default=None, max_length=64)
    isOptionable: bool | None = None
    sourceNasdaq: bool | None = None
    sourceMassive: bool | None = None
    sourceAlphaVantage: bool | None = None


class SymbolProfileValues(BaseModel):
    model_config = ConfigDict(extra="forbid")

    security_type_norm: str | None = Field(default=None, max_length=64)
    exchange_mic: str | None = Field(default=None, max_length=16)
    country_of_risk: str | None = Field(default=None, max_length=64)
    sector_norm: str | None = Field(default=None, max_length=255)
    industry_group_norm: str | None = Field(default=None, max_length=255)
    industry_norm: str | None = Field(default=None, max_length=255)
    is_adr: bool | None = None
    is_etf: bool | None = None
    is_cef: bool | None = None
    is_preferred: bool | None = None
    share_class: str | None = Field(default=None, max_length=64)
    listing_status_norm: str | None = Field(default=None, max_length=64)
    issuer_summary_short: str | None = Field(default=None, max_length=2_000)


class SymbolCleanupWorkItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workId: str = Field(min_length=1, max_length=64)
    runId: str = Field(min_length=1, max_length=64)
    symbol: str = Field(min_length=1, max_length=32)
    status: SymbolWorkStatus
    requestedFields: list[SymbolEnrichmentField]
    attemptCount: int = Field(default=0, ge=0)
    executionName: str | None = Field(default=None, max_length=255)
    claimedAt: datetime | None = None
    lastError: str | None = Field(default=None, max_length=2_000)


class SymbolCleanupRunSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    runId: str = Field(min_length=1, max_length=64)
    status: SymbolCleanupStatus
    mode: SymbolOverwriteMode = "fill_missing"
    queuedCount: int = Field(default=0, ge=0)
    claimedCount: int = Field(default=0, ge=0)
    completedCount: int = Field(default=0, ge=0)
    failedCount: int = Field(default=0, ge=0)
    acceptedUpdateCount: int = Field(default=0, ge=0)
    rejectedUpdateCount: int = Field(default=0, ge=0)
    lockedSkipCount: int = Field(default=0, ge=0)
    overwriteCount: int = Field(default=0, ge=0)
    startedAt: datetime | None = None
    completedAt: datetime | None = None


class SymbolEnrichmentResolveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol: str = Field(min_length=1, max_length=32)
    overwriteMode: SymbolOverwriteMode = "fill_missing"
    requestedFields: list[SymbolEnrichmentField]
    providerFacts: SymbolProviderFacts
    currentProfile: SymbolProfileValues | None = None


class SymbolEnrichmentResolveResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol: str = Field(min_length=1, max_length=32)
    profile: SymbolProfileValues
    model: str | None = Field(default=None, max_length=128)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    sourceFingerprint: str | None = Field(default=None, max_length=128)
    warnings: list[str] = []


class SymbolProfileCurrent(SymbolProfileValues):
    model_config = ConfigDict(extra="forbid")

    symbol: str = Field(min_length=1, max_length=32)
    sourceKind: SymbolSourceKind
    sourceFingerprint: str | None = Field(default=None, max_length=128)
    aiModel: str | None = Field(default=None, max_length=128)
    aiConfidence: float | None = Field(default=None, ge=0.0, le=1.0)
    validationStatus: SymbolValidationStatus = "accepted"
    marketCapUsd: float | None = None
    marketCapBucket: str | None = Field(default=None, max_length=64)
    avgDollarVolume20d: float | None = None
    liquidityBucket: str | None = Field(default=None, max_length=64)
    isTradeableCommonEquity: bool | None = None
    dataCompletenessScore: float | None = Field(default=None, ge=0.0, le=1.0)
    updatedAt: datetime | None = None


class SymbolProfileHistoryEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    historyId: str = Field(min_length=1, max_length=64)
    symbol: str = Field(min_length=1, max_length=32)
    fieldName: SymbolEnrichmentField
    previousValue: str | float | bool | None = None
    newValue: str | float | bool | None = None
    sourceKind: SymbolSourceKind
    aiModel: str | None = Field(default=None, max_length=128)
    aiConfidence: float | None = Field(default=None, ge=0.0, le=1.0)
    changeReason: str | None = Field(default=None, max_length=500)
    runId: str | None = Field(default=None, max_length=64)
    updatedAt: datetime


class SymbolProfileOverride(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol: str = Field(min_length=1, max_length=32)
    fieldName: SymbolEnrichmentField
    value: str | float | bool | None = None
    isLocked: bool = False
    updatedBy: str | None = Field(default=None, max_length=255)
    updatedAt: datetime | None = None


class SymbolEnrichmentSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    backlogCount: int = Field(default=0, ge=0)
    lastRun: SymbolCleanupRunSummary | None = None
    activeRun: SymbolCleanupRunSummary | None = None
    validationFailureCount: int = Field(default=0, ge=0)
    lockCount: int = Field(default=0, ge=0)


class SymbolEnrichmentSymbolListItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol: str = Field(min_length=1, max_length=32)
    name: str | None = Field(default=None, max_length=512)
    status: SymbolValidationStatus
    sourceKind: SymbolSourceKind
    updatedAt: datetime | None = None
    missingFieldCount: int = Field(default=0, ge=0)
    lockedFieldCount: int = Field(default=0, ge=0)
    dataCompletenessScore: float | None = Field(default=None, ge=0.0, le=1.0)


class SymbolEnrichmentSymbolDetailResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    providerFacts: SymbolProviderFacts
    currentProfile: SymbolProfileCurrent | None = None
    overrides: list[SymbolProfileOverride] = []
    history: list[SymbolProfileHistoryEntry] = []


class SymbolEnrichmentEnqueueRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbols: list[str] = []
    fullScan: bool = False
    overwriteMode: SymbolOverwriteMode = "fill_missing"
    maxSymbols: int | None = Field(default=None, ge=1, le=50_000)
