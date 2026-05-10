from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

OptionRight = Literal["call", "put"]
OptionExerciseStyle = Literal["american", "european"]
OptionSettlementStyle = Literal["physical", "cash"]
OptionLegSide = Literal["long", "short"]
OptionLegRole = Literal[
    "stock",
    "long_call",
    "short_call",
    "long_put",
    "short_put",
    "long_wing",
    "short_body",
    "underlying_stock",
    "cash_reserve",
]
OptionOpenClose = Literal["open", "close"]
OptionPayoffFamily = Literal[
    "stock_overlay_income",
    "outright_directional",
    "vertical_spread",
    "time_spread",
    "volatility",
    "hedge",
    "stock_overlay_hedge",
    "aggressive_income",
]
OptionStrategyId = Literal[
    "covered_call",
    "cash_secured_put",
    "long_call",
    "long_put",
    "protective_put",
    "collar",
    "bull_call_spread",
    "bear_put_spread",
    "bull_put_spread",
    "bear_call_spread",
    "long_straddle",
    "long_strangle",
    "iron_condor",
    "iron_butterfly",
    "long_butterfly",
    "calendar_spread",
    "diagonal_spread",
    "pmcc",
    "covered_straddle",
    "covered_combination",
    "covered_strangle",
]
OptionStrategyStage = Literal["core_research", "experimental_research", "specified_blocked", "out_of_v1"]
OptionApprovalLevel = Literal[1, 2, 3]
OptionNetPremiumDirection = Literal["debit", "credit", "zero_or_variable", "path_dependent"]
OptionExpirationScope = Literal["final_expiration", "short_leg_expiration", "path_dependent"]
OptionExposureSign = Literal["positive", "negative", "neutral", "mixed", "path_dependent"]
OptionIvEnvironment = Literal["cheap", "rich", "neutral", "term_structure", "event_vol", "unknown"]
OptionProvider = Literal["alpaca", "schwab", "etrade", "other"]
OptionEnvironment = Literal["paper", "sandbox", "live"]
OptionOrderType = Literal["market", "limit", "stop", "stop_limit"]
OptionTimeInForce = Literal["day", "gtc", "opg", "cls", "ioc", "fok"]
OptionLifecycleEventType = Literal[
    "expiration",
    "assignment",
    "exercise",
    "do_not_exercise",
    "forced_liquidation_window",
    "post_assignment_exposure",
]
OptionBacktestEventType = Literal[
    "payoff_evaluated",
    "risk_gate",
    "data_quality_gate",
    "lifecycle_event",
    "research_only_block",
    "broker_preview_block",
]
OptionGateStatus = Literal["pass", "warning", "fail"]
OptionEventSeverity = Literal["info", "warning", "error", "critical"]
OptionBacktestModelQuality = Literal["specified_only", "fixture_backed", "chain_backed", "lifecycle_backed"]
OptionOrderQuantityMode = Literal["whole_contracts"]


OUT_OF_V1_OPTION_STRATEGY_IDS: tuple[str, ...] = (
    "naked_short_straddle",
    "naked_short_strangle",
    "uncovered_short_option",
    "ratio_spread",
    "zero_dte_intraday_gamma",
    "portfolio_margin_optimization",
    "live_option_submission",
)

REQUIRED_OPTION_OBSERVABILITY_METRICS: tuple[str, ...] = (
    "option_chain_snapshot_count",
    "option_quote_missing_count",
    "greeks_missing_count",
    "chain_staleness_seconds",
    "wide_spread_reject_count",
    "assignment_event_count",
    "exercise_event_count",
    "expiry_event_count",
    "research_only_block_count",
    "option_backtest_model_quality",
)


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


def _normalize_symbol(value: object, field_name: str) -> str:
    normalized = _normalize_required_text(value, field_name).upper()
    if len(normalized) > 64:
        raise ValueError(f"{field_name} must be 64 characters or fewer.")
    return normalized


class OptionContractIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    underlyingSymbol: str = Field(..., min_length=1, max_length=32)
    optionSymbol: str = Field(..., min_length=1, max_length=64)
    expirationDate: date
    strikePrice: float = Field(..., gt=0)
    right: OptionRight
    multiplier: int = Field(default=100, gt=0)
    exerciseStyle: OptionExerciseStyle = "american"
    settlementStyle: OptionSettlementStyle = "physical"
    rootSymbol: str | None = Field(default=None, min_length=1, max_length=32)

    @field_validator("underlyingSymbol", mode="before")
    @classmethod
    def normalize_underlying_symbol(cls, value: object) -> str:
        return _normalize_symbol(value, "underlyingSymbol")

    @field_validator("optionSymbol", mode="before")
    @classmethod
    def normalize_option_symbol(cls, value: object) -> str:
        return _normalize_symbol(value, "optionSymbol")

    @field_validator("rootSymbol", mode="before")
    @classmethod
    def normalize_root_symbol(cls, value: object) -> str | None:
        if value is None:
            return None
        return _normalize_symbol(value, "rootSymbol")


class OptionLeg(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    legId: str = Field(..., min_length=1, max_length=128)
    contract: OptionContractIdentity
    side: OptionLegSide
    quantity: int = Field(default=1, ge=1)
    ratio: int = Field(default=1, ge=1)
    role: OptionLegRole
    openClose: OptionOpenClose = "open"
    premium: float | None = Field(default=None, ge=0)
    limitPrice: float | None = Field(default=None, gt=0)

    @field_validator("legId", mode="before")
    @classmethod
    def normalize_leg_id(cls, value: object) -> str:
        return _normalize_required_text(value, "legId")

    @model_validator(mode="after")
    def validate_role_matches_contract(self) -> "OptionLeg":
        if self.contract.right == "call" and self.role in {"long_put", "short_put"}:
            raise ValueError("Put leg roles require a put contract.")
        if self.contract.right == "put" and self.role in {"long_call", "short_call"}:
            raise ValueError("Call leg roles require a call contract.")
        if self.side == "long" and self.role in {"short_call", "short_put"}:
            raise ValueError("Short leg roles require side='short'.")
        if self.side == "short" and self.role in {"long_call", "long_put", "long_wing"}:
            raise ValueError("Long leg roles require side='long'.")
        return self


class OptionLegGroup(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    groupId: str = Field(..., min_length=1, max_length=128)
    strategyId: OptionStrategyId
    underlyingSymbol: str = Field(..., min_length=1, max_length=32)
    legs: list[OptionLeg] = Field(..., min_length=1)
    stockQuantity: int | None = None
    cashReserved: float | None = Field(default=None, ge=0)
    openedAt: datetime | None = None

    @field_validator("groupId", mode="before")
    @classmethod
    def normalize_group_id(cls, value: object) -> str:
        return _normalize_required_text(value, "groupId")

    @field_validator("underlyingSymbol", mode="before")
    @classmethod
    def normalize_underlying_symbol(cls, value: object) -> str:
        return _normalize_symbol(value, "underlyingSymbol")

    @model_validator(mode="after")
    def validate_underlying_consistency(self) -> "OptionLegGroup":
        mismatched = [leg.contract.optionSymbol for leg in self.legs if leg.contract.underlyingSymbol != self.underlyingSymbol]
        if mismatched:
            raise ValueError("All option legs must share the leg group's underlyingSymbol.")
        return self


class OptionStrategySupportFlags(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    researchBacktestSupported: bool = False
    brokerPreviewSupported: bool = False
    liveSubmitSupported: bool = False
    blockedReason: str | None = None

    @field_validator("blockedReason", mode="before")
    @classmethod
    def normalize_blocked_reason(cls, value: object) -> str | None:
        return _normalize_optional_text(value)

    @model_validator(mode="after")
    def validate_blocked_reason(self) -> "OptionStrategySupportFlags":
        if not (self.researchBacktestSupported or self.brokerPreviewSupported or self.liveSubmitSupported):
            if self.blockedReason is None:
                raise ValueError("blockedReason is required when every support flag is false.")
        if self.liveSubmitSupported and not self.brokerPreviewSupported:
            raise ValueError("liveSubmitSupported requires brokerPreviewSupported.")
        return self


class OptionStrategyTemplate(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    strategyId: OptionStrategyId
    displayName: str = Field(..., min_length=1, max_length=128)
    payoffFamily: OptionPayoffFamily
    stage: OptionStrategyStage
    approvalLevel: OptionApprovalLevel
    minLegs: int = Field(..., ge=1)
    maxLegs: int = Field(..., ge=1)
    requiredLegRoles: list[OptionLegRole] = Field(default_factory=list)
    usesStockOverlay: bool = False
    requiresStockPosition: bool = False
    requiresCashSecuring: bool = False
    definedRisk: bool = True
    netPremiumDirection: OptionNetPremiumDirection = "zero_or_variable"
    lifecycleModelRequired: bool = False
    support: OptionStrategySupportFlags
    summary: str = Field(..., min_length=1, max_length=512)
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_leg_bounds(self) -> "OptionStrategyTemplate":
        if self.maxLegs < self.minLegs:
            raise ValueError("maxLegs must be greater than or equal to minLegs.")
        if self.support.liveSubmitSupported:
            raise ValueError("Option strategy templates are research-only in v1; liveSubmitSupported must be false.")
        if self.stage == "specified_blocked" and self.support.researchBacktestSupported:
            raise ValueError("specified_blocked strategies cannot be researchBacktestSupported.")
        return self


class OptionStrategyExclusion(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    strategyId: str = Field(..., min_length=1, max_length=128)
    reason: str = Field(..., min_length=1, max_length=512)
    stage: OptionStrategyStage = "out_of_v1"


class OptionStrategyLadderResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ladderVersion: str = Field(default="options-ladder-v1", min_length=1, max_length=64)
    templates: list[OptionStrategyTemplate] = Field(..., min_length=1)
    exclusions: list[OptionStrategyExclusion] = Field(default_factory=list)
    generatedAt: datetime | None = None


class OptionPayoffProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    strategyId: OptionStrategyId
    expirationScope: OptionExpirationScope = "final_expiration"
    maxProfit: float | None = None
    maxProfitDescription: str | None = None
    maxLoss: float | None = Field(default=None, ge=0)
    maxLossDescription: str | None = None
    breakevens: list[float] = Field(default_factory=list)
    profitWindowLower: float | None = Field(default=None, ge=0)
    profitWindowUpper: float | None = Field(default=None, ge=0)
    profitWindowDescription: str = Field(..., min_length=1, max_length=512)
    deltaSign: OptionExposureSign = "mixed"
    thetaSign: OptionExposureSign = "mixed"
    vegaSign: OptionExposureSign = "mixed"
    idealIvEnvironment: OptionIvEnvironment = "unknown"
    assumptions: list[str] = Field(default_factory=list)
    support: OptionStrategySupportFlags

    @field_validator("maxProfitDescription", "maxLossDescription", mode="before")
    @classmethod
    def normalize_optional_description(cls, value: object) -> str | None:
        return _normalize_optional_text(value)

    @model_validator(mode="after")
    def validate_profit_window(self) -> "OptionPayoffProfile":
        if (
            self.profitWindowLower is not None
            and self.profitWindowUpper is not None
            and self.profitWindowUpper < self.profitWindowLower
        ):
            raise ValueError("profitWindowUpper must be greater than or equal to profitWindowLower.")
        return self


class OptionQuoteSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    snapshotId: str = Field(..., min_length=1, max_length=128)
    contract: OptionContractIdentity
    asOf: datetime
    bid: float | None = Field(default=None, ge=0)
    ask: float | None = Field(default=None, ge=0)
    mid: float | None = Field(default=None, ge=0)
    last: float | None = Field(default=None, ge=0)
    mark: float | None = Field(default=None, ge=0)
    bidAskWidth: float | None = Field(default=None, ge=0)
    bidAskWidthPct: float | None = Field(default=None, ge=0)
    impliedVolatility: float | None = Field(default=None, ge=0)
    delta: float | None = None
    gamma: float | None = None
    theta: float | None = None
    vega: float | None = None
    rho: float | None = None
    openInterest: int | None = Field(default=None, ge=0)
    volume: int | None = Field(default=None, ge=0)
    quoteAgeSeconds: int | None = Field(default=None, ge=0)
    feed: str | None = Field(default=None, min_length=1, max_length=64)
    provider: OptionProvider = "alpaca"
    stale: bool = False

    @field_validator("snapshotId", mode="before")
    @classmethod
    def normalize_snapshot_id(cls, value: object) -> str:
        return _normalize_required_text(value, "snapshotId")

    @model_validator(mode="after")
    def validate_quote_consistency(self) -> "OptionQuoteSnapshot":
        if self.bid is not None and self.ask is not None:
            if self.ask < self.bid:
                raise ValueError("ask must be greater than or equal to bid.")
            computed_width = self.ask - self.bid
            if self.bidAskWidth is None:
                self.bidAskWidth = computed_width
            if self.mid is None:
                self.mid = (self.bid + self.ask) / 2
        if self.bidAskWidthPct is None and self.bidAskWidth is not None and self.mid not in (None, 0):
            self.bidAskWidthPct = self.bidAskWidth / self.mid
        return self


class OptionChainSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    snapshotId: str = Field(..., min_length=1, max_length=128)
    provider: OptionProvider = "alpaca"
    underlyingSymbol: str = Field(..., min_length=1, max_length=32)
    asOf: datetime
    expirationDate: date | None = None
    quotes: list[OptionQuoteSnapshot] = Field(default_factory=list)
    totalContractCount: int = Field(..., ge=0)
    pageCount: int = Field(default=1, ge=1)
    paginationComplete: bool = False
    chainComplete: bool = False
    missingQuoteCount: int = Field(default=0, ge=0)
    missingGreeksCount: int = Field(default=0, ge=0)
    maxQuoteAgeSeconds: int | None = Field(default=None, ge=0)
    feed: str | None = Field(default=None, min_length=1, max_length=64)

    @field_validator("snapshotId", mode="before")
    @classmethod
    def normalize_snapshot_id(cls, value: object) -> str:
        return _normalize_required_text(value, "snapshotId")

    @field_validator("underlyingSymbol", mode="before")
    @classmethod
    def normalize_underlying_symbol(cls, value: object) -> str:
        return _normalize_symbol(value, "underlyingSymbol")

    @model_validator(mode="after")
    def validate_chain_counts(self) -> "OptionChainSnapshot":
        if self.totalContractCount < len(self.quotes):
            raise ValueError("totalContractCount cannot be less than the quote count.")
        if self.chainComplete and not self.paginationComplete:
            raise ValueError("chainComplete requires paginationComplete.")
        return self


class OptionLifecycleEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    eventId: str = Field(..., min_length=1, max_length=128)
    eventType: OptionLifecycleEventType
    occurredAt: datetime
    strategyId: OptionStrategyId | None = None
    contract: OptionContractIdentity | None = None
    quantity: int | None = Field(default=None, ge=0)
    cashImpact: float | None = None
    stockQuantityImpact: int | None = None
    message: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("eventId", mode="before")
    @classmethod
    def normalize_event_id(cls, value: object) -> str:
        return _normalize_required_text(value, "eventId")


class OptionBrokerCapability(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: OptionProvider = "alpaca"
    environment: OptionEnvironment = "paper"
    approvalLevel: OptionApprovalLevel | None = None
    supportsOptionAccounts: bool = False
    supportsOptionChains: bool = False
    supportsOptionQuotes: bool = False
    supportsOptionGreeks: bool = False
    supportsMultiLegOrders: bool = False
    supportsExercise: bool = False
    supportsWholeContractQuantityOnly: bool = True
    supportsNotionalOptionOrders: bool = False
    supportsExtendedHoursOptions: bool = False
    allowedOrderTypes: list[OptionOrderType] = Field(default_factory=lambda: ["market", "limit"])
    allowedTimeInForce: list[OptionTimeInForce] = Field(default_factory=lambda: ["day"])
    maxLegsPerOrder: int | None = Field(default=None, ge=1)
    restrictions: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_option_constraints(self) -> "OptionBrokerCapability":
        if not self.allowedOrderTypes:
            raise ValueError("allowedOrderTypes must include at least one order type.")
        if not self.allowedTimeInForce:
            raise ValueError("allowedTimeInForce must include at least one TIF.")
        if self.supportsNotionalOptionOrders:
            raise ValueError("Options contracts require whole-contract quantity; notional option orders are not supported.")
        if self.supportsExtendedHoursOptions:
            raise ValueError("Extended-hours option trading is not supported in v1 broker constraints.")
        return self


class OptionBrokerConstraintProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: OptionProvider = "alpaca"
    environment: OptionEnvironment = "paper"
    capability: OptionBrokerCapability
    orderQuantityMode: OptionOrderQuantityMode = "whole_contracts"
    allowedFamilies: list[OptionStrategyId] = Field(default_factory=list)
    blockedFamilies: list[OptionStrategyId] = Field(default_factory=list)
    multiLegRestrictions: list[str] = Field(default_factory=list)
    researchOnly: bool = True
    brokerPreviewSupported: bool = False
    liveSubmitSupported: bool = False

    @model_validator(mode="after")
    def validate_research_only_profile(self) -> "OptionBrokerConstraintProfile":
        if self.liveSubmitSupported:
            raise ValueError("liveSubmitSupported must remain false for v1 option constraint profiles.")
        if self.provider != self.capability.provider:
            raise ValueError("provider must match capability.provider.")
        if self.environment != self.capability.environment:
            raise ValueError("environment must match capability.environment.")
        overlap = set(self.allowedFamilies).intersection(self.blockedFamilies)
        if overlap:
            raise ValueError(f"Families cannot be both allowed and blocked: {sorted(overlap)}")
        return self


class OptionRiskLimitSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    maxUnderlierDeltaEquivalentExposure: float | None = Field(default=None, gt=0)
    maxGrossOptionNotional: float | None = Field(default=None, gt=0)
    maxPremiumAtRisk: float | None = Field(default=None, gt=0)
    maxDefinedMaxLoss: float | None = Field(default=None, gt=0)
    maxContractsPerUnderlier: int | None = Field(default=None, ge=1)
    maxContractsPerExpiry: int | None = Field(default=None, ge=1)
    maxContractsPerFamily: int | None = Field(default=None, ge=1)
    maxExpirationBucketConcentrationPct: float | None = Field(default=None, gt=0, le=100)
    maxShortGammaConcentrationPct: float | None = Field(default=None, gt=0, le=100)


class OptionDataQualityGateSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    maxQuoteAgeSeconds: int = Field(..., ge=0)
    maxBidAskWidthPct: float | None = Field(default=None, ge=0)
    requireChainCompleteness: bool = True
    requireGreeks: bool = True
    requireImpliedVolatility: bool = True
    minOpenInterest: int | None = Field(default=None, ge=0)
    minVolume: int | None = Field(default=None, ge=0)
    requireFeedMetadata: bool = True
    rejectStaleChain: bool = True
    requirePaginationCoverage: bool = True


class OptionLifecycleGateSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    handleExpiration: bool = True
    handleAssignment: bool = True
    handleExercise: bool = True
    handleDoNotExerciseGap: bool = True
    blockInsufficientBuyingPowerAtExpiry: bool = True
    handleForcedLiquidationWindow: bool = True
    trackPostAssignmentStockCashExposure: bool = True


class OptionRiskGateResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(..., min_length=1, max_length=128)
    status: OptionGateStatus
    severity: OptionEventSeverity = "info"
    blocking: bool = False
    message: str = Field(default="", max_length=512)
    observedValue: float | str | bool | None = None
    limitValue: float | str | bool | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class OptionRiskEvaluation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evaluationId: str = Field(..., min_length=1, max_length=128)
    strategyId: OptionStrategyId
    generatedAt: datetime
    support: OptionStrategySupportFlags
    payoff: OptionPayoffProfile
    riskLimits: OptionRiskLimitSet
    dataQualityGates: OptionDataQualityGateSet
    lifecycleGates: OptionLifecycleGateSet
    gateResults: list[OptionRiskGateResult] = Field(default_factory=list)
    metrics: list[str] = Field(default_factory=lambda: list(REQUIRED_OPTION_OBSERVABILITY_METRICS))
    approvedForResearchBacktest: bool = False
    approvedForBrokerPreview: bool = False
    approvedForLiveSubmit: bool = False

    @field_validator("evaluationId", mode="before")
    @classmethod
    def normalize_evaluation_id(cls, value: object) -> str:
        return _normalize_required_text(value, "evaluationId")

    @model_validator(mode="after")
    def validate_support_alignment(self) -> "OptionRiskEvaluation":
        if self.approvedForLiveSubmit:
            raise ValueError("Option live submission is out of scope for v1.")
        if self.approvedForResearchBacktest and not self.support.researchBacktestSupported:
            raise ValueError("approvedForResearchBacktest requires researchBacktestSupported.")
        if self.approvedForBrokerPreview and not self.support.brokerPreviewSupported:
            raise ValueError("approvedForBrokerPreview requires brokerPreviewSupported.")
        missing_metrics = [metric for metric in REQUIRED_OPTION_OBSERVABILITY_METRICS if metric not in self.metrics]
        if missing_metrics:
            raise ValueError(f"Missing required option observability metrics: {missing_metrics}")
        return self


class OptionBacktestEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    eventId: str = Field(..., min_length=1, max_length=128)
    runId: str = Field(..., min_length=1, max_length=128)
    eventType: OptionBacktestEventType
    severity: OptionEventSeverity = "info"
    occurredAt: datetime
    strategyId: OptionStrategyId | None = None
    contract: OptionContractIdentity | None = None
    message: str = Field(default="", max_length=512)
    blocking: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class OptionBacktestResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    resultId: str = Field(..., min_length=1, max_length=128)
    runId: str = Field(..., min_length=1, max_length=128)
    strategyTemplate: OptionStrategyTemplate
    payoff: OptionPayoffProfile
    modelQuality: OptionBacktestModelQuality = "specified_only"
    quoteSnapshots: list[OptionQuoteSnapshot] = Field(default_factory=list)
    chainSnapshots: list[OptionChainSnapshot] = Field(default_factory=list)
    lifecycleEvents: list[OptionLifecycleEvent] = Field(default_factory=list)
    events: list[OptionBacktestEvent] = Field(default_factory=list)
    riskEvaluation: OptionRiskEvaluation | None = None


def _support(
    *,
    research: bool,
    preview: bool = False,
    blocked_reason: str | None = None,
) -> OptionStrategySupportFlags:
    return OptionStrategySupportFlags(
        researchBacktestSupported=research,
        brokerPreviewSupported=preview,
        liveSubmitSupported=False,
        blockedReason=blocked_reason,
    )


def _template(
    strategy_id: OptionStrategyId,
    display_name: str,
    payoff_family: OptionPayoffFamily,
    stage: OptionStrategyStage,
    approval_level: OptionApprovalLevel,
    min_legs: int,
    max_legs: int,
    required_roles: list[OptionLegRole],
    summary: str,
    *,
    support: OptionStrategySupportFlags,
    uses_stock_overlay: bool = False,
    requires_stock_position: bool = False,
    requires_cash_securing: bool = False,
    defined_risk: bool = True,
    net_premium_direction: OptionNetPremiumDirection = "zero_or_variable",
    lifecycle_model_required: bool = False,
    notes: list[str] | None = None,
) -> OptionStrategyTemplate:
    return OptionStrategyTemplate(
        strategyId=strategy_id,
        displayName=display_name,
        payoffFamily=payoff_family,
        stage=stage,
        approvalLevel=approval_level,
        minLegs=min_legs,
        maxLegs=max_legs,
        requiredLegRoles=required_roles,
        usesStockOverlay=uses_stock_overlay,
        requiresStockPosition=requires_stock_position,
        requiresCashSecuring=requires_cash_securing,
        definedRisk=defined_risk,
        netPremiumDirection=net_premium_direction,
        lifecycleModelRequired=lifecycle_model_required,
        support=support,
        summary=summary,
        notes=notes or [],
    )


def canonical_option_strategy_templates() -> tuple[OptionStrategyTemplate, ...]:
    core = _support(research=True, preview=True)
    experimental = _support(research=True, preview=False, blocked_reason="Experimental research support requires core fixtures.")
    blocked = _support(
        research=False,
        preview=False,
        blocked_reason="Blocked until assignment, expiry, and path-dependent lifecycle modeling is trustworthy.",
    )

    return (
        _template(
            "covered_call",
            "Covered Call",
            "stock_overlay_income",
            "core_research",
            1,
            1,
            1,
            ["short_call", "underlying_stock"],
            "Long stock plus a short call for stock-overlay income with capped upside.",
            support=core,
            uses_stock_overlay=True,
            requires_stock_position=True,
            net_premium_direction="credit",
        ),
        _template(
            "cash_secured_put",
            "Cash-secured Put",
            "stock_overlay_income",
            "core_research",
            1,
            1,
            1,
            ["short_put", "cash_reserve"],
            "Short put backed by reserved cash for a defined assignment obligation.",
            support=core,
            requires_cash_securing=True,
            net_premium_direction="credit",
        ),
        _template("long_call", "Long Call", "outright_directional", "core_research", 2, 1, 1, ["long_call"], "Bullish convex upside with premium-paid max loss.", support=core, net_premium_direction="debit"),
        _template("long_put", "Long Put", "outright_directional", "core_research", 2, 1, 1, ["long_put"], "Bearish convex exposure or simple hedge with premium-paid max loss.", support=core, net_premium_direction="debit"),
        _template("protective_put", "Protective Put", "hedge", "core_research", 2, 1, 1, ["long_put", "underlying_stock"], "Long stock plus long put to preserve upside and define downside.", support=core, uses_stock_overlay=True, requires_stock_position=True, net_premium_direction="debit"),
        _template("collar", "Collar", "stock_overlay_hedge", "core_research", 3, 2, 2, ["long_put", "short_call", "underlying_stock"], "Long stock plus long put and short call for capped, lower-cost protection.", support=core, uses_stock_overlay=True, requires_stock_position=True, net_premium_direction="zero_or_variable"),
        _template("bull_call_spread", "Bull Call Spread", "vertical_spread", "core_research", 3, 2, 2, ["long_call", "short_call"], "Debit call vertical for a moderately bullish target view.", support=core, net_premium_direction="debit"),
        _template("bear_put_spread", "Bear Put Spread", "vertical_spread", "core_research", 3, 2, 2, ["long_put", "short_put"], "Debit put vertical for a moderately bearish target view.", support=core, net_premium_direction="debit"),
        _template("bull_put_spread", "Bull Put Spread", "vertical_spread", "core_research", 3, 2, 2, ["short_put", "long_put"], "Credit put vertical for neutral to mildly bullish defined-risk income.", support=core, net_premium_direction="credit"),
        _template("bear_call_spread", "Bear Call Spread", "vertical_spread", "core_research", 3, 2, 2, ["short_call", "long_call"], "Credit call vertical for neutral to mildly bearish defined-risk income.", support=core, net_premium_direction="credit"),
        _template("long_straddle", "Long Straddle", "volatility", "experimental_research", 3, 2, 2, ["long_call", "long_put"], "Long at-the-money call and put for a large move in either direction.", support=experimental, net_premium_direction="debit"),
        _template("long_strangle", "Long Strangle", "volatility", "experimental_research", 3, 2, 2, ["long_call", "long_put"], "Long out-of-the-money call and put for cheaper long-volatility convexity.", support=experimental, net_premium_direction="debit"),
        _template("iron_condor", "Iron Condor", "volatility", "experimental_research", 3, 4, 4, ["short_put", "long_put", "short_call", "long_call"], "Short OTM put spread plus short OTM call spread for defined-risk range income.", support=experimental, net_premium_direction="credit"),
        _template("iron_butterfly", "Iron Butterfly", "volatility", "experimental_research", 3, 4, 4, ["short_put", "short_call", "long_put", "long_call"], "Short ATM straddle with long wings for a tight range view.", support=experimental, net_premium_direction="credit"),
        _template("long_butterfly", "Long Butterfly", "volatility", "experimental_research", 3, 3, 3, ["long_wing", "short_body"], "Defined-risk target-price structure with maximum payoff near the body strike.", support=experimental, net_premium_direction="debit"),
        _template("calendar_spread", "Calendar Spread", "time_spread", "specified_blocked", 3, 2, 2, ["short_call", "long_call"], "Near-term short option plus farther-dated long option at the same strike.", support=blocked, net_premium_direction="debit", lifecycle_model_required=True),
        _template("diagonal_spread", "Diagonal Spread", "time_spread", "specified_blocked", 3, 2, 2, ["short_call", "long_call"], "Time spread with different strikes for directional calendar exposure.", support=blocked, net_premium_direction="debit", lifecycle_model_required=True),
        _template("pmcc", "Poor Man's Covered Call", "time_spread", "specified_blocked", 3, 2, 2, ["long_call", "short_call"], "Bullish call diagonal intended to mimic a covered call with lower capital.", support=blocked, net_premium_direction="debit", lifecycle_model_required=True),
        _template("covered_straddle", "Covered Straddle", "aggressive_income", "specified_blocked", 3, 2, 2, ["short_call", "short_put", "underlying_stock"], "Long stock with short call and short put; aggressive income with heavier downside exposure.", support=blocked, uses_stock_overlay=True, requires_stock_position=True, requires_cash_securing=True, defined_risk=False, net_premium_direction="credit", lifecycle_model_required=True),
        _template("covered_combination", "Covered Combination", "aggressive_income", "specified_blocked", 3, 2, 2, ["short_call", "short_put", "underlying_stock"], "Covered short call plus cash-secured short put at different strikes.", support=blocked, uses_stock_overlay=True, requires_stock_position=True, requires_cash_securing=True, defined_risk=False, net_premium_direction="credit", lifecycle_model_required=True),
        _template("covered_strangle", "Covered Strangle", "aggressive_income", "specified_blocked", 3, 2, 2, ["short_call", "short_put", "underlying_stock"], "Covered combination variant with out-of-the-money short call and put.", support=blocked, uses_stock_overlay=True, requires_stock_position=True, requires_cash_securing=True, defined_risk=False, net_premium_direction="credit", lifecycle_model_required=True),
    )


def canonical_option_strategy_exclusions() -> tuple[OptionStrategyExclusion, ...]:
    return tuple(
        OptionStrategyExclusion(strategyId=strategy_id, reason="Explicitly out of v1 options capability scope.")
        for strategy_id in OUT_OF_V1_OPTION_STRATEGY_IDS
    )


def canonical_option_strategy_ladder() -> OptionStrategyLadderResponse:
    return OptionStrategyLadderResponse(
        templates=list(canonical_option_strategy_templates()),
        exclusions=list(canonical_option_strategy_exclusions()),
    )
