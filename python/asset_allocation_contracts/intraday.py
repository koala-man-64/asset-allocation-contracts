from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


CurrencyIntradayBarInterval = Literal["1m", "5m", "15m"]
StockAggregateInterval = Literal[
    "1s", "1m", "5m", "15m", "daily", "weekly", "monthly"
]
LiveMarketPriceStatus = Literal["connecting", "healthy", "degraded", "unavailable"]
StockAggregateStreamEventType = Literal[
    "market_price.stock_aggregate",
    "market_price.stock_status",
]
StockTradeStreamEventType = Literal[
    "market_price.stock_trade",
    "market_price.stock_trade_status",
]
IntradayRefreshDomain = Literal["market", "currency"]
IntradayMarketSession = Literal["us_equities_regular"]
IntradayMonitorRunStatus = Literal["queued", "claimed", "completed", "failed"]
IntradayRefreshBatchStatus = Literal["queued", "claimed", "completed", "failed"]
IntradayMonitorTriggerKind = Literal["scheduled", "manual", "on_demand"]
IntradayEventSeverity = Literal["info", "warning", "error"]
IntradaySymbolMonitorStatus = Literal[
    "idle", "observed", "refresh_queued", "refreshed", "failed"
]
IntradayWatchlistSymbolAppendRunSkippedReason = Literal[
    "watchlist_disabled",
    "no_new_symbols",
    "queue_run_disabled",
]

INTRADAY_WATCHLIST_APPEND_SYMBOLS_MAX = 100
INTRADAY_WATCHLIST_SYMBOLS_MAX = 250


def _normalize_symbol(value: object) -> str:
    symbol = str(value or "").strip().upper()
    if not symbol:
        raise ValueError("Symbol values must be non-empty.")
    if len(symbol) > 32:
        raise ValueError("Symbol values must be 32 characters or fewer.")
    return symbol


_STOCK_SYMBOL_ALLOWED_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-")


def _strip_provider_stock_channel(symbol: str) -> str:
    if symbol.startswith("AM."):
        return symbol[3:]
    if symbol.startswith("A."):
        return symbol[2:]
    if symbol.startswith("T."):
        return symbol[2:]
    return symbol


def _normalize_stock_symbol(value: object) -> str:
    symbol = _strip_provider_stock_channel(str(value or "").strip().upper())
    if not symbol:
        raise ValueError("Stock symbols must be non-empty.")
    if len(symbol) > 32:
        raise ValueError("Stock symbols must be 32 characters or fewer.")
    if "*" in symbol:
        raise ValueError("Wildcard stock symbols are not supported.")
    if any(char not in _STOCK_SYMBOL_ALLOWED_CHARS for char in symbol):
        raise ValueError("Stock symbols may only contain letters, numbers, dots, or hyphens.")
    return symbol


def _normalize_stock_aggregate_interval(value: object) -> StockAggregateInterval:
    interval = str(value or "").strip().lower()
    if interval == "1s":
        return "1s"
    if interval == "1m":
        return "1m"
    if interval == "5m":
        return "5m"
    if interval == "15m":
        return "15m"
    if interval == "daily":
        return "daily"
    if interval == "weekly":
        return "weekly"
    if interval == "monthly":
        return "monthly"
    raise ValueError("Stock aggregate interval is not supported.")


_COMMON_QUOTE_CURRENCIES = (
    "USD",
    "EUR",
    "JPY",
    "GBP",
    "CHF",
    "CAD",
    "AUD",
    "NZD",
)


def _strip_provider_currency_prefix(symbol: str) -> str:
    if len(symbol) > 2 and symbol[1] == ":":
        return symbol[2:]
    return symbol


def _normalize_currency_code(value: object, *, field_name: str) -> str:
    code = str(value or "").strip().upper()
    if not code:
        raise ValueError(f"{field_name} must be non-empty.")
    if not code.isalnum():
        raise ValueError(f"{field_name} must be alphanumeric.")
    if len(code) > 16:
        raise ValueError(f"{field_name} must be 16 characters or fewer.")
    return code


def _normalize_currency_pair_symbol(value: object) -> str:
    symbol = _normalize_symbol(value)
    symbol = _strip_provider_currency_prefix(symbol)
    symbol = symbol.replace("/", "").replace("-", "").replace("_", "")
    if len(symbol) > 32:
        raise ValueError("Currency pair symbols must be 32 characters or fewer.")
    return _normalize_symbol(symbol)


def _split_currency_pair(
    symbol: object,
    *,
    default_quote_currency: object = "USD",
) -> tuple[str, str]:
    normalized = _normalize_currency_pair_symbol(symbol)
    default_quote = _normalize_currency_code(
        default_quote_currency,
        field_name="quoteCurrency",
    )
    for quote in _COMMON_QUOTE_CURRENCIES:
        if normalized.endswith(quote) and len(normalized) > len(quote):
            base = normalized[: -len(quote)]
            return (
                _normalize_currency_code(base, field_name="baseCurrency"),
                quote,
            )
    return (
        _normalize_currency_code(normalized, field_name="baseCurrency"),
        default_quote,
    )


def _normalize_quote_currency(value: object) -> str:
    return _normalize_currency_code(value, field_name="quoteCurrency")


def _normalize_base_currency(value: object) -> str:
    return _normalize_currency_code(value, field_name="baseCurrency")


def _normalize_provider_symbol(value: object) -> str:
    provider_symbol = str(value or "").strip().upper()
    if not provider_symbol:
        raise ValueError("providerSymbol must be non-empty.")
    if len(provider_symbol) > 64:
        raise ValueError("providerSymbol must be 64 characters or fewer.")
    return provider_symbol


def _normalize_provider_pair(value: object) -> str:
    provider_pair = str(value or "").strip().upper()
    if not provider_pair:
        raise ValueError("providerPair must be non-empty.")
    if len(provider_pair) > 64:
        raise ValueError("providerPair must be 64 characters or fewer.")
    return provider_pair


def _normalize_provider_channel(value: object) -> str:
    provider_channel = str(value or "").strip().upper()
    if not provider_channel:
        raise ValueError("providerChannel must be non-empty.")
    if len(provider_channel) > 80:
        raise ValueError("providerChannel must be 80 characters or fewer.")
    return provider_channel


def _normalize_utc_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _normalize_optional_utc_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return _normalize_utc_datetime(value)


def _normalize_symbols(values: object) -> list[str]:
    if values is None:
        return []
    if not isinstance(values, list):
        raise TypeError("symbols must be a list.")

    normalized: list[str] = []
    seen: set[str] = set()
    for raw in values:
        symbol = _normalize_symbol(raw)
        if symbol in seen:
            continue
        seen.add(symbol)
        normalized.append(symbol)
    return normalized


def _normalize_refresh_domain(value: object) -> IntradayRefreshDomain:
    domain = str(value or "market").strip().lower()
    if domain == "market":
        return "market"
    if domain == "currency":
        return "currency"
    raise ValueError("Intraday refresh domain must be market or currency.")


def _normalize_optional_refresh_domain(
    value: object,
) -> IntradayRefreshDomain | None:
    if value is None:
        return None
    if str(value).strip() == "":
        return None
    return _normalize_refresh_domain(value)


def _normalize_refresh_domains(values: object) -> list[IntradayRefreshDomain]:
    if values is None:
        return ["market"]
    if not isinstance(values, list):
        raise TypeError("refreshDomains must be a list.")

    normalized: list[IntradayRefreshDomain] = []
    seen: set[IntradayRefreshDomain] = set()
    for raw in values:
        domain = _normalize_refresh_domain(raw)
        if domain in seen:
            continue
        seen.add(domain)
        normalized.append(domain)
    if not normalized:
        raise ValueError("refreshDomains must include at least one domain.")
    return normalized


def _normalize_optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


class CurrencyIntradayBar(BaseModel):
    model_config = ConfigDict(extra="forbid")

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    vwap: float | None = None
    transactions: int | None = Field(default=None, ge=0)
    providerTimestampMs: int | None = Field(default=None, ge=0)

    _normalize_timestamp = field_validator("timestamp", mode="after")(
        _normalize_utc_datetime
    )


class CurrencyIntradayBarsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    symbol: str = Field(min_length=1, max_length=32)
    baseCurrency: str = Field(min_length=1, max_length=16)
    providerSymbol: str = Field(min_length=1, max_length=64)
    quoteCurrency: str = "USD"
    interval: CurrencyIntradayBarInterval
    from_: datetime = Field(alias="from")
    to: datetime
    rowCount: int = Field(ge=0)
    rows: list[CurrencyIntradayBar] = Field(default_factory=list)

    _normalize_symbol_field = field_validator("symbol", mode="before")(
        _normalize_currency_pair_symbol
    )
    _normalize_base_currency = field_validator("baseCurrency", mode="before")(
        _normalize_base_currency
    )
    _normalize_provider_symbol = field_validator("providerSymbol", mode="before")(
        _normalize_provider_symbol
    )
    _normalize_quote_currency = field_validator("quoteCurrency", mode="before")(
        _normalize_quote_currency
    )
    _normalize_from = field_validator("from_", mode="after")(_normalize_utc_datetime)
    _normalize_to = field_validator("to", mode="after")(_normalize_utc_datetime)

    @model_validator(mode="before")
    @classmethod
    def _normalize_pair_fields(cls, raw: object) -> object:
        if not isinstance(raw, dict):
            return raw

        data = dict(raw)
        quote_currency = data.get("quoteCurrency") or "USD"
        if data.get("baseCurrency") is None:
            base_currency, inferred_quote = _split_currency_pair(
                data.get("symbol"),
                default_quote_currency=quote_currency,
            )
            data["baseCurrency"] = base_currency
            data["quoteCurrency"] = data.get("quoteCurrency") or inferred_quote
        else:
            data["baseCurrency"] = _normalize_base_currency(data["baseCurrency"])
            data["quoteCurrency"] = _normalize_quote_currency(quote_currency)

        data["symbol"] = f"{data['baseCurrency']}{data['quoteCurrency']}"
        data["providerSymbol"] = data.get("providerSymbol") or data["symbol"]
        return data

    @model_validator(mode="after")
    def _validate_response(self) -> "CurrencyIntradayBarsResponse":
        if self.symbol != f"{self.baseCurrency}{self.quoteCurrency}":
            raise ValueError("symbol must match baseCurrency plus quoteCurrency.")
        provider_pair = _normalize_currency_pair_symbol(self.providerSymbol)
        if provider_pair != self.symbol:
            raise ValueError("providerSymbol must resolve to the canonical pair.")
        if self.rowCount != len(self.rows):
            raise ValueError("rowCount must match the number of rows.")
        return self


class StockAggregateBar(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: Literal["massive"] = "massive"
    assetClass: Literal["stocks"] = "stocks"
    symbol: str = Field(min_length=1, max_length=32)
    providerSymbol: str = Field(min_length=1, max_length=32)
    interval: StockAggregateInterval
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = Field(ge=0)
    vwap: float | None = None
    transactions: int | None = Field(default=None, ge=0)
    providerStartTimestampMs: int = Field(ge=0)
    providerEndTimestampMs: int | None = Field(default=None, ge=0)
    providerDelaySeconds: float | None = Field(default=None, ge=0)
    observedAt: datetime | None = None
    sequence: int | None = Field(default=None, ge=1)

    _normalize_symbol_field = field_validator("symbol", mode="before")(
        _normalize_stock_symbol
    )
    _normalize_provider_symbol = field_validator("providerSymbol", mode="before")(
        _normalize_stock_symbol
    )
    _normalize_interval = field_validator("interval", mode="before")(
        _normalize_stock_aggregate_interval
    )
    _normalize_timestamp = field_validator("timestamp", mode="after")(
        _normalize_utc_datetime
    )
    _normalize_observed_at = field_validator("observedAt", mode="after")(
        _normalize_optional_utc_datetime
    )

    @model_validator(mode="before")
    @classmethod
    def _default_provider_symbol(cls, raw: object) -> object:
        if not isinstance(raw, dict):
            return raw
        data = dict(raw)
        data["providerSymbol"] = data.get("providerSymbol") or data.get("symbol")
        return data

    @model_validator(mode="after")
    def _validate_bar(self) -> "StockAggregateBar":
        if self.providerSymbol != self.symbol:
            raise ValueError("providerSymbol must match the canonical stock symbol.")
        if (
            self.providerEndTimestampMs is not None
            and self.providerEndTimestampMs < self.providerStartTimestampMs
        ):
            raise ValueError("providerEndTimestampMs cannot precede providerStartTimestampMs.")
        return self


class StockAggregateBarsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    provider: Literal["massive"] = "massive"
    assetClass: Literal["stocks"] = "stocks"
    symbol: str = Field(min_length=1, max_length=32)
    providerSymbol: str = Field(min_length=1, max_length=32)
    interval: StockAggregateInterval
    from_: datetime = Field(alias="from")
    to: datetime
    rowCount: int = Field(ge=0)
    rows: list[StockAggregateBar] = Field(default_factory=list)

    _normalize_symbol_field = field_validator("symbol", mode="before")(
        _normalize_stock_symbol
    )
    _normalize_provider_symbol = field_validator("providerSymbol", mode="before")(
        _normalize_stock_symbol
    )
    _normalize_interval = field_validator("interval", mode="before")(
        _normalize_stock_aggregate_interval
    )
    _normalize_from = field_validator("from_", mode="after")(_normalize_utc_datetime)
    _normalize_to = field_validator("to", mode="after")(_normalize_utc_datetime)

    @model_validator(mode="before")
    @classmethod
    def _default_provider_symbol(cls, raw: object) -> object:
        if not isinstance(raw, dict):
            return raw
        data = dict(raw)
        data["providerSymbol"] = data.get("providerSymbol") or data.get("symbol")
        return data

    @model_validator(mode="after")
    def _validate_response(self) -> "StockAggregateBarsResponse":
        if self.providerSymbol != self.symbol:
            raise ValueError("providerSymbol must match the canonical stock symbol.")
        if self.from_ > self.to:
            raise ValueError("from must be earlier than or equal to to.")
        if self.rowCount != len(self.rows):
            raise ValueError("rowCount must match the number of rows.")
        for row in self.rows:
            if row.symbol != self.symbol:
                raise ValueError("row symbol must match response symbol.")
            if row.interval != self.interval:
                raise ValueError("row interval must match response interval.")
        return self


class LiveStockAggregateSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: Literal["massive"] = "massive"
    assetClass: Literal["stocks"] = "stocks"
    symbol: str = Field(min_length=1, max_length=32)
    providerSymbol: str = Field(min_length=1, max_length=32)
    interval: StockAggregateInterval
    topic: str = Field(min_length=1, max_length=200)
    status: LiveMarketPriceStatus
    lastBar: StockAggregateBar | None = None
    lastBarAgeSeconds: float | None = Field(default=None, ge=0)
    providerDelaySeconds: float | None = Field(default=None, ge=0)
    connectedAt: datetime | None = None
    lastProviderMessageAt: datetime | None = None
    lastStatusAt: datetime
    lastError: str | None = Field(default=None, max_length=2_000)

    _normalize_symbol_field = field_validator("symbol", mode="before")(
        _normalize_stock_symbol
    )
    _normalize_provider_symbol = field_validator("providerSymbol", mode="before")(
        _normalize_stock_symbol
    )
    _normalize_interval = field_validator("interval", mode="before")(
        _normalize_stock_aggregate_interval
    )
    _normalize_connected_at = field_validator("connectedAt", mode="after")(
        _normalize_optional_utc_datetime
    )
    _normalize_last_provider_message_at = field_validator(
        "lastProviderMessageAt",
        mode="after",
    )(_normalize_optional_utc_datetime)
    _normalize_last_status_at = field_validator("lastStatusAt", mode="after")(
        _normalize_utc_datetime
    )

    @model_validator(mode="before")
    @classmethod
    def _default_provider_symbol(cls, raw: object) -> object:
        if not isinstance(raw, dict):
            return raw
        data = dict(raw)
        data["providerSymbol"] = data.get("providerSymbol") or data.get("symbol")
        return data

    @model_validator(mode="after")
    def _validate_snapshot(self) -> "LiveStockAggregateSnapshot":
        if self.providerSymbol != self.symbol:
            raise ValueError("providerSymbol must match the canonical stock symbol.")
        expected_topic = (
            f"market-prices:massive:stocks:{self.symbol}:{self.interval}"
        )
        if self.topic != expected_topic:
            raise ValueError("topic must match the stock aggregate symbol and interval.")
        if self.lastBar is not None:
            if self.lastBar.symbol != self.symbol:
                raise ValueError("lastBar symbol must match snapshot symbol.")
            if self.lastBar.interval != self.interval:
                raise ValueError("lastBar interval must match snapshot interval.")
        return self


class LiveStockTradeTick(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: Literal["massive"] = "massive"
    assetClass: Literal["stocks"] = "stocks"
    symbol: str = Field(min_length=1, max_length=32)
    providerSymbol: str = Field(min_length=1, max_length=32)
    providerChannel: str = Field(min_length=1, max_length=80)
    price: float = Field(gt=0)
    size: float | None = Field(default=None, ge=0)
    exchangeId: int | None = Field(default=None, ge=0)
    conditions: list[int] = Field(default_factory=list)
    tradeId: str | None = Field(default=None, min_length=1, max_length=128)
    tape: int | None = Field(default=None, ge=0)
    providerSequenceNumber: int | None = Field(default=None, ge=0)
    providerTimestampMs: int = Field(ge=0)
    tradeReportingFacilityId: int | None = Field(default=None, ge=0)
    tradeReportingFacilityTimestampMs: int | None = Field(default=None, ge=0)
    observedAt: datetime
    sequence: int = Field(ge=1)

    _normalize_symbol_field = field_validator("symbol", mode="before")(
        _normalize_stock_symbol
    )
    _normalize_provider_symbol = field_validator("providerSymbol", mode="before")(
        _normalize_stock_symbol
    )
    _normalize_provider_channel = field_validator("providerChannel", mode="before")(
        _normalize_provider_channel
    )
    _normalize_observed_at = field_validator("observedAt", mode="after")(
        _normalize_utc_datetime
    )

    @model_validator(mode="before")
    @classmethod
    def _default_provider_fields(cls, raw: object) -> object:
        if not isinstance(raw, dict):
            return raw
        data = dict(raw)
        symbol = data.get("symbol")
        data["providerSymbol"] = data.get("providerSymbol") or symbol
        if data.get("providerChannel") is None and symbol is not None:
            data["providerChannel"] = f"T.{_normalize_stock_symbol(symbol)}"
        return data

    @field_validator("conditions", mode="before")
    @classmethod
    def _normalize_conditions(cls, value: object) -> list[int]:
        if value is None:
            return []
        if not isinstance(value, list):
            raise TypeError("conditions must be a list.")
        normalized: list[int] = []
        for condition in value:
            normalized.append(int(condition))
        return normalized

    @model_validator(mode="after")
    def _validate_tick(self) -> "LiveStockTradeTick":
        if self.providerSymbol != self.symbol:
            raise ValueError("providerSymbol must match the canonical stock symbol.")
        if not self.providerChannel.startswith("T."):
            raise ValueError("providerChannel must use the Massive T trade channel.")
        channel_symbol = self.providerChannel.removeprefix("T.")
        if _normalize_stock_symbol(channel_symbol) != self.symbol:
            raise ValueError("providerChannel must resolve to the canonical stock symbol.")
        return self


class LiveStockTradeSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: Literal["massive"] = "massive"
    assetClass: Literal["stocks"] = "stocks"
    symbol: str = Field(min_length=1, max_length=32)
    providerSymbol: str = Field(min_length=1, max_length=32)
    providerChannel: str = Field(min_length=1, max_length=80)
    topic: str = Field(min_length=1, max_length=200)
    status: LiveMarketPriceStatus
    lastTrade: LiveStockTradeTick | None = None
    lastTradeAgeSeconds: float | None = Field(default=None, ge=0)
    connectedAt: datetime | None = None
    lastProviderMessageAt: datetime | None = None
    lastStatusAt: datetime
    lastError: str | None = Field(default=None, max_length=2_000)

    _normalize_symbol_field = field_validator("symbol", mode="before")(
        _normalize_stock_symbol
    )
    _normalize_provider_symbol = field_validator("providerSymbol", mode="before")(
        _normalize_stock_symbol
    )
    _normalize_provider_channel = field_validator("providerChannel", mode="before")(
        _normalize_provider_channel
    )
    _normalize_connected_at = field_validator("connectedAt", mode="after")(
        _normalize_optional_utc_datetime
    )
    _normalize_last_provider_message_at = field_validator(
        "lastProviderMessageAt",
        mode="after",
    )(_normalize_optional_utc_datetime)
    _normalize_last_status_at = field_validator("lastStatusAt", mode="after")(
        _normalize_utc_datetime
    )

    @model_validator(mode="before")
    @classmethod
    def _default_provider_fields(cls, raw: object) -> object:
        if not isinstance(raw, dict):
            return raw
        data = dict(raw)
        symbol = data.get("symbol")
        data["providerSymbol"] = data.get("providerSymbol") or symbol
        if data.get("providerChannel") is None and symbol is not None:
            data["providerChannel"] = f"T.{_normalize_stock_symbol(symbol)}"
        return data

    @model_validator(mode="after")
    def _validate_snapshot(self) -> "LiveStockTradeSnapshot":
        if self.providerSymbol != self.symbol:
            raise ValueError("providerSymbol must match the canonical stock symbol.")
        if not self.providerChannel.startswith("T."):
            raise ValueError("providerChannel must use the Massive T trade channel.")
        channel_symbol = self.providerChannel.removeprefix("T.")
        if _normalize_stock_symbol(channel_symbol) != self.symbol:
            raise ValueError("providerChannel must resolve to the canonical stock symbol.")
        expected_topic = f"market-prices:massive:stocks:{self.symbol}:trades"
        if self.topic != expected_topic:
            raise ValueError("topic must match the stock trade symbol.")
        if self.lastTrade is not None and self.lastTrade.symbol != self.symbol:
            raise ValueError("lastTrade symbol must match snapshot symbol.")
        return self


class LiveCurrencyPriceTick(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: Literal["massive"] = "massive"
    assetClass: Literal["crypto"] = "crypto"
    symbol: str = Field(min_length=1, max_length=32)
    baseCurrency: str = Field(min_length=1, max_length=16)
    quoteCurrency: str = "USD"
    providerPair: str = Field(min_length=1, max_length=64)
    providerChannel: str = Field(min_length=1, max_length=80)
    price: float = Field(gt=0)
    size: float | None = Field(default=None, ge=0)
    exchangeId: int | None = Field(default=None, ge=0)
    conditions: list[int] = Field(default_factory=list)
    tradeId: str | None = Field(default=None, min_length=1, max_length=128)
    providerTimestampMs: int = Field(ge=0)
    providerReceivedTimestampMs: int | None = Field(default=None, ge=0)
    observedAt: datetime
    sequence: int = Field(ge=1)

    _normalize_symbol_field = field_validator("symbol", mode="before")(
        _normalize_currency_pair_symbol
    )
    _normalize_base_currency = field_validator("baseCurrency", mode="before")(
        _normalize_base_currency
    )
    _normalize_quote_currency = field_validator("quoteCurrency", mode="before")(
        _normalize_quote_currency
    )
    _normalize_provider_pair = field_validator("providerPair", mode="before")(
        _normalize_provider_pair
    )
    _normalize_provider_channel = field_validator("providerChannel", mode="before")(
        _normalize_provider_channel
    )
    _normalize_observed_at = field_validator("observedAt", mode="after")(
        _normalize_utc_datetime
    )

    @model_validator(mode="before")
    @classmethod
    def _normalize_pair_fields(cls, raw: object) -> object:
        if not isinstance(raw, dict):
            return raw

        data = dict(raw)
        quote_currency = data.get("quoteCurrency") or "USD"
        if data.get("baseCurrency") is None:
            base_currency, inferred_quote = _split_currency_pair(
                data.get("symbol"),
                default_quote_currency=quote_currency,
            )
            data["baseCurrency"] = base_currency
            data["quoteCurrency"] = data.get("quoteCurrency") or inferred_quote
        else:
            data["baseCurrency"] = _normalize_base_currency(data["baseCurrency"])
            data["quoteCurrency"] = _normalize_quote_currency(quote_currency)

        data["symbol"] = f"{data['baseCurrency']}{data['quoteCurrency']}"
        data["providerPair"] = data.get("providerPair") or (
            f"{data['baseCurrency']}-{data['quoteCurrency']}"
        )
        data["providerChannel"] = data.get("providerChannel") or (
            f"XT.{data['providerPair']}"
        )
        return data

    @field_validator("conditions", mode="before")
    @classmethod
    def _normalize_conditions(cls, value: object) -> list[int]:
        if value is None:
            return []
        if not isinstance(value, list):
            raise TypeError("conditions must be a list.")
        normalized: list[int] = []
        for condition in value:
            normalized.append(int(condition))
        return normalized

    @model_validator(mode="after")
    def _validate_tick(self) -> "LiveCurrencyPriceTick":
        if self.symbol != f"{self.baseCurrency}{self.quoteCurrency}":
            raise ValueError("symbol must match baseCurrency plus quoteCurrency.")
        provider_pair = _normalize_currency_pair_symbol(self.providerPair)
        if provider_pair != self.symbol:
            raise ValueError("providerPair must resolve to the canonical pair.")
        if not self.providerChannel.startswith("XT."):
            raise ValueError("providerChannel must use the Massive XT trade channel.")
        channel_pair = self.providerChannel.removeprefix("XT.")
        if _normalize_currency_pair_symbol(channel_pair) != self.symbol:
            raise ValueError("providerChannel must resolve to the canonical pair.")
        return self


class LiveCurrencyPriceSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: Literal["massive"] = "massive"
    assetClass: Literal["crypto"] = "crypto"
    symbol: str = Field(min_length=1, max_length=32)
    baseCurrency: str = Field(min_length=1, max_length=16)
    quoteCurrency: str = "USD"
    providerPair: str = Field(min_length=1, max_length=64)
    providerChannel: str = Field(min_length=1, max_length=80)
    topic: str = Field(min_length=1, max_length=160)
    status: LiveMarketPriceStatus
    lastTick: LiveCurrencyPriceTick | None = None
    lastTickAgeSeconds: float | None = Field(default=None, ge=0)
    connectedAt: datetime | None = None
    lastProviderMessageAt: datetime | None = None
    lastStatusAt: datetime
    lastError: str | None = Field(default=None, max_length=2_000)

    _normalize_symbol_field = field_validator("symbol", mode="before")(
        _normalize_currency_pair_symbol
    )
    _normalize_base_currency = field_validator("baseCurrency", mode="before")(
        _normalize_base_currency
    )
    _normalize_quote_currency = field_validator("quoteCurrency", mode="before")(
        _normalize_quote_currency
    )
    _normalize_provider_pair = field_validator("providerPair", mode="before")(
        _normalize_provider_pair
    )
    _normalize_provider_channel = field_validator("providerChannel", mode="before")(
        _normalize_provider_channel
    )
    _normalize_connected_at = field_validator("connectedAt", mode="after")(
        _normalize_optional_utc_datetime
    )
    _normalize_last_provider_message_at = field_validator(
        "lastProviderMessageAt",
        mode="after",
    )(_normalize_optional_utc_datetime)
    _normalize_last_status_at = field_validator("lastStatusAt", mode="after")(
        _normalize_utc_datetime
    )

    @model_validator(mode="before")
    @classmethod
    def _normalize_pair_fields(cls, raw: object) -> object:
        if not isinstance(raw, dict):
            return raw

        data = dict(raw)
        quote_currency = data.get("quoteCurrency") or "USD"
        if data.get("baseCurrency") is None:
            base_currency, inferred_quote = _split_currency_pair(
                data.get("symbol"),
                default_quote_currency=quote_currency,
            )
            data["baseCurrency"] = base_currency
            data["quoteCurrency"] = data.get("quoteCurrency") or inferred_quote
        else:
            data["baseCurrency"] = _normalize_base_currency(data["baseCurrency"])
            data["quoteCurrency"] = _normalize_quote_currency(quote_currency)

        data["symbol"] = f"{data['baseCurrency']}{data['quoteCurrency']}"
        data["providerPair"] = data.get("providerPair") or (
            f"{data['baseCurrency']}-{data['quoteCurrency']}"
        )
        data["providerChannel"] = data.get("providerChannel") or (
            f"XT.{data['providerPair']}"
        )
        return data

    @model_validator(mode="after")
    def _validate_snapshot(self) -> "LiveCurrencyPriceSnapshot":
        if self.symbol != f"{self.baseCurrency}{self.quoteCurrency}":
            raise ValueError("symbol must match baseCurrency plus quoteCurrency.")
        if _normalize_currency_pair_symbol(self.providerPair) != self.symbol:
            raise ValueError("providerPair must resolve to the canonical pair.")
        channel_pair = self.providerChannel.removeprefix("XT.")
        if not self.providerChannel.startswith("XT.") or (
            _normalize_currency_pair_symbol(channel_pair) != self.symbol
        ):
            raise ValueError("providerChannel must resolve to the canonical XT pair.")
        if self.lastTick is not None and self.lastTick.symbol != self.symbol:
            raise ValueError("lastTick symbol must match snapshot symbol.")
        return self


class IntradayWatchlistSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    watchlistId: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2_000)
    enabled: bool = True
    symbolCount: int = Field(default=0, ge=0)
    pollIntervalMinutes: int = Field(default=5, ge=1, le=1_440)
    refreshCooldownMinutes: int = Field(default=15, ge=1, le=1_440)
    autoRefreshEnabled: bool = True
    refreshDomains: list[IntradayRefreshDomain] = Field(
        default_factory=lambda: ["market"]
    )
    marketSession: IntradayMarketSession = "us_equities_regular"
    nextDueAt: datetime | None = None
    lastRunAt: datetime | None = None
    updatedAt: datetime | None = None

    _normalize_refresh_domains_field = field_validator(
        "refreshDomains", mode="before"
    )(_normalize_refresh_domains)


class IntradayWatchlistDetail(IntradayWatchlistSummary):
    model_config = ConfigDict(extra="forbid")

    symbols: list[str] = Field(default_factory=list)
    createdAt: datetime | None = None

    _normalize_symbols_field = field_validator("symbols", mode="before")(
        _normalize_symbols
    )


class IntradayWatchlistUpsertRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2_000)
    enabled: bool = True
    symbols: list[str] = Field(default_factory=list)
    pollIntervalMinutes: int = Field(default=5, ge=1, le=1_440)
    refreshCooldownMinutes: int = Field(default=15, ge=1, le=1_440)
    autoRefreshEnabled: bool = True
    refreshDomains: list[IntradayRefreshDomain] = Field(
        default_factory=lambda: ["market"]
    )
    marketSession: IntradayMarketSession = "us_equities_regular"

    _normalize_symbols_field = field_validator("symbols", mode="before")(
        _normalize_symbols
    )
    _normalize_refresh_domains_field = field_validator(
        "refreshDomains", mode="before"
    )(_normalize_refresh_domains)


class IntradayWatchlistSymbolAppendRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbols: list[str] = Field(
        min_length=1, max_length=INTRADAY_WATCHLIST_APPEND_SYMBOLS_MAX
    )
    queueRun: bool = True
    reason: str | None = Field(default=None, max_length=500)

    _normalize_symbols_field = field_validator("symbols", mode="before")(
        _normalize_symbols
    )

    @field_validator("reason", mode="before")
    @classmethod
    def _normalize_reason(cls, value: object) -> str | None:
        if value is None:
            return None
        reason = str(value).strip()
        return reason or None


class IntradaySymbolStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    watchlistId: str | None = Field(default=None, min_length=1, max_length=64)
    domain: IntradayRefreshDomain = "market"
    symbol: str = Field(min_length=1, max_length=32)
    monitorStatus: IntradaySymbolMonitorStatus = "idle"
    lastSnapshotAt: datetime | None = None
    lastObservedPrice: float | None = None
    lastSuccessfulRefreshAt: datetime | None = None
    lastSuccessfulMarketRefreshAt: datetime | None = None
    lastRunId: str | None = Field(default=None, min_length=1, max_length=64)
    lastError: str | None = Field(default=None, max_length=2_000)
    updatedAt: datetime | None = None

    _normalize_domain_field = field_validator("domain", mode="before")(
        _normalize_refresh_domain
    )

    @field_validator("symbol", mode="before")
    @classmethod
    def _normalize_symbol_field(cls, value: object) -> str:
        return _normalize_symbol(value)


class IntradayOnDemandSymbolConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol: str = Field(min_length=1, max_length=32)
    enabled: bool = True
    reason: str | None = Field(default=None, max_length=500)
    requestedBy: str | None = Field(default=None, max_length=255)
    createdAt: datetime | None = None
    updatedAt: datetime | None = None
    lastEnqueuedAt: datetime | None = None
    lastRefreshCompletedAt: datetime | None = None
    lastError: str | None = Field(default=None, max_length=2_000)

    @field_validator("symbol", mode="before")
    @classmethod
    def _normalize_symbol_field(cls, value: object) -> str:
        return _normalize_symbol(value)

    _normalize_reason = field_validator("reason", mode="before")(
        _normalize_optional_text
    )
    _normalize_requested_by = field_validator("requestedBy", mode="before")(
        _normalize_optional_text
    )


class IntradayOnDemandSymbolUpsertRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol: str = Field(min_length=1, max_length=32)
    enabled: bool = True
    reason: str | None = Field(default=None, max_length=500)

    @field_validator("symbol", mode="before")
    @classmethod
    def _normalize_symbol_field(cls, value: object) -> str:
        return _normalize_symbol(value)

    _normalize_reason = field_validator("reason", mode="before")(
        _normalize_optional_text
    )


class IntradayOnDemandSymbolListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total: int = Field(default=0, ge=0)
    items: list[IntradayOnDemandSymbolConfig] = Field(default_factory=list)


class IntradayOnDemandEnqueueSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabledSymbolCount: int = Field(default=0, ge=0)
    enqueuedSymbolCount: int = Field(default=0, ge=0)
    skippedSymbolCount: int = Field(default=0, ge=0)
    batchCount: int = Field(default=0, ge=0)
    queuedSymbols: list[str] = Field(default_factory=list)
    skippedSymbols: list[str] = Field(default_factory=list)

    _normalize_queued_symbols = field_validator("queuedSymbols", mode="before")(
        _normalize_symbols
    )
    _normalize_skipped_symbols = field_validator("skippedSymbols", mode="before")(
        _normalize_symbols
    )


class IntradayMonitorRunSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    runId: str = Field(min_length=1, max_length=64)
    watchlistId: str = Field(min_length=1, max_length=64)
    watchlistName: str | None = Field(default=None, max_length=255)
    triggerKind: IntradayMonitorTriggerKind = "scheduled"
    status: IntradayMonitorRunStatus = "queued"
    forceRefresh: bool = False
    symbolCount: int = Field(default=0, ge=0)
    observedSymbolCount: int = Field(default=0, ge=0)
    eligibleRefreshCount: int = Field(default=0, ge=0)
    refreshBatchCount: int = Field(default=0, ge=0)
    executionName: str | None = Field(default=None, max_length=255)
    dueAt: datetime | None = None
    queuedAt: datetime | None = None
    claimedAt: datetime | None = None
    completedAt: datetime | None = None
    lastError: str | None = Field(default=None, max_length=2_000)


class IntradayWatchlistSymbolAppendResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    watchlist: IntradayWatchlistDetail
    addedSymbols: list[str] = Field(default_factory=list)
    alreadyPresentSymbols: list[str] = Field(default_factory=list)
    queuedRun: IntradayMonitorRunSummary | None = None
    runSkippedReason: IntradayWatchlistSymbolAppendRunSkippedReason | None = None

    _normalize_added_symbols = field_validator("addedSymbols", mode="before")(
        _normalize_symbols
    )
    _normalize_already_present_symbols = field_validator(
        "alreadyPresentSymbols", mode="before"
    )(_normalize_symbols)


class IntradayMonitorEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    eventId: str | None = Field(default=None, min_length=1, max_length=64)
    runId: str | None = Field(default=None, min_length=1, max_length=64)
    watchlistId: str | None = Field(default=None, min_length=1, max_length=64)
    symbol: str | None = Field(default=None, min_length=1, max_length=32)
    eventType: str = Field(min_length=1, max_length=64)
    severity: IntradayEventSeverity = "info"
    message: str = Field(min_length=1, max_length=1_000)
    details: dict[str, Any] = Field(default_factory=dict)
    createdAt: datetime | None = None

    @field_validator("symbol", mode="before")
    @classmethod
    def _normalize_optional_symbol_field(cls, value: object) -> str | None:
        if value is None:
            return None
        return _normalize_symbol(value)


class IntradayMonitorClaimRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    executionName: str | None = Field(default=None, max_length=255)


class IntradayMonitorClaimResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run: IntradayMonitorRunSummary | None = None
    watchlist: IntradayWatchlistDetail | None = None
    currentSymbolStatuses: list[IntradaySymbolStatus] = Field(default_factory=list)
    claimToken: str | None = Field(default=None, min_length=1, max_length=128)


class IntradayRefreshRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    domain: IntradayRefreshDomain = "market"
    symbols: list[str] = Field(min_length=1)

    _normalize_domain_field = field_validator("domain", mode="before")(
        _normalize_refresh_domain
    )
    _normalize_symbols_field = field_validator("symbols", mode="before")(
        _normalize_symbols
    )


class IntradayMonitorCompleteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claimToken: str = Field(min_length=1, max_length=128)
    symbolStatuses: list[IntradaySymbolStatus] = Field(default_factory=list)
    events: list[IntradayMonitorEvent] = Field(default_factory=list)
    refreshRequests: list[IntradayRefreshRequest] = Field(default_factory=list)
    refreshSymbols: list[str] = Field(default_factory=list)

    _normalize_refresh_symbols = field_validator("refreshSymbols", mode="before")(
        _normalize_symbols
    )

    @model_validator(mode="after")
    def _sync_legacy_refresh_symbols_alias(
        self,
    ) -> "IntradayMonitorCompleteRequest":
        market_symbols: list[str] = []
        has_market_request = False
        for request in self.refreshRequests:
            if request.domain == "market":
                has_market_request = True
                market_symbols.extend(request.symbols)

        if self.refreshSymbols:
            market_symbols.extend(self.refreshSymbols)
            if not has_market_request:
                self.refreshRequests.insert(
                    0,
                    IntradayRefreshRequest(
                        domain="market",
                        symbols=self.refreshSymbols,
                    ),
                )

        self.refreshSymbols = _normalize_symbols(market_symbols)
        return self


class IntradayMonitorFailRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claimToken: str = Field(min_length=1, max_length=128)
    error: str = Field(min_length=1, max_length=2_000)


class IntradayRefreshBatchSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    batchId: str = Field(min_length=1, max_length=64)
    runId: str = Field(min_length=1, max_length=64)
    watchlistId: str = Field(min_length=1, max_length=64)
    watchlistName: str | None = Field(default=None, max_length=255)
    domain: IntradayRefreshDomain = "market"
    bucketLetter: str = Field(min_length=1, max_length=1)
    status: IntradayRefreshBatchStatus = "queued"
    symbols: list[str] = Field(default_factory=list)
    symbolCount: int = Field(default=0, ge=0)
    executionName: str | None = Field(default=None, max_length=255)
    claimedAt: datetime | None = None
    completedAt: datetime | None = None
    createdAt: datetime | None = None
    updatedAt: datetime | None = None
    lastError: str | None = Field(default=None, max_length=2_000)

    _normalize_symbols_field = field_validator("symbols", mode="before")(
        _normalize_symbols
    )
    _normalize_domain_field = field_validator("domain", mode="before")(
        _normalize_refresh_domain
    )


class IntradayRefreshClaimRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    executionName: str | None = Field(default=None, max_length=255)
    domain: IntradayRefreshDomain | None = None

    _normalize_domain_field = field_validator("domain", mode="before")(
        _normalize_optional_refresh_domain
    )


class IntradayRefreshClaimResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    batch: IntradayRefreshBatchSummary | None = None
    claimToken: str | None = Field(default=None, min_length=1, max_length=128)


class IntradayRefreshCompleteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claimToken: str = Field(min_length=1, max_length=128)


class IntradayRefreshFailRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claimToken: str = Field(min_length=1, max_length=128)
    error: str = Field(min_length=1, max_length=2_000)
