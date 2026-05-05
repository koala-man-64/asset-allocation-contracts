from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

BrokerVendor = Literal["alpaca", "schwab", "etrade", "kalshi"]
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
BrokerPolicySide = Literal["long", "short"]
BrokerPolicyAssetClass = Literal["equity", "option"]
BrokerPositionSizeMode = Literal["pct_of_allocatable_capital", "notional_base_ccy"]
BrokerAllocationMode = Literal["percent", "notional_base_ccy"]
BrokerConfigurationAuditCategory = Literal["trading_policy", "allocation", "onboarding"]
BrokerConfigurationAuditOutcome = Literal["saved", "denied", "warning"]
BrokerAccountExecutionPosture = Literal["monitor_only", "paper", "sandbox", "live"]
BrokerAccountOnboardingCandidateState = Literal[
    "available",
    "already_configured",
    "disabled",
    "blocked",
    "unavailable",
]
BrokerAccountOnboardingDiscoveryStatus = Literal[
    "completed",
    "provider_unavailable",
    "not_connected",
    "failed",
]
BrokerAccountActionType = Literal[
    "reconnect",
    "pause_sync",
    "resume_sync",
    "refresh",
    "acknowledge_alert",
    "update_trading_policy",
    "update_allocation",
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
    canReadTradingPolicy: bool = False
    canWriteTradingPolicy: bool = False
    canReadAllocation: bool = False
    canWriteAllocation: bool = False
    canReleaseTradeConfirmation: bool = False
    readOnlyReason: str | None = None

    @field_validator("readOnlyReason", mode="before")
    @classmethod
    def normalize_read_only_reason(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class BrokerPositionSizeLimit(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mode: BrokerPositionSizeMode = "pct_of_allocatable_capital"
    value: float = Field(..., gt=0.0)

    @model_validator(mode="after")
    def validate_limit(self) -> "BrokerPositionSizeLimit":
        if self.mode == "pct_of_allocatable_capital" and self.value > 100:
            raise ValueError("Percentage position limits cannot exceed 100.")
        return self


class BrokerTradingPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    maxOpenPositions: int | None = Field(default=None, ge=1)
    maxSinglePositionExposure: BrokerPositionSizeLimit | None = None
    allowedSides: list[BrokerPolicySide] = Field(default_factory=lambda: ["long"])
    allowedAssetClasses: list[BrokerPolicyAssetClass] = Field(default_factory=lambda: ["equity"])
    requireOrderConfirmation: bool = False

    @field_validator("allowedSides", "allowedAssetClasses", mode="before")
    @classmethod
    def normalize_literal_lists(cls, value: object) -> list[str]:
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValueError("Expected a list.")
        normalized: list[str] = []
        for item in value:
            text = str(item or "").strip().lower()
            if text and text not in normalized:
                normalized.append(text)
        return normalized

    @model_validator(mode="after")
    def validate_policy(self) -> "BrokerTradingPolicy":
        if not self.allowedSides:
            raise ValueError("allowedSides must include at least one side.")
        if not self.allowedAssetClasses:
            raise ValueError("allowedAssetClasses must include at least one asset class.")
        return self


class BrokerStrategyReference(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    strategyName: str = Field(..., min_length=1, max_length=128)
    strategyVersion: int = Field(..., ge=1)

    @field_validator("strategyName", mode="before")
    @classmethod
    def normalize_strategy_name(cls, value: object) -> str:
        return _normalize_required_text(value, "strategyName")


class BrokerStrategyAllocationItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sleeveId: str = Field(..., min_length=1, max_length=128)
    sleeveName: str = ""
    strategy: BrokerStrategyReference
    allocationMode: BrokerAllocationMode = "percent"
    targetWeightPct: float | None = Field(default=None, ge=0.0, le=100.0)
    targetNotionalBaseCcy: float | None = Field(default=None, gt=0.0)
    derivedWeightPct: float | None = Field(default=None, ge=0.0, le=100.0)
    enabled: bool = True
    notes: str = ""

    @field_validator("sleeveId", mode="before")
    @classmethod
    def normalize_sleeve_id(cls, value: object) -> str:
        return _normalize_required_text(value, "sleeveId")

    @field_validator("sleeveName", "notes", mode="before")
    @classmethod
    def normalize_text_fields(cls, value: object) -> str:
        return str(value or "").strip()

    @model_validator(mode="after")
    def validate_target(self) -> "BrokerStrategyAllocationItem":
        if self.allocationMode == "percent":
            if self.targetWeightPct is None:
                raise ValueError("Percent allocations require targetWeightPct.")
            if self.targetNotionalBaseCcy is not None:
                raise ValueError("Percent allocations do not accept targetNotionalBaseCcy.")
            return self

        if self.targetNotionalBaseCcy is None:
            raise ValueError("Notional allocations require targetNotionalBaseCcy.")
        if self.targetWeightPct is not None:
            raise ValueError("Notional allocations do not accept targetWeightPct.")
        return self


class BrokerStrategyAllocationSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    portfolioName: str | None = Field(default=None, min_length=1, max_length=128)
    portfolioVersion: int | None = Field(default=None, ge=1)
    allocationMode: BrokerAllocationMode = "percent"
    allocatableCapital: float | None = Field(default=None, ge=0.0)
    allocatedPercent: float | None = Field(default=None, ge=0.0, le=100.01)
    allocatedNotionalBaseCcy: float | None = Field(default=None, ge=0.0)
    remainingPercent: float | None = Field(default=None, ge=0.0, le=100.01)
    remainingNotionalBaseCcy: float | None = Field(default=None, ge=0.0)
    sharedActivePortfolio: bool = False
    effectiveFrom: date | None = None
    items: list[BrokerStrategyAllocationItem] = Field(default_factory=list)

    @field_validator("portfolioName", mode="before")
    @classmethod
    def normalize_portfolio_name(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class BrokerAccountConfigurationAuditRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    auditId: str = Field(..., min_length=1, max_length=128)
    accountId: str = Field(..., min_length=1, max_length=128)
    category: BrokerConfigurationAuditCategory
    outcome: BrokerConfigurationAuditOutcome = "saved"
    requestedAt: datetime
    actor: str | None = Field(default=None, min_length=1, max_length=128)
    requestId: str | None = Field(default=None, min_length=1, max_length=160)
    grantedRoles: list[str] = Field(default_factory=list)
    summary: str = ""
    before: dict[str, Any] = Field(default_factory=dict)
    after: dict[str, Any] = Field(default_factory=dict)
    denialReason: str | None = None

    @field_validator("auditId", "accountId", mode="before")
    @classmethod
    def normalize_required_text_fields(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator("actor", "requestId", "denialReason", mode="before")
    @classmethod
    def normalize_optional_text_fields(cls, value: object) -> str | None:
        return _normalize_optional_text(value)

    @field_validator("summary", mode="before")
    @classmethod
    def normalize_summary(cls, value: object) -> str:
        return str(value or "").strip()


class BrokerAccountConfiguration(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accountId: str = Field(..., min_length=1, max_length=128)
    accountName: str | None = Field(default=None, min_length=1, max_length=128)
    baseCurrency: str = Field(default="USD", min_length=3, max_length=3)
    configurationVersion: int = Field(default=1, ge=1)
    requestedPolicy: BrokerTradingPolicy = Field(default_factory=BrokerTradingPolicy)
    effectivePolicy: BrokerTradingPolicy = Field(default_factory=BrokerTradingPolicy)
    capabilities: BrokerCapabilityFlags = Field(default_factory=BrokerCapabilityFlags)
    allocation: BrokerStrategyAllocationSummary = Field(default_factory=BrokerStrategyAllocationSummary)
    warnings: list[str] = Field(default_factory=list)
    updatedAt: datetime | None = None
    updatedBy: str | None = Field(default=None, min_length=1, max_length=128)
    audit: list[BrokerAccountConfigurationAuditRecord] = Field(default_factory=list)

    @field_validator("accountId", mode="before")
    @classmethod
    def normalize_account_id(cls, value: object) -> str:
        return _normalize_required_text(value, "accountId")

    @field_validator("accountName", "updatedBy", mode="before")
    @classmethod
    def normalize_optional_text_fields(cls, value: object) -> str | None:
        return _normalize_optional_text(value)

    @field_validator("baseCurrency", mode="before")
    @classmethod
    def normalize_configuration_base_currency(cls, value: object) -> str:
        return _normalize_currency(value)

    @field_validator("warnings", mode="before")
    @classmethod
    def normalize_warning_list(cls, value: object) -> list[str]:
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValueError("warnings must be a list.")
        return [str(item).strip() for item in value if str(item).strip()]


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
    configurationVersion: int | None = Field(default=None, ge=1)
    allocationSummary: BrokerStrategyAllocationSummary | None = None
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
    configuration: BrokerAccountConfiguration | None = None

    @field_validator("tradingBlockedReason", mode="before")
    @classmethod
    def normalize_trading_blocked_reason(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class BrokerAccountListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accounts: list[BrokerAccountSummary] = Field(default_factory=list)
    generatedAt: datetime | None = None


class BrokerAccountOnboardingCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidateId: str = Field(..., min_length=1, max_length=160)
    provider: BrokerVendor
    environment: Literal["paper", "sandbox", "live"]
    suggestedAccountId: str = Field(..., min_length=1, max_length=128)
    displayName: str = Field(..., min_length=1, max_length=128)
    accountNumberMasked: str | None = Field(default=None, min_length=1, max_length=32)
    baseCurrency: str = Field(default="USD", min_length=3, max_length=3)
    state: BrokerAccountOnboardingCandidateState = "available"
    stateReason: str | None = None
    existingAccountId: str | None = Field(default=None, min_length=1, max_length=128)
    allowedExecutionPostures: list[BrokerAccountExecutionPosture] = Field(default_factory=lambda: ["monitor_only"])
    blockedExecutionPostureReasons: dict[str, str] = Field(default_factory=dict)
    canOnboard: bool = True

    @field_validator("candidateId", "suggestedAccountId", "displayName", mode="before")
    @classmethod
    def normalize_required_text_fields(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator("accountNumberMasked", "stateReason", "existingAccountId", mode="before")
    @classmethod
    def normalize_optional_text_fields(cls, value: object) -> str | None:
        return _normalize_optional_text(value)

    @field_validator("baseCurrency", mode="before")
    @classmethod
    def normalize_base_currency(cls, value: object) -> str:
        return _normalize_currency(value)

    @field_validator("allowedExecutionPostures", mode="before")
    @classmethod
    def normalize_allowed_postures(cls, value: object) -> list[str]:
        if value is None:
            return ["monitor_only"]
        if not isinstance(value, list):
            raise ValueError("allowedExecutionPostures must be a list.")
        normalized: list[str] = []
        for item in value:
            text = str(item or "").strip().lower()
            if text and text not in normalized:
                normalized.append(text)
        return normalized or ["monitor_only"]

    @field_validator("blockedExecutionPostureReasons", mode="before")
    @classmethod
    def normalize_blocked_posture_reasons(cls, value: object) -> dict[str, str]:
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise ValueError("blockedExecutionPostureReasons must be an object.")
        return {
            str(key).strip(): str(reason).strip()
            for key, reason in value.items()
            if str(key).strip() and str(reason).strip()
        }


class BrokerAccountOnboardingCandidateListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidates: list[BrokerAccountOnboardingCandidate] = Field(default_factory=list)
    discoveryStatus: BrokerAccountOnboardingDiscoveryStatus = "completed"
    message: str = ""
    generatedAt: datetime | None = None

    @field_validator("message", mode="before")
    @classmethod
    def normalize_message(cls, value: object) -> str:
        return str(value or "").strip()


class BrokerAccountOnboardingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidateId: str = Field(..., min_length=1, max_length=160)
    provider: BrokerVendor
    environment: Literal["paper", "sandbox", "live"]
    displayName: str = Field(..., min_length=1, max_length=128)
    readiness: BrokerTradeReadiness = "review"
    executionPosture: BrokerAccountExecutionPosture = "monitor_only"
    initialRefresh: bool = True
    reason: str = Field(..., min_length=1, max_length=500)

    @field_validator("candidateId", "displayName", mode="before")
    @classmethod
    def normalize_required_text_fields(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator("reason", mode="before")
    @classmethod
    def normalize_reason(cls, value: object) -> str:
        return _normalize_required_text(value, "reason")


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


class BrokerTradingPolicyUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expectedConfigurationVersion: int | None = Field(default=None, ge=1)
    requestedPolicy: BrokerTradingPolicy


class BrokerAccountAllocationUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expectedConfigurationVersion: int | None = Field(default=None, ge=1)
    allocationMode: BrokerAllocationMode = "percent"
    allocatableCapital: float | None = Field(default=None, gt=0.0)
    effectiveFrom: date | None = None
    items: list[BrokerStrategyAllocationItem] = Field(default_factory=list)
    notes: str = ""

    @field_validator("notes", mode="before")
    @classmethod
    def normalize_allocation_notes(cls, value: object) -> str:
        return str(value or "").strip()

    @model_validator(mode="after")
    def validate_allocation_request(self) -> "BrokerAccountAllocationUpdateRequest":
        if not self.items:
            raise ValueError("items must include at least one strategy allocation.")

        enabled_items = [item for item in self.items if item.enabled]
        if not enabled_items:
            raise ValueError("At least one strategy allocation must be enabled.")

        seen_sleeve_ids: set[str] = set()
        for item in self.items:
            if item.sleeveId in seen_sleeve_ids:
                raise ValueError(f"Duplicate sleeveId '{item.sleeveId}'.")
            seen_sleeve_ids.add(item.sleeveId)
            if item.allocationMode != self.allocationMode:
                raise ValueError("Mixed allocation modes are not supported in a single request.")

        if self.allocationMode == "percent":
            total = round(sum(float(item.targetWeightPct or 0.0) for item in enabled_items), 2)
            if abs(total - 100.0) > 0.01:
                raise ValueError("Enabled targetWeightPct values must sum to 100.00 +/- 0.01.")
            return self

        if self.allocatableCapital is None:
            raise ValueError("allocatableCapital is required for notional allocations.")
        allocated = sum(float(item.targetNotionalBaseCcy or 0.0) for item in enabled_items)
        if allocated - float(self.allocatableCapital) > 0.01:
            raise ValueError("Notional allocations cannot exceed allocatableCapital.")
        return self


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


class BrokerAccountOnboardingResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account: BrokerAccountSummary
    configuration: BrokerAccountConfiguration | None = None
    created: bool = True
    reenabled: bool = False
    refreshAction: BrokerAccountActionResponse | None = None
    audit: BrokerAccountConfigurationAuditRecord | None = None
    message: str = ""
    generatedAt: datetime | None = None

    @field_validator("message", mode="before")
    @classmethod
    def normalize_message(cls, value: object) -> str:
        return str(value or "").strip()
