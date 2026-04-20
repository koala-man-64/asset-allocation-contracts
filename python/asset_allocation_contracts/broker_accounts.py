from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

BrokerVendor = Literal["alpaca", "schwab", "etrade"]
BrokerHealthTone = Literal["healthy", "warning", "critical"]
BrokerConnectionState = Literal["connected", "degraded", "disconnected", "reconnect_required"]
BrokerAuthStatus = Literal["authenticated", "expires_soon", "expired", "reauth_required", "not_connected"]
BrokerSyncStatus = Literal["fresh", "stale", "syncing", "paused", "failed", "never_synced"]
BrokerTradeReadiness = Literal["ready", "review", "blocked"]
BrokerAccountType = Literal["cash", "margin", "retirement", "paper", "other"]
BrokerAlertSeverity = Literal["info", "warning", "critical"]
BrokerAlertStatus = Literal["open", "acknowledged", "resolved"]
BrokerSyncTrigger = Literal["scheduled", "manual", "reconnect", "backfill"]
BrokerSyncScope = Literal["balances", "positions", "orders", "full"]
BrokerSyncRunStatus = Literal["queued", "running", "completed", "failed"]
BrokerAccountActionType = Literal[
    "reconnect",
    "pause_sync",
    "resume_sync",
    "refresh",
    "acknowledge_alert",
]
BrokerAccountActionStatus = Literal["accepted", "in_progress", "completed", "failed"]


def _normalize_required_text(value: object, field_name: str) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        raise ValueError(f"{field_name} is required.")
    return normalized


def _normalize_optional_text(value: object) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _normalize_currency(value: object) -> str:
    normalized = str(value or "").strip().upper()
    if len(normalized) != 3:
        raise ValueError("baseCurrency must be a 3-letter ISO code.")
    return normalized


class BrokerConnectionHealth(BaseModel):
    model_config = ConfigDict(extra="forbid")

    overallStatus: BrokerHealthTone = "warning"
    authStatus: BrokerAuthStatus = "not_connected"
    connectionState: BrokerConnectionState = "disconnected"
    syncStatus: BrokerSyncStatus = "never_synced"
    lastCheckedAt: datetime | None = None
    lastSuccessfulSyncAt: datetime | None = None
    lastFailedSyncAt: datetime | None = None
    authExpiresAt: datetime | None = None
    staleReason: str | None = None
    failureMessage: str | None = None
    syncPaused: bool = False

    @field_validator("staleReason", "failureMessage", mode="before")
    @classmethod
    def normalize_optional_text_fields(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class BrokerCapabilityFlags(BaseModel):
    model_config = ConfigDict(extra="forbid")

    canReadBalances: bool = False
    canReadPositions: bool = False
    canReadOrders: bool = False
    canTrade: bool = False
    canReconnect: bool = False
    canPauseSync: bool = False
    canRefresh: bool = False
    canAcknowledgeAlerts: bool = False


class BrokerAccountAlert(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alertId: str = Field(..., min_length=1, max_length=128)
    accountId: str = Field(..., min_length=1, max_length=128)
    severity: BrokerAlertSeverity = "warning"
    status: BrokerAlertStatus = "open"
    code: str = Field(..., min_length=1, max_length=128)
    title: str = Field(..., min_length=1, max_length=160)
    message: str = ""
    observedAt: datetime
    acknowledgedAt: datetime | None = None
    acknowledgedBy: str | None = Field(default=None, min_length=1, max_length=128)
    resolvedAt: datetime | None = None
    asOfDate: datetime | None = None

    @field_validator("alertId", "accountId", "code", "title", mode="before")
    @classmethod
    def normalize_required_text_fields(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator("message", mode="before")
    @classmethod
    def normalize_message(cls, value: object) -> str:
        return str(value or "").strip()

    @field_validator("acknowledgedBy", mode="before")
    @classmethod
    def normalize_acknowledged_by(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class BrokerSyncRun(BaseModel):
    model_config = ConfigDict(extra="forbid")

    runId: str = Field(..., min_length=1, max_length=128)
    accountId: str = Field(..., min_length=1, max_length=128)
    trigger: BrokerSyncTrigger = "scheduled"
    scope: BrokerSyncScope = "full"
    status: BrokerSyncRunStatus = "queued"
    requestedAt: datetime
    startedAt: datetime | None = None
    completedAt: datetime | None = None
    warningCount: int = Field(default=0, ge=0)
    rowsSynced: int | None = Field(default=None, ge=0)
    summary: str | None = None
    errorMessage: str | None = None

    @field_validator("runId", "accountId", mode="before")
    @classmethod
    def normalize_required_text_fields(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator("summary", "errorMessage", mode="before")
    @classmethod
    def normalize_optional_text_fields(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class BrokerAccountActivity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    activityId: str = Field(..., min_length=1, max_length=128)
    accountId: str = Field(..., min_length=1, max_length=128)
    activityType: BrokerAccountActionType
    status: BrokerAccountActionStatus = "accepted"
    requestedAt: datetime
    completedAt: datetime | None = None
    actor: str | None = Field(default=None, min_length=1, max_length=128)
    summary: str = ""
    note: str | None = None
    relatedAlertId: str | None = Field(default=None, min_length=1, max_length=128)

    @field_validator("activityId", "accountId", mode="before")
    @classmethod
    def normalize_required_text_fields(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator("actor", "note", "relatedAlertId", mode="before")
    @classmethod
    def normalize_optional_text_fields(cls, value: object) -> str | None:
        return _normalize_optional_text(value)

    @field_validator("summary", mode="before")
    @classmethod
    def normalize_summary(cls, value: object) -> str:
        return str(value or "").strip()


class BrokerAccountSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accountId: str = Field(..., min_length=1, max_length=128)
    broker: BrokerVendor
    name: str = Field(..., min_length=1, max_length=128)
    accountNumberMasked: str | None = Field(default=None, min_length=1, max_length=32)
    baseCurrency: str = Field(default="USD", min_length=3, max_length=3)
    overallStatus: BrokerHealthTone = "warning"
    tradeReadiness: BrokerTradeReadiness = "review"
    tradeReadinessReason: str | None = None
    highestAlertSeverity: BrokerAlertSeverity | None = None
    connectionHealth: BrokerConnectionHealth = Field(default_factory=BrokerConnectionHealth)
    equity: float = 0.0
    cash: float = 0.0
    buyingPower: float = 0.0
    openPositionCount: int = Field(default=0, ge=0)
    openOrderCount: int = Field(default=0, ge=0)
    lastSyncedAt: datetime | None = None
    snapshotAsOf: datetime | None = None
    activePortfolioName: str | None = Field(default=None, min_length=1, max_length=128)
    strategyLabel: str | None = Field(default=None, min_length=1, max_length=128)
    alertCount: int = Field(default=0, ge=0)

    @field_validator("accountId", "name", mode="before")
    @classmethod
    def normalize_required_text_fields(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator(
        "accountNumberMasked",
        "tradeReadinessReason",
        "activePortfolioName",
        "strategyLabel",
        mode="before",
    )
    @classmethod
    def normalize_optional_text_fields(cls, value: object) -> str | None:
        return _normalize_optional_text(value)

    @field_validator("baseCurrency", mode="before")
    @classmethod
    def normalize_base_currency(cls, value: object) -> str:
        return _normalize_currency(value)


class BrokerAccountDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account: BrokerAccountSummary
    capabilities: BrokerCapabilityFlags = Field(default_factory=BrokerCapabilityFlags)
    accountType: BrokerAccountType = "other"
    tradingBlocked: bool = False
    tradingBlockedReason: str | None = None
    unsettledFunds: float | None = None
    dayTradeBuyingPower: float | None = None
    maintenanceExcess: float | None = None
    alerts: list[BrokerAccountAlert] = Field(default_factory=list)
    syncRuns: list[BrokerSyncRun] = Field(default_factory=list)
    recentActivity: list[BrokerAccountActivity] = Field(default_factory=list)

    @field_validator("tradingBlockedReason", mode="before")
    @classmethod
    def normalize_trading_blocked_reason(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class BrokerAccountListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accounts: list[BrokerAccountSummary] = Field(default_factory=list)
    generatedAt: datetime | None = None


class ReconnectBrokerAccountRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str = ""

    @field_validator("reason", mode="before")
    @classmethod
    def normalize_reason(cls, value: object) -> str:
        return str(value or "").strip()


class PauseBrokerSyncRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    paused: bool = True
    reason: str = ""

    @field_validator("reason", mode="before")
    @classmethod
    def normalize_reason(cls, value: object) -> str:
        return str(value or "").strip()


class RefreshBrokerAccountRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scope: BrokerSyncScope = "full"
    force: bool = False
    reason: str = ""

    @field_validator("reason", mode="before")
    @classmethod
    def normalize_reason(cls, value: object) -> str:
        return str(value or "").strip()


class AcknowledgeBrokerAlertRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    note: str = ""

    @field_validator("note", mode="before")
    @classmethod
    def normalize_note(cls, value: object) -> str:
        return str(value or "").strip()


class BrokerAccountActionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actionId: str = Field(..., min_length=1, max_length=128)
    accountId: str = Field(..., min_length=1, max_length=128)
    action: BrokerAccountActionType
    status: BrokerAccountActionStatus = "accepted"
    requestedAt: datetime
    message: str | None = None
    resultingConnectionHealth: BrokerConnectionHealth | None = None
    tradeReadiness: BrokerTradeReadiness | None = None
    syncPaused: bool | None = None

    @field_validator("actionId", "accountId", mode="before")
    @classmethod
    def normalize_required_text_fields(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator("message", mode="before")
    @classmethod
    def normalize_message(cls, value: object) -> str | None:
        return _normalize_optional_text(value)
