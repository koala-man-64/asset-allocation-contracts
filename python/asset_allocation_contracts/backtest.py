from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from asset_allocation_contracts.options import OptionBacktestModelQuality, OptionStrategyId
from asset_allocation_contracts.strategy import ExitRuleType, ExitRuleVisualKey, StrategyConfig
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator

RunStatus = Literal["queued", "running", "completed", "failed"]
BacktestLookupState = Literal["not_run", "queued", "running", "completed", "failed"]
BacktestStreamEventType = Literal["accepted", "status", "heartbeat", "completed", "failed"]
TradeRole = Literal["entry", "rebalance_increase", "rebalance_decrease", "exit"]
BacktestPolicyEventScope = Literal["strategy", "sleeve", "position", "symbol", "portfolio"]
BacktestPolicyEventType = Literal["rebalance", "strategy_risk", "position_exit", "reentry", "regime"]
BacktestPolicyDecision = Literal["applied", "skipped", "blocked"]
BacktestResearchIntegrityStatus = Literal["strict_passed", "strict_failed", "legacy_uncontrolled"]
BacktestExecutionModel = Literal["simple_bps"]
BacktestExecutionModelQuality = Literal["not_tca_grade"]
BacktestApprovalReadiness = Literal["research_only"]
BacktestDataQualityEventSeverity = Literal["warning", "error", "fatal"]
BacktestBenchmarkAttributionMethod = Literal["simple_total_return"]
BacktestBenchmarkAttributionDataQualityStatus = Literal["complete"]


class RunRecordResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    status: RunStatus
    submitted_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    run_name: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    error: str | None = None
    strategy_name: str | None = None
    strategy_version: int | None = Field(default=None, ge=1)
    bar_size: str | None = Field(default=None, min_length=1, max_length=32)
    execution_name: str | None = Field(default=None, min_length=1, max_length=255)


class RunListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    runs: list[RunRecordResponse]
    limit: int
    offset: int


class BacktestExecutionSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    initialCapital: float | None = Field(default=None, gt=0)
    benchmarkSymbol: str | None = Field(default=None, min_length=1, max_length=32)
    executionModel: BacktestExecutionModel = "simple_bps"
    commissionBps: float | None = Field(default=None, ge=0)
    slippageBps: float | None = Field(default=None, ge=0)
    notes: str = Field(default="", max_length=2000)

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_cost_model(cls, value: object) -> object:
        if not isinstance(value, dict):
            return value
        payload = dict(value)
        if "executionModel" not in payload and "costModel" in payload:
            legacy_cost_model = str(payload.get("costModel") or "").strip().lower()
            if legacy_cost_model:
                payload["executionModel"] = "simple_bps" if legacy_cost_model == "default" else legacy_cost_model
        payload.pop("costModel", None)
        return payload

    @model_validator(mode="after")
    def validate_supported_execution_model(self) -> "BacktestExecutionSettings":
        if self.executionModel != "simple_bps":
            raise ValueError(
                "Backtests currently only support executionSettings.executionModel='simple_bps'."
            )
        return self


BacktestExecutionAssumptions = BacktestExecutionSettings


class RunPinsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    strategyName: str | None = Field(default=None, min_length=1, max_length=128)
    strategyVersion: int | None = Field(default=None, ge=1)
    rankingSchemaName: str | None = Field(default=None, min_length=1, max_length=128)
    rankingSchemaVersion: int | None = Field(default=None, ge=1)
    universeName: str | None = Field(default=None, min_length=1, max_length=128)
    universeVersion: int | None = Field(default=None, ge=1)
    regimeModelName: str | None = Field(default=None, min_length=1, max_length=128)
    regimeModelVersion: int | None = Field(default=None, ge=1)
    regimePolicyName: str | None = Field(default=None, min_length=1, max_length=128)
    regimePolicyVersion: int | None = Field(default=None, ge=1)
    riskProfileName: str | None = Field(default=None, min_length=1, max_length=128)
    riskPolicyName: str | None = Field(default=None, min_length=1, max_length=128)
    riskPolicyVersion: int | None = Field(default=None, ge=1)
    exitPolicyName: str | None = Field(default=None, min_length=1, max_length=128)
    exitPolicyVersion: int | None = Field(default=None, ge=1)
    rebalancePolicyName: str | None = Field(default=None, min_length=1, max_length=128)
    rebalancePolicyVersion: int | None = Field(default=None, ge=1)


class RunStatusResponse(RunRecordResponse):
    model_config = ConfigDict(extra="forbid")

    results_ready_at: datetime | None = None
    results_schema_version: int | None = Field(default=None, ge=1)
    pins: RunPinsResponse | None = None
    executionSettings: BacktestExecutionSettings | None = None


class StrategyReferenceInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    strategyName: str = Field(..., min_length=1, max_length=128)
    strategyVersion: int | None = Field(default=None, ge=1)


class BacktestResultLinks(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summaryUrl: str = Field(..., min_length=1)
    metricsTimeseriesUrl: str = Field(..., min_length=1)
    metricsRollingUrl: str = Field(..., min_length=1)
    tradesUrl: str = Field(..., min_length=1)
    closedPositionsUrl: str = Field(..., min_length=1)
    policyEventsUrl: str | None = Field(default=None, min_length=1)
    dataQualityEventsUrl: str | None = Field(default=None, min_length=1)


def _has_legacy_regime_reference(strategy_config: StrategyConfig) -> bool:
    component_refs = strategy_config.componentRefs
    return (
        strategy_config.regimePolicyConfigName is not None
        or strategy_config.regimePolicyConfigVersion is not None
        or (component_refs is not None and component_refs.regimePolicy is not None)
    )


def _validate_inline_backtest_support(strategy_config: StrategyConfig) -> None:
    if strategy_config.costModel != "default":
        raise ValueError("Backtests currently only support strategyConfig.costModel='default'.")
    rebalance_policy = strategy_config.rebalancePolicy
    if rebalance_policy is not None and rebalance_policy.frequency == "manual":
        raise ValueError("Backtests do not support rebalancePolicy.frequency='manual'.")
    if strategy_config.regimeSource is None and _has_legacy_regime_reference(strategy_config):
        raise ValueError(
            "Legacy regime policy references must normalize to regimeSource before backtest submission."
        )


class _BacktestRequestBase(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "oneOf": [
                {"required": ["strategyRef"]},
                {"required": ["strategyConfig"]},
            ]
        },
    )

    strategyRef: StrategyReferenceInput | None = None
    strategyConfig: StrategyConfig | None = None
    startTs: datetime
    endTs: datetime
    barSize: str = Field(..., min_length=1, max_length=32)
    runName: str | None = Field(default=None, max_length=255)
    executionSettings: BacktestExecutionSettings | None = Field(
        default=None,
        validation_alias=AliasChoices("executionSettings", "assumptions"),
    )

    @property
    def assumptions(self) -> BacktestExecutionSettings | None:
        return self.executionSettings

    @model_validator(mode="after")
    def validate_strategy_input(self) -> "_BacktestRequestBase":
        has_strategy_ref = self.strategyRef is not None
        has_strategy_config = self.strategyConfig is not None
        if has_strategy_ref == has_strategy_config:
            raise ValueError("Exactly one of strategyRef or strategyConfig must be provided.")
        if self.strategyConfig is not None:
            _validate_inline_backtest_support(self.strategyConfig)
        return self


class BacktestLookupRequest(_BacktestRequestBase):
    pass


class BacktestRunRequest(_BacktestRequestBase):
    pass


class BacktestLookupResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    found: bool
    state: BacktestLookupState
    run: RunStatusResponse | None = None
    result: BacktestSummary | None = None
    links: BacktestResultLinks | None = None


class BacktestRunResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run: RunStatusResponse
    created: bool
    reusedInflight: bool
    streamUrl: str = Field(..., min_length=1)


class BacktestBenchmarkAttribution(BaseModel):
    model_config = ConfigDict(extra="forbid")

    benchmarkSymbol: str = Field(..., min_length=1, max_length=32)
    attributionMethod: BacktestBenchmarkAttributionMethod = "simple_total_return"
    dataQualityStatus: BacktestBenchmarkAttributionDataQualityStatus = "complete"
    strategyTotalReturn: float
    benchmarkTotalReturn: float
    excessTotalReturn: float
    strategyAnnualizedReturn: float | None = None
    benchmarkAnnualizedReturn: float | None = None
    excessAnnualizedReturn: float | None = None
    startTs: datetime
    endTs: datetime
    observationCount: int = Field(..., ge=1)


class BacktestSummary(BaseModel):
    model_config = ConfigDict(extra="allow")

    run_id: str | None = None
    run_name: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    total_return: float | None = None
    annualized_return: float | None = None
    annualized_volatility: float | None = None
    sharpe_ratio: float | None = None
    max_drawdown: float | None = None
    trades: int | None = None
    initial_cash: float | None = None
    final_equity: float | None = None
    gross_total_return: float | None = None
    gross_annualized_return: float | None = None
    total_commission: float | None = None
    total_slippage_cost: float | None = None
    total_transaction_cost: float | None = None
    cost_drag_bps: float | None = None
    avg_gross_exposure: float | None = None
    avg_net_exposure: float | None = None
    sortino_ratio: float | None = None
    calmar_ratio: float | None = None
    closed_positions: int | None = None
    winning_positions: int | None = None
    losing_positions: int | None = None
    hit_rate: float | None = None
    avg_win_pnl: float | None = None
    avg_loss_pnl: float | None = None
    avg_win_return: float | None = None
    avg_loss_return: float | None = None
    payoff_ratio: float | None = None
    profit_factor: float | None = None
    expectancy_pnl: float | None = None
    expectancy_return: float | None = None
    research_integrity_status: BacktestResearchIntegrityStatus | None = None
    execution_model: BacktestExecutionModel | None = None
    execution_model_quality: BacktestExecutionModelQuality | None = None
    approval_readiness: BacktestApprovalReadiness | None = None
    data_quality_event_count: int | None = Field(default=None, ge=0)
    policy_event_count: int | None = Field(default=None, ge=0)
    requested_residual_cash_weight: float | None = Field(default=None, ge=0, le=1)
    executed_residual_cash_weight: float | None = Field(default=None, ge=0, le=1)
    option_strategy_id: OptionStrategyId | None = None
    option_chain_snapshot_count: int | None = Field(default=None, ge=0)
    option_quote_missing_count: int | None = Field(default=None, ge=0)
    greeks_missing_count: int | None = Field(default=None, ge=0)
    chain_staleness_seconds: float | None = Field(default=None, ge=0)
    wide_spread_reject_count: int | None = Field(default=None, ge=0)
    assignment_event_count: int | None = Field(default=None, ge=0)
    exercise_event_count: int | None = Field(default=None, ge=0)
    expiry_event_count: int | None = Field(default=None, ge=0)
    research_only_block_count: int | None = Field(default=None, ge=0)
    option_backtest_model_quality: OptionBacktestModelQuality | None = None
    benchmarkAttribution: BacktestBenchmarkAttribution | None = None


class BacktestResultMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    results_schema_version: int = Field(default=9, ge=1)
    bar_size: str = Field(..., min_length=1, max_length=32)
    periods_per_year: int = Field(..., ge=1)
    strategy_scope: str = Field(..., min_length=1, max_length=128)


class BacktestStreamEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event: BacktestStreamEventType
    run: RunStatusResponse
    summary: BacktestSummary | None = None
    metadata: BacktestResultMetadata | None = None
    links: BacktestResultLinks | None = None


class TimeseriesPointResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: str
    portfolio_value: float
    drawdown: float
    period_return: float | None = None
    daily_return: float | None = Field(default=None, deprecated=True)
    cumulative_return: float | None = None
    cash: float | None = None
    gross_exposure: float | None = None
    net_exposure: float | None = None
    turnover: float | None = None
    commission: float | None = None
    slippage_cost: float | None = None
    trade_count: int | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_period_return_compatibility(cls, value: object) -> object:
        if not isinstance(value, dict):
            return value

        payload = dict(value)
        period_return = payload.get("period_return")
        daily_return = payload.get("daily_return")

        if period_return is None and daily_return is not None:
            payload["period_return"] = daily_return
        if daily_return is None and period_return is not None:
            payload["daily_return"] = period_return
        return payload


class TimeseriesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metadata: BacktestResultMetadata | None = None
    points: list[TimeseriesPointResponse]
    total_points: int
    truncated: bool


class RollingMetricPointResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: str
    window_periods: int | None = None
    window_days: int | None = Field(default=None, deprecated=True)
    rolling_return: float | None = None
    rolling_volatility: float | None = None
    rolling_sharpe: float | None = None
    rolling_max_drawdown: float | None = None
    turnover_sum: float | None = None
    commission_sum: float | None = None
    slippage_cost_sum: float | None = None
    n_trades_sum: float | None = None
    gross_exposure_avg: float | None = None
    net_exposure_avg: float | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_window_periods_compatibility(cls, value: object) -> object:
        if not isinstance(value, dict):
            return value

        payload = dict(value)
        window_periods = payload.get("window_periods")
        window_days = payload.get("window_days")

        if window_periods is None and window_days is not None:
            payload["window_periods"] = window_days
        if window_days is None and window_periods is not None:
            payload["window_days"] = window_periods
        return payload


class RollingMetricsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metadata: BacktestResultMetadata | None = None
    points: list[RollingMetricPointResponse]
    total_points: int
    truncated: bool


class TradeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    execution_date: str
    symbol: str
    quantity: float
    price: float
    notional: float
    commission: float
    slippage_cost: float
    cash_after: float
    position_id: str | None = None
    trade_role: TradeRole | None = None
    requested_target_weight: float | None = Field(default=None, ge=0, le=1)
    executed_target_weight: float | None = Field(default=None, ge=0, le=1)


class TradeListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trades: list[TradeResponse]
    total: int
    limit: int
    offset: int


class ClosedPositionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    position_id: str
    symbol: str
    opened_at: str
    closed_at: str
    holding_period_bars: int
    average_cost: float
    exit_price: float
    max_quantity: float
    resize_count: int
    realized_pnl: float
    realized_return: float | None = None
    total_commission: float
    total_slippage_cost: float
    total_transaction_cost: float
    exit_reason: str | None = None
    exit_rule_id: str | None = None


class ClosedPositionListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    positions: list[ClosedPositionResponse]
    total: int
    limit: int
    offset: int


class ExitRuleAttributionRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ruleId: str = Field(..., min_length=1, max_length=128)
    ruleType: ExitRuleType | None = None
    description: str = Field(default="", max_length=2048)
    visualKey: ExitRuleVisualKey | None = None
    priority: int | None = Field(default=None, ge=0)
    closedPositionCount: int = Field(default=0, ge=0)
    realizedPnl: float = 0.0
    averageRealizedReturn: float | None = None
    winRate: float | None = None
    averageHoldingPeriodBars: float | None = None
    totalTransactionCost: float = 0.0


class ExitRuleAttributionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    runId: str = Field(..., min_length=1, max_length=128)
    exitPolicyName: str | None = Field(default=None, min_length=1, max_length=128)
    exitPolicyVersion: int | None = Field(default=None, ge=1)
    exitPolicyConfigHash: str | None = Field(default=None, min_length=1, max_length=128)
    rules: list[ExitRuleAttributionRow] = Field(default_factory=list)
    unattributedExitCount: int = Field(default=0, ge=0)
    missingRuleIds: list[str] = Field(default_factory=list)


class BacktestPolicyEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    event_seq: int = Field(..., ge=0)
    bar_ts: datetime
    scope: BacktestPolicyEventScope
    policy_type: BacktestPolicyEventType
    decision: BacktestPolicyDecision
    reason_code: str = Field(..., min_length=1, max_length=128)
    symbol: str | None = Field(default=None, min_length=1, max_length=32)
    position_id: str | None = Field(default=None, min_length=1, max_length=128)
    policy_id: str | None = Field(default=None, min_length=1, max_length=128)
    observed_value: float | None = None
    threshold_value: float | None = None
    action: str | None = Field(default=None, min_length=1, max_length=128)
    requested_target_weight: float | None = Field(default=None, ge=0, le=1)
    executed_target_weight: float | None = Field(default=None, ge=0, le=1)
    requested_residual_cash_weight: float | None = Field(default=None, ge=0, le=1)
    executed_residual_cash_weight: float | None = Field(default=None, ge=0, le=1)
    details: dict[str, Any] = Field(default_factory=dict)


class BacktestPolicyEventListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    events: list[BacktestPolicyEvent]
    total: int
    limit: int
    offset: int


class BacktestDataQualityEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    event_seq: int = Field(..., ge=0)
    bar_ts: datetime
    severity: BacktestDataQualityEventSeverity
    table_name: str = Field(..., min_length=1, max_length=128)
    symbol: str | None = Field(default=None, min_length=1, max_length=32)
    field_name: str | None = Field(default=None, min_length=1, max_length=128)
    reason_code: str = Field(..., min_length=1, max_length=128)
    action: str = Field(..., min_length=1, max_length=128)
    details: dict[str, Any] = Field(default_factory=dict)


class BacktestDataQualityEventListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    events: list[BacktestDataQualityEvent]
    total: int
    limit: int
    offset: int


class BacktestClaimRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    executionName: str | None = Field(default=None, max_length=255)


class BacktestStartRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    executionName: str | None = Field(default=None, max_length=255)


class BacktestCompleteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: dict[str, Any] = Field(default_factory=dict)


class BacktestFailRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    error: str = Field(..., min_length=1, max_length=4000)


class BacktestReconcileResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dispatchedCount: int = Field(default=0, ge=0)
    dispatchFailedCount: int = Field(default=0, ge=0)
    failedStaleRunningCount: int = Field(default=0, ge=0)
    skippedActiveCount: int = Field(default=0, ge=0)
    noActionCount: int = Field(default=0, ge=0)
    dispatchedRunIds: list[str] = Field(default_factory=list)
    dispatchFailedRunIds: list[str] = Field(default_factory=list)
    failedRunIds: list[str] = Field(default_factory=list)
