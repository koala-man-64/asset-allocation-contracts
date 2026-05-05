from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


StockScreenerSortKey = Literal[
    "symbol",
    "close",
    "volume",
    "return_1d",
    "return_5d",
    "vol_20d",
    "drawdown_1y",
    "atr_14d",
    "gap_atr",
    "sma_50d",
    "sma_200d",
    "trend_50_200",
    "above_sma_50",
    "bb_width_20d",
    "compression_score",
    "volume_z_20d",
    "volume_pct_rank_252d",
]
StockScreenerSortDirection = Literal["asc", "desc"]


def _normalize_optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _normalize_filter_values(value: object) -> list[str] | None:
    if value is None:
        return None
    if isinstance(value, str):
        raw_values = value.split(",")
    elif isinstance(value, list):
        raw_values = value
    else:
        raise TypeError("Filter values must be a list or comma-separated string.")

    normalized: list[str] = []
    seen: set[str] = set()
    for raw in raw_values:
        item = str(raw or "").strip()
        if not item:
            continue
        key = item.casefold()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(item)
    return normalized or None


class StockScreenerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    q: str | None = Field(default=None, max_length=255)
    as_of: date | None = None
    limit: int = Field(default=250, ge=1, le=2_000)
    offset: int = Field(default=0, ge=0)
    sort: StockScreenerSortKey = "volume"
    direction: StockScreenerSortDirection = "desc"
    sectors: list[str] | None = None
    industries: list[str] | None = None
    countries: list[str] | None = None
    is_optionable: bool | None = None
    has_silver: bool | None = None
    has_gold: bool | None = None
    above_sma_50: bool | None = None
    min_close: float | None = None
    max_close: float | None = None
    min_volume: float | None = None
    max_volume: float | None = None
    min_return_1d: float | None = None
    max_return_1d: float | None = None
    min_return_5d: float | None = None
    max_return_5d: float | None = None
    min_vol_20d: float | None = None
    max_vol_20d: float | None = None
    min_drawdown_1y: float | None = None
    max_drawdown_1y: float | None = None
    min_atr_14d: float | None = None
    max_atr_14d: float | None = None
    min_gap_atr: float | None = None
    max_gap_atr: float | None = None
    min_sma_50d: float | None = None
    max_sma_50d: float | None = None
    min_sma_200d: float | None = None
    max_sma_200d: float | None = None
    min_trend_50_200: float | None = None
    max_trend_50_200: float | None = None
    min_bb_width_20d: float | None = None
    max_bb_width_20d: float | None = None
    min_compression_score: float | None = None
    max_compression_score: float | None = None
    min_volume_z_20d: float | None = None
    max_volume_z_20d: float | None = None
    min_volume_pct_rank_252d: float | None = None
    max_volume_pct_rank_252d: float | None = None

    _normalize_query = field_validator("q", mode="before")(_normalize_optional_text)
    _normalize_sectors = field_validator("sectors", mode="before")(_normalize_filter_values)
    _normalize_industries = field_validator("industries", mode="before")(_normalize_filter_values)
    _normalize_countries = field_validator("countries", mode="before")(_normalize_filter_values)

    @model_validator(mode="after")
    def _validate_numeric_ranges(self) -> StockScreenerRequest:
        for minimum_name, maximum_name in (
            ("min_close", "max_close"),
            ("min_volume", "max_volume"),
            ("min_return_1d", "max_return_1d"),
            ("min_return_5d", "max_return_5d"),
            ("min_vol_20d", "max_vol_20d"),
            ("min_drawdown_1y", "max_drawdown_1y"),
            ("min_atr_14d", "max_atr_14d"),
            ("min_gap_atr", "max_gap_atr"),
            ("min_sma_50d", "max_sma_50d"),
            ("min_sma_200d", "max_sma_200d"),
            ("min_trend_50_200", "max_trend_50_200"),
            ("min_bb_width_20d", "max_bb_width_20d"),
            ("min_compression_score", "max_compression_score"),
            ("min_volume_z_20d", "max_volume_z_20d"),
            ("min_volume_pct_rank_252d", "max_volume_pct_rank_252d"),
        ):
            minimum = getattr(self, minimum_name)
            maximum = getattr(self, maximum_name)
            if minimum is not None and maximum is not None and minimum > maximum:
                raise ValueError(f"{minimum_name} must be less than or equal to {maximum_name}.")
        return self


class StockScreenerRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol: str = Field(min_length=1, max_length=32)
    name: str | None = Field(default=None, max_length=255)
    sector: str | None = Field(default=None, max_length=255)
    industry: str | None = Field(default=None, max_length=255)
    country: str | None = Field(default=None, max_length=64)
    isOptionable: bool | None = None
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    volume: float | None = None
    return1d: float | None = None
    return5d: float | None = None
    vol20d: float | None = None
    drawdown1y: float | None = None
    atr14d: float | None = None
    gapAtr: float | None = None
    sma50d: float | None = None
    sma200d: float | None = None
    trend50_200: float | None = None
    aboveSma50: float | None = None
    bbWidth20d: float | None = None
    compressionScore: float | None = None
    volumeZ20d: float | None = None
    volumePctRank252d: float | None = None
    hasSilver: bool | int | None = None
    hasGold: bool | int | None = None

    @field_validator("symbol", mode="before")
    @classmethod
    def _normalize_symbol(cls, value: object) -> str:
        symbol = str(value or "").strip().upper()
        if not symbol:
            raise ValueError("symbol must be non-empty.")
        return symbol


class StockScreenerCoverageSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total: int = Field(ge=0)
    withSilver: int = Field(default=0, ge=0)
    withGold: int = Field(default=0, ge=0)
    missingSilver: int = Field(default=0, ge=0)
    missingGold: int = Field(default=0, ge=0)


class StockScreenerSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    universeCount: int = Field(ge=0)
    totalResultCount: int = Field(ge=0)
    returnedCount: int = Field(ge=0)
    coverage: StockScreenerCoverageSummary
    generatedAt: datetime | None = None


class StockScreenerFacetBucket(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: str = Field(min_length=1, max_length=255)
    count: int = Field(ge=0)


class StockScreenerFacets(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sectors: list[StockScreenerFacetBucket] = Field(default_factory=list)
    industries: list[StockScreenerFacetBucket] = Field(default_factory=list)
    countries: list[StockScreenerFacetBucket] = Field(default_factory=list)


class StockScreenerResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asOf: date
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=2_000)
    offset: int = Field(ge=0)
    rows: list[StockScreenerRow] = Field(default_factory=list)
    summary: StockScreenerSummary | None = None
    facets: StockScreenerFacets | None = None
    filters: StockScreenerRequest | None = None
