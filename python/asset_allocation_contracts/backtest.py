from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from asset_allocation_contracts.strategy import StrategyConfig
from pydantic import BaseModel, ConfigDict, Field, model_validator

RunStatus = Literal["queued", "running", "completed", "failed"]
BacktestLookupState = Literal["not_run", "queued", "running", "completed", "failed"]
BacktestStreamEventType = Literal["accepted", "status", "heartbeat", "completed", "failed"]
TradeRole = Literal["entry", "rebalance_increase", "rebalance_decrease", "exit"]
BacktestPolicyEventScope = Literal["strategy", "sleeve", "position", "symbol", "portfolio"]
BacktestPolicyEventType = Literal["rebalance", "strategy_risk", "position_exit", "reentry"]
BacktestPolicyDecision = Literal["applied", "skipped", "blocked"]


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


class RunStatusResponse(RunRecordResponse):
    model_config = ConfigDict(extra="forbid")

    results_ready_at: datetime | None = None
    results_schema_version: int | None = Field(default=None, ge=1)
    pins: RunPinsResponse | None = None


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

    @model_validator(mode="after")
    def validate_strategy_input(self) -> "_BacktestRequestBase":
        has_strategy_ref = self.strategyRef is not None
        has_strategy_config = self.strategyConfig is not None
        if has_strategy_ref == has_strategy_config:
            raise ValueError("Exactly one of strategyRef or strategyConfig must be provided.")
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


class BacktestResultMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    results_schema_version: int = Field(default=4, ge=1)
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
    details: dict[str, Any] = Field(default_factory=dict)


class BacktestPolicyEventListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    events: list[BacktestPolicyEvent]
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
