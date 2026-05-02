from __future__ import annotations

from asset_allocation_contracts.market_history import (
    GOLD_MARKET_SILVER_SOURCE_COLUMNS,
    LEGACY_SILVER_MARKET_COLUMNS,
    SILVER_MARKET_COLUMNS,
    SILVER_MARKET_CORPORATE_ACTION_COLUMNS,
    SILVER_MARKET_NUMERIC_COLUMNS,
)


def test_silver_market_schema_columns_are_canonical_ordered_contract() -> None:
    assert SILVER_MARKET_COLUMNS == (
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


def test_silver_market_schema_documents_legacy_and_corporate_action_columns() -> None:
    assert LEGACY_SILVER_MARKET_COLUMNS == SILVER_MARKET_COLUMNS[:9]
    assert SILVER_MARKET_CORPORATE_ACTION_COLUMNS == (
        "dividend_amount",
        "split_coefficient",
    )
    assert set(SILVER_MARKET_NUMERIC_COLUMNS) == set(SILVER_MARKET_COLUMNS) - {"date", "symbol"}


def test_gold_market_silver_source_columns_are_subset_of_silver_contract() -> None:
    assert GOLD_MARKET_SILVER_SOURCE_COLUMNS == (
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
    assert set(GOLD_MARKET_SILVER_SOURCE_COLUMNS).issubset(set(SILVER_MARKET_COLUMNS))
