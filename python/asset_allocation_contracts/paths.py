from __future__ import annotations

import os

from asset_allocation_contracts.market_layout import (
    MARKET_LAYOUT_DATE_PARTITIONED_V1,
    MARKET_LAYOUT_SYMBOL_HASH_SHARD_V1,
    market_symbol_hash_shard_key,
    normalize_market_date,
    normalize_market_layout_layer,
    normalize_market_layout_version,
)

ALPHABET_BUCKETS: tuple[str, ...] = tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
FINANCE_ALPHA26_SUBDOMAINS: tuple[str, ...] = (
    "balance_sheet",
    "income_statement",
    "cash_flow",
    "valuation",
)
QUIVER_DOMAIN_SLUG: str = "quiver"
QUIVER_SILVER_DOMAIN_SLUG: str = "quiver-data"
CURRENCY_DOMAIN_SLUG: str = "currency"
CURRENCY_INTRADAY_PATH_SLUG: str = "intraday"
CURRENCY_INTRADAY_DOMAIN_SLUG: str = CURRENCY_DOMAIN_SLUG
CURRENCY_INTRADAY_STORAGE_PREFIX: str = (
    f"{CURRENCY_DOMAIN_SLUG}/{CURRENCY_INTRADAY_PATH_SLUG}"
)


def normalize_finance_folder(folder: str) -> str:
    return str(folder or "").strip().lower().replace(" ", "_").replace("-", "_")


def normalize_quiver_folder(folder: str) -> str:
    return str(folder or "").strip().lower().replace(" ", "_").replace("-", "_")


def normalize_currency_intraday_interval(interval: str) -> str:
    normalized = str(interval or "").strip().lower()
    if normalized not in {"1m", "5m", "15m"}:
        raise ValueError("Currency intraday interval must be one of 1m, 5m, or 15m.")
    return normalized


def bucket_letter(symbol: str) -> str:
    normalized = str(symbol or "").strip().upper()
    for char in normalized:
        if "A" <= char <= "Z":
            return char
    return "X"


class DataPaths:
    _FINANCE_ALPHA26_SUBDOMAINS = FINANCE_ALPHA26_SUBDOMAINS

    @staticmethod
    def get_silver_market_bucket_path(bucket: str) -> str:
        return f"market-data/buckets/{str(bucket).strip().upper()}"

    @staticmethod
    def get_gold_market_bucket_path(bucket: str) -> str:
        return f"market/buckets/{str(bucket).strip().upper()}"

    @staticmethod
    def get_bronze_market_date_partition_path(observation_date, *, vendor: str = "massive") -> str:
        clean_vendor = str(vendor or "").strip().lower().replace(" ", "_").replace("-", "_")
        if not clean_vendor:
            raise ValueError("vendor must be non-empty.")
        clean_date = normalize_market_date(observation_date)
        return (
            f"market-data/layouts/{MARKET_LAYOUT_DATE_PARTITIONED_V1}/"
            f"vendor={clean_vendor}/observation_date={clean_date}"
        )

    @staticmethod
    def get_silver_market_date_partition_path(observation_date) -> str:
        clean_date = normalize_market_date(observation_date)
        return f"market-data/layouts/{MARKET_LAYOUT_DATE_PARTITIONED_V1}/observation_date={clean_date}"

    @staticmethod
    def get_gold_market_feature_shard_path(
        feature_date,
        *,
        symbol: str | None = None,
        shard_key: str | None = None,
        shard_count: int = 64,
    ) -> str:
        clean_date = normalize_market_date(feature_date)
        resolved_shard_key = str(shard_key or "").strip()
        if not resolved_shard_key:
            if symbol is None:
                raise ValueError("symbol or shard_key is required.")
            resolved_shard_key = market_symbol_hash_shard_key(symbol, shard_count)
        return (
            f"market/layouts/{MARKET_LAYOUT_SYMBOL_HASH_SHARD_V1}/"
            f"feature_date={clean_date}/shard_key={resolved_shard_key}"
        )

    @staticmethod
    def get_market_layout_manifest_path(
        *,
        layer: str,
        layout_version: str,
        observation_date=None,
        date_start=None,
        date_end=None,
        shard_key: str | None = None,
    ) -> str:
        clean_layer = normalize_market_layout_layer(layer)
        clean_layout = normalize_market_layout_version(layout_version)
        fragments = [f"system/market-layouts/{clean_layer}/{clean_layout}"]
        if observation_date is not None:
            fragments.append(f"observation_date={normalize_market_date(observation_date)}")
        if date_start is not None:
            fragments.append(f"date_start={normalize_market_date(date_start)}")
        if date_end is not None:
            fragments.append(f"date_end={normalize_market_date(date_end)}")
        clean_shard = str(shard_key or "").strip()
        if clean_shard:
            fragments.append(f"shard_key={clean_shard}")
        fragments.append("manifest.json")
        return "/".join(fragments)

    @staticmethod
    def get_technical_analysis_path(ticker: str) -> str:
        return f"technical-analysis/{ticker}"

    @staticmethod
    def get_gold_earnings_bucket_path(bucket: str) -> str:
        return f"earnings/buckets/{str(bucket).strip().upper()}"

    @staticmethod
    def get_gold_finance_bucket_path(folder: str, bucket: str) -> str:
        clean_folder = normalize_finance_folder(folder)
        return f"finance/{clean_folder}/buckets/{str(bucket).strip().upper()}"

    @staticmethod
    def get_gold_finance_domain_path(folder: str) -> str:
        clean_folder = normalize_finance_folder(folder)
        return f"finance/{clean_folder}"

    @staticmethod
    def get_gold_finance_bucket_paths(bucket: str) -> list[str]:
        return [
            DataPaths.get_gold_finance_bucket_path(folder, bucket)
            for folder in DataPaths._FINANCE_ALPHA26_SUBDOMAINS
        ]

    @staticmethod
    def get_gold_finance_alpha26_bucket_path(bucket: str) -> str:
        return f"finance/buckets/{str(bucket).strip().upper()}"

    @staticmethod
    def get_gold_price_targets_bucket_path(bucket: str) -> str:
        return f"targets/buckets/{str(bucket).strip().upper()}"

    @staticmethod
    def get_silver_price_target_bucket_path(bucket: str) -> str:
        return f"price-target-data/buckets/{str(bucket).strip().upper()}"

    @staticmethod
    def get_silver_earnings_bucket_path(bucket: str, prefix: str | None = None) -> str:
        resolved_prefix = str(prefix or os.environ.get("EARNINGS_DATA_PREFIX") or "earnings-data").strip()
        return f"{resolved_prefix}/buckets/{str(bucket).strip().upper()}"

    @staticmethod
    def get_silver_finance_bucket_path(folder: str, bucket: str) -> str:
        clean_folder = normalize_finance_folder(folder)
        return f"finance-data/{clean_folder}/buckets/{str(bucket).strip().upper()}"

    @staticmethod
    def get_silver_quiver_bucket_path(folder: str, bucket: str) -> str:
        clean_folder = normalize_quiver_folder(folder)
        return f"{QUIVER_SILVER_DOMAIN_SLUG}/{clean_folder}/buckets/{str(bucket).strip().upper()}"

    @staticmethod
    def get_gold_quiver_bucket_path(folder: str, bucket: str) -> str:
        clean_folder = normalize_quiver_folder(folder)
        return f"{QUIVER_DOMAIN_SLUG}/{clean_folder}/buckets/{str(bucket).strip().upper()}"

    @staticmethod
    def get_gold_quiver_domain_path(folder: str) -> str:
        clean_folder = normalize_quiver_folder(folder)
        return f"{QUIVER_DOMAIN_SLUG}/{clean_folder}"

    @staticmethod
    def get_bronze_currency_intraday_run_path(run_id: str) -> str:
        clean_run_id = str(run_id or "").strip()
        if not clean_run_id:
            raise ValueError("run_id must be non-empty.")
        return f"{CURRENCY_INTRADAY_STORAGE_PREFIX}/runs/{clean_run_id}"

    @staticmethod
    def get_silver_currency_intraday_bucket_path(interval: str, bucket: str) -> str:
        clean_interval = normalize_currency_intraday_interval(interval)
        return (
            f"{CURRENCY_INTRADAY_STORAGE_PREFIX}/{clean_interval}/buckets/"
            f"{str(bucket).strip().upper()}"
        )

    @staticmethod
    def get_gold_currency_intraday_features_bucket_path(
        interval: str,
        bucket: str,
    ) -> str:
        clean_interval = normalize_currency_intraday_interval(interval)
        return (
            f"{CURRENCY_INTRADAY_STORAGE_PREFIX}/features/{clean_interval}/buckets/"
            f"{str(bucket).strip().upper()}"
        )

    @staticmethod
    def get_gold_currency_intraday_features_domain_path(interval: str) -> str:
        clean_interval = normalize_currency_intraday_interval(interval)
        return f"{CURRENCY_INTRADAY_STORAGE_PREFIX}/features/{clean_interval}"
