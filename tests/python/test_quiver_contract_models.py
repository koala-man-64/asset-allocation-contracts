from asset_allocation_contracts.paths import DataPaths
from asset_allocation_contracts.quiver_signals import (
    QUIVER_FORWARD_LOOKING_COLUMNS,
    filter_quiver_feature_columns,
    normalize_quiver_dataset,
    quiver_event_time_field,
    quiver_public_availability_field,
    quiver_symbol_field_hints,
)


def test_quiver_dataset_normalization() -> None:
    assert normalize_quiver_dataset("Political Trading") == "political_trading"
    assert normalize_quiver_dataset("government-contracts") == "government_contracts"


def test_quiver_public_availability_rules() -> None:
    assert quiver_public_availability_field("political_trading") == "ReportDate"
    assert quiver_public_availability_field("insider_trading") == "uploaded"
    assert quiver_public_availability_field("government_contracts_all") == "action_date"
    assert quiver_event_time_field("institutional_holding_changes") == "ReportPeriod"
    assert quiver_symbol_field_hints("etf_holdings") == ("Holding Symbol", "ETF Symbol")


def test_quiver_paths_use_shared_domain_roots() -> None:
    assert DataPaths.get_silver_quiver_bucket_path("political_trading", "a") == "quiver-data/political_trading/buckets/A"
    assert DataPaths.get_gold_quiver_bucket_path("government_contracts", "p") == "quiver/government_contracts/buckets/P"
    assert DataPaths.get_gold_quiver_domain_path("institutional_holdings") == "quiver/institutional_holdings"


def test_quiver_forward_looking_columns_are_filtered_from_features() -> None:
    assert "ExcessReturn" in QUIVER_FORWARD_LOOKING_COLUMNS
    assert filter_quiver_feature_columns(["symbol", "PriceChange", "net_signal", "spy_change"]) == [
        "symbol",
        "net_signal",
    ]
