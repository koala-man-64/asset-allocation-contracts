from __future__ import annotations

import os

ALPHABET_BUCKETS: tuple[str, ...] = tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
FINANCE_ALPHA26_SUBDOMAINS: tuple[str, ...] = (
    "balance_sheet",
    "income_statement",
    "cash_flow",
    "valuation",
)
QUIVER_DOMAIN_SLUG: str = "quiver"
QUIVER_SILVER_DOMAIN_SLUG: str = "quiver-data"


def normalize_finance_folder(folder: str) -> str:
    return str(folder or "").strip().lower().replace(" ", "_").replace("-", "_")


def normalize_quiver_folder(folder: str) -> str:
    return str(folder or "").strip().lower().replace(" ", "_").replace("-", "_")


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
