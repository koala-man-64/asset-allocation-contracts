from __future__ import annotations

MARKET_HISTORY_START_DATE = "2016-01-01"
MARKET_HISTORY_STATUS_OK = "ok"
MARKET_HISTORY_STATUS_NO_HISTORY = "no_history"

BRONZE_MARKET_COLUMNS = (
    "symbol",
    "date",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "short_interest",
    "short_volume",
    "dividend_amount",
    "split_coefficient",
    "ingested_at",
    "source_hash",
)

LEGACY_SILVER_MARKET_COLUMNS = (
    "date",
    "symbol",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "short_interest",
    "short_volume",
)

SILVER_MARKET_COLUMNS = (
    "date",
    "symbol",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "short_interest",
    "short_volume",
    "dividend_amount",
    "split_coefficient",
)

SILVER_MARKET_NUMERIC_COLUMNS = (
    "open",
    "high",
    "low",
    "close",
    "volume",
    "short_interest",
    "short_volume",
    "dividend_amount",
    "split_coefficient",
)

SILVER_MARKET_CORPORATE_ACTION_COLUMNS = (
    "dividend_amount",
    "split_coefficient",
)

GOLD_MARKET_SILVER_SOURCE_COLUMNS = (
    "date",
    "symbol",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "dividend_amount",
    "split_coefficient",
)

