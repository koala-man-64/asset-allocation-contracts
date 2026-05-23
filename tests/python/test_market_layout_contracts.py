from __future__ import annotations

from datetime import date

import pytest

from asset_allocation_contracts.market_layout import (
    DEFAULT_MARKET_SYMBOL_HASH_SHARDS,
    MARKET_LAYOUT_DATE_PARTITIONED_V1,
    MARKET_LAYOUT_MANIFEST_REQUIRED_FIELDS,
    MARKET_LAYOUT_SYMBOL_HASH_SHARD_V1,
    MarketLayoutManifest,
    market_symbol_hash_shard,
    market_symbol_hash_shard_key,
)
from asset_allocation_contracts.paths import DataPaths


def test_alpha26_market_paths_are_unchanged() -> None:
    assert DataPaths.get_silver_market_bucket_path("a") == "market-data/buckets/A"
    assert DataPaths.get_gold_market_bucket_path("a") == "market/buckets/A"


def test_date_partitioned_market_paths_are_stable() -> None:
    assert (
        DataPaths.get_bronze_market_date_partition_path("2026-05-21", vendor="Massive")
        == "market-data/layouts/date_partitioned_v1/vendor=massive/observation_date=2026-05-21"
    )
    assert (
        DataPaths.get_silver_market_date_partition_path(date(2026, 5, 21))
        == "market-data/layouts/date_partitioned_v1/observation_date=2026-05-21"
    )


def test_symbol_hash_shard_paths_use_deterministic_key() -> None:
    shard_key = market_symbol_hash_shard_key("AAPL")

    assert shard_key == market_symbol_hash_shard_key(" aapl ")
    assert shard_key.startswith("symbol_hash_")
    assert 0 <= market_symbol_hash_shard("AAPL") < DEFAULT_MARKET_SYMBOL_HASH_SHARDS
    assert DataPaths.get_gold_market_feature_shard_path("2026-05-21", symbol="AAPL") == (
        "market/layouts/symbol_hash_shard_v1/"
        f"feature_date=2026-05-21/shard_key={shard_key}"
    )


def test_market_layout_manifest_path_includes_version_and_partition_fields() -> None:
    assert DataPaths.get_market_layout_manifest_path(
        layer="gold",
        layout_version="symbol_hash_shard",
        date_start="2026-05-01",
        date_end="2026-05-21",
        shard_key="symbol_hash_07",
    ) == (
        "system/market-layouts/gold/symbol_hash_shard_v1/"
        "date_start=2026-05-01/date_end=2026-05-21/shard_key=symbol_hash_07/manifest.json"
    )


def test_market_layout_manifest_validates_required_shape() -> None:
    assert MARKET_LAYOUT_MANIFEST_REQUIRED_FIELDS == (
        "layout_version",
        "observation_date",
        "date_start",
        "date_end",
        "shard_key",
        "source_manifest",
        "source_hash",
    )

    manifest = MarketLayoutManifest(
        layout_version=MARKET_LAYOUT_DATE_PARTITIONED_V1,
        layer="silver",
        observation_date=date(2026, 5, 21),
        date_start=date(2026, 5, 21),
        date_end=date(2026, 5, 21),
        source_manifest="system/market-layouts/bronze/date_partitioned_v1/manifest.json",
        source_hash="abc123",
        rows_out=2,
        symbols_out=1,
        touched_dates=(date(2026, 5, 21),),
        touched_symbols=("AAPL",),
    )

    assert manifest.layout_version == MARKET_LAYOUT_DATE_PARTITIONED_V1
    assert manifest.observation_date == date(2026, 5, 21)


def test_market_layout_manifest_rejects_missing_date_or_shard_identity() -> None:
    with pytest.raises(ValueError, match="observation_date is required"):
        MarketLayoutManifest(layout_version=MARKET_LAYOUT_DATE_PARTITIONED_V1, layer="bronze")

    with pytest.raises(ValueError, match="shard_key is required"):
        MarketLayoutManifest(layout_version=MARKET_LAYOUT_SYMBOL_HASH_SHARD_V1, layer="gold")
