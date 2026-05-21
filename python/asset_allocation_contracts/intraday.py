from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


CryptoIntradayBarInterval = Literal["1m", "5m", "15m"]
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


def _normalize_crypto_symbol(value: object) -> str:
    symbol = _normalize_symbol(value)
    if symbol.startswith("X:"):
        if not symbol.endswith("USD"):
            raise ValueError("Crypto provider symbols must be USD pairs.")
        symbol = symbol[2:]
    if symbol.endswith("USD") and len(symbol) > 3:
        symbol = symbol[:-3]
    return _normalize_symbol(symbol)


def _normalize_crypto_provider_symbol(value: object) -> str:
    symbol = _normalize_symbol(value)
    if symbol.startswith("X:"):
        if not symbol.endswith("USD"):
            raise ValueError("Crypto provider symbols must be USD pairs.")
        provider_symbol = symbol
    else:
        provider_symbol = f"X:{symbol}"

    if not provider_symbol.endswith("USD"):
        provider_symbol = f"{provider_symbol}USD"

    if not provider_symbol.startswith("X:") or len(provider_symbol) <= len("X:USD"):
        raise ValueError("Crypto provider symbols must resolve to an X:{base}USD pair.")
    return provider_symbol


def _normalize_quote_currency(value: object) -> str:
    quote_currency = str(value or "").strip().upper()
    if quote_currency != "USD":
        raise ValueError("Crypto intraday bars currently support USD quote pairs only.")
    return quote_currency


def _normalize_utc_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


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


def _normalize_optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


class CryptoIntradayBar(BaseModel):
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


class CryptoIntradayBarsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    symbol: str = Field(min_length=1, max_length=32)
    providerSymbol: str = Field(min_length=1, max_length=64)
    quoteCurrency: str = "USD"
    interval: CryptoIntradayBarInterval
    from_: datetime = Field(alias="from")
    to: datetime
    rowCount: int = Field(ge=0)
    rows: list[CryptoIntradayBar] = Field(default_factory=list)

    _normalize_symbol_field = field_validator("symbol", mode="before")(
        _normalize_crypto_symbol
    )
    _normalize_provider_symbol = field_validator("providerSymbol", mode="before")(
        _normalize_crypto_provider_symbol
    )
    _normalize_quote_currency = field_validator("quoteCurrency", mode="before")(
        _normalize_quote_currency
    )
    _normalize_from = field_validator("from_", mode="after")(_normalize_utc_datetime)
    _normalize_to = field_validator("to", mode="after")(_normalize_utc_datetime)

    @model_validator(mode="after")
    def _validate_row_count(self) -> "CryptoIntradayBarsResponse":
        provider_base = self.providerSymbol[2:-3]
        if provider_base != self.symbol:
            raise ValueError("providerSymbol must match the canonical symbol.")
        if self.rowCount != len(self.rows):
            raise ValueError("rowCount must match the number of rows.")
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
    marketSession: IntradayMarketSession = "us_equities_regular"
    nextDueAt: datetime | None = None
    lastRunAt: datetime | None = None
    updatedAt: datetime | None = None


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
    marketSession: IntradayMarketSession = "us_equities_regular"

    _normalize_symbols_field = field_validator("symbols", mode="before")(
        _normalize_symbols
    )


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
    symbol: str = Field(min_length=1, max_length=32)
    monitorStatus: IntradaySymbolMonitorStatus = "idle"
    lastSnapshotAt: datetime | None = None
    lastObservedPrice: float | None = None
    lastSuccessfulMarketRefreshAt: datetime | None = None
    lastRunId: str | None = Field(default=None, min_length=1, max_length=64)
    lastError: str | None = Field(default=None, max_length=2_000)
    updatedAt: datetime | None = None

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


class IntradayMonitorCompleteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claimToken: str = Field(min_length=1, max_length=128)
    symbolStatuses: list[IntradaySymbolStatus] = Field(default_factory=list)
    events: list[IntradayMonitorEvent] = Field(default_factory=list)
    refreshSymbols: list[str] = Field(default_factory=list)

    _normalize_refresh_symbols = field_validator("refreshSymbols", mode="before")(
        _normalize_symbols
    )


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
    domain: str = Field(default="market", min_length=1, max_length=64)
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


class IntradayRefreshClaimRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    executionName: str | None = Field(default=None, max_length=255)


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
