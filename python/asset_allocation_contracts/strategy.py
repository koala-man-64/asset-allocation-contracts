from __future__ import annotations

from datetime import date, datetime
from typing import Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from asset_allocation_contracts.regime import RegimePolicy

ExitRuleType = Literal[
    "stop_loss_fixed",
    "take_profit_fixed",
    "trailing_stop_pct",
    "trailing_stop_atr",
    "time_stop",
]
ExitScope = Literal["position"]
ExitAction = Literal["exit_full"]
PriceField = Literal["open", "high", "low", "close"]
ExitReference = Literal["entry_price", "highest_since_entry"]
IntrabarConflictPolicy = Literal["stop_first", "take_profit_first", "priority_order"]
UniverseSource = Literal["postgres_gold"]
UniverseGroupOperator = Literal["and", "or"]
UniverseConditionOperator = Literal[
    "eq",
    "ne",
    "gt",
    "gte",
    "lt",
    "lte",
    "in",
    "not_in",
    "is_null",
    "is_not_null",
]
UniverseFieldId = Literal[
    "market.close",
    "security.is_active",
    "security.sector",
    "security.delisted_at",
    "market.trade_date",
    "market.timestamp",
    "returns.return_20d",
    "returns.return_126d",
    "quality.piotroski_f_score",
    "earnings.surprise_pct",
]
UniverseValueKind = Literal["string", "number", "boolean", "date", "datetime"]
UniverseValue: TypeAlias = str | int | float | bool
StrategyAnalyticsSource = Literal["control_plane", "backtest", "portfolio", "trade_desk", "broker"]
StrategyComparisonRole = Literal["baseline", "challenger", "candidate"]
StrategyMetricUnit = Literal["ratio", "currency", "count", "bps", "days", "score"]
StrategyForecastConfidence = Literal["high", "medium", "low", "thin"]
StrategyForecastSampleMode = Literal["regime_conditioned", "fallback_history", "insufficient_history"]
StrategyTradeHistorySource = Literal["backtest", "portfolio_ledger", "trade_order", "broker_fill"]
StrategyTradeSide = Literal["buy", "sell"]
StrategyAllocationExposureStatus = Literal["active", "staged", "paused", "missing"]


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


class UniverseFieldDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: UniverseFieldId
    label: str = Field(..., min_length=1, max_length=128)
    valueKind: UniverseValueKind
    operators: list[UniverseConditionOperator] = Field(..., min_length=1)


UNIVERSE_FIELD_DEFINITIONS: tuple[UniverseFieldDefinition, ...] = (
    UniverseFieldDefinition(
        id="market.close",
        label="Close Price",
        valueKind="number",
        operators=["eq", "ne", "gt", "gte", "lt", "lte", "in", "not_in", "is_null", "is_not_null"],
    ),
    UniverseFieldDefinition(
        id="security.is_active",
        label="Security Active Flag",
        valueKind="boolean",
        operators=["eq", "ne", "in", "not_in", "is_null", "is_not_null"],
    ),
    UniverseFieldDefinition(
        id="security.sector",
        label="Security Sector",
        valueKind="string",
        operators=["eq", "ne", "in", "not_in", "is_null", "is_not_null"],
    ),
    UniverseFieldDefinition(
        id="security.delisted_at",
        label="Delisted Timestamp",
        valueKind="datetime",
        operators=["eq", "ne", "gt", "gte", "lt", "lte", "in", "not_in", "is_null", "is_not_null"],
    ),
    UniverseFieldDefinition(
        id="market.trade_date",
        label="Trade Date",
        valueKind="date",
        operators=["eq", "ne", "gt", "gte", "lt", "lte", "in", "not_in", "is_null", "is_not_null"],
    ),
    UniverseFieldDefinition(
        id="market.timestamp",
        label="Market Timestamp",
        valueKind="datetime",
        operators=["eq", "ne", "gt", "gte", "lt", "lte", "in", "not_in", "is_null", "is_not_null"],
    ),
    UniverseFieldDefinition(
        id="returns.return_20d",
        label="20 Day Return",
        valueKind="number",
        operators=["eq", "ne", "gt", "gte", "lt", "lte", "in", "not_in", "is_null", "is_not_null"],
    ),
    UniverseFieldDefinition(
        id="returns.return_126d",
        label="126 Day Return",
        valueKind="number",
        operators=["eq", "ne", "gt", "gte", "lt", "lte", "in", "not_in", "is_null", "is_not_null"],
    ),
    UniverseFieldDefinition(
        id="quality.piotroski_f_score",
        label="Piotroski F-Score",
        valueKind="number",
        operators=["eq", "ne", "gt", "gte", "lt", "lte", "in", "not_in", "is_null", "is_not_null"],
    ),
    UniverseFieldDefinition(
        id="earnings.surprise_pct",
        label="Earnings Surprise Percent",
        valueKind="number",
        operators=["eq", "ne", "gt", "gte", "lt", "lte", "in", "not_in", "is_null", "is_not_null"],
    ),
)
UNIVERSE_FIELD_DEFINITION_BY_ID: dict[UniverseFieldId, UniverseFieldDefinition] = {
    field.id: field for field in UNIVERSE_FIELD_DEFINITIONS
}


class UniverseCondition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["condition"] = "condition"
    field: UniverseFieldId
    operator: UniverseConditionOperator
    value: UniverseValue | None = None
    values: list[UniverseValue] | None = None

    @field_validator("field", mode="before")
    @classmethod
    def normalize_field(cls, value: object) -> object:
        if value is None:
            return value
        normalized = str(value).strip().lower()
        return normalized or value

    @model_validator(mode="after")
    def validate_condition(self) -> "UniverseCondition":
        field_definition = UNIVERSE_FIELD_DEFINITION_BY_ID[self.field]

        if self.operator not in field_definition.operators:
            raise ValueError(f"{self.operator} is not supported for field '{self.field}'.")

        if self.operator in {"is_null", "is_not_null"}:
            if self.value is not None or self.values is not None:
                raise ValueError(f"{self.operator} does not accept value or values.")
            return self

        if self.operator in {"in", "not_in"}:
            if self.value is not None:
                raise ValueError(f"{self.operator} only supports values.")
            if not self.values:
                raise ValueError(f"{self.operator} requires at least one value.")
            return self

        if self.value is None:
            raise ValueError(f"{self.operator} requires value.")
        if self.values is not None:
            raise ValueError(f"{self.operator} does not support values.")
        return self


class UniverseGroup(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["group"] = "group"
    operator: UniverseGroupOperator = "and"
    clauses: list["UniverseGroup | UniverseCondition"] = Field(..., min_length=1)


class UniverseDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: UniverseSource = "postgres_gold"
    root: UniverseGroup


class UniverseCatalogResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: UniverseSource = "postgres_gold"
    fields: list[UniverseFieldDefinition] = Field(default_factory=list)


class UniversePreviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: UniverseSource = "postgres_gold"
    symbolCount: int = Field(..., ge=0)
    sampleSymbols: list[str] = Field(default_factory=list)
    fieldsUsed: list[UniverseFieldId] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


UniverseGroup.model_rebuild()
UniverseDefinition.model_rebuild()


class ExitRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., min_length=1, max_length=128)
    type: ExitRuleType
    scope: ExitScope = "position"
    priceField: PriceField | None = None
    value: float | None = None
    atrColumn: str | None = Field(default=None, min_length=1, max_length=128)
    priority: int | None = Field(default=None, ge=0)
    action: ExitAction = "exit_full"
    minHoldBars: int = Field(default=0, ge=0)
    reference: ExitReference | None = None

    @model_validator(mode="after")
    def validate_rule(self) -> "ExitRule":
        if self.type == "stop_loss_fixed":
            self._require_positive_value()
            self._default_reference("entry_price")
            self._default_price_field("low")
            self._reject_atr_column()
        elif self.type == "take_profit_fixed":
            self._require_positive_value()
            self._default_reference("entry_price")
            self._default_price_field("high")
            self._reject_atr_column()
        elif self.type == "trailing_stop_pct":
            self._require_positive_value()
            self._default_reference("highest_since_entry")
            self._default_price_field("low")
            self._reject_atr_column()
        elif self.type == "trailing_stop_atr":
            self._require_positive_value()
            self._default_reference("highest_since_entry")
            self._default_price_field("low")
            if not self.atrColumn:
                raise ValueError("trailing_stop_atr requires atrColumn.")
        elif self.type == "time_stop":
            self._require_positive_value(integer_only=True)
            self._reject_reference()
            self._reject_atr_column()
            if self.priceField is None:
                self.priceField = "close"
            elif self.priceField != "close":
                raise ValueError("time_stop only supports priceField='close'.")

        return self

    def _require_positive_value(self, *, integer_only: bool = False) -> None:
        if self.value is None or self.value <= 0:
            raise ValueError(f"{self.type} requires value > 0.")
        if integer_only and not float(self.value).is_integer():
            raise ValueError(f"{self.type} requires an integer value.")

    def _default_reference(self, expected: ExitReference) -> None:
        if self.reference is None:
            self.reference = expected
            return
        if self.reference != expected:
            raise ValueError(f"{self.type} only supports reference='{expected}'.")

    def _default_price_field(self, expected: PriceField) -> None:
        if self.priceField is None:
            self.priceField = expected
            return
        if self.priceField not in {"open", "high", "low", "close"}:
            raise ValueError(f"{self.type} received unsupported priceField='{self.priceField}'.")

    def _reject_atr_column(self) -> None:
        if self.atrColumn is not None:
            raise ValueError(f"{self.type} does not support atrColumn.")

    def _reject_reference(self) -> None:
        if self.reference is not None:
            raise ValueError(f"{self.type} does not support reference.")


class StrategyRiskPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    grossExposureLimit: float | None = Field(default=None, ge=0.0)
    netExposureLimit: float | None = Field(default=None, ge=0.0)
    singleNameMaxWeight: float | None = Field(default=None, ge=0.0, le=1.0)
    sectorMaxWeight: float | None = Field(default=None, ge=0.0, le=1.0)
    turnoverBudget: float | None = Field(default=None, ge=0.0)
    maxDrawdownLimit: float | None = Field(default=None, ge=0.0, le=1.0)
    liquidityParticipationRate: float | None = Field(default=None, ge=0.0, le=1.0)
    maxTradeNotionalBaseCcy: float | None = Field(default=None, gt=0.0)
    notes: str = ""

    @field_validator("notes", mode="before")
    @classmethod
    def normalize_notes(cls, value: object) -> str:
        return str(value or "").strip()


class StrategyAnalyticsReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    strategyName: str = Field(..., min_length=1, max_length=128)
    strategyVersion: int | None = Field(default=None, ge=1)
    runId: str | None = Field(default=None, min_length=1, max_length=128)
    role: StrategyComparisonRole = "candidate"
    label: str | None = Field(default=None, min_length=1, max_length=128)

    @field_validator("strategyName", mode="before")
    @classmethod
    def normalize_strategy_name(cls, value: object) -> str:
        return _normalize_required_text(value, "strategyName")

    @field_validator("runId", "label", mode="before")
    @classmethod
    def normalize_optional_text_fields(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class StrategyComparisonRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    strategies: list[StrategyAnalyticsReference] = Field(..., min_length=2)
    startDate: date
    endDate: date
    benchmarkSymbol: str | None = Field(default=None, min_length=1, max_length=32)
    costModel: str = Field(default="default", min_length=1, max_length=64)
    barSize: str = Field(default="1d", min_length=1, max_length=32)
    regimeModelName: str | None = Field(default=None, min_length=1, max_length=128)
    scenarioAssumption: str | None = Field(default=None, min_length=1, max_length=128)
    includeForecast: bool = False

    @field_validator("benchmarkSymbol", mode="before")
    @classmethod
    def normalize_benchmark_symbol(cls, value: object) -> str | None:
        normalized = _normalize_optional_text(value)
        return normalized.upper() if normalized else None

    @field_validator("costModel", "barSize", "regimeModelName", "scenarioAssumption", mode="before")
    @classmethod
    def normalize_text_fields(cls, value: object) -> object:
        return _normalize_optional_text(value) if value is not None else value

    @model_validator(mode="after")
    def validate_window(self) -> "StrategyComparisonRequest":
        if self.endDate < self.startDate:
            raise ValueError("endDate cannot be before startDate.")
        return self


class StrategyComparisonMetricRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metric: str = Field(..., min_length=1, max_length=128)
    label: str = Field(..., min_length=1, max_length=160)
    unit: StrategyMetricUnit
    values: dict[str, float | None] = Field(default_factory=dict)
    winnerStrategyName: str | None = Field(default=None, min_length=1, max_length=128)
    notes: str = ""

    @field_validator("metric", "label", mode="before")
    @classmethod
    def normalize_required_fields(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator("winnerStrategyName", mode="before")
    @classmethod
    def normalize_winner(cls, value: object) -> str | None:
        return _normalize_optional_text(value)

    @field_validator("notes", mode="before")
    @classmethod
    def normalize_notes(cls, value: object) -> str:
        return str(value or "").strip()


class StrategyComparisonRunEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    strategyName: str = Field(..., min_length=1, max_length=128)
    strategyVersion: int | None = Field(default=None, ge=1)
    runId: str | None = Field(default=None, min_length=1, max_length=128)
    startDate: date
    endDate: date
    barSize: str = Field(..., min_length=1, max_length=32)
    costModel: str = Field(default="default", min_length=1, max_length=64)
    resultSchemaVersion: int | None = Field(default=None, ge=1)
    warnings: list[str] = Field(default_factory=list)

    @field_validator("strategyName", "barSize", "costModel", mode="before")
    @classmethod
    def normalize_required_fields(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator("runId", mode="before")
    @classmethod
    def normalize_run_id(cls, value: object) -> str | None:
        return _normalize_optional_text(value)

    @field_validator("warnings", mode="before")
    @classmethod
    def normalize_warnings(cls, value: object) -> list[str]:
        if value is None:
            return []
        return [str(item).strip() for item in value if str(item).strip()]

    @model_validator(mode="after")
    def validate_window(self) -> "StrategyComparisonRunEvidence":
        if self.endDate < self.startDate:
            raise ValueError("endDate cannot be before startDate.")
        return self


class StrategyComparisonResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asOf: datetime
    benchmarkSymbol: str | None = Field(default=None, min_length=1, max_length=32)
    costModel: str = Field(..., min_length=1, max_length=64)
    barSize: str = Field(..., min_length=1, max_length=32)
    strategies: list[StrategyAnalyticsReference] = Field(..., min_length=2)
    metrics: list[StrategyComparisonMetricRow] = Field(default_factory=list)
    runEvidence: list[StrategyComparisonRunEvidence] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blockedReasons: list[str] = Field(default_factory=list)

    @field_validator("warnings", "blockedReasons", mode="before")
    @classmethod
    def normalize_text_lists(cls, value: object) -> list[str]:
        if value is None:
            return []
        return [str(item).strip() for item in value if str(item).strip()]


class StrategyScenarioForecastRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    strategies: list[StrategyAnalyticsReference] = Field(..., min_length=1)
    asOfDate: date | None = None
    horizon: str = Field(default="3M", min_length=1, max_length=32)
    regimeModelName: str | None = Field(default=None, min_length=1, max_length=128)
    regimeAssumption: str = Field(default="current", min_length=1, max_length=128)
    costDragOverrideBps: float | None = None
    tunableParameters: dict[str, str | int | float | bool | None] = Field(default_factory=dict)


class StrategyForecastRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    strategyName: str = Field(..., min_length=1, max_length=128)
    strategyVersion: int | None = Field(default=None, ge=1)
    expectedReturn: float | None = None
    expectedActiveReturn: float | None = None
    downside: float | None = None
    upside: float | None = None
    confidence: StrategyForecastConfidence
    sampleSize: int = Field(default=0, ge=0)
    sampleMode: StrategyForecastSampleMode
    appliedRegimeCode: str = Field(default="unclassified", min_length=1, max_length=128)
    source: StrategyAnalyticsSource = "control_plane"
    notes: list[str] = Field(default_factory=list)

    @field_validator("strategyName", "appliedRegimeCode", mode="before")
    @classmethod
    def normalize_required_fields(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator("notes", mode="before")
    @classmethod
    def normalize_notes(cls, value: object) -> list[str]:
        if value is None:
            return []
        return [str(item).strip() for item in value if str(item).strip()]


class StrategyScenarioForecastResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asOf: datetime
    horizon: str = Field(..., min_length=1, max_length=32)
    regimeAssumption: str = Field(..., min_length=1, max_length=128)
    source: StrategyAnalyticsSource = "control_plane"
    forecasts: list[StrategyForecastRow] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @field_validator("warnings", mode="before")
    @classmethod
    def normalize_warnings(cls, value: object) -> list[str]:
        if value is None:
            return []
        return [str(item).strip() for item in value if str(item).strip()]


class StrategyAllocationExposureRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    strategyName: str = Field(..., min_length=1, max_length=128)
    strategyVersion: int | None = Field(default=None, ge=1)
    accountIds: list[str] = Field(default_factory=list)
    includePositions: bool = True

    @field_validator("strategyName", mode="before")
    @classmethod
    def normalize_strategy_name(cls, value: object) -> str:
        return _normalize_required_text(value, "strategyName")

    @field_validator("accountIds", mode="before")
    @classmethod
    def normalize_account_ids(cls, value: object) -> list[str]:
        if value is None:
            return []
        return [str(item).strip() for item in value if str(item).strip()]


class StrategyAllocationExposureRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accountId: str = Field(..., min_length=1, max_length=128)
    accountName: str = Field(..., min_length=1, max_length=128)
    portfolioName: str = Field(..., min_length=1, max_length=128)
    portfolioVersion: int | None = Field(default=None, ge=1)
    sleeveId: str = Field(..., min_length=1, max_length=128)
    sleeveName: str = ""
    strategyName: str = Field(..., min_length=1, max_length=128)
    strategyVersion: int = Field(..., ge=1)
    asOf: date
    targetWeight: float | None = Field(default=None, ge=0.0, le=1.0)
    actualWeight: float | None = Field(default=None, ge=0.0, le=1.0)
    drift: float | None = None
    marketValue: float | None = None
    grossExposure: float | None = None
    netExposure: float | None = None
    status: StrategyAllocationExposureStatus = "active"

    @field_validator("accountId", "accountName", "portfolioName", "sleeveId", "strategyName", mode="before")
    @classmethod
    def normalize_required_fields(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator("sleeveName", mode="before")
    @classmethod
    def normalize_sleeve_name(cls, value: object) -> str:
        return str(value or "").strip()


class StrategyAllocationPositionRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accountId: str = Field(..., min_length=1, max_length=128)
    portfolioName: str = Field(..., min_length=1, max_length=128)
    sleeveId: str = Field(..., min_length=1, max_length=128)
    symbol: str = Field(..., min_length=1, max_length=32)
    asOf: date
    quantity: float
    marketValue: float
    weight: float = Field(..., ge=0.0, le=1.0)

    @field_validator("accountId", "portfolioName", "sleeveId", mode="before")
    @classmethod
    def normalize_required_fields(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator("symbol", mode="before")
    @classmethod
    def normalize_symbol(cls, value: object) -> str:
        return _normalize_required_text(value, "symbol").upper()


class StrategyAllocationExposureResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    strategyName: str = Field(..., min_length=1, max_length=128)
    strategyVersion: int | None = Field(default=None, ge=1)
    asOf: datetime
    totalMarketValue: float | None = None
    aggregateTargetWeight: float | None = Field(default=None, ge=0.0)
    aggregateActualWeight: float | None = Field(default=None, ge=0.0)
    aggregateGrossExposure: float | None = None
    aggregateNetExposure: float | None = None
    exposures: list[StrategyAllocationExposureRow] = Field(default_factory=list)
    positions: list[StrategyAllocationPositionRow] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @field_validator("strategyName", mode="before")
    @classmethod
    def normalize_strategy_name(cls, value: object) -> str:
        return _normalize_required_text(value, "strategyName")

    @field_validator("warnings", mode="before")
    @classmethod
    def normalize_warnings(cls, value: object) -> list[str]:
        if value is None:
            return []
        return [str(item).strip() for item in value if str(item).strip()]


class StrategyTradeHistoryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    strategyName: str = Field(..., min_length=1, max_length=128)
    strategyVersion: int | None = Field(default=None, ge=1)
    startDate: date | None = None
    endDate: date | None = None
    sources: list[StrategyTradeHistorySource] = Field(default_factory=list)
    limit: int = Field(default=200, ge=1, le=5000)
    offset: int = Field(default=0, ge=0)

    @field_validator("strategyName", mode="before")
    @classmethod
    def normalize_strategy_name(cls, value: object) -> str:
        return _normalize_required_text(value, "strategyName")

    @model_validator(mode="after")
    def validate_window(self) -> "StrategyTradeHistoryRequest":
        if self.startDate and self.endDate and self.endDate < self.startDate:
            raise ValueError("endDate cannot be before startDate.")
        return self


class StrategyTradeHistoryRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: StrategyTradeHistorySource
    timestamp: datetime
    symbol: str = Field(..., min_length=1, max_length=32)
    side: StrategyTradeSide | None = None
    quantity: float
    price: float | None = Field(default=None, ge=0.0)
    notional: float | None = None
    commission: float = Field(default=0.0, ge=0.0)
    slippageCost: float = Field(default=0.0, ge=0.0)
    realizedPnl: float | None = None
    accountId: str | None = Field(default=None, min_length=1, max_length=128)
    portfolioName: str | None = Field(default=None, min_length=1, max_length=128)
    runId: str | None = Field(default=None, min_length=1, max_length=128)
    orderId: str | None = Field(default=None, min_length=1, max_length=128)
    eventId: str | None = Field(default=None, min_length=1, max_length=128)

    @field_validator("symbol", mode="before")
    @classmethod
    def normalize_symbol(cls, value: object) -> str:
        return _normalize_required_text(value, "symbol").upper()

    @field_validator("accountId", "portfolioName", "runId", "orderId", "eventId", mode="before")
    @classmethod
    def normalize_optional_text_fields(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class StrategyTradeHistoryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    strategyName: str = Field(..., min_length=1, max_length=128)
    strategyVersion: int | None = Field(default=None, ge=1)
    trades: list[StrategyTradeHistoryRow] = Field(default_factory=list)
    total: int = Field(default=0, ge=0)
    limit: int = Field(default=200, ge=1)
    offset: int = Field(default=0, ge=0)
    warnings: list[str] = Field(default_factory=list)

    @field_validator("strategyName", mode="before")
    @classmethod
    def normalize_strategy_name(cls, value: object) -> str:
        return _normalize_required_text(value, "strategyName")

    @field_validator("warnings", mode="before")
    @classmethod
    def normalize_warnings(cls, value: object) -> list[str]:
        if value is None:
            return []
        return [str(item).strip() for item in value if str(item).strip()]


class StrategyConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    universeConfigName: str | None = Field(default=None, min_length=1, max_length=128)
    universe: UniverseDefinition | None = None
    rebalance: str = Field(default="monthly", min_length=1, max_length=64)
    longOnly: bool = True
    topN: int = Field(default=20, ge=1)
    lookbackWindow: int = Field(default=63, ge=1)
    holdingPeriod: int = Field(default=21, ge=1)
    costModel: str = Field(default="default", min_length=1, max_length=64)
    rankingSchemaName: str | None = Field(default=None, min_length=1, max_length=128)
    regimePolicy: RegimePolicy | None = None
    riskPolicy: StrategyRiskPolicy | None = None
    intrabarConflictPolicy: IntrabarConflictPolicy = "stop_first"
    exits: list[ExitRule] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def strip_legacy_toggle_fields(cls, value: object) -> object:
        if not isinstance(value, dict):
            return value

        payload = dict(value)
        regime_policy = payload.get("regimePolicy")
        if isinstance(regime_policy, dict):
            normalized_policy = dict(regime_policy)
            if normalized_policy.get("enabled") is False:
                payload["regimePolicy"] = None
            else:
                normalized_policy.pop("enabled", None)
                payload["regimePolicy"] = normalized_policy

        raw_exits = payload.get("exits")
        if isinstance(raw_exits, list):
            normalized_exits: list[object] = []
            for raw_rule in raw_exits:
                if not isinstance(raw_rule, dict):
                    normalized_exits.append(raw_rule)
                    continue
                if raw_rule.get("enabled") is False:
                    continue
                normalized_rule = dict(raw_rule)
                normalized_rule.pop("enabled", None)
                normalized_exits.append(normalized_rule)
            payload["exits"] = normalized_exits

        return payload

    @field_validator("universeConfigName", mode="before")
    @classmethod
    def normalize_universe_config_name(cls, value: object) -> object:
        if value is None:
            return None
        normalized = str(value).strip()
        return normalized or None

    @field_validator("rankingSchemaName", mode="before")
    @classmethod
    def normalize_ranking_schema_name(cls, value: object) -> object:
        if value is None:
            return None
        normalized = str(value).strip()
        return normalized or None

    @model_validator(mode="after")
    def normalize_exits(self) -> "StrategyConfig":
        if not self.universeConfigName and self.universe is None:
            raise ValueError("universeConfigName is required.")
        seen_ids: set[str] = set()
        for idx, rule in enumerate(self.exits):
            if rule.id in seen_ids:
                raise ValueError(f"Duplicate exit rule id '{rule.id}'.")
            seen_ids.add(rule.id)
            if rule.priority is None:
                rule.priority = idx
        return self
