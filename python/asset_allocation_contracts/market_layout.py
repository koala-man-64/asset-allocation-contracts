from __future__ import annotations

import hashlib
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


MARKET_LAYOUT_ALPHA26 = "alpha26"
MARKET_LAYOUT_DATE_PARTITIONED_V1 = "date_partitioned_v1"
MARKET_LAYOUT_SYMBOL_HASH_SHARD_V1 = "symbol_hash_shard_v1"
DEFAULT_MARKET_SYMBOL_HASH_SHARDS = 64

MarketLayoutVersion = Literal[
    "alpha26",
    "date_partitioned_v1",
    "symbol_hash_shard_v1",
]
MarketLayoutLayer = Literal["bronze", "silver", "gold"]

MARKET_LAYOUT_MANIFEST_REQUIRED_FIELDS: tuple[str, ...] = (
    "layout_version",
    "observation_date",
    "date_start",
    "date_end",
    "shard_key",
    "source_manifest",
    "source_hash",
)


def normalize_market_date(value: date | str) -> str:
    if isinstance(value, date):
        return value.isoformat()
    text = str(value or "").strip()
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError as exc:
        raise ValueError(f"Invalid market partition date: {value!r}") from exc


def normalize_market_layout_version(value: str) -> MarketLayoutVersion:
    normalized = str(value or "").strip().lower().replace("-", "_")
    aliases = {
        "date": MARKET_LAYOUT_DATE_PARTITIONED_V1,
        "date_partitioned": MARKET_LAYOUT_DATE_PARTITIONED_V1,
        "symbol_hash_shard": MARKET_LAYOUT_SYMBOL_HASH_SHARD_V1,
    }
    normalized = aliases.get(normalized, normalized)
    if normalized not in {
        MARKET_LAYOUT_ALPHA26,
        MARKET_LAYOUT_DATE_PARTITIONED_V1,
        MARKET_LAYOUT_SYMBOL_HASH_SHARD_V1,
    }:
        raise ValueError(f"Unsupported market layout version: {value!r}")
    return normalized  # type: ignore[return-value]


def normalize_market_layout_layer(value: str) -> MarketLayoutLayer:
    normalized = str(value or "").strip().lower()
    if normalized not in {"bronze", "silver", "gold"}:
        raise ValueError(f"Unsupported market layout layer: {value!r}")
    return normalized  # type: ignore[return-value]


def normalize_market_symbol(value: str) -> str:
    symbol = str(value or "").strip().upper()
    if not symbol:
        raise ValueError("symbol must be non-empty.")
    return symbol


def validate_market_symbol_hash_shard_count(shard_count: int) -> int:
    try:
        count = int(shard_count)
    except (TypeError, ValueError) as exc:
        raise ValueError("shard_count must be an integer.") from exc
    if count <= 0:
        raise ValueError("shard_count must be positive.")
    if count > 10_000:
        raise ValueError("shard_count must be 10,000 or less.")
    return count


def market_symbol_hash_shard(symbol: str, shard_count: int = DEFAULT_MARKET_SYMBOL_HASH_SHARDS) -> int:
    count = validate_market_symbol_hash_shard_count(shard_count)
    normalized_symbol = normalize_market_symbol(symbol)
    digest = hashlib.sha256(normalized_symbol.encode("utf-8")).hexdigest()
    return int(digest[:16], 16) % count


def market_symbol_hash_shard_key(symbol: str, shard_count: int = DEFAULT_MARKET_SYMBOL_HASH_SHARDS) -> str:
    count = validate_market_symbol_hash_shard_count(shard_count)
    width = max(2, len(str(count - 1)))
    return f"symbol_hash_{market_symbol_hash_shard(symbol, count):0{width}d}"


class MarketLayoutManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    layout_version: MarketLayoutVersion
    layer: MarketLayoutLayer
    observation_date: date | None = None
    date_start: date | None = None
    date_end: date | None = None
    shard_key: str | None = Field(default=None, min_length=1, max_length=128)
    source_manifest: str | None = Field(default=None, min_length=1)
    source_hash: str | None = Field(default=None, min_length=1, max_length=256)
    rows_out: int = Field(default=0, ge=0)
    symbols_out: int = Field(default=0, ge=0)
    touched_dates: tuple[date, ...] = Field(default_factory=tuple)
    touched_symbols: tuple[str, ...] = Field(default_factory=tuple)
    provider: str | None = Field(default=None, min_length=1, max_length=128)
    vendor: str | None = Field(default=None, min_length=1, max_length=128)
    correction_version: str | None = Field(default=None, min_length=1, max_length=128)
    parity_status: Literal["unknown", "pending", "matched", "mismatch"] = "unknown"

    @model_validator(mode="after")
    def _validate_date_range(self) -> "MarketLayoutManifest":
        if self.date_start is not None and self.date_end is not None and self.date_start > self.date_end:
            raise ValueError("date_start must be before or equal to date_end.")
        if self.layout_version == MARKET_LAYOUT_DATE_PARTITIONED_V1 and self.observation_date is None:
            raise ValueError("observation_date is required for date_partitioned_v1 manifests.")
        if self.layout_version == MARKET_LAYOUT_SYMBOL_HASH_SHARD_V1 and not self.shard_key:
            raise ValueError("shard_key is required for symbol_hash_shard_v1 manifests.")
        return self
