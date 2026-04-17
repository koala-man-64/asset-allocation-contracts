from __future__ import annotations

from asset_allocation_contracts.backtest import (
    BacktestClaimRequest,
    BacktestCompleteRequest,
    BacktestReconcileResponse,
    RunRecordResponse,
)
from asset_allocation_contracts.paths import DataPaths, bucket_letter
from asset_allocation_contracts.ranking import RankingGroup, RankingSchemaConfig
from asset_allocation_contracts.regime import RegimeModelConfig, RegimePolicy, RegimeSnapshot
from asset_allocation_contracts.strategy import StrategyConfig, UniverseCondition, UniverseDefinition, UniverseGroup
from asset_allocation_contracts.ui_config import AuthSessionStatus, UiRuntimeConfig


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
    assert config.oidcPostLogoutRedirectUri is None


def test_ui_runtime_config_normalizes_string_scopes() -> None:
    config = UiRuntimeConfig(
        oidcScopes="api://asset-allocation-api/user_impersonation openid",
        oidcAudience="asset-allocation-api,asset-allocation-jobs",
    )
    assert config.oidcScopes == ["api://asset-allocation-api/user_impersonation", "openid"]
    assert config.oidcAudience == ["asset-allocation-api", "asset-allocation-jobs"]


def test_ui_runtime_config_schema_includes_post_logout_redirect_uri() -> None:
    schema = UiRuntimeConfig.model_json_schema()
    post_logout_schema = schema["properties"]["oidcPostLogoutRedirectUri"]
    assert post_logout_schema["default"] is None
    assert post_logout_schema["title"] == "Oidcpostlogoutredirecturi"


def test_auth_session_status_defaults_and_schema() -> None:
    payload = AuthSessionStatus(authMode="oidc", subject="user-123")
    schema = AuthSessionStatus.model_json_schema()
    assert payload.displayName is None
    assert payload.username is None
    assert payload.requiredRoles == []
    assert payload.grantedRoles == []
    assert schema["required"] == ["authMode", "subject"]
    assert "requiredRoles" in schema["properties"]
    assert "grantedRoles" in schema["properties"]


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


def test_backtest_run_record_response_rejects_legacy_artifact_fields() -> None:
    try:
        RunRecordResponse(
            run_id="run-123",
            status="queued",
            submitted_at="2026-03-08T00:00:00Z",
            output_dir="/tmp/backtests",
        )
    except Exception as exc:
        assert "output_dir" in str(exc)
    else:
        raise AssertionError("Expected RunRecordResponse to reject legacy artifact fields.")


def test_backtest_complete_request_rejects_legacy_artifact_manifest_path() -> None:
    try:
        BacktestCompleteRequest(summary={"run_id": "run-123"}, artifactManifestPath="backtests/run-123")
    except Exception as exc:
        assert "artifactManifestPath" in str(exc)
    else:
        raise AssertionError("Expected BacktestCompleteRequest to reject artifactManifestPath.")


def test_backtest_reconcile_response_defaults_and_payload() -> None:
    payload = BacktestReconcileResponse(
        dispatchedCount=2,
        dispatchFailedCount=1,
        failedStaleRunningCount=1,
        skippedActiveCount=3,
        noActionCount=4,
        dispatchedRunIds=["run-a", "run-b"],
        dispatchFailedRunIds=["run-c"],
        failedRunIds=["run-d"],
    )
    assert payload.dispatchedCount == 2
    assert payload.dispatchFailedRunIds == ["run-c"]
    assert payload.failedRunIds == ["run-d"]


def test_shared_path_rules_are_stable() -> None:
    assert DataPaths.get_gold_finance_bucket_path("Balance Sheet", "a") == "finance/balance_sheet/buckets/A"
    assert bucket_letter("1msft") == "M"
