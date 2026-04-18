from __future__ import annotations

from asset_allocation_contracts.backtest import (
    BacktestClaimRequest,
    BacktestCompleteRequest,
    BacktestReconcileResponse,
    BacktestResultMetadata,
    RollingMetricPointResponse,
    RollingMetricsResponse,
    RunRecordResponse,
    TimeseriesPointResponse,
    TimeseriesResponse,
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


def test_backtest_result_metadata_and_response_schema() -> None:
    metadata = BacktestResultMetadata(
        results_schema_version=2,
        bar_size="1d",
        periods_per_year=252,
        strategy_scope="portfolio",
    )
    schema = TimeseriesResponse.model_json_schema()

    assert metadata.results_schema_version == 2
    assert metadata.bar_size == "1d"
    assert schema["properties"]["metadata"]["default"] is None
    assert schema["$defs"]["BacktestResultMetadata"]["properties"]["results_schema_version"]["default"] == 2


def test_timeseries_point_response_supports_period_return_and_daily_return_compatibility() -> None:
    from_daily = TimeseriesPointResponse.model_validate(
        {
            "date": "2026-03-08",
            "portfolio_value": 101.5,
            "drawdown": 0.02,
            "daily_return": 0.015,
        }
    )
    from_period = TimeseriesPointResponse.model_validate(
        {
            "date": "2026-03-09",
            "portfolio_value": 102.0,
            "drawdown": 0.01,
            "period_return": 0.02,
        }
    )
    schema = TimeseriesPointResponse.model_json_schema()

    assert from_daily.period_return == 0.015
    assert from_period.period_return == 0.02
    assert from_daily.model_dump()["daily_return"] == 0.015
    assert from_period.model_dump()["daily_return"] == 0.02
    assert schema["properties"]["daily_return"]["deprecated"] is True
    assert "period_return" in schema["properties"]


def test_rolling_metric_point_response_supports_window_periods_and_legacy_window_days() -> None:
    from_days = RollingMetricPointResponse.model_validate(
        {
            "date": "2026-03-08",
            "window_days": 63,
            "rolling_return": 0.12,
        }
    )
    from_periods = RollingMetricPointResponse.model_validate(
        {
            "date": "2026-03-09",
            "window_periods": 21,
            "rolling_return": 0.08,
        }
    )
    schema = RollingMetricPointResponse.model_json_schema()

    assert from_days.window_periods == 63
    assert from_periods.window_periods == 21
    assert from_days.model_dump()["window_days"] == 63
    assert from_periods.model_dump()["window_days"] == 21
    assert schema["properties"]["window_days"]["deprecated"] is True
    assert "window_periods" in schema["properties"]


def test_backtest_response_metadata_attaches_to_timeseries_and_rolling_metrics() -> None:
    metadata = BacktestResultMetadata(
        results_schema_version=2,
        bar_size="1d",
        periods_per_year=252,
        strategy_scope="strategy",
    )
    timeseries = TimeseriesResponse(metadata=metadata, points=[], total_points=0, truncated=False)
    rolling_metrics = RollingMetricsResponse(metadata=metadata, points=[], total_points=0, truncated=True)

    assert timeseries.metadata is metadata
    assert rolling_metrics.metadata is metadata


def test_shared_path_rules_are_stable() -> None:
    assert DataPaths.get_gold_finance_bucket_path("Balance Sheet", "a") == "finance/balance_sheet/buckets/A"
    assert bucket_letter("1msft") == "M"
