from __future__ import annotations

from typing import Literal

QuiverDatasetFamily = Literal[
    "political_trading",
    "government_contracts",
    "government_contracts_all",
    "insider_trading",
    "institutional_holdings",
    "institutional_holding_changes",
    "lobbying",
    "etf_holdings",
    "congress_holdings",
    "wall_street_bets",
    "patents",
]

QUIVER_DATASET_FAMILIES: tuple[QuiverDatasetFamily, ...] = (
    "political_trading",
    "government_contracts",
    "government_contracts_all",
    "insider_trading",
    "institutional_holdings",
    "institutional_holding_changes",
    "lobbying",
    "etf_holdings",
    "congress_holdings",
    "wall_street_bets",
    "patents",
)

QUIVER_GOLD_FEATURE_DATASETS: tuple[QuiverDatasetFamily, ...] = (
    "political_trading",
    "government_contracts",
    "insider_trading",
    "institutional_holding_changes",
    "wall_street_bets",
    "patents",
    "congress_holdings",
)

QUIVER_BRONZE_SILVER_ONLY_DATASETS: tuple[QuiverDatasetFamily, ...] = (
    "government_contracts_all",
    "institutional_holdings",
    "lobbying",
    "etf_holdings",
)

QUIVER_PUBLIC_AVAILABILITY_FIELDS: dict[QuiverDatasetFamily, str] = {
    "political_trading": "ReportDate",
    "government_contracts": "Date",
    "government_contracts_all": "action_date",
    "insider_trading": "uploaded",
    "institutional_holdings": "Date",
    "institutional_holding_changes": "Date",
    "lobbying": "Date",
    "etf_holdings": "",
    "congress_holdings": "",
    "wall_street_bets": "Time",
    "patents": "Date",
}

QUIVER_EVENT_TIME_FIELDS: dict[QuiverDatasetFamily, str] = {
    "political_trading": "Date",
    "government_contracts": "Date",
    "government_contracts_all": "action_date",
    "insider_trading": "Date",
    "institutional_holdings": "ReportPeriod",
    "institutional_holding_changes": "ReportPeriod",
    "lobbying": "Date",
    "etf_holdings": "",
    "congress_holdings": "",
    "wall_street_bets": "Time",
    "patents": "Date",
}

QUIVER_SYMBOL_FIELD_HINTS: dict[QuiverDatasetFamily, tuple[str, ...]] = {
    "political_trading": ("Ticker",),
    "government_contracts": ("Ticker",),
    "government_contracts_all": ("Ticker",),
    "insider_trading": ("Ticker",),
    "institutional_holdings": ("Ticker",),
    "institutional_holding_changes": ("Ticker",),
    "lobbying": ("Ticker",),
    "etf_holdings": ("Holding Symbol", "ETF Symbol"),
    "congress_holdings": (),
    "wall_street_bets": ("Ticker",),
    "patents": ("Ticker",),
}

QUIVER_GOLD_DATASET_BLOCKERS: dict[QuiverDatasetFamily, str] = {
    "congress_holdings": (
        "Provider schema does not expose a ticker or event/public-availability timestamp. "
        "The official live congress holdings response only includes Politician, Holdings, and Type."
    ),
}

QUIVER_FORWARD_LOOKING_COLUMNS: frozenset[str] = frozenset(
    {
        "ExcessReturn",
        "PriceChange",
        "SPYChange",
        "excess_return",
        "price_change",
        "spy_change",
    }
)


def quiver_public_availability_field(dataset: str) -> str:
    key = normalize_quiver_dataset(dataset)
    return QUIVER_PUBLIC_AVAILABILITY_FIELDS[key]


def quiver_event_time_field(dataset: str) -> str:
    key = normalize_quiver_dataset(dataset)
    return QUIVER_EVENT_TIME_FIELDS[key]


def quiver_symbol_field_hints(dataset: str) -> tuple[str, ...]:
    key = normalize_quiver_dataset(dataset)
    return QUIVER_SYMBOL_FIELD_HINTS[key]


def quiver_gold_dataset_blocker(dataset: str) -> str:
    key = normalize_quiver_dataset(dataset)
    return str(QUIVER_GOLD_DATASET_BLOCKERS.get(key, "") or "")


def validate_quiver_gold_dataset(dataset: str) -> None:
    key = normalize_quiver_dataset(dataset)
    if key not in QUIVER_GOLD_FEATURE_DATASETS:
        raise ValueError(f"Unsupported Quiver gold dataset family: {dataset!r}.")
    blocker = quiver_gold_dataset_blocker(key)
    if blocker:
        raise ValueError(f"Quiver gold dataset {key!r} is blocked: {blocker}")


def normalize_quiver_dataset(dataset: str) -> QuiverDatasetFamily:
    key = str(dataset or "").strip().lower().replace("-", "_").replace(" ", "_")
    if key not in QUIVER_DATASET_FAMILIES:
        raise ValueError(f"Unsupported Quiver dataset family: {dataset!r}.")
    return key  # type: ignore[return-value]


def filter_quiver_feature_columns(columns: list[str] | tuple[str, ...]) -> list[str]:
    return [column for column in columns if str(column) not in QUIVER_FORWARD_LOOKING_COLUMNS]
