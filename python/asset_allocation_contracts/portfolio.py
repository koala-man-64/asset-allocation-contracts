from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

PORTFOLIO_WEIGHT_TOLERANCE = 1e-6

PortfolioStatus = Literal["draft", "active", "archived"]
PortfolioMode = Literal["internal_model_managed"]
PortfolioAccountingDepth = Literal["position_level"]
PortfolioCadenceMode = Literal["strategy_native"]
PortfolioRebalanceCadence = Literal["daily", "weekly", "monthly"]
PortfolioAllocationMode = Literal["percent", "notional_base_ccy"]
PortfolioAssignmentStatus = Literal["scheduled", "active", "ended"]
LedgerEventType = Literal[
    "opening_balance",
    "deposit",
    "withdrawal",
    "fee",
    "dividend",
    "rebalance_buy",
    "rebalance_sell",
    "correction",
]
FreshnessState = Literal["fresh", "stale", "error", "missing"]
PortfolioDataDomain = Literal["valuation", "positions", "risk", "attribution", "ledger", "alerts"]
PortfolioAlertSeverity = Literal["info", "warning", "critical"]
PortfolioAlertStatus = Literal["open", "acknowledged", "resolved"]
TradeSide = Literal["buy", "sell"]
PortfolioForecastHorizon = Literal["1M", "3M", "6M"]
PortfolioForecastAssumption = Literal[
    "current",
    "trending_up",
    "trending_down",
    "mean_reverting",
    "low_volatility",
    "high_volatility",
    "liquidity_stress",
    "macro_alignment",
    "unclassified",
]
PortfolioForecastConfidence = Literal["high", "medium", "low", "thin"]
PortfolioForecastSampleMode = Literal["regime-conditioned", "fallback-history", "insufficient-history"]
PortfolioRebalanceBasis = Literal["anchor", "cadence", "unknown"]


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


def _normalize_optional_symbol(value: object) -> str | None:
    normalized = _normalize_optional_text(value)
    return normalized.upper() if normalized else None


def _normalize_currency(value: object) -> str:
    normalized = str(value or "").strip().upper()
    if len(normalized) != 3:
        raise ValueError("baseCurrency must be a 3-letter ISO code.")
    return normalized


class StrategyVersionReference(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    strategyName: str = Field(..., min_length=1, max_length=128)
    strategyVersion: int = Field(..., ge=1)

    @field_validator("strategyName", mode="before")
    @classmethod
    def normalize_strategy_name(cls, value: object) -> str:
        return _normalize_required_text(value, "strategyName")


class PortfolioSleeveAllocation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sleeveId: str = Field(..., min_length=1, max_length=128)
    sleeveName: str = ""
    strategy: StrategyVersionReference
    allocationMode: PortfolioAllocationMode = "percent"
    targetWeight: float | None = Field(default=None, ge=0.0, le=1.0)
    targetNotionalBaseCcy: float | None = Field(default=None, gt=0.0)
    derivedWeight: float | None = Field(default=None, ge=0.0, le=1.0)
    minWeight: float | None = Field(default=None, ge=0.0, le=1.0)
    maxWeight: float | None = Field(default=None, ge=0.0, le=1.0)
    enabled: bool = True
    rebalancePriority: int = Field(default=0, ge=0)
    notes: str = ""

    @field_validator("sleeveId", mode="before")
    @classmethod
    def normalize_sleeve_id(cls, value: object) -> str:
        return _normalize_required_text(value, "sleeveId")

    @field_validator("sleeveName", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> str:
        return str(value or "").strip()

    @model_validator(mode="after")
    def validate_bounds(self) -> "PortfolioSleeveAllocation":
        if self.allocationMode == "percent":
            if self.targetWeight is None:
                raise ValueError("Percent allocations require targetWeight.")
            if self.targetNotionalBaseCcy is not None:
                raise ValueError("Percent allocations do not accept targetNotionalBaseCcy.")
            if self.minWeight is not None and self.minWeight > self.targetWeight:
                raise ValueError("minWeight cannot exceed targetWeight.")
            if self.maxWeight is not None and self.maxWeight < self.targetWeight:
                raise ValueError("maxWeight cannot be below targetWeight.")
            if self.minWeight is not None and self.maxWeight is not None and self.minWeight > self.maxWeight:
                raise ValueError("minWeight cannot exceed maxWeight.")
            return self

        if self.targetNotionalBaseCcy is None:
            raise ValueError("Notional allocations require targetNotionalBaseCcy.")
        if self.targetWeight is not None:
            raise ValueError("Notional allocations do not accept targetWeight.")
        if self.minWeight is not None or self.maxWeight is not None:
            raise ValueError("Notional allocations do not accept minWeight or maxWeight in v1.")
        return self


class PortfolioDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=128)
    description: str = ""
    benchmarkSymbol: str | None = Field(default=None, min_length=1, max_length=32)
    status: PortfolioStatus = "draft"
    latestVersion: int | None = Field(default=None, ge=1)
    activeVersion: int | None = Field(default=None, ge=1)
    createdAt: datetime | None = None
    updatedAt: datetime | None = None

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: object) -> str:
        return _normalize_required_text(value, "name")

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value: object) -> str:
        return str(value or "").strip()

    @field_validator("benchmarkSymbol", mode="before")
    @classmethod
    def normalize_benchmark_symbol(cls, value: object) -> str | None:
        return _normalize_optional_symbol(value)


class PortfolioRevision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    portfolioName: str = Field(..., min_length=1, max_length=128)
    version: int = Field(..., ge=1)
    description: str = ""
    benchmarkSymbol: str | None = Field(default=None, min_length=1, max_length=32)
    allocationMode: PortfolioAllocationMode = "percent"
    allocatableCapital: float | None = Field(default=None, gt=0.0)
    allocations: list[PortfolioSleeveAllocation] = Field(..., min_length=1)
    notes: str = ""
    publishedAt: datetime | None = None
    createdAt: datetime | None = None
    createdBy: str | None = Field(default=None, min_length=1, max_length=128)

    @field_validator("portfolioName", mode="before")
    @classmethod
    def normalize_portfolio_name(cls, value: object) -> str:
        return _normalize_required_text(value, "portfolioName")

    @field_validator("description", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> str:
        return str(value or "").strip()

    @field_validator("benchmarkSymbol", mode="before")
    @classmethod
    def normalize_benchmark_symbol(cls, value: object) -> str | None:
        return _normalize_optional_symbol(value)

    @field_validator("createdBy", mode="before")
    @classmethod
    def normalize_created_by(cls, value: object) -> str | None:
        return _normalize_optional_text(value)

    @model_validator(mode="after")
    def validate_allocations(self) -> "PortfolioRevision":
        seen_sleeve_ids: set[str] = set()
        enabled_allocations = [allocation for allocation in self.allocations if allocation.enabled]
        for allocation in self.allocations:
            if allocation.sleeveId in seen_sleeve_ids:
                raise ValueError(f"Duplicate sleeveId '{allocation.sleeveId}'.")
            seen_sleeve_ids.add(allocation.sleeveId)
            if allocation.allocationMode != self.allocationMode:
                raise ValueError("Mixed allocation modes are not supported in a single portfolio revision.")

        if not enabled_allocations:
            raise ValueError("At least one allocation must be enabled.")

        if self.allocationMode == "percent":
            enabled_total = sum(float(allocation.targetWeight or 0.0) for allocation in enabled_allocations)
            if abs(enabled_total - 1.0) > PORTFOLIO_WEIGHT_TOLERANCE:
                raise ValueError("Enabled target weights must sum to 1.0.")
            return self

        if self.allocatableCapital is None:
            raise ValueError("allocatableCapital is required for notional allocation mode.")
        enabled_total_notional = sum(
            float(allocation.targetNotionalBaseCcy or 0.0) for allocation in enabled_allocations
        )
        if enabled_total_notional - float(self.allocatableCapital) > 0.01:
            raise ValueError("Enabled notional targets cannot exceed allocatableCapital.")
        return self


class PortfolioAccount(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accountId: str = Field(..., min_length=1, max_length=128)
    name: str = Field(..., min_length=1, max_length=128)
    description: str = ""
    status: PortfolioStatus = "draft"
    mode: PortfolioMode = "internal_model_managed"
    accountingDepth: PortfolioAccountingDepth = "position_level"
    cadenceMode: PortfolioCadenceMode = "strategy_native"
    rebalanceCadence: PortfolioRebalanceCadence = "weekly"
    rebalanceAnchor: str = Field(default="Strategy native cadence", min_length=1, max_length=160)
    baseCurrency: str = Field(default="USD", min_length=3, max_length=3)
    benchmarkSymbol: str | None = Field(default=None, min_length=1, max_length=32)
    inceptionDate: date
    mandate: str = ""
    latestRevision: int | None = Field(default=None, ge=1)
    activeRevision: int | None = Field(default=None, ge=1)
    activePortfolioName: str | None = Field(default=None, min_length=1, max_length=128)
    activePortfolioVersion: int | None = Field(default=None, ge=1)
    createdAt: datetime | None = None
    updatedAt: datetime | None = None
    lastMaterializedAt: datetime | None = None
    openAlertCount: int = Field(default=0, ge=0)

    @field_validator("accountId", "name", mode="before")
    @classmethod
    def normalize_required_text(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator("description", "mandate", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> str:
        return str(value or "").strip()

    @field_validator("rebalanceAnchor", mode="before")
    @classmethod
    def normalize_rebalance_anchor(cls, value: object) -> str:
        return _normalize_required_text(value, "rebalanceAnchor")

    @field_validator("baseCurrency", mode="before")
    @classmethod
    def normalize_base_currency(cls, value: object) -> str:
        return _normalize_currency(value)

    @field_validator("benchmarkSymbol", mode="before")
    @classmethod
    def normalize_benchmark_symbol(cls, value: object) -> str | None:
        return _normalize_optional_symbol(value)

    @field_validator("activePortfolioName", mode="before")
    @classmethod
    def normalize_active_portfolio_name(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class PortfolioAccountRevision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accountId: str = Field(..., min_length=1, max_length=128)
    version: int = Field(..., ge=1)
    name: str = Field(..., min_length=1, max_length=128)
    description: str = ""
    mandate: str = ""
    status: PortfolioStatus = "draft"
    mode: PortfolioMode = "internal_model_managed"
    accountingDepth: PortfolioAccountingDepth = "position_level"
    cadenceMode: PortfolioCadenceMode = "strategy_native"
    rebalanceCadence: PortfolioRebalanceCadence = "weekly"
    rebalanceAnchor: str = Field(default="Strategy native cadence", min_length=1, max_length=160)
    baseCurrency: str = Field(default="USD", min_length=3, max_length=3)
    benchmarkSymbol: str | None = Field(default=None, min_length=1, max_length=32)
    inceptionDate: date
    notes: str = ""
    createdAt: datetime | None = None
    createdBy: str | None = Field(default=None, min_length=1, max_length=128)

    @field_validator("accountId", "name", mode="before")
    @classmethod
    def normalize_required_text(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator("description", "mandate", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> str:
        return str(value or "").strip()

    @field_validator("rebalanceAnchor", mode="before")
    @classmethod
    def normalize_rebalance_anchor(cls, value: object) -> str:
        return _normalize_required_text(value, "rebalanceAnchor")

    @field_validator("baseCurrency", mode="before")
    @classmethod
    def normalize_base_currency(cls, value: object) -> str:
        return _normalize_currency(value)

    @field_validator("benchmarkSymbol", mode="before")
    @classmethod
    def normalize_benchmark_symbol(cls, value: object) -> str | None:
        return _normalize_optional_symbol(value)

    @field_validator("createdBy", mode="before")
    @classmethod
    def normalize_created_by(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class PortfolioAssignment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assignmentId: str = Field(..., min_length=1, max_length=128)
    accountId: str = Field(..., min_length=1, max_length=128)
    accountVersion: int = Field(..., ge=1)
    portfolioName: str = Field(..., min_length=1, max_length=128)
    portfolioVersion: int = Field(..., ge=1)
    effectiveFrom: date
    effectiveTo: date | None = None
    status: PortfolioAssignmentStatus = "scheduled"
    notes: str = ""
    createdAt: datetime | None = None

    @field_validator("assignmentId", "accountId", "portfolioName", mode="before")
    @classmethod
    def normalize_required_text(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator("notes", mode="before")
    @classmethod
    def normalize_notes(cls, value: object) -> str:
        return str(value or "").strip()

    @model_validator(mode="after")
    def validate_dates(self) -> "PortfolioAssignment":
        if self.effectiveTo is not None and self.effectiveTo < self.effectiveFrom:
            raise ValueError("effectiveTo cannot be before effectiveFrom.")
        return self


class PortfolioLedgerEventPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    effectiveAt: datetime
    eventType: LedgerEventType
    currency: str = Field(default="USD", min_length=3, max_length=3)
    cashAmount: float
    symbol: str | None = Field(default=None, min_length=1, max_length=32)
    quantity: float | None = Field(default=None, gt=0)
    price: float | None = Field(default=None, gt=0)
    commission: float = Field(default=0.0, ge=0.0)
    slippageCost: float = Field(default=0.0, ge=0.0)
    description: str = ""

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, value: object) -> str:
        return _normalize_currency(value)

    @field_validator("symbol", mode="before")
    @classmethod
    def normalize_symbol(cls, value: object) -> str | None:
        return _normalize_optional_symbol(value)

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value: object) -> str:
        return str(value or "").strip()

    @model_validator(mode="after")
    def validate_event_shape(self) -> "PortfolioLedgerEventPayload":
        cash_only_events = {"opening_balance", "deposit", "withdrawal", "fee", "dividend", "correction"}
        trade_events = {"rebalance_buy", "rebalance_sell"}

        if self.eventType in cash_only_events:
            if self.symbol is not None or self.quantity is not None or self.price is not None:
                raise ValueError(f"{self.eventType} does not accept symbol, quantity, or price.")
            if self.eventType in {"opening_balance", "deposit", "dividend"} and self.cashAmount <= 0:
                raise ValueError(f"{self.eventType} requires cashAmount > 0.")
            if self.eventType in {"withdrawal", "fee"} and self.cashAmount >= 0:
                raise ValueError(f"{self.eventType} requires cashAmount < 0.")
            if self.eventType == "correction" and self.cashAmount == 0:
                raise ValueError("correction requires a non-zero cashAmount.")
            if self.commission or self.slippageCost:
                raise ValueError(f"{self.eventType} does not accept commission or slippageCost.")
            return self

        if self.eventType in trade_events:
            if self.symbol is None or self.quantity is None or self.price is None:
                raise ValueError(f"{self.eventType} requires symbol, quantity, and price.")
            if self.eventType == "rebalance_buy" and self.cashAmount >= 0:
                raise ValueError("rebalance_buy requires cashAmount < 0.")
            if self.eventType == "rebalance_sell" and self.cashAmount <= 0:
                raise ValueError("rebalance_sell requires cashAmount > 0.")
            return self

        raise ValueError(f"Unsupported eventType '{self.eventType}'.")


class PortfolioLedgerEvent(PortfolioLedgerEventPayload):
    model_config = ConfigDict(extra="forbid")

    eventId: str = Field(..., min_length=1, max_length=128)
    accountId: str = Field(..., min_length=1, max_length=128)

    @field_validator("eventId", "accountId", mode="before")
    @classmethod
    def normalize_required_text(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)


class FreshnessStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    domain: PortfolioDataDomain
    state: FreshnessState
    asOf: datetime | None = None
    checkedAt: datetime | None = None
    reason: str = ""

    @field_validator("reason", mode="before")
    @classmethod
    def normalize_reason(cls, value: object) -> str:
        return str(value or "").strip()


class PortfolioAlert(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alertId: str = Field(..., min_length=1, max_length=128)
    accountId: str = Field(..., min_length=1, max_length=128)
    severity: PortfolioAlertSeverity
    status: PortfolioAlertStatus = "open"
    code: str = Field(..., min_length=1, max_length=128)
    title: str = Field(..., min_length=1, max_length=160)
    description: str = ""
    detectedAt: datetime
    acknowledgedAt: datetime | None = None
    acknowledgedBy: str | None = Field(default=None, min_length=1, max_length=128)
    resolvedAt: datetime | None = None
    asOf: date | None = None

    @field_validator("alertId", "accountId", "code", "title", mode="before")
    @classmethod
    def normalize_required_text(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value: object) -> str:
        return str(value or "").strip()

    @field_validator("acknowledgedBy", mode="before")
    @classmethod
    def normalize_acknowledged_by(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class StrategySliceAttribution(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asOf: date
    sleeveId: str = Field(..., min_length=1, max_length=128)
    strategyName: str = Field(..., min_length=1, max_length=128)
    strategyVersion: int = Field(..., ge=1)
    targetWeight: float = Field(..., ge=0.0, le=1.0)
    actualWeight: float = Field(..., ge=0.0, le=1.0)
    marketValue: float
    grossExposure: float = 0.0
    netExposure: float = 0.0
    pnlContribution: float = 0.0
    returnContribution: float = 0.0
    drawdownContribution: float = 0.0
    turnover: float | None = Field(default=None, ge=0.0)
    sinceInceptionReturn: float | None = None

    @field_validator("sleeveId", "strategyName", mode="before")
    @classmethod
    def normalize_required_text(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)


class PortfolioPositionContributor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sleeveId: str = Field(..., min_length=1, max_length=128)
    strategyName: str = Field(..., min_length=1, max_length=128)
    strategyVersion: int = Field(..., ge=1)
    quantity: float
    marketValue: float
    weight: float = Field(..., ge=0.0, le=1.0)

    @field_validator("sleeveId", "strategyName", mode="before")
    @classmethod
    def normalize_required_text(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)


class PortfolioPosition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asOf: date
    symbol: str = Field(..., min_length=1, max_length=32)
    quantity: float
    marketValue: float
    weight: float = Field(..., ge=0.0, le=1.0)
    averageCost: float | None = Field(default=None, ge=0.0)
    lastPrice: float | None = Field(default=None, ge=0.0)
    unrealizedPnl: float | None = None
    realizedPnl: float | None = None
    contributors: list[PortfolioPositionContributor] = Field(default_factory=list)

    @field_validator("symbol", mode="before")
    @classmethod
    def normalize_symbol(cls, value: object) -> str:
        normalized = _normalize_optional_symbol(value)
        if normalized is None:
            raise ValueError("symbol is required.")
        return normalized


class PortfolioSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accountId: str = Field(..., min_length=1, max_length=128)
    accountName: str = Field(..., min_length=1, max_length=128)
    asOf: date
    nav: float
    cash: float
    grossExposure: float
    netExposure: float
    sinceInceptionPnl: float
    sinceInceptionReturn: float
    currentDrawdown: float
    maxDrawdown: float | None = None
    openAlertCount: int = Field(default=0, ge=0)
    activeAssignment: PortfolioAssignment | None = None
    freshness: list[FreshnessStatus] = Field(default_factory=list)
    slices: list[StrategySliceAttribution] = Field(default_factory=list)

    @field_validator("accountId", "accountName", mode="before")
    @classmethod
    def normalize_required_text(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)


class PortfolioHistoryPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asOf: date
    nav: float
    cash: float
    grossExposure: float
    netExposure: float
    periodPnl: float | None = None
    periodReturn: float | None = None
    cumulativePnl: float | None = None
    cumulativeReturn: float | None = None
    drawdown: float | None = None
    turnover: float | None = Field(default=None, ge=0.0)
    costDragBps: float | None = None


class PortfolioForecastResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accountId: str = Field(..., min_length=1, max_length=128)
    asOf: date | None = None
    modelName: str = Field(..., min_length=1, max_length=128)
    modelVersion: int | None = Field(default=None, ge=1)
    benchmarkSymbol: str | None = Field(default=None, min_length=1, max_length=32)
    horizon: PortfolioForecastHorizon
    assumption: PortfolioForecastAssumption
    costDragOverrideBps: float = 0.0
    expectedReturnPct: float | None = None
    expectedActiveReturnPct: float | None = None
    downsidePct: float | None = None
    upsidePct: float | None = None
    confidence: PortfolioForecastConfidence
    confidenceLabel: str = Field(..., min_length=1, max_length=64)
    sampleSize: int = Field(default=0, ge=0)
    sampleMode: PortfolioForecastSampleMode
    appliedRegimeCode: str = Field(..., min_length=1, max_length=64)
    notes: list[str] = Field(default_factory=list)

    @field_validator("accountId", "modelName", "confidenceLabel", "appliedRegimeCode", mode="before")
    @classmethod
    def normalize_required_text(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator("benchmarkSymbol", mode="before")
    @classmethod
    def normalize_benchmark_symbol(cls, value: object) -> str | None:
        return _normalize_optional_symbol(value)

    @field_validator("notes", mode="before")
    @classmethod
    def normalize_notes(cls, value: object) -> list[str]:
        if value is None:
            return []
        return [str(item).strip() for item in value if str(item).strip()]


class PortfolioNextRebalanceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accountId: str = Field(..., min_length=1, max_length=128)
    asOf: date | None = None
    rebalanceCadence: PortfolioRebalanceCadence
    anchorText: str = Field(..., min_length=1, max_length=160)
    nextDate: date | None = None
    inferred: bool = False
    basis: PortfolioRebalanceBasis = "unknown"
    reason: str = ""

    @field_validator("accountId", "anchorText", mode="before")
    @classmethod
    def normalize_required_text(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator("reason", mode="before")
    @classmethod
    def normalize_reason(cls, value: object) -> str:
        return str(value or "").strip()


class PortfolioPositionListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    positions: list[PortfolioPosition] = Field(default_factory=list)
    total: int = Field(default=0, ge=0)
    limit: int = Field(default=200, ge=1)
    offset: int = Field(default=0, ge=0)


class PortfolioHistoryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    points: list[PortfolioHistoryPoint] = Field(default_factory=list)
    totalPoints: int = Field(default=0, ge=0)
    truncated: bool = False


class PortfolioAlertListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alerts: list[PortfolioAlert] = Field(default_factory=list)
    total: int = Field(default=0, ge=0)
    openCount: int = Field(default=0, ge=0)


class RebalanceTradeProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sleeveId: str = Field(..., min_length=1, max_length=128)
    symbol: str = Field(..., min_length=1, max_length=32)
    side: TradeSide
    quantity: float = Field(..., gt=0.0)
    estimatedPrice: float = Field(..., gt=0.0)
    estimatedNotional: float
    estimatedCommission: float = Field(default=0.0, ge=0.0)
    estimatedSlippageCost: float = Field(default=0.0, ge=0.0)

    @field_validator("sleeveId", mode="before")
    @classmethod
    def normalize_sleeve_id(cls, value: object) -> str:
        return _normalize_required_text(value, "sleeveId")

    @field_validator("symbol", mode="before")
    @classmethod
    def normalize_symbol(cls, value: object) -> str:
        normalized = _normalize_optional_symbol(value)
        if normalized is None:
            raise ValueError("symbol is required.")
        return normalized


class RebalanceProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    proposalId: str = Field(..., min_length=1, max_length=128)
    accountId: str = Field(..., min_length=1, max_length=128)
    asOf: date
    portfolioName: str = Field(..., min_length=1, max_length=128)
    portfolioVersion: int = Field(..., ge=1)
    blocked: bool = False
    warnings: list[str] = Field(default_factory=list)
    blockedReasons: list[str] = Field(default_factory=list)
    estimatedCashImpact: float = 0.0
    estimatedTurnover: float = Field(default=0.0, ge=0.0)
    trades: list[RebalanceTradeProposal] = Field(default_factory=list)

    @field_validator("proposalId", "accountId", "portfolioName", mode="before")
    @classmethod
    def normalize_required_text(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator("warnings", "blockedReasons", mode="before")
    @classmethod
    def normalize_text_list(cls, value: object) -> list[str]:
        if value is None:
            return []
        return [str(item).strip() for item in value if str(item).strip()]


class PortfolioAccountListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accounts: list[PortfolioAccount] = Field(default_factory=list)


class PortfolioAccountDetailResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account: PortfolioAccount
    revision: PortfolioAccountRevision | None = None
    activeAssignment: PortfolioAssignment | None = None
    recentLedgerEvents: list[PortfolioLedgerEvent] = Field(default_factory=list)


class PortfolioListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    portfolios: list[PortfolioDefinition] = Field(default_factory=list)


class PortfolioDefinitionDetailResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    portfolio: PortfolioDefinition
    activeRevision: PortfolioRevision | None = None
    revisions: list[PortfolioRevision] = Field(default_factory=list)


class PortfolioAccountUpsertRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=128)
    description: str = ""
    mandate: str = ""
    rebalanceCadence: PortfolioRebalanceCadence | None = None
    rebalanceAnchor: str | None = Field(default=None, min_length=1, max_length=160)
    baseCurrency: str = Field(default="USD", min_length=3, max_length=3)
    benchmarkSymbol: str | None = Field(default=None, min_length=1, max_length=32)
    inceptionDate: date
    openingCash: float | None = Field(default=None, gt=0.0)
    notes: str = ""

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: object) -> str:
        return _normalize_required_text(value, "name")

    @field_validator("description", "mandate", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> str:
        return str(value or "").strip()

    @field_validator("rebalanceAnchor", mode="before")
    @classmethod
    def normalize_rebalance_anchor(cls, value: object) -> str | None:
        return _normalize_optional_text(value)

    @field_validator("baseCurrency", mode="before")
    @classmethod
    def normalize_base_currency(cls, value: object) -> str:
        return _normalize_currency(value)

    @field_validator("benchmarkSymbol", mode="before")
    @classmethod
    def normalize_benchmark_symbol(cls, value: object) -> str | None:
        return _normalize_optional_symbol(value)


class PortfolioUpsertRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=128)
    description: str = ""
    benchmarkSymbol: str | None = Field(default=None, min_length=1, max_length=32)
    allocationMode: PortfolioAllocationMode = "percent"
    allocatableCapital: float | None = Field(default=None, gt=0.0)
    allocations: list[PortfolioSleeveAllocation] = Field(..., min_length=1)
    notes: str = ""

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: object) -> str:
        return _normalize_required_text(value, "name")

    @field_validator("description", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> str:
        return str(value or "").strip()

    @field_validator("benchmarkSymbol", mode="before")
    @classmethod
    def normalize_benchmark_symbol(cls, value: object) -> str | None:
        return _normalize_optional_symbol(value)

    @model_validator(mode="after")
    def validate_allocations(self) -> "PortfolioUpsertRequest":
        PortfolioRevision(
            portfolioName=self.name,
            version=1,
            description=self.description,
            benchmarkSymbol=self.benchmarkSymbol,
            allocationMode=self.allocationMode,
            allocatableCapital=self.allocatableCapital,
            allocations=self.allocations,
            notes=self.notes,
        )
        return self


class PortfolioAssignmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accountVersion: int = Field(..., ge=1)
    portfolioName: str = Field(..., min_length=1, max_length=128)
    portfolioVersion: int = Field(..., ge=1)
    effectiveFrom: date
    notes: str = ""

    @field_validator("portfolioName", mode="before")
    @classmethod
    def normalize_portfolio_name(cls, value: object) -> str:
        return _normalize_required_text(value, "portfolioName")

    @field_validator("notes", mode="before")
    @classmethod
    def normalize_notes(cls, value: object) -> str:
        return str(value or "").strip()


class PortfolioRebalancePreviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asOf: date
    notes: str = ""

    @field_validator("notes", mode="before")
    @classmethod
    def normalize_notes(cls, value: object) -> str:
        return str(value or "").strip()


class PortfolioRebalanceApplyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    proposalId: str = Field(..., min_length=1, max_length=128)
    executedAt: datetime
    notes: str = ""

    @field_validator("proposalId", mode="before")
    @classmethod
    def normalize_proposal_id(cls, value: object) -> str:
        return _normalize_required_text(value, "proposalId")

    @field_validator("notes", mode="before")
    @classmethod
    def normalize_notes(cls, value: object) -> str:
        return str(value or "").strip()
