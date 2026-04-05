from __future__ import annotations

from asset_allocation_contracts.backtest import BacktestClaimRequest
from asset_allocation_contracts.paths import DataPaths, bucket_letter
from asset_allocation_contracts.ranking import RankingGroup, RankingSchemaConfig
from asset_allocation_contracts.regime import RegimeModelConfig, RegimePolicy, RegimeSnapshot
from asset_allocation_contracts.strategy import StrategyConfig, UniverseCondition, UniverseDefinition, UniverseGroup
from asset_allocation_contracts.ui_config import UiRuntimeConfig


def test_strategy_contract_accepts_regime_policy() -> None:
    payload = StrategyConfig(
        universe=UniverseDefinition(
            root=UniverseGroup(
                clauses=[
                    UniverseCondition(table="market_data", column="close", operator="gt", value=0),
                ]
            )
        ),
        rankingSchemaName="default-ranking",
        regimePolicy=RegimePolicy(),
    )
    assert payload.regimePolicy is not None
    assert payload.regimePolicy.modelName == "default-regime"


def test_ranking_schema_requires_groups() -> None:
    try:
        RankingSchemaConfig(groups=[])
    except Exception as exc:
        assert "groups" in str(exc)
    else:
        raise AssertionError("Expected validation failure for empty groups.")


def test_ranking_schema_accepts_group_payload() -> None:
    payload = RankingSchemaConfig(
        universeConfigName="core-universe",
        groups=[
            RankingGroup(
                name="quality",
                factors=[
                    {
                        "name": "pe",
                        "table": "market_data",
                        "column": "close",
                        "weight": 1.0,
                    }
                ],
            )
        ],
    )
    assert payload.groups[0].name == "quality"


def test_ui_runtime_config_defaults_to_api_root() -> None:
    config = UiRuntimeConfig()
    assert config.apiBaseUrl == "/api"
    assert config.oidcScopes == []
    assert config.oidcAudience == []


def test_ui_runtime_config_normalizes_string_scopes() -> None:
    config = UiRuntimeConfig(
        oidcScopes="api://asset-allocation-api/user_impersonation openid",
        oidcAudience="asset-allocation-api,asset-allocation-jobs",
    )
    assert config.oidcScopes == ["api://asset-allocation-api/user_impersonation", "openid"]
    assert config.oidcAudience == ["asset-allocation-api", "asset-allocation-jobs"]


def test_regime_snapshot_and_model_config_validate() -> None:
    snapshot = RegimeSnapshot(
        as_of_date="2026-03-07",
        effective_from_date="2026-03-10",
        model_name="default-regime",
        model_version=2,
        regime_code="trending_bull",
        regime_status="confirmed",
        halt_flag=False,
    )
    config = RegimeModelConfig()
    assert snapshot.model_version == 2
    assert config.highVolEnterThreshold == 28.0


def test_backtest_claim_request_accepts_optional_execution_name() -> None:
    payload = BacktestClaimRequest(executionName="backtest-job-01")
    assert payload.executionName == "backtest-job-01"


def test_shared_path_rules_are_stable() -> None:
    assert DataPaths.get_gold_finance_bucket_path("Balance Sheet", "a") == "finance/balance_sheet/buckets/A"
    assert bucket_letter("1msft") == "M"
