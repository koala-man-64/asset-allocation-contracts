from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator, field_validator

from asset_allocation_contracts.backtest import StrategyReferenceInput
from asset_allocation_contracts.broker_accounts import BrokerAlertStatus, BrokerTradingPolicy
from asset_allocation_contracts.options import OptionApprovalLevel, OptionLeg, OptionStrategyId

TradeProvider = Literal["alpaca", "etrade", "schwab", "kalshi"]
TradeEnvironment = Literal["paper", "sandbox", "live"]
TradeReadiness = Literal["ready", "review", "blocked"]
TradeAssetClass = Literal["equity", "etf", "option", "crypto", "mutual_fund", "prediction_market", "unknown"]
TradeOrderSide = Literal["buy", "sell"]
TradeOutcomeSide = Literal["yes", "no", "unknown"]
TradeOrderType = Literal["market", "limit", "stop", "stop_limit"]
TradeTimeInForce = Literal["day", "gtc", "opg", "cls", "ioc", "fok"]
TradeOrderStatus = Literal[
    "draft",
    "previewed",
    "submitted",
    "accepted",
    "partially_filled",
    "filled",
    "cancel_pending",
    "cancelled",
    "rejected",
    "expired",
    "unknown_reconcile_required",
]
TradeRiskCheckStatus = Literal["pass", "warning", "fail"]
TradeAuditEventType = Literal[
    "preview",
    "submit",
    "cancel",
    "status_update",
    "reject",
    "fill",
    "reconcile",
    "system_block",
    "authz_block",
]
TradeDataFreshnessState = Literal["fresh", "stale", "unknown"]
TradeAuditSeverity = Literal["info", "warning", "critical"]
TradeBlotterEventType = Literal[
    "fill",
    "order",
    "cancel",
    "fee",
    "cash_adjustment",
    "dividend",
    "interest",
    "journal",
    "settlement",
    "deposit",
    "withdrawal",
    "other",
]
TradeMetricValueType = Literal["count", "currency"]
TradeMetricStatus = Literal["available", "partial", "unavailable"]

TRADE_SYMBOL_MAX_LENGTH = 128


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


def _normalize_symbol(value: object) -> str:
    normalized = _normalize_required_text(value, "symbol").upper()
    if len(normalized) > TRADE_SYMBOL_MAX_LENGTH:
        raise ValueError(f"symbol must be {TRADE_SYMBOL_MAX_LENGTH} characters or fewer.")
    return normalized


def _normalize_currency(value: object) -> str:
    normalized = str(value or "").strip().upper()
    if len(normalized) != 3:
        raise ValueError("baseCurrency must be a 3-letter ISO code.")
    return normalized


class TradeCapabilityFlags(BaseModel):
    model_config = ConfigDict(extra="forbid")

    canReadAccount: bool = False
    canReadPositions: bool = False
    canReadOrders: bool = False
    canReadHistory: bool = False
    canPreview: bool = False
    canSubmitPaper: bool = False
    canSubmitSandbox: bool = False
    canSubmitLive: bool = False
    canCancel: bool = False
    supportsMarketOrders: bool = False
    supportsLimitOrders: bool = False
    supportsStopOrders: bool = False
    supportsFractionalQuantity: bool = False
    supportsNotionalOrders: bool = False
    supportsEquities: bool = False
    supportsEtfs: bool = False
    supportsOptions: bool = False
    optionApprovalLevel: OptionApprovalLevel | None = None
    supportsOptionChains: bool = False
    supportsOptionGreeks: bool = False
    supportsOptionMultiLegOrders: bool = False
    supportsOptionExercise: bool = False
    readOnly: bool = True
    unsupportedReason: str | None = None

    @field_validator("unsupportedReason", mode="before")
    @classmethod
    def normalize_unsupported_reason(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class TradeDataFreshness(BaseModel):
    model_config = ConfigDict(extra="forbid")

    balancesState: TradeDataFreshnessState = "unknown"
    positionsState: TradeDataFreshnessState = "unknown"
    ordersState: TradeDataFreshnessState = "unknown"
    balancesAsOf: datetime | None = None
    positionsAsOf: datetime | None = None
    ordersAsOf: datetime | None = None
    maxAgeSeconds: int | None = Field(default=None, ge=0)
    staleReason: str | None = None

    @field_validator("staleReason", mode="before")
    @classmethod
    def normalize_stale_reason(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class TradeRiskLimit(BaseModel):
    model_config = ConfigDict(extra="forbid")

    maxOrderNotional: float | None = Field(default=None, gt=0)
    maxDailyNotional: float | None = Field(default=None, gt=0)
    maxShareQuantity: float | None = Field(default=None, gt=0)
    maxOptionContracts: int | None = Field(default=None, ge=1)
    maxOptionPremiumAtRisk: float | None = Field(default=None, gt=0)
    maxDefinedOptionLoss: float | None = Field(default=None, gt=0)
    allowedAssetClasses: list[TradeAssetClass] = Field(default_factory=list)
    allowedOrderTypes: list[TradeOrderType] = Field(default_factory=list)
    allowedOptionStrategies: list[OptionStrategyId] = Field(default_factory=list)
    liveTradingAllowed: bool = False
    liveOptionSubmitAllowed: bool = False
    liveTradingReason: str | None = None

    @field_validator("liveTradingReason", mode="before")
    @classmethod
    def normalize_live_trading_reason(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class TradeRiskCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    checkId: str = Field(..., min_length=1, max_length=128)
    code: str = Field(..., min_length=1, max_length=128)
    label: str = Field(..., min_length=1, max_length=160)
    status: TradeRiskCheckStatus
    severity: TradeAuditSeverity = "info"
    blocking: bool = False
    message: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("checkId", "code", "label", mode="before")
    @classmethod
    def normalize_required_text_fields(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator("message", mode="before")
    @classmethod
    def normalize_message(cls, value: object) -> str:
        return str(value or "").strip()


class TradeNormalizationWarning(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(..., min_length=1, max_length=128)
    message: str = Field(..., min_length=1, max_length=320)
    severity: TradeAuditSeverity = "warning"
    providerField: str | None = Field(default=None, min_length=1, max_length=160)
    rawValue: str | None = Field(default=None, min_length=1, max_length=320)

    @field_validator("code", "message", mode="before")
    @classmethod
    def normalize_required_text_fields(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator("providerField", "rawValue", mode="before")
    @classmethod
    def normalize_optional_text_fields(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class TradePnlSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    realizedPnl: float | None = None
    unrealizedPnl: float | None = None
    dayPnl: float | None = None
    grossExposure: float | None = None
    netExposure: float | None = None
    asOf: datetime | None = None
    # realizedSource discriminates where realizedPnl came from:
    #   "broker"  - the broker reported realized P/L directly on positions or activities
    #               (today: Kalshi via market_positions[].realized_pnl_dollars).
    #   "ledger"  - we computed it ourselves via FIFO cost-basis matching of the
    #               broker_fill_ledger (Alpaca / E*TRADE / Schwab).
    # None means realizedPnl is None and no source applies. This lets the UI surface
    # an honest "Realized from {ledgerHorizonAt} forward" caveat for ledger-derived
    # values where the broker's transaction history window limits how far back we see.
    realizedSource: Literal["broker", "ledger"] | None = None
    ledgerHorizonAt: datetime | None = None


class TradeMetricCoverage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accountCount: int = Field(default=0, ge=0)
    includedAccountCount: int = Field(default=0, ge=0)
    environments: list[TradeEnvironment] = Field(default_factory=list)
    currencies: list[str] = Field(default_factory=list)
    mixedEnvironment: bool = False
    mixedCurrency: bool = False

    @field_validator("currencies", mode="before")
    @classmethod
    def normalize_currencies(cls, value: object) -> list[str]:
        if value is None:
            return []
        return sorted({_normalize_currency(currency) for currency in value})


class TradeMetricSegmentValue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    segmentId: str = Field(..., min_length=1, max_length=128)
    environment: TradeEnvironment
    accountCount: int = Field(default=0, ge=0)
    value: float | None = None
    status: TradeMetricStatus
    asOf: datetime | None = None
    currency: str | None = Field(default=None, min_length=3, max_length=3)

    @field_validator("segmentId", mode="before")
    @classmethod
    def normalize_segment_id(cls, value: object) -> str:
        return _normalize_required_text(value, "segmentId")

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, value: object) -> str | None:
        if value is None:
            return None
        return _normalize_currency(value)


class TradeMetricValue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metricId: str = Field(..., min_length=1, max_length=128)
    label: str = Field(..., min_length=1, max_length=160)
    value: float | None = None
    valueType: TradeMetricValueType
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    status: TradeMetricStatus
    asOf: datetime | None = None
    segments: list[TradeMetricSegmentValue] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @field_validator("metricId", "label", mode="before")
    @classmethod
    def normalize_required_text_fields(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, value: object) -> str | None:
        if value is None:
            return None
        return _normalize_currency(value)

    @field_validator("warnings", mode="before")
    @classmethod
    def normalize_warnings(cls, value: object) -> list[str]:
        if value is None:
            return []
        return [warning for warning in (str(item).strip() for item in value) if warning]


class TradeMetricFeedResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scope: str = Field(..., min_length=1, max_length=128)
    generatedAt: datetime
    metrics: list[TradeMetricValue] = Field(default_factory=list)
    coverage: TradeMetricCoverage = Field(default_factory=TradeMetricCoverage)
    warnings: list[str] = Field(default_factory=list)

    @field_validator("scope", mode="before")
    @classmethod
    def normalize_scope(cls, value: object) -> str:
        return _normalize_required_text(value, "scope")

    @field_validator("warnings", mode="before")
    @classmethod
    def normalize_warnings(cls, value: object) -> list[str]:
        if value is None:
            return []
        return [warning for warning in (str(item).strip() for item in value) if warning]


class TradeDeskAlert(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alertId: str = Field(..., min_length=1, max_length=128)
    accountId: str = Field(..., min_length=1, max_length=128)
    severity: TradeAuditSeverity = "warning"
    status: BrokerAlertStatus = "open"
    code: str = Field(..., min_length=1, max_length=128)
    title: str = Field(..., min_length=1, max_length=160)
    message: str = ""
    blocking: bool = False
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


class TradeAccountSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accountId: str = Field(..., min_length=1, max_length=128)
    name: str = Field(..., min_length=1, max_length=128)
    provider: TradeProvider
    environment: TradeEnvironment
    accountNumberMasked: str | None = Field(default=None, min_length=1, max_length=32)
    baseCurrency: str = Field(default="USD", min_length=3, max_length=3)
    readiness: TradeReadiness = "review"
    readinessReason: str | None = None
    capabilities: TradeCapabilityFlags = Field(default_factory=TradeCapabilityFlags)
    cash: float = 0.0
    buyingPower: float = 0.0
    equity: float = 0.0
    openOrderCount: int = Field(default=0, ge=0)
    positionCount: int = Field(default=0, ge=0)
    unresolvedAlertCount: int = Field(default=0, ge=0)
    killSwitchActive: bool = False
    pnl: TradePnlSnapshot | None = None
    lastSyncedAt: datetime | None = None
    lastTradeAt: datetime | None = None
    snapshotAsOf: datetime | None = None
    freshness: TradeDataFreshness = Field(default_factory=TradeDataFreshness)
    policyVersion: int | None = Field(default=None, ge=1)
    projectedTradingPolicy: BrokerTradingPolicy | None = None
    confirmationRequired: bool = False
    sourceObservedAt: datetime | None = None
    syncRunId: str | None = Field(default=None, min_length=1, max_length=160)
    normalizationWarnings: list[TradeNormalizationWarning] = Field(default_factory=list)
    quarantinedRowCount: int = Field(default=0, ge=0)

    @field_validator("accountId", "name", mode="before")
    @classmethod
    def normalize_required_text_fields(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator("accountNumberMasked", "readinessReason", "syncRunId", mode="before")
    @classmethod
    def normalize_optional_text_fields(cls, value: object) -> str | None:
        return _normalize_optional_text(value)

    @field_validator("baseCurrency", mode="before")
    @classmethod
    def normalize_base_currency(cls, value: object) -> str:
        return _normalize_currency(value)


class TradeAccountDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account: TradeAccountSummary
    restrictions: list[str] = Field(default_factory=list)
    riskLimits: TradeRiskLimit = Field(default_factory=TradeRiskLimit)
    unresolvedAlerts: list[str] = Field(default_factory=list)
    alerts: list["TradeDeskAlert"] = Field(default_factory=list)
    recentAuditEvents: list["TradeDeskAuditEvent"] = Field(default_factory=list)


class TradeAccountListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accounts: list[TradeAccountSummary] = Field(default_factory=list)
    generatedAt: datetime | None = None


class TradeAccountBalanceHistoryPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accountId: str = Field(..., min_length=1, max_length=128)
    provider: TradeProvider
    environment: TradeEnvironment
    asOf: datetime
    balance: float
    equity: float
    cash: float | None = None
    buyingPower: float | None = None
    currency: str = Field(default="USD", min_length=3, max_length=3)
    sourceObservedAt: datetime | None = None
    syncRunId: str | None = Field(default=None, min_length=1, max_length=160)

    @field_validator("accountId", mode="before")
    @classmethod
    def normalize_account_id(cls, value: object) -> str:
        return _normalize_required_text(value, "accountId")

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, value: object) -> str:
        return _normalize_currency(value)

    @field_validator("syncRunId", mode="before")
    @classmethod
    def normalize_sync_run_id(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class TradeAccountBalanceHistoryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accountId: str = Field(..., min_length=1, max_length=128)
    points: list[TradeAccountBalanceHistoryPoint] = Field(default_factory=list)
    totalPoints: int = Field(default=0, ge=0)
    truncated: bool = False
    generatedAt: datetime | None = None

    @field_validator("accountId", mode="before")
    @classmethod
    def normalize_account_id(cls, value: object) -> str:
        return _normalize_required_text(value, "accountId")


class TradePosition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accountId: str = Field(..., min_length=1, max_length=128)
    symbol: str = Field(..., min_length=1, max_length=TRADE_SYMBOL_MAX_LENGTH)
    assetClass: TradeAssetClass = "equity"
    providerPositionId: str | None = Field(default=None, min_length=1, max_length=160)
    providerInstrumentId: str | None = Field(default=None, min_length=1, max_length=160)
    instrumentName: str | None = Field(default=None, min_length=1, max_length=240)
    outcomeSide: TradeOutcomeSide | None = None
    rawProviderStatus: str | None = Field(default=None, min_length=1, max_length=160)
    quantity: float = 0.0
    marketValue: float = 0.0
    averageEntryPrice: float | None = None
    lastPrice: float | None = None
    costBasis: float | None = None
    unrealizedPnl: float | None = None
    unrealizedPnlPercent: float | None = None
    dayPnl: float | None = None
    weight: float | None = None
    asOf: datetime | None = None
    sourceObservedAt: datetime | None = None
    ingestedAt: datetime | None = None
    syncRunId: str | None = Field(default=None, min_length=1, max_length=160)
    sourcePayloadHash: str | None = Field(default=None, min_length=1, max_length=160)
    normalizationWarnings: list[TradeNormalizationWarning] = Field(default_factory=list)
    quarantined: bool = False
    quarantineReason: str | None = Field(default=None, min_length=1, max_length=320)

    @field_validator("accountId", mode="before")
    @classmethod
    def normalize_account_id(cls, value: object) -> str:
        return _normalize_required_text(value, "accountId")

    @field_validator("symbol", mode="before")
    @classmethod
    def normalize_position_symbol(cls, value: object) -> str:
        return _normalize_symbol(value)

    @field_validator(
        "providerPositionId",
        "providerInstrumentId",
        "instrumentName",
        "rawProviderStatus",
        "syncRunId",
        "sourcePayloadHash",
        "quarantineReason",
        mode="before",
    )
    @classmethod
    def normalize_optional_text_fields(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class TradePositionListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accountId: str = Field(..., min_length=1, max_length=128)
    positions: list[TradePosition] = Field(default_factory=list)
    generatedAt: datetime | None = None
    freshness: TradeDataFreshness = Field(default_factory=TradeDataFreshness)
    sourceObservedAt: datetime | None = None
    syncRunId: str | None = Field(default=None, min_length=1, max_length=160)
    normalizationWarnings: list[TradeNormalizationWarning] = Field(default_factory=list)
    unmappedRowCount: int = Field(default=0, ge=0)
    quarantinedRowCount: int = Field(default=0, ge=0)

    @field_validator("accountId", mode="before")
    @classmethod
    def normalize_account_id(cls, value: object) -> str:
        return _normalize_required_text(value, "accountId")

    @field_validator("syncRunId", mode="before")
    @classmethod
    def normalize_sync_run_id(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class TradeOrder(BaseModel):
    model_config = ConfigDict(extra="forbid")

    orderId: str = Field(..., min_length=1, max_length=128)
    accountId: str = Field(..., min_length=1, max_length=128)
    provider: TradeProvider
    environment: TradeEnvironment
    status: TradeOrderStatus
    symbol: str = Field(..., min_length=1, max_length=TRADE_SYMBOL_MAX_LENGTH)
    side: TradeOrderSide
    orderType: TradeOrderType
    timeInForce: TradeTimeInForce = "day"
    assetClass: TradeAssetClass = "equity"
    clientRequestId: str | None = Field(default=None, min_length=1, max_length=128)
    idempotencyKey: str | None = Field(default=None, min_length=1, max_length=160)
    correlationId: str | None = Field(default=None, min_length=1, max_length=160)
    providerOrderId: str | None = Field(default=None, min_length=1, max_length=160)
    providerCorrelationId: str | None = Field(default=None, min_length=1, max_length=160)
    providerInstrumentId: str | None = Field(default=None, min_length=1, max_length=160)
    instrumentName: str | None = Field(default=None, min_length=1, max_length=240)
    outcomeSide: TradeOutcomeSide | None = None
    rawProviderStatus: str | None = Field(default=None, min_length=1, max_length=160)
    quantity: float | None = Field(default=None, gt=0)
    notional: float | None = Field(default=None, gt=0)
    optionStrategyId: OptionStrategyId | None = None
    optionLegs: list[OptionLeg] = Field(default_factory=list)
    limitPrice: float | None = Field(default=None, gt=0)
    stopPrice: float | None = Field(default=None, gt=0)
    estimatedPrice: float | None = None
    estimatedNotional: float | None = None
    filledQuantity: float = Field(default=0.0, ge=0)
    averageFillPrice: float | None = Field(default=None, ge=0)
    submittedAt: datetime | None = None
    acceptedAt: datetime | None = None
    filledAt: datetime | None = None
    cancelledAt: datetime | None = None
    expiresAt: datetime | None = None
    createdAt: datetime | None = None
    updatedAt: datetime | None = None
    sourceObservedAt: datetime | None = None
    ingestedAt: datetime | None = None
    syncRunId: str | None = Field(default=None, min_length=1, max_length=160)
    sourcePayloadHash: str | None = Field(default=None, min_length=1, max_length=160)
    statusReason: str | None = None
    riskChecks: list[TradeRiskCheck] = Field(default_factory=list)
    normalizationWarnings: list[TradeNormalizationWarning] = Field(default_factory=list)
    reconciliationRequired: bool = False

    @field_validator("orderId", "accountId", mode="before")
    @classmethod
    def normalize_required_text_fields(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator(
        "clientRequestId",
        "idempotencyKey",
        "correlationId",
        "providerOrderId",
        "providerCorrelationId",
        "providerInstrumentId",
        "instrumentName",
        "rawProviderStatus",
        "syncRunId",
        "sourcePayloadHash",
        "statusReason",
        mode="before",
    )
    @classmethod
    def normalize_optional_text_fields(cls, value: object) -> str | None:
        return _normalize_optional_text(value)

    @field_validator("symbol", mode="before")
    @classmethod
    def normalize_order_symbol(cls, value: object) -> str:
        return _normalize_symbol(value)

    @model_validator(mode="after")
    def validate_option_order_shape(self) -> "TradeOrder":
        if self.assetClass != "option" and (self.optionStrategyId is not None or self.optionLegs):
            raise ValueError("optionStrategyId and optionLegs require assetClass='option'.")
        if self.assetClass == "option":
            if self.notional is not None:
                raise ValueError("Option orders must use whole-contract quantity, not notional.")
            if self.quantity is not None and int(self.quantity) != self.quantity:
                raise ValueError("Option quantity must be a whole-contract quantity.")
        return self


class TradeOrderHistoryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accountId: str = Field(..., min_length=1, max_length=128)
    orders: list[TradeOrder] = Field(default_factory=list)
    generatedAt: datetime | None = None
    nextCursor: str | None = None
    sourceObservedAt: datetime | None = None
    syncRunId: str | None = Field(default=None, min_length=1, max_length=160)
    normalizationWarnings: list[TradeNormalizationWarning] = Field(default_factory=list)
    unmappedRowCount: int = Field(default=0, ge=0)
    quarantinedRowCount: int = Field(default=0, ge=0)

    @field_validator("accountId", mode="before")
    @classmethod
    def normalize_account_id(cls, value: object) -> str:
        return _normalize_required_text(value, "accountId")

    @field_validator("nextCursor", "syncRunId", mode="before")
    @classmethod
    def normalize_next_cursor(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class TradeBlotterRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rowId: str = Field(..., min_length=1, max_length=128)
    accountId: str = Field(..., min_length=1, max_length=128)
    provider: TradeProvider
    environment: TradeEnvironment
    eventType: TradeBlotterEventType
    occurredAt: datetime
    orderId: str | None = Field(default=None, min_length=1, max_length=128)
    providerOrderId: str | None = Field(default=None, min_length=1, max_length=160)
    providerEventId: str | None = Field(default=None, min_length=1, max_length=160)
    providerActivityId: str | None = Field(default=None, min_length=1, max_length=160)
    providerActivityType: str | None = Field(default=None, min_length=1, max_length=80)
    providerInstrumentId: str | None = Field(default=None, min_length=1, max_length=160)
    instrumentName: str | None = Field(default=None, min_length=1, max_length=240)
    clientRequestId: str | None = Field(default=None, min_length=1, max_length=128)
    symbol: str | None = Field(default=None, min_length=1, max_length=TRADE_SYMBOL_MAX_LENGTH)
    assetClass: TradeAssetClass = "equity"
    side: TradeOrderSide | None = None
    outcomeSide: TradeOutcomeSide | None = None
    status: TradeOrderStatus | None = None
    rawProviderStatus: str | None = Field(default=None, min_length=1, max_length=160)
    quantity: float | None = Field(default=None, gt=0)
    price: float | None = Field(default=None, ge=0)
    fees: float | None = None
    realizedPnl: float | None = None
    cashImpact: float | None = None
    sourceObservedAt: datetime | None = None
    ingestedAt: datetime | None = None
    syncRunId: str | None = Field(default=None, min_length=1, max_length=160)
    sourcePayloadHash: str | None = Field(default=None, min_length=1, max_length=160)
    normalizationWarnings: list[TradeNormalizationWarning] = Field(default_factory=list)
    reconciliationRequired: bool = False
    quarantined: bool = False
    quarantineReason: str | None = Field(default=None, min_length=1, max_length=320)
    note: str | None = None

    @field_validator("rowId", "accountId", mode="before")
    @classmethod
    def normalize_required_text_fields(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator(
        "orderId",
        "providerOrderId",
        "providerEventId",
        "providerActivityId",
        "providerActivityType",
        "providerInstrumentId",
        "instrumentName",
        "clientRequestId",
        "rawProviderStatus",
        "syncRunId",
        "sourcePayloadHash",
        "quarantineReason",
        "note",
        mode="before",
    )
    @classmethod
    def normalize_optional_text_fields(cls, value: object) -> str | None:
        return _normalize_optional_text(value)

    @field_validator("symbol", mode="before")
    @classmethod
    def normalize_optional_symbol(cls, value: object) -> str | None:
        if value is None:
            return None
        return _normalize_symbol(value)


class TradeBlotterResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accountId: str = Field(..., min_length=1, max_length=128)
    rows: list[TradeBlotterRow] = Field(default_factory=list)
    generatedAt: datetime | None = None
    nextCursor: str | None = None
    sourceObservedAt: datetime | None = None
    syncRunId: str | None = Field(default=None, min_length=1, max_length=160)
    normalizationWarnings: list[TradeNormalizationWarning] = Field(default_factory=list)
    unmappedRowCount: int = Field(default=0, ge=0)
    quarantinedRowCount: int = Field(default=0, ge=0)

    @field_validator("accountId", mode="before")
    @classmethod
    def normalize_account_id(cls, value: object) -> str:
        return _normalize_required_text(value, "accountId")

    @field_validator("nextCursor", "syncRunId", mode="before")
    @classmethod
    def normalize_next_cursor(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class TradeOrderPreviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accountId: str = Field(..., min_length=1, max_length=128)
    environment: TradeEnvironment
    clientRequestId: str = Field(..., min_length=1, max_length=128)
    symbol: str = Field(..., min_length=1, max_length=TRADE_SYMBOL_MAX_LENGTH)
    side: TradeOrderSide
    orderType: TradeOrderType
    timeInForce: TradeTimeInForce = "day"
    assetClass: TradeAssetClass = "equity"
    providerInstrumentId: str | None = Field(default=None, min_length=1, max_length=160)
    instrumentName: str | None = Field(default=None, min_length=1, max_length=240)
    outcomeSide: TradeOutcomeSide | None = None
    quantity: float | None = Field(default=None, gt=0)
    notional: float | None = Field(default=None, gt=0)
    optionStrategyId: OptionStrategyId | None = None
    optionLegs: list[OptionLeg] = Field(default_factory=list)
    limitPrice: float | None = Field(default=None, gt=0)
    stopPrice: float | None = Field(default=None, gt=0)
    allowExtendedHours: bool = False
    source: Literal["manual", "rebalance_preview", "system"] = "manual"
    strategyRef: StrategyReferenceInput | None = None

    @field_validator("accountId", "clientRequestId", mode="before")
    @classmethod
    def normalize_required_text_fields(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator("symbol", mode="before")
    @classmethod
    def normalize_order_symbol(cls, value: object) -> str:
        return _normalize_symbol(value)

    @field_validator("providerInstrumentId", "instrumentName", mode="before")
    @classmethod
    def normalize_optional_text_fields(cls, value: object) -> str | None:
        return _normalize_optional_text(value)

    @model_validator(mode="after")
    def validate_intent(self) -> "TradeOrderPreviewRequest":
        if (self.quantity is None) == (self.notional is None):
            raise ValueError("Exactly one of quantity or notional must be provided.")
        if self.assetClass != "option" and (self.optionStrategyId is not None or self.optionLegs):
            raise ValueError("optionStrategyId and optionLegs require assetClass='option'.")
        if self.assetClass == "option":
            if self.notional is not None:
                raise ValueError("Option orders must use whole-contract quantity, not notional.")
            if self.quantity is None or int(self.quantity) != self.quantity:
                raise ValueError("Option quantity must be a whole-contract quantity.")
            if self.allowExtendedHours:
                raise ValueError("Extended-hours option orders are not supported.")
        if self.orderType in {"limit", "stop_limit"} and self.limitPrice is None:
            raise ValueError("limitPrice is required for limit and stop_limit orders.")
        if self.orderType in {"stop", "stop_limit"} and self.stopPrice is None:
            raise ValueError("stopPrice is required for stop and stop_limit orders.")
        return self


class TradeOrderPreviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    previewId: str = Field(..., min_length=1, max_length=128)
    accountId: str = Field(..., min_length=1, max_length=128)
    provider: TradeProvider
    environment: TradeEnvironment
    order: TradeOrder
    generatedAt: datetime
    expiresAt: datetime
    estimatedCost: float | None = None
    estimatedPriceSource: Literal["broker_live", "massive_live", "gold_market_postgres"] | None = None
    estimatedPriceObservedAt: datetime | None = None
    estimatedFees: float = Field(default=0.0, ge=0)
    cashAfter: float | None = None
    buyingPowerAfter: float | None = None
    riskChecks: list[TradeRiskCheck] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocked: bool = False
    blockReason: str | None = None
    freshness: TradeDataFreshness = Field(default_factory=TradeDataFreshness)
    projectedPolicy: BrokerTradingPolicy | None = None
    policyVersion: int | None = Field(default=None, ge=1)
    confirmationRequired: bool = False
    orderHash: str | None = Field(default=None, min_length=1, max_length=128)
    confirmationToken: str | None = Field(default=None, min_length=1, max_length=160)

    @field_validator("previewId", "accountId", mode="before")
    @classmethod
    def normalize_required_text_fields(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator("blockReason", "orderHash", "confirmationToken", mode="before")
    @classmethod
    def normalize_block_reason(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class TradeOrderPlaceRequest(TradeOrderPreviewRequest):
    idempotencyKey: str = Field(..., min_length=16, max_length=160)
    previewId: str = Field(..., min_length=1, max_length=128)
    confirmedAt: datetime
    confirmedRiskCheckIds: list[str] = Field(default_factory=list)
    policyVersion: int | None = Field(default=None, ge=1)
    orderHash: str | None = Field(default=None, min_length=1, max_length=128)
    confirmationToken: str | None = Field(default=None, min_length=1, max_length=160)

    @field_validator("idempotencyKey", "previewId", mode="before")
    @classmethod
    def normalize_place_text_fields(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator("orderHash", "confirmationToken", mode="before")
    @classmethod
    def normalize_optional_place_text_fields(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class TradeOrderPlaceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order: TradeOrder
    submitted: bool = False
    replayed: bool = False
    reconciliationRequired: bool = False
    auditEventId: str | None = Field(default=None, min_length=1, max_length=128)
    message: str | None = None
    confirmationRequired: bool = False
    policyVersion: int | None = Field(default=None, ge=1)

    @field_validator("auditEventId", "message", mode="before")
    @classmethod
    def normalize_optional_text_fields(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class TradeOrderCancelRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accountId: str = Field(..., min_length=1, max_length=128)
    orderId: str = Field(..., min_length=1, max_length=128)
    clientRequestId: str = Field(..., min_length=1, max_length=128)
    idempotencyKey: str = Field(..., min_length=16, max_length=160)
    reason: str = ""

    @field_validator("accountId", "orderId", "clientRequestId", "idempotencyKey", mode="before")
    @classmethod
    def normalize_required_text_fields(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator("reason", mode="before")
    @classmethod
    def normalize_reason(cls, value: object) -> str:
        return str(value or "").strip()


class TradeOrderCancelResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order: TradeOrder
    cancelAccepted: bool = False
    replayed: bool = False
    reconciliationRequired: bool = False
    auditEventId: str | None = Field(default=None, min_length=1, max_length=128)
    message: str | None = None

    @field_validator("auditEventId", "message", mode="before")
    @classmethod
    def normalize_optional_text_fields(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class TradeDeskAuditEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    eventId: str = Field(..., min_length=1, max_length=128)
    accountId: str = Field(..., min_length=1, max_length=128)
    provider: TradeProvider
    environment: TradeEnvironment
    eventType: TradeAuditEventType
    severity: TradeAuditSeverity = "info"
    occurredAt: datetime
    actor: str | None = Field(default=None, min_length=1, max_length=128)
    orderId: str | None = Field(default=None, min_length=1, max_length=128)
    providerOrderId: str | None = Field(default=None, min_length=1, max_length=160)
    clientRequestId: str | None = Field(default=None, min_length=1, max_length=128)
    idempotencyKey: str | None = Field(default=None, min_length=1, max_length=160)
    previewId: str | None = Field(default=None, min_length=1, max_length=128)
    confirmationTokenId: str | None = Field(default=None, min_length=1, max_length=160)
    requestId: str | None = Field(default=None, min_length=1, max_length=160)
    statusBefore: TradeOrderStatus | None = None
    statusAfter: TradeOrderStatus | None = None
    summary: str = ""
    sanitizedError: str | None = None
    denialReason: str | None = None
    grantedRoles: list[str] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)

    @field_validator("eventId", "accountId", mode="before")
    @classmethod
    def normalize_required_text_fields(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator(
        "actor",
        "orderId",
        "providerOrderId",
        "clientRequestId",
        "idempotencyKey",
        "previewId",
        "confirmationTokenId",
        "requestId",
        "sanitizedError",
        "denialReason",
        mode="before",
    )
    @classmethod
    def normalize_optional_text_fields(cls, value: object) -> str | None:
        return _normalize_optional_text(value)

    @field_validator("summary", mode="before")
    @classmethod
    def normalize_summary(cls, value: object) -> str:
        return str(value or "").strip()


class TradeDeskAuditEventListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accountId: str = Field(..., min_length=1, max_length=128)
    events: list[TradeDeskAuditEvent] = Field(default_factory=list)
    generatedAt: datetime | None = None
    nextCursor: str | None = None

    @field_validator("accountId", mode="before")
    @classmethod
    def normalize_account_id(cls, value: object) -> str:
        return _normalize_required_text(value, "accountId")

    @field_validator("nextCursor", mode="before")
    @classmethod
    def normalize_next_cursor(cls, value: object) -> str | None:
        return _normalize_optional_text(value)
