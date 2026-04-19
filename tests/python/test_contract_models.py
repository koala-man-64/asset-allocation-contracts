from __future__ import annotations

from pydantic import TypeAdapter

from asset_allocation_contracts.ai_chat import AiChatRequest, AiChatStreamEvent
from asset_allocation_contracts.backtest import (
    BacktestClaimRequest,
    BacktestCompleteRequest,
    BacktestLookupRequest,
    BacktestLookupResponse,
    BacktestResultLinks,
    BacktestRunRequest,
    BacktestRunResponse,
    BacktestSummary,
    BacktestStreamEvent,
    ClosedPositionResponse,
    BacktestReconcileResponse,
    BacktestResultMetadata,
    RollingMetricPointResponse,
    RollingMetricsResponse,
    RunRecordResponse,
    RunStatusResponse,
    StrategyReferenceInput,
    TradeResponse,
    TimeseriesPointResponse,
    TimeseriesResponse,
)
from asset_allocation_contracts.government_signals import (
    CongressTradeEvent,
    CongressTradeVersion,
    GovernmentContractEvent,
    GovernmentSignalAlert,
    GovernmentSignalIssuerSummaryResponse,
    GovernmentSignalMappingOverrideRequest,
    GovernmentSignalPortfolioExposureRequest,
    IssuerGovernmentSignalDaily,
)
from asset_allocation_contracts.intraday import (
    IntradayMonitorClaimResponse,
    IntradayMonitorCompleteRequest,
    IntradayMonitorEvent,
    IntradayMonitorRunSummary,
    IntradaySymbolStatus,
    IntradayWatchlistDetail,
    IntradayWatchlistUpsertRequest,
)
from asset_allocation_contracts.portfolio import (
    PortfolioAccount,
    PortfolioAccountUpsertRequest,
    PortfolioAlert,
    PortfolioAssignment,
    PortfolioLedgerEvent,
    PortfolioPosition,
    PortfolioRevision,
    PortfolioSleeveAllocation,
    PortfolioSnapshot,
    PortfolioUpsertRequest,
    RebalanceProposal,
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


def test_intraday_watchlist_upsert_normalizes_and_deduplicates_symbols() -> None:
    payload = IntradayWatchlistUpsertRequest(
        name="Large Cap Momentum",
        description="Operator-managed intraday names.",
        symbols=["aapl", " msft ", "AAPL"],
    )

    assert payload.symbols == ["AAPL", "MSFT"]
    assert payload.pollIntervalMinutes == 5
    assert payload.refreshCooldownMinutes == 15
    assert payload.marketSession == "us_equities_regular"


def test_intraday_monitor_claim_response_supports_nested_watchlist_contract() -> None:
    payload = IntradayMonitorClaimResponse(
        claimToken="claim-1",
        run=IntradayMonitorRunSummary(
            runId="run-1",
            watchlistId="watch-1",
            watchlistName="Tech Core",
            triggerKind="manual",
            status="claimed",
            forceRefresh=True,
            symbolCount=2,
        ),
        watchlist=IntradayWatchlistDetail(
            watchlistId="watch-1",
            name="Tech Core",
            description="operator list",
            enabled=True,
            symbolCount=2,
            symbols=["AAPL", "MSFT"],
        ),
        currentSymbolStatuses=[
            IntradaySymbolStatus(
                symbol="aapl",
                monitorStatus="observed",
                lastObservedPrice=213.42,
            )
        ],
    )

    assert payload.claimToken == "claim-1"
    assert payload.run is not None
    assert payload.run.forceRefresh is True
    assert payload.watchlist is not None
    assert payload.watchlist.symbols == ["AAPL", "MSFT"]
    assert payload.currentSymbolStatuses[0].symbol == "AAPL"


def test_intraday_monitor_complete_request_accepts_statuses_and_events() -> None:
    payload = IntradayMonitorCompleteRequest(
        claimToken="claim-1",
        symbolStatuses=[
            IntradaySymbolStatus(
                symbol="aapl",
                monitorStatus="refresh_queued",
                lastObservedPrice=213.42,
            )
        ],
        events=[
            IntradayMonitorEvent(
                eventType="snapshot_polled",
                severity="info",
                message="Fetched latest snapshot.",
                details={"source": "massive"},
            )
        ],
        refreshSymbols=["aapl", "msft", "AAPL"],
    )

    assert payload.symbolStatuses[0].symbol == "AAPL"
    assert payload.events[0].details["source"] == "massive"
    assert payload.refreshSymbols == ["AAPL", "MSFT"]


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


def test_strategy_reference_input_accepts_optional_version() -> None:
    payload = StrategyReferenceInput(strategyName="quality-trend")
    assert payload.strategyName == "quality-trend"
    assert payload.strategyVersion is None


def test_backtest_lookup_request_requires_exactly_one_strategy_input() -> None:
    payload = BacktestLookupRequest(
        strategyRef={"strategyName": "quality-trend", "strategyVersion": 4},
        startTs="2026-03-08T00:00:00Z",
        endTs="2026-03-09T00:00:00Z",
        barSize="1d",
        runName="lookup-smoke",
    )
    assert payload.strategyRef is not None
    assert payload.strategyConfig is None
    schema = BacktestLookupRequest.model_json_schema()
    assert schema["oneOf"] == [{"required": ["strategyRef"]}, {"required": ["strategyConfig"]}]

    for invalid_payload in (
        {
            "startTs": "2026-03-08T00:00:00Z",
            "endTs": "2026-03-09T00:00:00Z",
            "barSize": "1d",
        },
        {
            "strategyRef": {"strategyName": "quality-trend"},
            "strategyConfig": {
                "universeConfigName": "large-cap-quality",
                "rebalance": "weekly",
                "longOnly": True,
                "topN": 2,
                "lookbackWindow": 20,
                "holdingPeriod": 5,
                "costModel": "default",
                "rankingSchemaName": "quality",
                "intrabarConflictPolicy": "stop_first",
                "exits": [],
            },
            "startTs": "2026-03-08T00:00:00Z",
            "endTs": "2026-03-09T00:00:00Z",
            "barSize": "1d",
        },
    ):
        try:
            BacktestLookupRequest.model_validate(invalid_payload)
        except Exception as exc:
            assert "Exactly one of strategyRef or strategyConfig must be provided" in str(exc)
        else:
            raise AssertionError("Expected BacktestLookupRequest to enforce exactly one strategy input.")


def test_backtest_run_response_and_lookup_response_support_links_and_summary() -> None:
    run = RunStatusResponse(
        run_id="run-123",
        status="completed",
        submitted_at="2026-03-08T00:00:00Z",
        results_ready_at="2026-03-08T01:05:00Z",
        results_schema_version=4,
    )
    links = BacktestResultLinks(
        summaryUrl="/api/backtests/run-123/summary",
        metricsTimeseriesUrl="/api/backtests/run-123/metrics/timeseries",
        metricsRollingUrl="/api/backtests/run-123/metrics/rolling",
        tradesUrl="/api/backtests/run-123/trades",
        closedPositionsUrl="/api/backtests/run-123/positions/closed",
    )
    summary = BacktestSummary(total_return=0.12)

    lookup = BacktestLookupResponse(
        found=True,
        state="completed",
        run=run,
        result=summary,
        links=links,
    )
    run_response = BacktestRunResponse(
        run=run,
        created=True,
        reusedInflight=False,
        streamUrl="/api/backtests/run-123/events",
    )

    assert lookup.links is not None
    assert lookup.links.closedPositionsUrl.endswith("/positions/closed")
    assert lookup.result is not None
    assert lookup.result.total_return == 0.12
    assert run_response.streamUrl.endswith("/events")


def test_backtest_run_request_accepts_inline_strategy_config() -> None:
    payload = BacktestRunRequest(
        strategyConfig={
            "universeConfigName": "large-cap-quality",
            "rebalance": "weekly",
            "longOnly": True,
            "topN": 2,
            "lookbackWindow": 20,
            "holdingPeriod": 5,
            "costModel": "default",
            "rankingSchemaName": "quality",
            "intrabarConflictPolicy": "stop_first",
            "exits": [],
        },
        startTs="2026-03-08T00:00:00Z",
        endTs="2026-03-09T00:00:00Z",
        barSize="1d",
        runName="run-smoke",
    )
    assert payload.strategyConfig is not None
    assert payload.strategyRef is None


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


def test_backtest_stream_event_supports_terminal_payload() -> None:
    payload = BacktestStreamEvent(
        event="completed",
        run={
            "run_id": "run-123",
            "status": "completed",
            "submitted_at": "2026-03-08T00:00:00Z",
            "completed_at": "2026-03-08T01:00:00Z",
            "results_ready_at": "2026-03-08T01:05:00Z",
            "results_schema_version": 4,
        },
        summary={"total_return": 0.12},
        metadata={
            "results_schema_version": 4,
            "bar_size": "1d",
            "periods_per_year": 252,
            "strategy_scope": "long_only",
        },
        links={
            "summaryUrl": "/api/backtests/run-123/summary",
            "metricsTimeseriesUrl": "/api/backtests/run-123/metrics/timeseries",
            "metricsRollingUrl": "/api/backtests/run-123/metrics/rolling",
            "tradesUrl": "/api/backtests/run-123/trades",
            "closedPositionsUrl": "/api/backtests/run-123/positions/closed",
        },
    )

    assert payload.event == "completed"
    assert payload.summary is not None
    assert payload.summary.total_return == 0.12
    assert payload.links is not None
    assert payload.metadata is not None
    assert payload.metadata.periods_per_year == 252


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


def test_portfolio_revision_requires_enabled_weights_to_sum_to_one() -> None:
    revision = PortfolioRevision(
        portfolioName="core-balanced",
        version=3,
        allocations=[
            PortfolioSleeveAllocation(
                sleeveId="quality-core",
                sleeveName="Quality Core",
                strategy={"strategyName": "quality-trend", "strategyVersion": 4},
                targetWeight=0.6,
            ),
            PortfolioSleeveAllocation(
                sleeveId="defensive",
                sleeveName="Defensive",
                strategy={"strategyName": "defensive-value", "strategyVersion": 2},
                targetWeight=0.4,
                minWeight=0.2,
                maxWeight=0.5,
            ),
        ],
    )

    assert revision.portfolioName == "core-balanced"
    assert revision.allocations[0].strategy.strategyVersion == 4

    try:
        PortfolioRevision(
            portfolioName="broken-balanced",
            version=1,
            allocations=[
                PortfolioSleeveAllocation(
                    sleeveId="only-sleeve",
                    strategy={"strategyName": "quality-trend", "strategyVersion": 4},
                    targetWeight=0.8,
                )
            ],
        )
    except Exception as exc:
        assert "sum to 1.0" in str(exc)
    else:
        raise AssertionError("Expected revision validation failure when weights do not sum to 1.0.")


def test_portfolio_account_defaults_capture_internal_model_managed_scope() -> None:
    account = PortfolioAccount(
        accountId="acct-001",
        name="Core Long Only",
        baseCurrency="usd",
        inceptionDate="2026-01-02",
        mandate="Internal model sleeve account",
    )
    request = PortfolioAccountUpsertRequest(
        name="Core Long Only",
        baseCurrency="usd",
        inceptionDate="2026-01-02",
        openingCash=1_000_000,
    )

    assert account.mode == "internal_model_managed"
    assert account.accountingDepth == "position_level"
    assert account.cadenceMode == "strategy_native"
    assert account.baseCurrency == "USD"
    assert request.openingCash == 1_000_000


def test_portfolio_ledger_event_separates_cash_and_trade_shapes() -> None:
    deposit = PortfolioLedgerEvent(
        eventId="evt-001",
        accountId="acct-001",
        effectiveAt="2026-01-02T15:30:00Z",
        eventType="deposit",
        currency="usd",
        cashAmount=50_000,
        description="Additional funding",
    )
    trade = PortfolioLedgerEvent(
        eventId="evt-002",
        accountId="acct-001",
        effectiveAt="2026-01-03T15:30:00Z",
        eventType="rebalance_buy",
        currency="USD",
        cashAmount=-10_050,
        symbol="msft",
        quantity=100,
        price=100,
        commission=25,
        slippageCost=25,
    )

    assert deposit.cashAmount == 50_000
    assert deposit.currency == "USD"
    assert trade.symbol == "MSFT"
    assert trade.commission == 25

    try:
        PortfolioLedgerEvent(
            eventId="evt-003",
            accountId="acct-001",
            effectiveAt="2026-01-04T15:30:00Z",
            eventType="fee",
            currency="USD",
            cashAmount=-10,
            symbol="AAPL",
        )
    except Exception as exc:
        assert "does not accept symbol" in str(exc)
    else:
        raise AssertionError("Expected fee event validation failure when symbol is provided.")


def test_portfolio_snapshot_and_rebalance_proposal_capture_monitoring_contracts() -> None:
    assignment = PortfolioAssignment(
        assignmentId="asg-001",
        accountId="acct-001",
        accountVersion=2,
        portfolioName="core-balanced",
        portfolioVersion=3,
        effectiveFrom="2026-01-02",
        status="active",
    )
    snapshot = PortfolioSnapshot(
        accountId="acct-001",
        accountName="Core Long Only",
        asOf="2026-03-31",
        nav=1_025_000,
        cash=25_000,
        grossExposure=1.0,
        netExposure=1.0,
        sinceInceptionPnl=25_000,
        sinceInceptionReturn=0.025,
        currentDrawdown=0.03,
        openAlertCount=1,
        activeAssignment=assignment,
        freshness=[{"domain": "valuation", "state": "fresh"}],
        slices=[
            {
                "asOf": "2026-03-31",
                "sleeveId": "quality-core",
                "strategyName": "quality-trend",
                "strategyVersion": 4,
                "targetWeight": 0.6,
                "actualWeight": 0.58,
                "marketValue": 594_500,
            }
        ],
    )
    proposal = RebalanceProposal(
        proposalId="rb-001",
        accountId="acct-001",
        asOf="2026-03-31",
        portfolioName="core-balanced",
        portfolioVersion=3,
        warnings=["Sector overlap elevated"],
        trades=[
            {
                "sleeveId": "quality-core",
                "symbol": "MSFT",
                "side": "buy",
                "quantity": 25,
                "estimatedPrice": 101.5,
                "estimatedNotional": 2_537.5,
            }
        ],
    )
    position = PortfolioPosition(
        asOf="2026-03-31",
        symbol="msft",
        quantity=125,
        marketValue=12_687.5,
        weight=0.012375,
        averageCost=97.0,
        lastPrice=101.5,
        contributors=[
            {
                "sleeveId": "quality-core",
                "strategyName": "quality-trend",
                "strategyVersion": 4,
                "quantity": 125,
                "marketValue": 12_687.5,
                "weight": 0.012375,
            }
        ],
    )
    alert = PortfolioAlert(
        alertId="alt-001",
        accountId="acct-001",
        severity="warning",
        code="allocation_drift",
        title="Allocation drift is above policy",
        detectedAt="2026-03-31T21:00:00Z",
    )
    upsert = PortfolioUpsertRequest(
        name="core-balanced",
        allocations=[
            {
                "sleeveId": "quality-core",
                "strategy": {"strategyName": "quality-trend", "strategyVersion": 4},
                "targetWeight": 0.6,
            },
            {
                "sleeveId": "defensive",
                "strategy": {"strategyName": "defensive-value", "strategyVersion": 2},
                "targetWeight": 0.4,
            },
        ],
    )

    assert snapshot.activeAssignment is not None
    assert snapshot.slices[0].actualWeight == 0.58
    assert proposal.trades[0].side == "buy"
    assert position.symbol == "MSFT"
    assert alert.status == "open"
    assert upsert.allocations[1].strategy.strategyVersion == 2


def test_government_signal_congress_trade_validates_amount_bounds() -> None:
    payload = CongressTradeEvent(
        event_id="house-123",
        source_name="quiver",
        source_event_key="house-123",
        member_name="Member Example",
        chamber="house",
        committee_names=["Armed Services"],
        traded_at="2026-04-15T14:30:00Z",
        transaction_type="purchase",
        asset_name="Lockheed Martin Corporation",
        issuer_name="Lockheed Martin Corporation",
        issuer_ticker="LMT",
        amount_lower_usd=1_000,
        amount_upper_usd=15_000,
    )

    assert payload.issuer_ticker == "LMT"
    assert payload.mapping_status == "pending_review"

    try:
        CongressTradeEvent(
            event_id="house-124",
            source_name="quiver",
            source_event_key="house-124",
            member_name="Member Example",
            committee_names=[],
            traded_at="2026-04-15T14:30:00Z",
            transaction_type="purchase",
            asset_name="Lockheed Martin Corporation",
            amount_lower_usd=15_000,
            amount_upper_usd=1_000,
        )
    except Exception as exc:
        assert "amount_upper_usd" in str(exc)
    else:
        raise AssertionError("Expected congress amount bounds validation failure.")


def test_government_signal_contract_and_summary_models_accept_expected_payloads() -> None:
    contract_event = GovernmentContractEvent(
        event_id="award-1",
        source_name="usaspending",
        source_event_key="award-1",
        event_type="award",
        event_at="2026-04-16T00:00:00Z",
        recipient_name="Lockheed Martin Corporation",
        recipient_ticker="LMT",
        awarding_agency="Department of Defense",
        title="Missile systems support",
        award_amount_usd=125_000_000,
        obligation_delta_usd=125_000_000,
    )
    daily = IssuerGovernmentSignalDaily(as_of_date="2026-04-16", symbol="LMT")
    summary = GovernmentSignalIssuerSummaryResponse(
        symbol="LMT",
        as_of_date="2026-04-16",
        issuer_daily=daily,
        recent_congress_trades=[],
        recent_contract_events=[contract_event],
        active_alerts=[
            GovernmentSignalAlert(
                alert_id="alert-1",
                symbol="LMT",
                as_of_date="2026-04-16",
                alert_type="contract_event",
                severity="high",
                title="Large defense award",
                summary="Lockheed received a large new award.",
            )
        ],
    )
    version = CongressTradeVersion(
        version_id="v1",
        event_id="house-123",
        version_seq=1,
        version_kind="initial",
        version_observed_at="2026-04-16T00:00:00Z",
        event=CongressTradeEvent(
            event_id="house-123",
            source_name="quiver",
            source_event_key="house-123",
            member_name="Member Example",
            committee_names=[],
            traded_at="2026-04-15T14:30:00Z",
            transaction_type="purchase",
            asset_name="Lockheed Martin Corporation",
        ),
    )

    assert summary.recent_contract_events[0].recipient_ticker == "LMT"
    assert version.event.event_id == "house-123"


def test_government_signal_mapping_override_and_portfolio_request_validate() -> None:
    payload = GovernmentSignalMappingOverrideRequest(action="map", symbol="RTX", reason="Matched issuer")
    exposure = GovernmentSignalPortfolioExposureRequest(
        holdings=[{"symbol": "LMT", "market_value": 100_000, "portfolio_weight": 0.1}]
    )

    assert payload.symbol == "RTX"
    assert exposure.holdings[0].symbol == "LMT"

    try:
        GovernmentSignalMappingOverrideRequest(action="map")
    except Exception as exc:
        assert "symbol is required" in str(exc)
    else:
        raise AssertionError("Expected map action to require a symbol.")

    try:
        GovernmentSignalPortfolioExposureRequest(holdings=[])
    except Exception as exc:
        assert "holdings must not be empty" in str(exc)
    else:
        raise AssertionError("Expected non-empty holdings validation failure.")


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
