from __future__ import annotations

from pydantic import TypeAdapter
from asset_allocation_contracts.ai_chat import AiChatRequest, AiChatStreamEvent
from asset_allocation_contracts.backtest import (
    BacktestClaimRequest,
    BacktestCompleteRequest,
    BacktestSummary,
    ClosedPositionResponse,
    BacktestReconcileResponse,
    BacktestResultMetadata,
    RollingMetricPointResponse,
    RollingMetricsResponse,
    RunRecordResponse,
    RunStatusResponse,
    TradeResponse,
    TimeseriesPointResponse,
    TimeseriesResponse,
)
from asset_allocation_contracts.paths import DataPaths, bucket_letter
from asset_allocation_contracts.ranking import RankingGroup, RankingSchemaConfig
from asset_allocation_contracts.regime import RegimeModelConfig, RegimePolicy, RegimeSnapshot
from asset_allocation_contracts.symbol_enrichment import (
    SymbolCleanupRunSummary,
    SymbolEnrichmentResolveRequest,
    SymbolEnrichmentResolveResponse,
    SymbolEnrichmentSummaryResponse,
    SymbolEnrichmentSymbolDetailResponse,
    SymbolProfileCurrent,
    SymbolProfileOverride,
)
from asset_allocation_contracts.strategy import (
    StrategyConfig,
    UniverseCatalogResponse,
    UNIVERSE_FIELD_DEFINITIONS,
    UniverseCondition,
    UniverseDefinition,
    UniverseGroup,
    UniversePreviewResponse,
)
from asset_allocation_contracts.ui_config import AuthSessionStatus, UiRuntimeConfig


def test_strategy_contract_accepts_regime_policy() -> None:
    payload = StrategyConfig(
        universe=UniverseDefinition(
            root=UniverseGroup(
                clauses=[
                    UniverseCondition(field="market.close", operator="gt", value=0),
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


def test_universe_condition_uses_governed_field_catalog() -> None:
    condition = UniverseCondition(field="security.sector", operator="in", values=["technology"])

    assert condition.field == "security.sector"
    assert any(field.id == "security.sector" for field in UNIVERSE_FIELD_DEFINITIONS)


def test_universe_condition_rejects_unknown_field() -> None:
    try:
        UniverseCondition(field="market_data.close", operator="gt", value=0)
    except Exception as exc:
        assert "field" in str(exc)
    else:
        raise AssertionError("Expected validation failure for unknown universe field.")


def test_universe_catalog_response_uses_governed_field_definitions() -> None:
    payload = UniverseCatalogResponse(fields=list(UNIVERSE_FIELD_DEFINITIONS[:2]))

    assert payload.source == "postgres_gold"
    assert payload.fields[0].id == "market.close"
    assert payload.fields[1].label == "Security Active Flag"


def test_universe_preview_response_uses_governed_field_ids() -> None:
    payload = UniversePreviewResponse(
        symbolCount=2,
        sampleSymbols=["AAPL", "MSFT"],
        fieldsUsed=["market.close", "quality.piotroski_f_score"],
    )

    assert payload.fieldsUsed == ["market.close", "quality.piotroski_f_score"]
    assert payload.warnings == []


def test_universe_preview_response_rejects_unknown_field_ids() -> None:
    try:
        UniversePreviewResponse(symbolCount=1, sampleSymbols=["AAPL"], fieldsUsed=["market_data.close"])
    except Exception as exc:
        assert "fieldsUsed" in str(exc)
    else:
        raise AssertionError("Expected validation failure for unknown preview field id.")


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


def test_backtest_run_status_response_accepts_frozen_pin_metadata() -> None:
    payload = RunStatusResponse(
        run_id="run-123",
        status="completed",
        submitted_at="2026-03-08T00:00:00Z",
        completed_at="2026-03-08T01:00:00Z",
        strategy_name="quality-trend",
        strategy_version=4,
        bar_size="5m",
        execution_name="backtest-exec-01",
        results_ready_at="2026-03-08T01:05:00Z",
        results_schema_version=4,
        pins={
            "strategyName": "quality-trend",
            "strategyVersion": 4,
            "rankingSchemaName": "quality-momentum",
            "rankingSchemaVersion": 7,
            "universeName": "large-cap-quality",
            "universeVersion": 5,
            "regimeModelName": "default-regime",
            "regimeModelVersion": 1,
        },
    )

    assert payload.strategy_version == 4
    assert payload.bar_size == "5m"
    assert payload.results_schema_version == 4
    assert payload.pins is not None
    assert payload.pins.rankingSchemaVersion == 7


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
        results_schema_version=4,
        bar_size="1d",
        periods_per_year=252,
        strategy_scope="portfolio",
    )
    schema = TimeseriesResponse.model_json_schema()

    assert metadata.results_schema_version == 4
    assert metadata.bar_size == "1d"
    assert schema["properties"]["metadata"]["default"] is None
    assert schema["$defs"]["BacktestResultMetadata"]["properties"]["results_schema_version"]["default"] == 4


def test_ai_chat_contracts_validate_and_discriminate_stream_events() -> None:
    request = AiChatRequest(prompt="Summarize AAPL.")
    adapter = TypeAdapter(AiChatStreamEvent)
    completed = adapter.validate_python(
        {
            "sequenceNumber": 1,
            "event": "completed",
            "data": {
                "requestId": "req-1",
                "model": "gpt-5.4",
                "outputText": "Apple summary",
                "reasoningSummary": "",
            },
        }
    )

    assert request.prompt == "Summarize AAPL."
    assert completed.event == "completed"
    assert completed.data.outputText == "Apple summary"


def test_symbol_enrichment_contracts_validate_current_profile_and_response() -> None:
    resolve_request = SymbolEnrichmentResolveRequest(
        symbol="AAPL",
        requestedFields=["sector_norm", "industry_norm", "issuer_summary_short"],
        providerFacts={"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"},
    )
    resolve_response = SymbolEnrichmentResolveResponse(
        symbol="AAPL",
        profile={
            "sector_norm": "Technology",
            "industry_norm": "Technology Hardware, Storage & Peripherals",
            "issuer_summary_short": "Consumer hardware and services company.",
        },
        model="gpt-5.4",
        confidence=0.92,
    )
    current = SymbolProfileCurrent(
        symbol="AAPL",
        sourceKind="ai",
        validationStatus="accepted",
        sector_norm="Technology",
        marketCapBucket="mega",
        avgDollarVolume20d=125_000_000.0,
    )

    assert resolve_request.providerFacts.symbol == "AAPL"
    assert resolve_response.profile.industry_norm is not None
    assert current.marketCapBucket == "mega"


def test_symbol_enrichment_operator_contracts_default_lists() -> None:
    detail = SymbolEnrichmentSymbolDetailResponse(
        providerFacts={"symbol": "AAPL"},
        currentProfile={"symbol": "AAPL", "sourceKind": "provider"},
    )
    summary = SymbolEnrichmentSummaryResponse()
    override = SymbolProfileOverride(symbol="AAPL", fieldName="sector_norm", value="Technology", isLocked=True)
    run = SymbolCleanupRunSummary(runId="run-1", status="queued")

    assert detail.overrides == []
    assert summary.backlogCount == 0
    assert override.isLocked is True
    assert run.mode == "fill_missing"


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
    assert from_period.model_dump()["trade_count"] is None
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
        results_schema_version=4,
        bar_size="1d",
        periods_per_year=252,
        strategy_scope="strategy",
    )
    timeseries = TimeseriesResponse(metadata=metadata, points=[], total_points=0, truncated=False)
    rolling_metrics = RollingMetricsResponse(metadata=metadata, points=[], total_points=0, truncated=True)

    assert timeseries.metadata is metadata
    assert rolling_metrics.metadata is metadata


def test_backtest_summary_supports_additive_v3_and_v4_fields() -> None:
    payload = BacktestSummary.model_validate(
        {
            "gross_total_return": 0.15,
            "gross_annualized_return": 0.35,
            "total_commission": 25.0,
            "total_slippage_cost": 10.0,
            "total_transaction_cost": 35.0,
            "cost_drag_bps": 35.0,
            "avg_gross_exposure": 0.92,
            "avg_net_exposure": 0.88,
            "sortino_ratio": 1.8,
            "calmar_ratio": 1.4,
            "closed_positions": 12,
            "winning_positions": 7,
            "losing_positions": 5,
            "hit_rate": 7 / 12,
            "avg_win_pnl": 220.0,
            "avg_loss_pnl": -140.0,
            "avg_win_return": 0.08,
            "avg_loss_return": -0.04,
            "payoff_ratio": 1.57,
            "profit_factor": 1.92,
            "expectancy_pnl": 68.0,
            "expectancy_return": 0.021,
        }
    )

    assert payload.gross_total_return == 0.15
    assert payload.total_transaction_cost == 35.0
    assert payload.closed_positions == 12
    assert payload.expectancy_return == 0.021


def test_trade_and_closed_position_contracts_support_position_lifecycle_fields() -> None:
    trade = TradeResponse.model_validate(
        {
            "execution_date": "2026-03-10T14:35:00Z",
            "symbol": "MSFT",
            "quantity": 10.0,
            "price": 100.0,
            "notional": 1000.0,
            "commission": 1.0,
            "slippage_cost": 0.5,
            "cash_after": 98998.5,
            "position_id": "pos-123",
            "trade_role": "entry",
        }
    )
    closed = ClosedPositionResponse.model_validate(
        {
            "position_id": "pos-123",
            "symbol": "MSFT",
            "opened_at": "2026-03-10T14:35:00Z",
            "closed_at": "2026-03-12T14:35:00Z",
            "holding_period_bars": 8,
            "average_cost": 101.0,
            "exit_price": 108.0,
            "max_quantity": 25.0,
            "resize_count": 2,
            "realized_pnl": 160.0,
            "realized_return": 0.063,
            "total_commission": 3.0,
            "total_slippage_cost": 1.5,
            "total_transaction_cost": 4.5,
            "exit_reason": "take_profit_fixed",
            "exit_rule_id": "tp-1",
        }
    )

    assert trade.trade_role == "entry"
    assert trade.position_id == "pos-123"
    assert closed.realized_return == 0.063
    assert closed.exit_rule_id == "tp-1"


def test_shared_path_rules_are_stable() -> None:
    assert DataPaths.get_gold_finance_bucket_path("Balance Sheet", "a") == "finance/balance_sheet/buckets/A"
    assert bucket_letter("1msft") == "M"
