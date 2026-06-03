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
    "ranking_rank",
    "ranking_score",
]
StockScreenerSortDirection = Literal["asc", "desc"]
StockScreenerSourceLayer = Literal["gold", "platinum"]
StockScreenerSourceKind = Literal["layer", "table"]
StockScreenerSourceCapability = Literal["stock_identity", "as_of_date", "ranking", "screening"]
StockScreenerSourceValueKind = Literal["string", "number", "boolean", "date", "datetime", "unknown"]
StockScreenerDynamicFilterOperator = Literal[
    "eq",
    "neq",
    "contains",
    "starts_with",
    "ends_with",
    "gt",
    "gte",
    "lt",
    "lte",
    "is_null",
    "is_not_null",
]
StockScreenerDynamicValue = str | int | float | bool | date | datetime | None
_RANKING_SORT_KEYS = {"ranking_rank", "ranking_score"}
_NUMERIC_RANGE_FIELDS = (
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
)


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


def _normalize_visible_column_ids(value: object) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise TypeError("visible_column_ids must be a list of strings.")

    normalized: list[str] = []
    seen: set[str] = set()
    for raw in value:
        column_id = str(raw or "").strip()
        if not column_id:
            continue
        if len(column_id) > 128:
            raise ValueError("visible_column_ids entries must be 128 characters or fewer.")
        key = column_id.casefold()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(column_id)
    return normalized


def _normalize_column_ids(value: object) -> list[str]:
    return _normalize_visible_column_ids(value)


def _normalize_identifier(value: object) -> str | None:
    text = _normalize_optional_text(value)
    if text is None:
        return None
    if len(text) > 128:
        raise ValueError("Identifier fields must be 128 characters or fewer.")
    return text


def _validate_filter_workspace_ranges_and_ranking(
    payload: object,
    *,
    sort: StockScreenerSortKey,
    sorts: list["StockScreenerSortClause"] | None,
    strategy_name: str | None,
    ranking_schema_name: str | None,
    ranking_schema_version: int | None,
) -> None:
    if ranking_schema_version is not None and ranking_schema_name is None:
        raise ValueError("ranking_schema_version requires ranking_schema_name.")
    if ranking_schema_name is not None and strategy_name is None:
        raise ValueError("ranking_schema_name requires strategy_name.")
    if ranking_schema_name is None:
        sort_keys = [sort, *(clause.key for clause in sorts or [])]
        if any(key in _RANKING_SORT_KEYS for key in sort_keys):
            raise ValueError("ranking_rank and ranking_score sorts require ranking_schema_name.")

    for minimum_name, maximum_name in _NUMERIC_RANGE_FIELDS:
        minimum = getattr(payload, minimum_name)
        maximum = getattr(payload, maximum_name)
        if minimum is not None and maximum is not None and minimum > maximum:
            raise ValueError(f"{minimum_name} must be less than or equal to {maximum_name}.")


class StockScreenerSourceDescriptor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: StockScreenerSourceKind = "layer"
    source_layer: StockScreenerSourceLayer | None = None
    schema_name: str | None = Field(default=None, max_length=128)
    table_name: str | None = Field(default=None, max_length=128)
    symbol_column: str | None = Field(default=None, max_length=128)
    as_of_column: str | None = Field(default=None, max_length=128)
    selected_columns: list[str] = Field(default_factory=list, max_length=128)

    _normalize_schema_name = field_validator("schema_name", mode="before")(_normalize_identifier)
    _normalize_table_name = field_validator("table_name", mode="before")(_normalize_identifier)
    _normalize_symbol_column = field_validator("symbol_column", mode="before")(_normalize_identifier)
    _normalize_as_of_column = field_validator("as_of_column", mode="before")(_normalize_identifier)
    _normalize_selected_columns = field_validator("selected_columns", mode="before")(
        _normalize_column_ids
    )

    @model_validator(mode="after")
    def _validate_source_shape(self) -> "StockScreenerSourceDescriptor":
        if self.kind == "layer":
            if self.source_layer is None:
                self.source_layer = "gold"
            if self.schema_name or self.table_name:
                raise ValueError("Layer sources cannot include schema_name or table_name.")
            return self

        if self.source_layer is not None:
            raise ValueError("Table sources cannot include source_layer.")
        if not self.schema_name or not self.table_name:
            raise ValueError("Table sources require schema_name and table_name.")
        return self


class StockScreenerSourceColumn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=128)
    label: str | None = Field(default=None, max_length=128)
    data_type: str = Field(min_length=1, max_length=128)
    value_kind: StockScreenerSourceValueKind = "unknown"
    operators: list[StockScreenerDynamicFilterOperator] = Field(default_factory=list)
    sortable: bool = True
    filterable: bool = True
    default_visible: bool = False

    _normalize_name = field_validator("name", mode="before")(_normalize_identifier)
    _normalize_label = field_validator("label", mode="before")(_normalize_optional_text)
    _normalize_data_type = field_validator("data_type", mode="before")(_normalize_optional_text)


class StockScreenerDynamicFilterClause(BaseModel):
    model_config = ConfigDict(extra="forbid")

    column_name: str = Field(min_length=1, max_length=128)
    operator: StockScreenerDynamicFilterOperator
    value: StockScreenerDynamicValue = None

    _normalize_column_name = field_validator("column_name", mode="before")(_normalize_identifier)


class StockScreenerDynamicSortClause(BaseModel):
    model_config = ConfigDict(extra="forbid")

    column_name: str = Field(min_length=1, max_length=128)
    direction: StockScreenerSortDirection = "desc"

    _normalize_column_name = field_validator("column_name", mode="before")(_normalize_identifier)


class StockScreenerSourceCatalogEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: StockScreenerSourceDescriptor
    label: str = Field(min_length=1, max_length=128)
    description: str | None = Field(default=None, max_length=512)
    capabilities: list[StockScreenerSourceCapability] = Field(default_factory=list)
    columns: list[StockScreenerSourceColumn] = Field(default_factory=list)
    default_column_names: list[str] = Field(default_factory=list, max_length=128)
    unsupported_reason: str | None = Field(default=None, max_length=512)

    _normalize_label = field_validator("label", mode="before")(_normalize_optional_text)
    _normalize_description = field_validator("description", mode="before")(_normalize_optional_text)
    _normalize_default_column_names = field_validator("default_column_names", mode="before")(
        _normalize_column_ids
    )
    _normalize_unsupported_reason = field_validator("unsupported_reason", mode="before")(
        _normalize_optional_text
    )


class StockScreenerSourceCatalogResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sources: list[StockScreenerSourceCatalogEntry] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class StockScreenerSortClause(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: StockScreenerSortKey
    direction: StockScreenerSortDirection = "desc"


class StockScreenerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    q: str | None = Field(default=None, max_length=255)
    as_of: date | None = None
    source_layer: StockScreenerSourceLayer | None = None
    source: StockScreenerSourceDescriptor | None = None
    selected_columns: list[str] = Field(default_factory=list, max_length=128)
    dynamic_filters: list[StockScreenerDynamicFilterClause] | None = Field(default=None, max_length=20)
    dynamic_sorts: list[StockScreenerDynamicSortClause] | None = Field(default=None, max_length=5)
    limit: int = Field(default=250, ge=1, le=2_000)
    offset: int = Field(default=0, ge=0)
    sort: StockScreenerSortKey = "volume"
    direction: StockScreenerSortDirection = "desc"
    sorts: list[StockScreenerSortClause] | None = Field(default=None, max_length=5)
    strategy_name: str | None = Field(default=None, max_length=128)
    ranking_schema_name: str | None = Field(default=None, max_length=128)
    ranking_schema_version: int | None = Field(default=None, ge=1)
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
    _normalize_selected_columns = field_validator("selected_columns", mode="before")(
        _normalize_column_ids
    )
    _normalize_strategy_name = field_validator("strategy_name", mode="before")(_normalize_optional_text)
    _normalize_ranking_schema_name = field_validator("ranking_schema_name", mode="before")(_normalize_optional_text)
    _normalize_sectors = field_validator("sectors", mode="before")(_normalize_filter_values)
    _normalize_industries = field_validator("industries", mode="before")(_normalize_filter_values)
    _normalize_countries = field_validator("countries", mode="before")(_normalize_filter_values)

    @field_validator("sorts", mode="after")
    @classmethod
    def _normalize_sort_stack(
        cls, value: list[StockScreenerSortClause] | None
    ) -> list[StockScreenerSortClause] | None:
        if not value:
            return None

        normalized: list[StockScreenerSortClause] = []
        seen: set[StockScreenerSortKey] = set()
        for clause in value:
            if clause.key in seen:
                continue
            seen.add(clause.key)
            normalized.append(clause)
        return normalized or None

    @model_validator(mode="after")
    def _validate_numeric_ranges(self) -> StockScreenerRequest:
        if self.source is None and self.source_layer is not None:
            self.source = StockScreenerSourceDescriptor(kind="layer", source_layer=self.source_layer)
        if self.source is not None and self.source.kind == "layer":
            self.source_layer = self.source.source_layer
        _validate_filter_workspace_ranges_and_ranking(
            self,
            sort=self.sort,
            sorts=self.sorts,
            strategy_name=self.strategy_name,
            ranking_schema_name=self.ranking_schema_name,
            ranking_schema_version=self.ranking_schema_version,
        )
        return self


class StockScreenerPresetWorkspace(BaseModel):
    model_config = ConfigDict(extra="forbid")

    q: str | None = Field(default=None, max_length=255)
    as_of: date | None = None
    source_layer: StockScreenerSourceLayer = "gold"
    source: StockScreenerSourceDescriptor | None = None
    selected_columns: list[str] = Field(default_factory=list, max_length=128)
    dynamic_filters: list[StockScreenerDynamicFilterClause] | None = Field(default=None, max_length=20)
    dynamic_sorts: list[StockScreenerDynamicSortClause] | None = Field(default=None, max_length=5)
    sort: StockScreenerSortKey = "volume"
    direction: StockScreenerSortDirection = "desc"
    sorts: list[StockScreenerSortClause] | None = Field(default=None, max_length=5)
    strategy_name: str | None = Field(default=None, max_length=128)
    ranking_schema_name: str | None = Field(default=None, max_length=128)
    ranking_schema_version: int | None = Field(default=None, ge=1)
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
    visible_column_ids: list[str] = Field(default_factory=list, max_length=64)

    _normalize_query = field_validator("q", mode="before")(_normalize_optional_text)
    _normalize_selected_columns = field_validator("selected_columns", mode="before")(
        _normalize_column_ids
    )
    _normalize_strategy_name = field_validator("strategy_name", mode="before")(_normalize_optional_text)
    _normalize_ranking_schema_name = field_validator("ranking_schema_name", mode="before")(_normalize_optional_text)
    _normalize_sectors = field_validator("sectors", mode="before")(_normalize_filter_values)
    _normalize_industries = field_validator("industries", mode="before")(_normalize_filter_values)
    _normalize_countries = field_validator("countries", mode="before")(_normalize_filter_values)
    _normalize_visible_column_ids = field_validator("visible_column_ids", mode="before")(
        _normalize_visible_column_ids
    )

    @field_validator("sorts", mode="after")
    @classmethod
    def _normalize_sort_stack(
        cls, value: list[StockScreenerSortClause] | None
    ) -> list[StockScreenerSortClause] | None:
        return StockScreenerRequest._normalize_sort_stack(value)

    @model_validator(mode="after")
    def _validate_numeric_ranges(self) -> StockScreenerPresetWorkspace:
        if self.source is None:
            self.source = StockScreenerSourceDescriptor(kind="layer", source_layer=self.source_layer)
        elif self.source.kind == "layer":
            self.source_layer = self.source.source_layer or "gold"
        _validate_filter_workspace_ranges_and_ranking(
            self,
            sort=self.sort,
            sorts=self.sorts,
            strategy_name=self.strategy_name,
            ranking_schema_name=self.ranking_schema_name,
            ranking_schema_version=self.ranking_schema_version,
        )
        return self


class StockScreenerPresetSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preset_id: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=96)
    description: str | None = Field(default=None, max_length=512)
    workspace: StockScreenerPresetWorkspace
    created_at: datetime | None = None
    updated_at: datetime | None = None
    last_used_at: datetime | None = None

    _normalize_name = field_validator("name", mode="before")(_normalize_optional_text)
    _normalize_description = field_validator("description", mode="before")(_normalize_optional_text)


class StockScreenerPresetUpsertRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=96)
    description: str | None = Field(default=None, max_length=512)
    workspace: StockScreenerPresetWorkspace

    _normalize_name = field_validator("name", mode="before")(_normalize_optional_text)
    _normalize_description = field_validator("description", mode="before")(_normalize_optional_text)


class StockScreenerPresetListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    presets: list[StockScreenerPresetSummary] = Field(default_factory=list)


class StockScreenerPresetDeleteResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preset_id: str = Field(min_length=1, max_length=64)
    archived: bool = True


class StockScreenerRankingComponent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=128)
    score: float | None = None


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
    rankingRank: int | None = None
    rankingOverallScore: float | None = None
    rankingComponents: list[StockScreenerRankingComponent] | None = None
    values: dict[str, StockScreenerDynamicValue] = Field(default_factory=dict)

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


class StockScreenerRankingMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schemaName: str | None = Field(default=None, max_length=128)
    schemaVersion: int | None = Field(default=None, ge=1)
    componentNames: list[str] = Field(default_factory=list)


class StockScreenerResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asOf: date
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=2_000)
    offset: int = Field(ge=0)
    source: StockScreenerSourceDescriptor | None = None
    sourceColumns: list[StockScreenerSourceColumn] = Field(default_factory=list)
    rows: list[StockScreenerRow] = Field(default_factory=list)
    summary: StockScreenerSummary | None = None
    facets: StockScreenerFacets | None = None
    ranking: StockScreenerRankingMetadata | None = None
    filters: StockScreenerRequest | None = None
