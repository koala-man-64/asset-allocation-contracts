from __future__ import annotations

from datetime import datetime
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
StrategyPositionSizeMode = Literal["pct_of_allocatable_capital", "notional_base_ccy"]
StrategyPositionAssetClass = Literal["equity", "option"]
RiskTolerancePreset = Literal["conservative", "balanced", "aggressive"]
RebalanceFrequency = Literal["every_bar", "daily", "weekly", "monthly", "quarterly", "every_n_bars", "manual"]
RebalanceExecutionTiming = Literal["next_bar_open"]
StrategyRiskPolicyScope = Literal["strategy", "sleeve"]
StrategyRiskStopLossBasis = Literal["strategy_nav_drawdown", "sleeve_nav_drawdown"]
StrategyRiskTakeProfitBasis = Literal["strategy_nav_gain", "sleeve_nav_gain"]
StrategyRiskStopLossAction = Literal["reduce_exposure", "liquidate", "freeze_buys"]
StrategyRiskTakeProfitAction = Literal["reduce_exposure", "rebalance_to_target"]
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


class StrategyPositionSizeLimit(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mode: StrategyPositionSizeMode = "pct_of_allocatable_capital"
    value: float = Field(..., gt=0.0)

    @model_validator(mode="after")
    def validate_limit(self) -> "StrategyPositionSizeLimit":
        if self.mode == "pct_of_allocatable_capital" and self.value > 100:
            raise ValueError("Percentage position sizing values cannot exceed 100.")
        return self


class StrategyPositionPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    targetPositionSize: StrategyPositionSizeLimit | None = None
    maxPositionSize: StrategyPositionSizeLimit | None = None
    maxOpenPositions: int | None = Field(default=None, ge=1)
    allowedAssetClasses: list[StrategyPositionAssetClass] = Field(default_factory=lambda: ["equity"])
    requireOrderConfirmation: bool = False

    @field_validator("allowedAssetClasses", mode="before")
    @classmethod
    def normalize_allowed_asset_classes(cls, value: object) -> list[str]:
        if value is None:
            return ["equity"]
        if not isinstance(value, list):
            raise ValueError("allowedAssetClasses must be a list.")
        normalized: list[str] = []
        for item in value:
            text = str(item or "").strip().lower()
            if text and text not in normalized:
                normalized.append(text)
        return normalized

    @model_validator(mode="after")
    def validate_policy(self) -> "StrategyPositionPolicy":
        if not self.allowedAssetClasses:
            raise ValueError("allowedAssetClasses must include at least one asset class.")
        return self


class StrategyRiskProfileConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    presetClass: RiskTolerancePreset
    positionPolicy: StrategyPositionPolicy

    @model_validator(mode="after")
    def validate_config(self) -> "StrategyRiskProfileConfig":
        target = self.positionPolicy.targetPositionSize
        maximum = self.positionPolicy.maxPositionSize
        max_open_positions = self.positionPolicy.maxOpenPositions

        if target is None:
            raise ValueError("Strategy risk profiles require targetPositionSize.")
        if maximum is None:
            raise ValueError("Strategy risk profiles require maxPositionSize.")
        if max_open_positions is None:
            raise ValueError("Strategy risk profiles require maxOpenPositions.")
        if target.mode != maximum.mode:
            raise ValueError("Strategy risk profiles require targetPositionSize and maxPositionSize to share a mode.")
        if maximum.value < target.value:
            raise ValueError("maxPositionSize must be greater than or equal to targetPositionSize.")

        return self


class StrategyRiskProfileSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=128)
    description: str = Field(default="", max_length=2048)
    presetClass: RiskTolerancePreset
    version: int = Field(default=1, ge=1)
    isSystem: bool = False
    usageCount: int = Field(default=0, ge=0)
    updatedAt: datetime | None = None


class StrategyRiskProfileDetail(StrategyRiskProfileSummary):
    config: StrategyRiskProfileConfig


class RebalancePolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    frequency: RebalanceFrequency = "every_bar"
    executionTiming: RebalanceExecutionTiming = "next_bar_open"
    intervalBars: int | None = Field(default=None, ge=1)
    driftThresholdPct: float | None = Field(default=None, ge=0.0, le=100.0)
    minTradeNotional: float = Field(default=0.0, ge=0.0)
    cashBufferPct: float = Field(default=0.0, ge=0.0, lt=100.0)
    maxTurnoverPct: float | None = Field(default=None, ge=0.0, le=100.0)
    allowPartialRebalance: bool = True
    closeRemovedPositions: bool = True

    @model_validator(mode="after")
    def validate_policy(self) -> "RebalancePolicy":
        if self.frequency == "every_n_bars":
            if self.intervalBars is None:
                raise ValueError("every_n_bars rebalance frequency requires intervalBars.")
        elif self.intervalBars is not None:
            raise ValueError("intervalBars is only supported when frequency='every_n_bars'.")
        return self


class StrategyRiskReentryPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cooldownBars: int = Field(default=0, ge=0)
    requireApproval: bool = False


class StrategyRiskStopLossPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default="strategy-stop-loss", min_length=1, max_length=128)
    enabled: bool = True
    basis: StrategyRiskStopLossBasis = "strategy_nav_drawdown"
    thresholdPct: float = Field(..., gt=0.0, le=100.0)
    action: StrategyRiskStopLossAction = "reduce_exposure"
    reductionPct: float | None = Field(default=None, gt=0.0, le=100.0)

    @model_validator(mode="after")
    def validate_policy(self) -> "StrategyRiskStopLossPolicy":
        if self.enabled and self.action == "reduce_exposure" and self.reductionPct is None:
            raise ValueError("reduce_exposure stop-loss policies require reductionPct.")
        if self.action != "reduce_exposure" and self.reductionPct is not None:
            raise ValueError("reductionPct is only supported for reduce_exposure stop-loss policies.")
        return self


class StrategyRiskTakeProfitPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default="strategy-take-profit", min_length=1, max_length=128)
    enabled: bool = True
    basis: StrategyRiskTakeProfitBasis = "strategy_nav_gain"
    thresholdPct: float = Field(..., gt=0.0, le=100.0)
    action: StrategyRiskTakeProfitAction = "rebalance_to_target"
    reductionPct: float | None = Field(default=None, gt=0.0, le=100.0)

    @model_validator(mode="after")
    def validate_policy(self) -> "StrategyRiskTakeProfitPolicy":
        if self.enabled and self.action == "reduce_exposure" and self.reductionPct is None:
            raise ValueError("reduce_exposure take-profit policies require reductionPct.")
        if self.action != "reduce_exposure" and self.reductionPct is not None:
            raise ValueError("reductionPct is only supported for reduce_exposure take-profit policies.")
        return self


class StrategyRiskPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    scope: StrategyRiskPolicyScope = "strategy"
    stopLoss: StrategyRiskStopLossPolicy | None = None
    takeProfit: StrategyRiskTakeProfitPolicy | None = None
    reentry: StrategyRiskReentryPolicy = Field(default_factory=StrategyRiskReentryPolicy)

    @model_validator(mode="after")
    def validate_policy(self) -> "StrategyRiskPolicy":
        if self.enabled:
            enabled_stop = self.stopLoss is not None and self.stopLoss.enabled
            enabled_take = self.takeProfit is not None and self.takeProfit.enabled
            reentry_control = self.reentry.cooldownBars > 0 or self.reentry.requireApproval
            if not enabled_stop and not enabled_take and not reentry_control:
                raise ValueError(
                    "Enabled strategyRiskPolicy requires an enabled stopLoss, takeProfit, or reentry control."
                )
        return self


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
    riskProfileName: str | None = Field(default=None, min_length=1, max_length=128)
    positionPolicy: StrategyPositionPolicy | None = None
    rebalancePolicy: RebalancePolicy | None = None
    strategyRiskPolicy: StrategyRiskPolicy | None = None
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

    @field_validator("riskProfileName", mode="before")
    @classmethod
    def normalize_risk_profile_name(cls, value: object) -> object:
        if value is None:
            return None
        normalized = str(value).strip()
        return normalized or None

    @model_validator(mode="after")
    def normalize_exits(self) -> "StrategyConfig":
        if not self.universeConfigName and self.universe is None:
            raise ValueError("universeConfigName is required.")
        if not self.longOnly:
            raise ValueError("Strategy position policy v1 only supports longOnly=true.")
        if self.riskProfileName and self.positionPolicy is None:
            raise ValueError("riskProfileName requires a positionPolicy snapshot.")
        if self.positionPolicy is not None:
            self._validate_position_policy_exposure()
        seen_ids: set[str] = set()
        for idx, rule in enumerate(self.exits):
            if rule.id in seen_ids:
                raise ValueError(f"Duplicate exit rule id '{rule.id}'.")
            seen_ids.add(rule.id)
            if rule.priority is None:
                rule.priority = idx
        return self

    def _validate_position_policy_exposure(self) -> None:
        policy = self.positionPolicy
        if policy is None or policy.targetPositionSize is None:
            return
        target = policy.targetPositionSize
        if target.mode != "pct_of_allocatable_capital":
            return
        selected_positions = min(int(self.topN), int(policy.maxOpenPositions or self.topN))
        total_target_pct = float(target.value) * selected_positions
        if total_target_pct > 100:
            raise ValueError(
                "Long-only targetPositionSize percentage cannot allocate more than 100% "
                "across selected positions."
            )
