from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

KalshiProviderEnvironment = Literal["demo", "live"]
KalshiOutcomeSide = Literal["yes", "no"]
KalshiBookSide = Literal["bid", "ask"]
KalshiPaginationTier = Literal["live", "historical"]
KalshiStreamState = Literal["fresh", "stale", "partial", "unknown", "failed"]
KalshiWarningSeverity = Literal["info", "warning", "critical"]


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


def _normalize_lower_required_text(value: object, field_name: str) -> str:
    return _normalize_required_text(value, field_name).lower()


def _normalize_decimal_text(value: object, field_name: str, *, allow_negative: bool) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be provided as a string.")
    normalized = _normalize_required_text(value, field_name)
    try:
        parsed = Decimal(normalized)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field_name} must be an exact decimal string.") from exc
    if not parsed.is_finite():
        raise ValueError(f"{field_name} must be finite.")
    if not allow_negative and parsed < 0:
        raise ValueError(f"{field_name} must be non-negative.")
    return normalized


def _normalize_optional_decimal_text(
    value: object,
    field_name: str,
    *,
    allow_negative: bool,
) -> str | None:
    normalized = _normalize_optional_text(value)
    if normalized is None:
        return None
    return _normalize_decimal_text(normalized, field_name, allow_negative=allow_negative)


class KalshiLineage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sync_run_id: str = Field(..., min_length=1, max_length=128)
    source_observed_at: datetime
    ingested_at: datetime
    source_payload_hash: str = Field(..., min_length=1, max_length=160)
    endpoint: str = Field(..., min_length=1, max_length=160)
    request_id: str | None = Field(default=None, min_length=1, max_length=160)
    cursor_in: str | None = Field(default=None, min_length=1, max_length=1024)
    cursor_out: str | None = Field(default=None, min_length=1, max_length=1024)
    page_number: int | None = Field(default=None, ge=0)
    tier: KalshiPaginationTier = "live"
    cutoff_field: str | None = Field(default=None, min_length=1, max_length=80)
    cutoff_value: datetime | None = None

    @field_validator(
        "sync_run_id",
        "source_payload_hash",
        "endpoint",
        "request_id",
        "cursor_in",
        "cursor_out",
        "cutoff_field",
        mode="before",
    )
    @classmethod
    def normalize_text_fields(cls, value: object, info) -> str | None:
        if info.field_name in {"request_id", "cursor_in", "cursor_out", "cutoff_field"}:
            return _normalize_optional_text(value)
        return _normalize_required_text(value, info.field_name)


class KalshiPage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cursor: str | None = Field(default=None, min_length=1, max_length=1024)
    limit: int | None = Field(default=None, ge=1, le=1000)
    page_number: int = Field(default=0, ge=0)
    tier: KalshiPaginationTier = "live"
    exhausted: bool = False

    @field_validator("cursor", mode="before")
    @classmethod
    def normalize_cursor(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class KalshiStreamFreshness(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state: KalshiStreamState = "unknown"
    as_of: datetime | None = None
    row_count: int = Field(default=0, ge=0)
    cursor_exhausted: bool = False
    stale_reason: str | None = Field(default=None, min_length=1, max_length=320)
    warning_count: int = Field(default=0, ge=0)

    @field_validator("stale_reason", mode="before")
    @classmethod
    def normalize_stale_reason(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class KalshiAccountFreshness(BaseModel):
    model_config = ConfigDict(extra="forbid")

    balance: KalshiStreamFreshness = Field(default_factory=KalshiStreamFreshness)
    positions: KalshiStreamFreshness = Field(default_factory=KalshiStreamFreshness)
    orders: KalshiStreamFreshness = Field(default_factory=KalshiStreamFreshness)
    fills: KalshiStreamFreshness = Field(default_factory=KalshiStreamFreshness)
    account_limits: KalshiStreamFreshness = Field(default_factory=KalshiStreamFreshness)
    historical_cutoff: KalshiStreamFreshness = Field(default_factory=KalshiStreamFreshness)


class KalshiWarning(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(..., min_length=1, max_length=128)
    message: str = Field(..., min_length=1, max_length=500)
    severity: KalshiWarningSeverity = "warning"
    domain: str | None = Field(default=None, min_length=1, max_length=80)
    provider_field: str | None = Field(default=None, min_length=1, max_length=160)
    raw_value: str | None = Field(default=None, min_length=1, max_length=320)

    @field_validator("code", "message", "domain", "provider_field", "raw_value", mode="before")
    @classmethod
    def normalize_text_fields(cls, value: object, info) -> str | None:
        if info.field_name in {"domain", "provider_field", "raw_value"}:
            return _normalize_optional_text(value)
        return _normalize_required_text(value, info.field_name)


class KalshiQuarantineRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    domain: str = Field(..., min_length=1, max_length=80)
    reason: str = Field(..., min_length=1, max_length=500)
    source_payload_hash: str = Field(..., min_length=1, max_length=160)
    observed_at: datetime
    endpoint: str | None = Field(default=None, min_length=1, max_length=160)
    request_id: str | None = Field(default=None, min_length=1, max_length=160)

    @field_validator("domain", "reason", "source_payload_hash", "endpoint", "request_id", mode="before")
    @classmethod
    def normalize_text_fields(cls, value: object, info) -> str | None:
        if info.field_name in {"endpoint", "request_id"}:
            return _normalize_optional_text(value)
        return _normalize_required_text(value, info.field_name)


class KalshiBalanceBreakdown(BaseModel):
    model_config = ConfigDict(extra="forbid")

    exchange_index: int = Field(..., ge=0)
    balance: str = Field(..., min_length=1)

    @field_validator("balance", mode="before")
    @classmethod
    def validate_balance_string(cls, value: object) -> str:
        return _normalize_decimal_text(value, "balance", allow_negative=False)


class KalshiBalance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    balance: int = Field(..., ge=0)
    portfolio_value: int = Field(..., ge=0)
    updated_ts: int = Field(..., ge=0)
    balance_breakdown: list[KalshiBalanceBreakdown] = Field(default_factory=list)
    subaccount: int = Field(default=0, ge=0, le=32)
    lineage: KalshiLineage | None = None


class KalshiMarketPosition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ticker: str = Field(..., min_length=1, max_length=128)
    total_traded_dollars: str = Field(..., min_length=1)
    position_fp: str = Field(..., min_length=1)
    market_exposure_dollars: str = Field(..., min_length=1)
    realized_pnl_dollars: str = Field(..., min_length=1)
    resting_orders_count: int = Field(default=0, ge=0)
    fees_paid_dollars: str = Field(..., min_length=1)
    last_updated_ts: datetime | None = None
    subaccount_number: int | None = Field(default=None, ge=0, le=32)
    lineage: KalshiLineage | None = None

    @field_validator("ticker", mode="before")
    @classmethod
    def normalize_ticker(cls, value: object) -> str:
        return _normalize_required_text(value, "ticker").upper()

    @field_validator(
        "total_traded_dollars",
        "position_fp",
        "market_exposure_dollars",
        "fees_paid_dollars",
        mode="before",
    )
    @classmethod
    def validate_non_negative_decimal_strings(cls, value: object, info) -> str:
        return _normalize_decimal_text(value, info.field_name, allow_negative=False)

    @field_validator("realized_pnl_dollars", mode="before")
    @classmethod
    def validate_realized_pnl_string(cls, value: object) -> str:
        return _normalize_decimal_text(value, "realized_pnl_dollars", allow_negative=True)


class KalshiEventPosition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_ticker: str = Field(..., min_length=1, max_length=128)
    total_cost_dollars: str = Field(..., min_length=1)
    total_cost_shares_fp: str = Field(..., min_length=1)
    event_exposure_dollars: str = Field(..., min_length=1)
    realized_pnl_dollars: str = Field(..., min_length=1)
    fees_paid_dollars: str = Field(..., min_length=1)
    subaccount_number: int | None = Field(default=None, ge=0, le=32)
    lineage: KalshiLineage | None = None

    @field_validator("event_ticker", mode="before")
    @classmethod
    def normalize_event_ticker(cls, value: object) -> str:
        return _normalize_required_text(value, "event_ticker").upper()

    @field_validator(
        "total_cost_dollars",
        "total_cost_shares_fp",
        "event_exposure_dollars",
        "fees_paid_dollars",
        mode="before",
    )
    @classmethod
    def validate_non_negative_decimal_strings(cls, value: object, info) -> str:
        return _normalize_decimal_text(value, info.field_name, allow_negative=False)

    @field_validator("realized_pnl_dollars", mode="before")
    @classmethod
    def validate_realized_pnl_string(cls, value: object) -> str:
        return _normalize_decimal_text(value, "realized_pnl_dollars", allow_negative=True)


class KalshiPositionsPage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    market_positions: list[KalshiMarketPosition] = Field(default_factory=list)
    event_positions: list[KalshiEventPosition] = Field(default_factory=list)
    cursor: str | None = Field(default=None, min_length=1, max_length=1024)
    page: KalshiPage | None = None
    lineage: KalshiLineage | None = None

    @field_validator("cursor", mode="before")
    @classmethod
    def normalize_cursor(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class KalshiOrder(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_id: str = Field(..., min_length=1, max_length=160)
    user_id: str | None = Field(default=None, min_length=1, max_length=160)
    client_order_id: str | None = Field(default=None, min_length=1, max_length=160)
    ticker: str = Field(..., min_length=1, max_length=128)
    side: str | None = Field(default=None, min_length=1, max_length=16)
    action: str | None = Field(default=None, min_length=1, max_length=16)
    outcome_side: KalshiOutcomeSide
    book_side: KalshiBookSide
    type: str = Field(..., min_length=1, max_length=40)
    status: str = Field(..., min_length=1, max_length=80)
    yes_price_dollars: str | None = Field(default=None, min_length=1)
    no_price_dollars: str | None = Field(default=None, min_length=1)
    fill_count_fp: str = Field(..., min_length=1)
    remaining_count_fp: str = Field(..., min_length=1)
    initial_count_fp: str = Field(..., min_length=1)
    taker_fill_cost_dollars: str | None = Field(default=None, min_length=1)
    maker_fill_cost_dollars: str | None = Field(default=None, min_length=1)
    taker_fees_dollars: str | None = Field(default=None, min_length=1)
    maker_fees_dollars: str | None = Field(default=None, min_length=1)
    expiration_time: datetime | None = None
    created_time: datetime | None = None
    last_update_time: datetime | None = None
    self_trade_prevention_type: str | None = Field(default=None, min_length=1, max_length=80)
    order_group_id: str | None = Field(default=None, min_length=1, max_length=160)
    cancel_order_on_pause: bool | None = None
    subaccount_number: int | None = Field(default=None, ge=0, le=32)
    tier: KalshiPaginationTier = "live"
    lineage: KalshiLineage | None = None

    @field_validator(
        "order_id",
        "user_id",
        "client_order_id",
        "ticker",
        "side",
        "action",
        "type",
        "status",
        "self_trade_prevention_type",
        "order_group_id",
        mode="before",
    )
    @classmethod
    def normalize_text_fields(cls, value: object, info) -> str | None:
        if info.field_name in {
            "user_id",
            "client_order_id",
            "side",
            "action",
            "self_trade_prevention_type",
            "order_group_id",
        }:
            normalized = _normalize_optional_text(value)
            return normalized.upper() if info.field_name == "ticker" and normalized is not None else normalized
        normalized = _normalize_required_text(value, info.field_name)
        return normalized.upper() if info.field_name == "ticker" else normalized

    @field_validator("outcome_side", "book_side", mode="before")
    @classmethod
    def normalize_side_fields(cls, value: object, info) -> str:
        return _normalize_lower_required_text(value, info.field_name)

    @field_validator(
        "yes_price_dollars",
        "no_price_dollars",
        "taker_fill_cost_dollars",
        "maker_fill_cost_dollars",
        "taker_fees_dollars",
        "maker_fees_dollars",
        mode="before",
    )
    @classmethod
    def validate_optional_money_strings(cls, value: object, info) -> str | None:
        return _normalize_optional_decimal_text(value, info.field_name, allow_negative=False)

    @field_validator("fill_count_fp", "remaining_count_fp", "initial_count_fp", mode="before")
    @classmethod
    def validate_count_strings(cls, value: object, info) -> str:
        return _normalize_decimal_text(value, info.field_name, allow_negative=False)


class KalshiOrdersPage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    orders: list[KalshiOrder] = Field(default_factory=list)
    cursor: str | None = Field(default=None, min_length=1, max_length=1024)
    page: KalshiPage | None = None
    lineage: KalshiLineage | None = None

    @field_validator("cursor", mode="before")
    @classmethod
    def normalize_cursor(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class KalshiFill(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fill_id: str = Field(..., min_length=1, max_length=160)
    trade_id: str | None = Field(default=None, min_length=1, max_length=160)
    order_id: str | None = Field(default=None, min_length=1, max_length=160)
    ticker: str = Field(..., min_length=1, max_length=128)
    market_ticker: str | None = Field(default=None, min_length=1, max_length=128)
    side: str | None = Field(default=None, min_length=1, max_length=16)
    action: str | None = Field(default=None, min_length=1, max_length=16)
    outcome_side: KalshiOutcomeSide
    book_side: KalshiBookSide
    count_fp: str = Field(..., min_length=1)
    yes_price_dollars: str | None = Field(default=None, min_length=1)
    no_price_dollars: str | None = Field(default=None, min_length=1)
    is_taker: bool | None = None
    fee_cost: str | None = Field(default=None, min_length=1)
    created_time: datetime | None = None
    subaccount_number: int | None = Field(default=None, ge=0, le=32)
    ts: int | None = Field(default=None, ge=0)
    tier: KalshiPaginationTier = "live"
    lineage: KalshiLineage | None = None

    @field_validator(
        "fill_id",
        "trade_id",
        "order_id",
        "ticker",
        "market_ticker",
        "side",
        "action",
        mode="before",
    )
    @classmethod
    def normalize_text_fields(cls, value: object, info) -> str | None:
        if info.field_name in {"trade_id", "order_id", "market_ticker", "side", "action"}:
            normalized = _normalize_optional_text(value)
        else:
            normalized = _normalize_required_text(value, info.field_name)
        if info.field_name in {"ticker", "market_ticker"} and normalized is not None:
            return normalized.upper()
        return normalized

    @field_validator("outcome_side", "book_side", mode="before")
    @classmethod
    def normalize_side_fields(cls, value: object, info) -> str:
        return _normalize_lower_required_text(value, info.field_name)

    @field_validator("count_fp", mode="before")
    @classmethod
    def validate_count_string(cls, value: object) -> str:
        return _normalize_decimal_text(value, "count_fp", allow_negative=False)

    @field_validator("yes_price_dollars", "no_price_dollars", "fee_cost", mode="before")
    @classmethod
    def validate_optional_money_strings(cls, value: object, info) -> str | None:
        return _normalize_optional_decimal_text(value, info.field_name, allow_negative=False)


class KalshiFillsPage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fills: list[KalshiFill] = Field(default_factory=list)
    cursor: str | None = Field(default=None, min_length=1, max_length=1024)
    page: KalshiPage | None = None
    lineage: KalshiLineage | None = None

    @field_validator("cursor", mode="before")
    @classmethod
    def normalize_cursor(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class KalshiRateLimitBucket(BaseModel):
    model_config = ConfigDict(extra="forbid")

    refill_rate: int = Field(..., ge=0)
    bucket_capacity: int = Field(..., ge=0)


class KalshiAccountLimits(BaseModel):
    model_config = ConfigDict(extra="forbid")

    usage_tier: str = Field(..., min_length=1, max_length=80)
    read: KalshiRateLimitBucket
    write: KalshiRateLimitBucket
    lineage: KalshiLineage | None = None

    @field_validator("usage_tier", mode="before")
    @classmethod
    def normalize_usage_tier(cls, value: object) -> str:
        return _normalize_required_text(value, "usage_tier")


class KalshiHistoricalCutoff(BaseModel):
    model_config = ConfigDict(extra="forbid")

    market_settled_ts: datetime | None = None
    trades_created_ts: datetime
    orders_updated_ts: datetime
    observed_at: datetime | None = None
    lineage: KalshiLineage | None = None


class KalshiAccountSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account_id: str = Field(..., min_length=1, max_length=128)
    environment: KalshiProviderEnvironment
    subaccount: int = Field(default=0, ge=0, le=32)
    generated_at: datetime
    balance: KalshiBalance
    positions: KalshiPositionsPage = Field(default_factory=KalshiPositionsPage)
    orders: KalshiOrdersPage = Field(default_factory=KalshiOrdersPage)
    fills: KalshiFillsPage = Field(default_factory=KalshiFillsPage)
    account_limits: KalshiAccountLimits | None = None
    historical_cutoff: KalshiHistoricalCutoff | None = None
    freshness: KalshiAccountFreshness = Field(default_factory=KalshiAccountFreshness)
    warnings: list[KalshiWarning] = Field(default_factory=list)
    quarantine: list[KalshiQuarantineRecord] = Field(default_factory=list)

    @field_validator("account_id", mode="before")
    @classmethod
    def normalize_account_id(cls, value: object) -> str:
        return _normalize_required_text(value, "account_id")
