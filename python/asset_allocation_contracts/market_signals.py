from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

MarketSignalSource = Literal["congressional_trading", "insider_trading", "wall_street_bets"]
MarketSignalDateBasis = Literal["filed_at", "notified_at", "uploaded", "event_time", "as_of_date", "unknown"]
MarketSignalActivityType = Literal[
    "purchase",
    "sale",
    "mixed",
    "mention",
    "filing",
    "unavailable",
    "unknown",
]
MarketSignalMappingStatus = Literal["mapped", "pending_review", "ignored", "unmapped", "unknown"]
MarketSignalSizeUnit = Literal[
    "usd_midpoint_proxy",
    "usd_notional_proxy",
    "mentions",
    "activity_count",
    "unavailable",
]
MarketSignalQualityFlag = Literal[
    "stale_source",
    "missing_daily_measure",
    "missing_symbol",
    "unmapped_symbol",
    "low_confidence_mapping",
    "missing_amount_proxy",
    "amount_range_midpoint_proxy",
    "notional_proxy",
    "mentions_not_dollars",
    "source_unavailable",
]

MARKET_SIGNAL_SUPPORTED_SOURCES: tuple[MarketSignalSource, ...] = (
    "congressional_trading",
    "insider_trading",
    "wall_street_bets",
)

MARKET_SIGNAL_EXCLUDED_QUIVER_TABLES: tuple[str, ...] = ("quiver_congress_holdings_daily",)


def _validate_size_semantics(
    *,
    source: MarketSignalSource,
    size_unit: MarketSignalSizeUnit,
    quality_flags: list[MarketSignalQualityFlag],
) -> None:
    if source == "congressional_trading" and size_unit not in {"usd_midpoint_proxy", "activity_count", "unavailable"}:
        raise ValueError("congressional_trading size must be an activity count or USD midpoint proxy.")
    if source == "insider_trading" and size_unit not in {"usd_notional_proxy", "activity_count", "unavailable"}:
        raise ValueError("insider_trading size must be an activity count or USD notional proxy.")
    if source == "wall_street_bets" and size_unit not in {"mentions", "activity_count", "unavailable"}:
        raise ValueError("wall_street_bets size must be mention/activity based, not dollars.")
    if size_unit == "usd_midpoint_proxy" and "amount_range_midpoint_proxy" not in quality_flags:
        raise ValueError("usd_midpoint_proxy requires the amount_range_midpoint_proxy quality flag.")
    if size_unit == "usd_notional_proxy" and "notional_proxy" not in quality_flags:
        raise ValueError("usd_notional_proxy requires the notional_proxy quality flag.")
    if source == "wall_street_bets" and "mentions_not_dollars" not in quality_flags:
        raise ValueError("wall_street_bets points must flag that size is mentions/activity, not dollars.")


class SignalActivityPlotPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: MarketSignalSource
    activity_date: date
    date_basis: MarketSignalDateBasis
    activity_count: int = Field(default=0, ge=0)
    size_value: float | None = Field(default=None, ge=0)
    size_unit: MarketSignalSizeUnit
    active_symbol_count: int = Field(default=0, ge=0)
    mapped_symbol_count: int = Field(default=0, ge=0)
    missing_symbol_count: int = Field(default=0, ge=0)
    buy_count: int = Field(default=0, ge=0)
    sell_count: int = Field(default=0, ge=0)
    mention_count: int = Field(default=0, ge=0)
    amount_lower_usd_sum: float | None = Field(default=None, ge=0)
    amount_upper_usd_sum: float | None = Field(default=None, ge=0)
    amount_midpoint_proxy_usd_sum: float | None = Field(default=None, ge=0)
    net_amount_midpoint_proxy_usd: float | None = None
    notional_proxy_usd: float | None = Field(default=None, ge=0)
    quality_flags: list[MarketSignalQualityFlag] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_point_semantics(self) -> "SignalActivityPlotPoint":
        if (
            self.amount_lower_usd_sum is not None
            and self.amount_upper_usd_sum is not None
            and self.amount_lower_usd_sum > self.amount_upper_usd_sum
        ):
            raise ValueError("amount_upper_usd_sum must be >= amount_lower_usd_sum.")
        _validate_size_semantics(
            source=self.source,
            size_unit=self.size_unit,
            quality_flags=self.quality_flags,
        )
        return self


class SignalActivityPlot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: MarketSignalSource
    label: str = Field(..., min_length=1, max_length=64)
    size_unit: MarketSignalSizeUnit
    points: list[SignalActivityPlotPoint] = Field(default_factory=list)
    unavailable_reason: str | None = Field(default=None, max_length=512)
    quality_flags: list[MarketSignalQualityFlag] = Field(default_factory=list)


class SignalActivityEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(..., min_length=1, max_length=160)
    source: MarketSignalSource
    activity_date: date
    date_basis: MarketSignalDateBasis
    event_time: datetime | None = None
    symbol: str | None = Field(default=None, min_length=1, max_length=32)
    issuer_name: str | None = Field(default=None, min_length=1, max_length=255)
    actor_name: str | None = Field(default=None, min_length=1, max_length=255)
    asset_name: str | None = Field(default=None, min_length=1, max_length=255)
    activity_type: MarketSignalActivityType = "unknown"
    activity_label: str = Field(..., min_length=1, max_length=160)
    size_value: float | None = Field(default=None, ge=0)
    size_unit: MarketSignalSizeUnit
    amount_lower_usd: float | None = Field(default=None, ge=0)
    amount_upper_usd: float | None = Field(default=None, ge=0)
    amount_bucket_label: str | None = Field(default=None, min_length=1, max_length=64)
    source_detail: str | None = Field(default=None, max_length=512)
    mapping_status: MarketSignalMappingStatus = "unknown"
    confidence: float | None = Field(default=None, ge=0, le=1)
    late_filing_days: int | None = Field(default=None, ge=0)
    quality_flags: list[MarketSignalQualityFlag] = Field(default_factory=list)
    updated_at: datetime | None = None

    @model_validator(mode="after")
    def validate_event_semantics(self) -> "SignalActivityEvent":
        if (
            self.amount_lower_usd is not None
            and self.amount_upper_usd is not None
            and self.amount_lower_usd > self.amount_upper_usd
        ):
            raise ValueError("amount_upper_usd must be >= amount_lower_usd.")
        _validate_size_semantics(
            source=self.source,
            size_unit=self.size_unit,
            quality_flags=self.quality_flags,
        )
        return self


class SignalActivityFreshness(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: MarketSignalSource
    latest_activity_date: date | None = None
    latest_updated_at: datetime | None = None
    stale: bool = False
    stale_after_date: date | None = None
    unavailable_reason: str | None = Field(default=None, max_length=512)


class SignalActivityDataQuality(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: MarketSignalSource
    row_count: int = Field(default=0, ge=0)
    mapped_symbol_count: int = Field(default=0, ge=0)
    missing_symbol_count: int = Field(default=0, ge=0)
    unmapped_symbol_count: int = Field(default=0, ge=0)
    unavailable_metric_columns: list[str] = Field(default_factory=list)
    excluded_tables: list[str] = Field(default_factory=list)
    quality_flags: list[MarketSignalQualityFlag] = Field(default_factory=list)


class SignalActivityScreenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    from_date: date | None = None
    to_date: date | None = None
    sources: list[MarketSignalSource] = Field(default_factory=lambda: list(MARKET_SIGNAL_SUPPORTED_SOURCES))
    symbol: str | None = Field(default=None, min_length=1, max_length=32)
    query: str | None = Field(default=None, min_length=1, max_length=128)
    activity_types: list[MarketSignalActivityType] = Field(default_factory=list)
    mapping_statuses: list[MarketSignalMappingStatus] = Field(default_factory=list)
    minimum_size: float | None = Field(default=None, ge=0)
    minimum_count: int | None = Field(default=None, ge=0)
    limit: int = Field(default=250, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_date_range(self) -> "SignalActivityScreenRequest":
        if self.from_date and self.to_date and self.from_date > self.to_date:
            raise ValueError("from_date must be <= to_date.")
        if not self.sources:
            raise ValueError("sources must not be empty.")
        return self


class SignalActivityScreenResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plots: list[SignalActivityPlot]
    events: list[SignalActivityEvent]
    freshness: list[SignalActivityFreshness]
    data_quality: list[SignalActivityDataQuality]
    total_events: int = Field(..., ge=0)
    limit: int = Field(..., ge=1)
    offset: int = Field(..., ge=0)
