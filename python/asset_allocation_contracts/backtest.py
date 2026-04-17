from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

RunStatus = Literal["queued", "running", "completed", "failed"]


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


class RunListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    runs: list[RunRecordResponse]
    limit: int
    offset: int


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


class TimeseriesPointResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: str
    portfolio_value: float
    drawdown: float
    daily_return: float | None = None
    cumulative_return: float | None = None
    cash: float | None = None
    gross_exposure: float | None = None
    net_exposure: float | None = None
    turnover: float | None = None
    commission: float | None = None
    slippage_cost: float | None = None


class TimeseriesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    points: list[TimeseriesPointResponse]
    total_points: int
    truncated: bool


class RollingMetricPointResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: str
    window_days: int
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


class RollingMetricsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

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


class TradeListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trades: list[TradeResponse]
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
