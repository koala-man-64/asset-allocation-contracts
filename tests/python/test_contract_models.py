from __future__ import annotations

from pydantic import TypeAdapter

from asset_allocation_contracts.ai_chat import AiChatRequest, AiChatStreamEvent
from asset_allocation_contracts.backtest import (
    BacktestClaimRequest,
    BacktestCompleteRequest,
    BacktestDataQualityEvent,
    BacktestDataQualityEventListResponse,
    BacktestLookupRequest,
    BacktestLookupResponse,
    BacktestPolicyEvent,
    BacktestPolicyEventListResponse,
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
from asset_allocation_contracts.broker_accounts import (
    AcknowledgeBrokerAlertRequest,
    BrokerAccountAllocationUpdateRequest,
    BrokerAccountActionResponse,
    BrokerAccountConfiguration,
    BrokerAccountDetail,
    BrokerAccountListResponse,
    BrokerAccountOnboardingCandidate,
    BrokerAccountOnboardingCandidateListResponse,
    BrokerAccountOnboardingRequest,
    BrokerAccountOnboardingResponse,
    BrokerAccountSummary,
    BrokerAccountConfigurationAuditRecord,
    BrokerCapabilityFlags,
    BrokerConnectionHealth,
    BrokerStrategyAllocationSummary,
    BrokerTradingPolicy,
    BrokerTradingPolicyUpdateRequest,
    BrokerSyncRun,
    PauseBrokerSyncRequest,
    ReconnectBrokerAccountRequest,
    RefreshBrokerAccountRequest,
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
    IntradayWatchlistSymbolAppendRequest,
    IntradayWatchlistSymbolAppendResponse,
    IntradayWatchlistUpsertRequest,
)
from asset_allocation_contracts.job_metadata import RuntimeJobMetadata
from asset_allocation_contracts.portfolio import (
    PortfolioAccount,
    PortfolioAccountUpsertRequest,
    PortfolioAlert,
    PortfolioAssignment,
    PortfolioForecastResponse,
    PortfolioLedgerEvent,
    PortfolioNextRebalanceResponse,
    PortfolioPosition,
    PortfolioRevision,
    PortfolioSleeveAllocation,
    PortfolioSnapshot,
    PortfolioUpsertRequest,
    RebalanceProposal,
)
from asset_allocation_contracts.paths import DataPaths, bucket_letter
from asset_allocation_contracts.ranking import RankingGroup, RankingSchemaConfig
from asset_allocation_contracts.regime import (
    CANONICAL_DEFAULT_REGIME_VERSION,
    RegimePolicy,
    RegimePolicyConfig,
    RegimePolicyConfigDetailResponse,
    RegimePolicyConfigSummary,
    RegimePolicyConfigRevision,
    RegimeSignal,
    RegimeSnapshot,
    canonical_default_regime_config_errors,
    canonical_default_regime_model_config,
    validate_canonical_default_regime_config,
)
from asset_allocation_contracts.results import ResultsReconcileRequest, ResultsReconcileResponse
from asset_allocation_contracts.strategy_publication import (
    RegimePublicationReconcileMetadata,
    StrategyPublicationReconcileSignalRequest,
)
from asset_allocation_contracts.symbol_enrichment import (
    SymbolCleanupRunSummary,
    SymbolEnrichmentResolveRequest,
    SymbolEnrichmentResolveResponse,
    SymbolEnrichmentSummaryResponse,
    SymbolEnrichmentSymbolDetailResponse,
    SymbolProfileCurrent,
    SymbolProfileOverride,
)
from asset_allocation_contracts.symbol_identity import (
    SYMBOL_ALIAS_RULESET_VERSION,
    SYMBOL_ALIAS_RULES,
    SymbolResolutionResult,
)
from asset_allocation_contracts.strategy import (
    ConfigIdentity,
    ConfigReference,
    ConfigRevisionReference,
    ExitPolicyPreset,
    ExitRuleSetConfig,
    ExitRuleSetDetailResponse,
    ExitRuleSetRevision,
    ExitRuleSetSummary,
    RankingSchemaPreset,
    RebalancePolicy,
    RebalancePolicyPreset,
    RegimePolicyPreset,
    RiskPolicyConfigDetailResponse,
    RiskPolicyConfigRevision,
    RiskPolicyConfigSummary,
    StrategyComponentRefs,
    StrategyRiskPolicy,
    StrategyRiskPolicyPreset,
    StrategyPositionPolicy,
    StrategyRiskProfileConfig,
    StrategyRiskProfileDetail,
    StrategyRiskProfileSummary,
    StrategyConfig,
    UniverseConfigPreset,
    UniverseCatalogResponse,
    UNIVERSE_FIELD_DEFINITIONS,
    UniverseCondition,
    UniverseDefinition,
    UniverseGroup,
    UniversePreviewResponse,
)
from asset_allocation_contracts.trade_desk import TradeOrderPreviewRequest
from asset_allocation_contracts.ui_config import (
    AuthSessionStatus,
    PasswordAuthSessionRequest,
    UiRuntimeConfig,
)


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
    assert payload.regimePolicy.mode == "observe_only"


def test_strategy_config_accepts_pinned_configuration_references_with_resolved_snapshots() -> None:
    payload = StrategyConfig(
        universeConfigName="large-cap-quality",
        universeConfigVersion=4,
        rankingSchemaName="quality-momentum",
        rankingSchemaVersion=7,
        regimePolicyConfigName="observe-default",
        regimePolicyConfigVersion=2,
        regimePolicy={"modelName": "default-regime", "modelVersion": 3, "mode": "observe_only"},
        riskPolicyName="balanced-risk",
        riskPolicyVersion=5,
        strategyRiskPolicy={
            "scope": "strategy",
            "stopLoss": {
                "thresholdPct": 8,
                "action": "reduce_exposure",
                "reductionPct": 50,
            },
        },
        exitRuleSetName="standard-exits",
        exitRuleSetVersion=6,
        exits=[{"id": "stop-8", "type": "stop_loss_fixed", "value": 0.08}],
    )

    assert payload.universeConfigVersion == 4
    assert payload.rankingSchemaVersion == 7
    assert payload.regimePolicyConfigName == "observe-default"
    assert payload.regimePolicy is not None
    assert payload.regimePolicy.modelVersion == 3
    assert payload.riskPolicyName == "balanced-risk"
    assert payload.strategyRiskPolicy is not None
    assert payload.exitRuleSetName == "standard-exits"
    assert payload.exits[0].priority == 0


def test_strategy_config_rejects_version_without_matching_name() -> None:
    try:
        StrategyConfig(universeConfigName="core", riskPolicyVersion=2)
    except Exception as exc:
        assert "riskPolicyVersion" in str(exc)
        assert "matching config name" in str(exc)
    else:
        raise AssertionError("Expected pinned version without config name to fail validation.")


def test_config_revision_reference_normalizes_name() -> None:
    ref = ConfigRevisionReference(name="  core-risk  ", version=3)

    assert ref.name == "core-risk"
    assert ref.version == 3


def test_strategy_config_accepts_component_refs_as_canonical_pins() -> None:
    payload = StrategyConfig(
        componentRefs={
            "universe": {"name": "us-large-liquid", "version": 1},
            "ranking": {"name": "quality-momentum", "version": 2},
            "rebalance": {"name": "monthly-last-trading-day", "version": 1},
            "regimePolicy": {"name": "observe-only-default", "version": 1},
            "riskPolicy": {"name": "balanced-long-only", "version": 1},
            "exitPolicy": {"name": "rank-decay-exit", "version": 1},
        }
    )

    assert isinstance(payload.componentRefs, StrategyComponentRefs)
    assert payload.componentRefs.universe is not None
    assert payload.componentRefs.universe.name == "us-large-liquid"
    assert payload.componentRefs.ranking is not None
    assert payload.componentRefs.ranking.version == 2


def test_config_reference_requires_integer_version() -> None:
    try:
        ConfigReference(name="us-large-liquid", version="v1")
    except Exception as exc:
        assert "version" in str(exc)
    else:
        raise AssertionError("Expected non-integer config version to fail validation.")


def test_config_reference_rejects_blank_name() -> None:
    try:
        ConfigReference(name="   ", version=1)
    except Exception as exc:
        assert "name" in str(exc)
    else:
        raise AssertionError("Expected blank config reference name to fail validation.")


def test_reusable_preset_wrappers_forbid_unknown_fields() -> None:
    identity = {
        "name": "starter",
        "version": 1,
        "status": "draft",
        "description": "Starter preset.",
        "intendedUse": "research",
    }
    universe = {
        "root": {
            "clauses": [
                {"field": "market.close", "operator": "gt", "value": 0},
            ]
        }
    }
    ranking = {
        "groups": [
            {
                "name": "momentum",
                "factors": [{"name": "return_126d", "table": "market_data", "column": "return_126d"}],
            }
        ]
    }
    reusable_rebalance = {"cadence": "monthly", "dayRule": "last_trading_day", "anchor": "next_open"}
    regime_policy = {"modelName": "default-regime", "mode": "observe_only"}
    risk_policy = {
        "scope": "strategy",
        "stopLoss": {"thresholdPct": 8, "action": "reduce_exposure", "reductionPct": 50},
    }
    exit_policy = {"exits": [{"id": "rank-decay", "type": "rank_decay", "rankThreshold": 40}]}
    cases = [
        (UniverseConfigPreset, {"identity": identity, "config": universe}),
        (RankingSchemaPreset, {"identity": identity, "config": ranking}),
        (RebalancePolicyPreset, {"identity": identity, "config": reusable_rebalance}),
        (RegimePolicyPreset, {"identity": identity, "config": regime_policy}),
        (StrategyRiskPolicyPreset, {"identity": identity, "config": risk_policy}),
        (ExitPolicyPreset, {"identity": identity, "config": exit_policy}),
    ]

    for model, payload in cases:
        try:
            model.model_validate({**payload, "unexpected": True})
        except Exception as exc:
            assert "unexpected" in str(exc)
        else:
            raise AssertionError(f"Expected {model.__name__} to reject unknown fields.")


def test_config_identity_normalizes_metadata() -> None:
    identity = ConfigIdentity(
        name="  us-large-liquid  ",
        version=1,
        status="active",
        description="  Large liquid US equities.  ",
        intendedUse="validation",
        thesis="  Baseline liquidity screen.  ",
        whatToMonitor=[" turnover ", "", " slippage "],
    )

    assert identity.name == "us-large-liquid"
    assert identity.description == "Large liquid US equities."
    assert identity.thesis == "Baseline liquidity screen."
    assert identity.whatToMonitor == ["turnover", "slippage"]


def test_strategy_position_policy_defaults_to_equity_without_changing_legacy_configs() -> None:
    payload = StrategyConfig(
        universe=UniverseDefinition(
            root=UniverseGroup(
                clauses=[
                    UniverseCondition(field="market.close", operator="gt", value=0),
                ]
            )
        ),
        positionPolicy=StrategyPositionPolicy(),
    )

    assert payload.positionPolicy is not None
    assert payload.positionPolicy.allowedAssetClasses == ["equity"]
    assert payload.positionPolicy.requireOrderConfirmation is False


def test_strategy_position_policy_accepts_target_and_max_sizing() -> None:
    payload = StrategyConfig(
        universe=UniverseDefinition(
            root=UniverseGroup(
                clauses=[
                    UniverseCondition(field="market.close", operator="gt", value=0),
                ]
            )
        ),
        topN=10,
        positionPolicy={
            "targetPositionSize": {"mode": "pct_of_allocatable_capital", "value": 5},
            "maxPositionSize": {"mode": "notional_base_ccy", "value": 25_000},
            "maxOpenPositions": 4,
            "allowedAssetClasses": ["equity", "option", "equity"],
            "requireOrderConfirmation": True,
        },
    )

    assert payload.positionPolicy is not None
    assert payload.positionPolicy.targetPositionSize is not None
    assert payload.positionPolicy.targetPositionSize.value == 5
    assert payload.positionPolicy.allowedAssetClasses == ["equity", "option"]
    assert payload.positionPolicy.requireOrderConfirmation is True


def test_strategy_position_policy_rejects_invalid_percentage_limit() -> None:
    try:
        StrategyPositionPolicy(targetPositionSize={"mode": "pct_of_allocatable_capital", "value": 101})
    except Exception as exc:
        assert "cannot exceed 100" in str(exc)
    else:
        raise AssertionError("Expected validation failure for oversized percentage position limit.")


def test_strategy_position_policy_rejects_long_only_overallocation() -> None:
    try:
        StrategyConfig(
            universe=UniverseDefinition(
                root=UniverseGroup(
                    clauses=[
                        UniverseCondition(field="market.close", operator="gt", value=0),
                    ]
                )
            ),
            topN=3,
            positionPolicy={"targetPositionSize": {"mode": "pct_of_allocatable_capital", "value": 40}},
        )
    except Exception as exc:
        assert "cannot allocate more than 100%" in str(exc)
    else:
        raise AssertionError("Expected validation failure for long-only over-allocation.")


def test_strategy_risk_profile_config_requires_complete_position_policy() -> None:
    payload = StrategyRiskProfileConfig(
        presetClass="balanced",
        positionPolicy={
            "targetPositionSize": {"mode": "pct_of_allocatable_capital", "value": 5},
            "maxPositionSize": {"mode": "pct_of_allocatable_capital", "value": 8},
            "maxOpenPositions": 20,
        },
    )

    assert payload.presetClass == "balanced"
    assert payload.positionPolicy.maxOpenPositions == 20

    for invalid_payload in (
        {
            "presetClass": "balanced",
            "positionPolicy": {
                "maxPositionSize": {"mode": "pct_of_allocatable_capital", "value": 8},
                "maxOpenPositions": 20,
            },
        },
        {
            "presetClass": "balanced",
            "positionPolicy": {
                "targetPositionSize": {"mode": "pct_of_allocatable_capital", "value": 5},
                "maxPositionSize": {"mode": "notional_base_ccy", "value": 25_000},
                "maxOpenPositions": 20,
            },
        },
        {
            "presetClass": "balanced",
            "positionPolicy": {
                "targetPositionSize": {"mode": "pct_of_allocatable_capital", "value": 8},
                "maxPositionSize": {"mode": "pct_of_allocatable_capital", "value": 5},
                "maxOpenPositions": 20,
            },
        },
    ):
        try:
            StrategyRiskProfileConfig.model_validate(invalid_payload)
        except Exception as exc:
            assert "Strategy risk profiles require targetPositionSize" in str(exc) or "share a mode" in str(exc) or "greater than or equal" in str(exc)
        else:
            raise AssertionError("Expected validation failure for incomplete or invalid risk profile policy.")


def test_strategy_risk_profile_summary_and_detail_support_usage_metadata() -> None:
    summary = StrategyRiskProfileSummary(
        name="balanced",
        description="Default balanced posture.",
        presetClass="balanced",
        version=2,
        isSystem=True,
        usageCount=14,
    )
    detail = StrategyRiskProfileDetail(
        **summary.model_dump(),
        config={
            "presetClass": "balanced",
            "positionPolicy": {
                "targetPositionSize": {"mode": "pct_of_allocatable_capital", "value": 5},
                "maxPositionSize": {"mode": "pct_of_allocatable_capital", "value": 8},
                "maxOpenPositions": 20,
            },
        },
    )

    assert detail.name == "balanced"
    assert detail.isSystem is True
    assert detail.config.positionPolicy.maxOpenPositions == 20


def test_strategy_config_requires_position_policy_snapshot_when_risk_profile_name_is_set() -> None:
    try:
        StrategyConfig(
            universe=UniverseDefinition(
                root=UniverseGroup(
                    clauses=[
                        UniverseCondition(field="market.close", operator="gt", value=0),
                    ]
                )
            ),
            riskProfileName="balanced",
        )
    except Exception as exc:
        assert "riskProfileName requires a positionPolicy snapshot" in str(exc)
    else:
        raise AssertionError("Expected validation failure for incomplete risk profile strategy config.")


def test_strategy_config_accepts_risk_profile_name_with_snapshot() -> None:
    payload = StrategyConfig(
        universe=UniverseDefinition(
            root=UniverseGroup(
                clauses=[
                    UniverseCondition(field="market.close", operator="gt", value=0),
                ]
            )
        ),
        riskProfileName="balanced",
        positionPolicy={
            "targetPositionSize": {"mode": "pct_of_allocatable_capital", "value": 5},
            "maxPositionSize": {"mode": "pct_of_allocatable_capital", "value": 8},
            "maxOpenPositions": 20,
        },
    )

    assert payload.riskProfileName == "balanced"
    assert payload.positionPolicy is not None


def test_strategy_config_accepts_rebalance_and_strategy_risk_policies() -> None:
    payload = StrategyConfig(
        universe=UniverseDefinition(
            root=UniverseGroup(
                clauses=[
                    UniverseCondition(field="market.close", operator="gt", value=0),
                ]
            )
        ),
        rebalancePolicy={
            "frequency": "every_n_bars",
            "intervalBars": 3,
            "executionTiming": "next_bar_open",
            "driftThresholdPct": 1.5,
            "minTradeNotional": 25,
            "cashBufferPct": 1,
            "maxTurnoverPct": 35,
            "allowPartialRebalance": True,
            "closeRemovedPositions": True,
        },
        strategyRiskPolicy={
            "scope": "strategy",
            "stopLoss": {
                "thresholdPct": 8,
                "action": "reduce_exposure",
                "reductionPct": 50,
            },
            "takeProfit": {
                "thresholdPct": 15,
                "action": "rebalance_to_target",
            },
            "reentry": {
                "cooldownBars": 12,
                "requireApproval": False,
            },
        },
    )

    assert payload.rebalancePolicy is not None
    assert payload.rebalancePolicy.intervalBars == 3
    assert payload.strategyRiskPolicy is not None
    assert payload.strategyRiskPolicy.stopLoss is not None
    assert payload.strategyRiskPolicy.stopLoss.thresholdPct == 8
    assert payload.strategyRiskPolicy.reentry.cooldownBars == 12


def test_rebalance_policy_requires_interval_only_for_every_n_bars() -> None:
    try:
        RebalancePolicy(frequency="every_n_bars")
    except Exception as exc:
        assert "requires intervalBars" in str(exc)
    else:
        raise AssertionError("Expected every_n_bars policy to require intervalBars.")

    try:
        RebalancePolicy(frequency="daily", intervalBars=3)
    except Exception as exc:
        assert "only supported" in str(exc)
    else:
        raise AssertionError("Expected non every_n_bars policy to reject intervalBars.")


def test_reusable_rebalance_policy_requires_complete_calendar_fields() -> None:
    policy = RebalancePolicy(
        cadence="monthly",
        dayRule="last_trading_day",
        anchor="next_open",
        tradeDelayBars=1,
        driftThresholdBps=50,
        maxTurnoverPerRebalance=0.35,
    )

    assert policy.cadence == "monthly"
    assert policy.dayRule == "last_trading_day"
    assert policy.anchor == "next_open"

    try:
        RebalancePolicy(cadence="monthly")
    except Exception as exc:
        assert "cadence, dayRule, and anchor together" in str(exc)
    else:
        raise AssertionError("Expected partial reusable rebalance fields to fail validation.")


def test_reusable_rebalance_policy_rejects_invalid_turnover_and_presets_require_calendar_fields() -> None:
    try:
        RebalancePolicy(cadence="weekly", dayRule="last_trading_day", anchor="next_open")
    except Exception as exc:
        assert "cadence" in str(exc)
    else:
        raise AssertionError("Expected unsupported reusable rebalance cadence to fail validation.")

    try:
        RebalancePolicy(cadence="monthly", dayRule="middle_trading_day", anchor="next_open")
    except Exception as exc:
        assert "dayRule" in str(exc)
    else:
        raise AssertionError("Expected unsupported reusable rebalance dayRule to fail validation.")

    try:
        RebalancePolicy(
            cadence="quarterly",
            dayRule="last_trading_day",
            anchor="next_open",
            maxTurnoverPerRebalance=1.25,
        )
    except Exception as exc:
        assert "maxTurnoverPerRebalance" in str(exc)
    else:
        raise AssertionError("Expected maxTurnoverPerRebalance above 1.0 to fail validation.")

    try:
        RebalancePolicyPreset(
            identity={"name": "monthly-last-trading-day", "version": 1},
            config={"frequency": "monthly"},
        )
    except Exception as exc:
        assert "cadence, dayRule, and anchor" in str(exc)
    else:
        raise AssertionError("Expected reusable rebalance preset to require calendar fields.")


def test_strategy_risk_policy_rejects_ambiguous_enabled_empty_policy() -> None:
    try:
        StrategyRiskPolicy()
    except Exception as exc:
        assert "stopLoss, takeProfit, or reentry control" in str(exc)
    else:
        raise AssertionError("Expected enabled empty strategy risk policy to fail validation.")


def test_strategy_risk_policy_accepts_reentry_only_controls() -> None:
    policy = StrategyRiskPolicy(reentry={"cooldownBars": 3, "requireApproval": True})

    assert policy.stopLoss is None
    assert policy.takeProfit is None
    assert policy.reentry.cooldownBars == 3
    assert policy.reentry.requireApproval is True


def test_risk_policy_library_contracts_wrap_strategy_risk_policy() -> None:
    summary = RiskPolicyConfigSummary(name="balanced-risk", description="Desk balanced risk.", version=2, usageCount=4)
    revision = RiskPolicyConfigRevision(
        name="balanced-risk",
        version=2,
        description="Desk balanced risk.",
        config={
            "policy": {
                "scope": "strategy",
                "stopLoss": {"thresholdPct": 8, "action": "reduce_exposure", "reductionPct": 50},
            }
        },
        configHash="hash-1",
    )
    detail = RiskPolicyConfigDetailResponse(policy=summary, activeRevision=revision, revisions=[revision])

    assert detail.policy.version == 2
    assert detail.activeRevision is not None
    assert detail.activeRevision.config.policy.stopLoss is not None


def test_strategy_risk_policy_requires_reduction_percentage_for_reduce_exposure() -> None:
    try:
        StrategyRiskPolicy(stopLoss={"thresholdPct": 8, "action": "reduce_exposure"})
    except Exception as exc:
        assert "reduce_exposure" in str(exc)
        assert "reductionPct" in str(exc)
    else:
        raise AssertionError("Expected reduce_exposure stop-loss policy to require reductionPct.")


def test_exit_rule_set_contracts_normalize_priorities_and_metadata() -> None:
    config = ExitRuleSetConfig(
        intrabarConflictPolicy="priority_order",
        exits=[
            {"id": "profit-10", "type": "take_profit_fixed", "value": 0.10},
            {"id": "stop-5", "type": "stop_loss_fixed", "value": 0.05},
        ],
    )
    summary = ExitRuleSetSummary(name="standard-exits", version=3, ruleCount=len(config.exits))
    revision = ExitRuleSetRevision(name="standard-exits", version=3, config=config)
    detail = ExitRuleSetDetailResponse(ruleSet=summary, activeRevision=revision, revisions=[revision])

    assert detail.ruleSet.ruleCount == 2
    assert detail.activeRevision is not None
    assert detail.activeRevision.config.exits[0].priority == 0
    assert detail.activeRevision.config.exits[1].priority == 1


def test_exit_rule_set_rejects_duplicate_rule_ids() -> None:
    try:
        ExitRuleSetConfig(
            exits=[
                {"id": "stop", "type": "stop_loss_fixed", "value": 0.05},
                {"id": "stop", "type": "take_profit_fixed", "value": 0.10},
            ]
        )
    except Exception as exc:
        assert "Duplicate exit rule id" in str(exc)
    else:
        raise AssertionError("Expected duplicate exit ids to fail validation.")


def test_rank_decay_exit_requires_rank_threshold_and_rejects_price_stop_fields() -> None:
    config = ExitRuleSetConfig(exits=[{"id": "rank-decay", "type": "rank_decay", "rankThreshold": 40}])

    assert config.exits[0].rankThreshold == 40
    assert config.exits[0].value is None

    invalid_payloads = [
        {"id": "missing-threshold", "type": "rank_decay"},
        {"id": "value-not-supported", "type": "rank_decay", "rankThreshold": 40, "value": 0.1},
        {"id": "reference-not-supported", "type": "rank_decay", "rankThreshold": 40, "reference": "entry_price"},
        {"id": "atr-not-supported", "type": "rank_decay", "rankThreshold": 40, "atrColumn": "atr_14"},
        {"id": "price-not-supported", "type": "rank_decay", "rankThreshold": 40, "priceField": "close"},
    ]

    for payload in invalid_payloads:
        try:
            ExitRuleSetConfig(exits=[payload])
        except Exception as exc:
            assert "rank_decay" in str(exc)
        else:
            raise AssertionError(f"Expected invalid rank_decay payload to fail validation: {payload['id']}")


def test_price_based_exit_rules_reject_rank_threshold() -> None:
    try:
        ExitRuleSetConfig(
            exits=[
                {
                    "id": "stop-8",
                    "type": "stop_loss_fixed",
                    "value": 0.08,
                    "rankThreshold": 40,
                }
            ]
        )
    except Exception as exc:
        assert "rankThreshold" in str(exc)
    else:
        raise AssertionError("Expected price-based exit rule to reject rankThreshold.")


def test_strategy_config_rejects_short_side_until_supported() -> None:
    try:
        StrategyConfig(
            universe=UniverseDefinition(
                root=UniverseGroup(
                    clauses=[
                        UniverseCondition(field="market.close", operator="gt", value=0),
                    ]
                )
            ),
            longOnly=False,
        )
    except Exception as exc:
        assert "only supports longOnly=true" in str(exc)
    else:
        raise AssertionError("Expected validation failure for longOnly=false.")


def test_backtest_policy_event_contract_captures_policy_diagnostics() -> None:
    event = BacktestPolicyEvent(
        run_id="run-123",
        event_seq=1,
        bar_ts="2026-03-08T14:31:00Z",
        scope="position",
        policy_type="reentry",
        decision="blocked",
        reason_code="cooldown_active",
        symbol="AAPL",
        position_id="run-123:AAPL:1",
        policy_id="stop-8",
        observed_value=1,
        threshold_value=12,
        action="block_reentry",
        details={"cooldownBarsRemaining": 11},
    )
    response = BacktestPolicyEventListResponse(events=[event], total=1, limit=50, offset=0)

    assert response.events[0].reason_code == "cooldown_active"
    assert response.events[0].details["cooldownBarsRemaining"] == 11


def test_backtest_data_quality_event_contract_captures_strict_mode_diagnostics() -> None:
    event = BacktestDataQualityEvent(
        run_id="run-123",
        event_seq=1,
        bar_ts="2026-03-08T14:35:00Z",
        severity="error",
        table_name="fundamental_signal_daily",
        symbol="AAPL",
        field_name="quality_score",
        reason_code="available_after_bar",
        action="exclude_value",
        details={"availableAt": "2026-03-08T14:37:00Z"},
    )
    response = BacktestDataQualityEventListResponse(events=[event], total=1, limit=50, offset=0)

    assert response.events[0].severity == "error"
    assert response.events[0].reason_code == "available_after_bar"
    assert response.events[0].details["availableAt"] == "2026-03-08T14:37:00Z"


def test_trade_order_preview_accepts_optional_strategy_reference() -> None:
    request = TradeOrderPreviewRequest(
        accountId="acct-1",
        environment="paper",
        clientRequestId="preview-1",
        symbol="aapl",
        side="buy",
        orderType="market",
        quantity=1,
        strategyRef={"strategyName": "quality-trend", "strategyVersion": 3},
    )

    assert request.symbol == "AAPL"
    assert request.strategyRef is not None
    assert request.strategyRef.strategyName == "quality-trend"
    assert request.strategyRef.strategyVersion == 3


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


def test_universe_condition_accepts_us_liquid_equity_filter_fields() -> None:
    definition = UniverseDefinition(
        root={
            "operator": "and",
            "clauses": [
                {"field": "security.country", "operator": "eq", "value": "US"},
                {"field": "security.primary_listing", "operator": "eq", "value": True},
                {"field": "security.market_cap", "operator": "gte", "value": 10_000_000_000},
                {"field": "market.dollar_volume_20d", "operator": "gte", "value": 50_000_000},
                {"field": "security.is_price_liquidity_eligible", "operator": "eq", "value": True},
            ],
        }
    )

    used_fields = [clause.field for clause in definition.root.clauses if isinstance(clause, UniverseCondition)]
    assert used_fields == [
        "security.country",
        "security.primary_listing",
        "security.market_cap",
        "market.dollar_volume_20d",
        "security.is_price_liquidity_eligible",
    ]


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
    assert config.authSessionMode == "bearer"
    assert config.authProvider == "disabled"
    assert config.oidcScopes == []
    assert config.oidcAudience == []
    assert config.oidcPostLogoutRedirectUri is None


def test_ui_runtime_config_accepts_cookie_auth_session_mode() -> None:
    config = UiRuntimeConfig(authSessionMode="cookie")
    assert config.authSessionMode == "cookie"


def test_ui_runtime_config_accepts_password_auth_provider_with_cookie_session_mode() -> None:
    config = UiRuntimeConfig(authProvider="password", authSessionMode="cookie", authRequired=True)

    assert config.authProvider == "password"
    assert config.authSessionMode == "cookie"
    assert config.authRequired is True


def test_ui_runtime_config_rejects_unknown_auth_session_mode() -> None:
    try:
        UiRuntimeConfig(authSessionMode="local-storage")
    except Exception as exc:
        assert "authSessionMode" in str(exc)
    else:
        raise AssertionError("Expected validation failure for unknown auth session mode.")


def test_ui_runtime_config_rejects_password_auth_provider_without_cookie_session_mode() -> None:
    try:
        UiRuntimeConfig(authProvider="password", authSessionMode="bearer")
    except Exception as exc:
        assert "authSessionMode" in str(exc)
        assert "authProvider" in str(exc)
    else:
        raise AssertionError("Expected password auth provider to require cookie session mode.")


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


def test_password_auth_session_request_requires_non_empty_password() -> None:
    payload = PasswordAuthSessionRequest(password="operator-secret")
    schema = PasswordAuthSessionRequest.model_json_schema()

    assert payload.password == "operator-secret"
    assert schema["required"] == ["password"]
    assert schema["properties"]["password"]["minLength"] == 1

    try:
        PasswordAuthSessionRequest(password="")
    except Exception as exc:
        assert "password" in str(exc)
    else:
        raise AssertionError("Expected password auth session request validation to reject blank passwords.")


def test_runtime_job_metadata_contract_validates_strategy_compute_fields() -> None:
    payload = RuntimeJobMetadata(
        jobCategory="strategy-compute",
        jobKey="regime",
        jobRole="publish",
        triggerOwner="schedule",
        metadataSource="tags",
        metadataStatus="valid",
    )
    schema = RuntimeJobMetadata.model_json_schema()

    assert payload.jobCategory == "strategy-compute"
    assert schema["properties"]["jobCategory"]["enum"] == [
        "data-pipeline",
        "strategy-compute",
        "operational-support",
    ]
    assert schema["required"] == [
        "jobCategory",
        "jobKey",
        "jobRole",
        "triggerOwner",
        "metadataSource",
        "metadataStatus",
    ]


def test_runtime_job_metadata_rejects_unknown_category() -> None:
    try:
        RuntimeJobMetadata(
            jobCategory="data-ingest",
            jobKey="market",
            jobRole="load",
            triggerOwner="pipeline-chain",
            metadataSource="tags",
            metadataStatus="valid",
        )
    except Exception as exc:
        assert "jobCategory" in str(exc)
    else:
        raise AssertionError("Expected RuntimeJobMetadata to reject legacy job categories.")


def test_strategy_publication_reconcile_signal_request_validates_key_and_fingerprint() -> None:
    payload = StrategyPublicationReconcileSignalRequest(
        jobKey="regime",
        sourceFingerprint="abc123",
        metadata=RegimePublicationReconcileMetadata(
            publishedAsOfDate="2026-04-23",
            inputAsOfDate="2026-04-23",
            historyRows=10,
            latestRows=1,
            transitionRows=0,
            activeModels=[{"model_name": "default-regime", "model_version": 1}],
            domainArtifactPath="regime/_metadata/domain.json",
        ),
    )

    assert payload.jobKey == "regime"
    assert payload.sourceFingerprint == "abc123"
    assert payload.metadata.activeModels[0].modelName == "default-regime"

    try:
        StrategyPublicationReconcileSignalRequest(
            jobKey="Gold Regime",
            sourceFingerprint="",
            metadata={
                "publishedAsOfDate": "2026-04-23",
                "historyRows": -1,
                "latestRows": 1,
                "transitionRows": 0,
                "unexpected": True,
            },
        )
    except Exception as exc:
        assert "jobKey" in str(exc)
        assert "sourceFingerprint" in str(exc)
        assert "historyRows" in str(exc)
        assert "unexpected" in str(exc)
    else:
        raise AssertionError("Expected strategy publication signal request validation to reject bad inputs.")


def test_results_reconcile_contract_requires_strict_complete_payloads() -> None:
    request = ResultsReconcileRequest(dryRun=True)
    response = ResultsReconcileResponse(
        dryRun=True,
        rankingDirtyCount=1,
        rankingNoopCount=2,
        canonicalEnqueuedCount=3,
        canonicalUpToDateCount=4,
        canonicalSkippedCount=5,
        publicationSignalsProcessedCount=6,
        publicationSignalsErrorCount=0,
        errorCount=0,
        errors=[],
    )

    assert request.dryRun is True
    assert response.publicationSignalsProcessedCount == 6

    try:
        ResultsReconcileRequest.model_validate({"dryRun": "true"})
    except Exception:
        pass
    else:
        raise AssertionError("Expected results reconcile request validation to reject non-boolean dryRun.")

    bad_payloads = (
        {},
        {
            "dryRun": True,
            "rankingDirtyCount": "1",
            "rankingNoopCount": 0,
            "canonicalEnqueuedCount": 0,
            "canonicalUpToDateCount": 0,
            "canonicalSkippedCount": 0,
            "publicationSignalsProcessedCount": 0,
            "publicationSignalsErrorCount": 0,
            "errorCount": 0,
            "errors": [],
        },
    )
    for payload in bad_payloads:
        try:
            ResultsReconcileResponse.model_validate(payload)
        except Exception:
            continue
        raise AssertionError(f"Expected results reconcile response validation to reject {payload!r}.")


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


def test_intraday_watchlist_symbol_append_contract_normalizes_and_reports_run_state() -> None:
    request = IntradayWatchlistSymbolAppendRequest(
        symbols=[" aapl ", "MSFT", "AAPL"],
        reason="  operator add  ",
    )

    response = IntradayWatchlistSymbolAppendResponse(
        watchlist=IntradayWatchlistDetail(
            watchlistId="watch-1",
            name="Tech Core",
            enabled=True,
            symbolCount=3,
            symbols=["AAPL", "MSFT", "NVDA"],
        ),
        addedSymbols=["msft"],
        alreadyPresentSymbols=[" aapl "],
        queuedRun=IntradayMonitorRunSummary(
            runId="run-1",
            watchlistId="watch-1",
            triggerKind="manual",
            status="queued",
            forceRefresh=False,
            symbolCount=3,
        ),
    )

    assert request.symbols == ["AAPL", "MSFT"]
    assert request.queueRun is True
    assert request.reason == "operator add"
    assert response.addedSymbols == ["MSFT"]
    assert response.alreadyPresentSymbols == ["AAPL"]
    assert response.queuedRun is not None
    assert response.queuedRun.forceRefresh is False
    assert response.runSkippedReason is None


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
        model_version=3,
        signals=[
            RegimeSignal(
                regime_code="trending_up",
                display_name="Trending (Up)",
                signal_state="active",
                score=1.0,
                activation_threshold=0.6,
                is_active=True,
                matched_rule_id="trending_up",
                evidence={"spy_above_sma_200": True},
            )
        ],
        active_regimes=["trending_up"],
        halt_flag=False,
    )
    config = canonical_default_regime_model_config()
    assert snapshot.model_version == 3
    assert snapshot.active_regimes == ["trending_up"]
    assert config.activationThreshold == 0.6
    assert config.signalConfigs["trending_up"].displayName == "Trending (Up)"


def test_default_regime_canonical_v3_config_rejects_rule_drift_and_halt_drift() -> None:
    assert CANONICAL_DEFAULT_REGIME_VERSION == 3
    canonical = validate_canonical_default_regime_config({})
    assert canonical.activationThreshold == 0.6
    assert canonical.haltVixThreshold == 32.0
    assert canonical.haltVixStreakDays == 2

    errors = canonical_default_regime_config_errors(
        {
            "signalConfigs": {
                **canonical.model_dump(mode="python")["signalConfigs"],
                "trending_up": {
                    **canonical.model_dump(mode="python")["signalConfigs"]["trending_up"],
                    "displayName": "Trend Up",
                },
            },
            "haltVixThreshold": 31.5,
            "haltVixStreakDays": 3,
        }
    )
    assert any("signalConfigs.trending_up" in message for message in errors)
    assert any("haltVixThreshold" in message for message in errors)
    assert any("haltVixStreakDays" in message for message in errors)


def test_default_regime_policy_rejects_legacy_fields() -> None:
    try:
        RegimePolicy.model_validate(
            {
                "modelName": "default-regime",
                "targetGrossExposureByRegime": {"trending_up": 1.0},
            }
        )
    except Exception as exc:
        assert "legacy fields" in str(exc)
        assert "observe_only" in str(exc)
    else:
        raise AssertionError("Expected legacy default-regime policy fields to be rejected.")


def test_regime_policy_library_contracts_reference_model_revision() -> None:
    config = RegimePolicyConfig(modelName="default-regime", modelVersion=3, mode="observe_only")
    summary = RegimePolicyConfigSummary(
        name="observe-default",
        description="Observe default regime model.",
        version=2,
        usageCount=5,
        modelName=config.modelName,
        modelVersion=config.modelVersion,
        mode=config.mode,
    )
    revision = RegimePolicyConfigRevision(
        name="observe-default",
        version=2,
        description="Observe default regime model.",
        config=config,
        configHash="hash-1",
    )
    detail = RegimePolicyConfigDetailResponse(policy=summary, activeRevision=revision, revisions=[revision])
    resolved = config.resolved_policy()

    assert detail.policy.modelVersion == 3
    assert detail.activeRevision is not None
    assert detail.activeRevision.config.mode == "observe_only"
    assert resolved.modelName == "default-regime"
    assert resolved.modelVersion == 3


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
        results_schema_version=7,
        bar_size="1d",
        periods_per_year=252,
        strategy_scope="portfolio",
    )
    schema = TimeseriesResponse.model_json_schema()

    assert metadata.results_schema_version == 7
    assert metadata.bar_size == "1d"
    assert schema["properties"]["metadata"]["default"] is None
    assert schema["$defs"]["BacktestResultMetadata"]["properties"]["results_schema_version"]["default"] == 7


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


def test_backtest_summary_supports_research_safe_v7_metadata() -> None:
    payload = BacktestSummary.model_validate(
        {
            "research_integrity_status": "strict_passed",
            "execution_model": "simple_bps",
            "execution_model_quality": "not_tca_grade",
            "approval_readiness": "research_only",
            "data_quality_event_count": 2,
            "policy_event_count": 3,
        }
    )

    assert payload.research_integrity_status == "strict_passed"
    assert payload.execution_model_quality == "not_tca_grade"
    assert payload.approval_readiness == "research_only"
    assert payload.data_quality_event_count == 2
    assert payload.policy_event_count == 3


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


def test_portfolio_revision_accepts_notional_allocation_mode() -> None:
    revision = PortfolioRevision(
        portfolioName="core-balanced-notional",
        version=1,
        allocationMode="notional_base_ccy",
        allocatableCapital=1_000_000.0,
        allocations=[
            PortfolioSleeveAllocation(
                sleeveId="quality-core",
                sleeveName="Quality Core",
                strategy={"strategyName": "quality-trend", "strategyVersion": 4},
                allocationMode="notional_base_ccy",
                targetNotionalBaseCcy=600_000.0,
            ),
            PortfolioSleeveAllocation(
                sleeveId="defensive",
                sleeveName="Defensive",
                strategy={"strategyName": "defensive-value", "strategyVersion": 2},
                allocationMode="notional_base_ccy",
                targetNotionalBaseCcy=400_000.0,
            ),
        ],
    )
    upsert = PortfolioUpsertRequest(
        name="core-balanced-notional",
        allocationMode="notional_base_ccy",
        allocatableCapital=1_000_000.0,
        allocations=[
            {
                "sleeveId": "quality-core",
                "strategy": {"strategyName": "quality-trend", "strategyVersion": 4},
                "allocationMode": "notional_base_ccy",
                "targetNotionalBaseCcy": 600_000.0,
            },
            {
                "sleeveId": "defensive",
                "strategy": {"strategyName": "defensive-value", "strategyVersion": 2},
                "allocationMode": "notional_base_ccy",
                "targetNotionalBaseCcy": 400_000.0,
            },
        ],
    )

    assert revision.allocationMode == "notional_base_ccy"
    assert revision.allocatableCapital == 1_000_000.0
    assert revision.allocations[0].targetNotionalBaseCcy == 600_000.0
    assert upsert.allocations[1].allocationMode == "notional_base_ccy"


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
    assert account.rebalanceCadence == "weekly"
    assert account.rebalanceAnchor == "Strategy native cadence"
    assert account.baseCurrency == "USD"
    assert request.openingCash == 1_000_000


def test_portfolio_account_upsert_request_accepts_optional_rebalance_schedule_overrides() -> None:
    payload = PortfolioAccountUpsertRequest(
        name="Core Long Only",
        baseCurrency="usd",
        inceptionDate="2026-01-02",
        rebalanceCadence="monthly",
        rebalanceAnchor="15th close",
    )

    assert payload.rebalanceCadence == "monthly"
    assert payload.rebalanceAnchor == "15th close"


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


def test_portfolio_forecast_and_next_rebalance_contracts_capture_authoritative_monitoring_shapes() -> None:
    forecast = PortfolioForecastResponse(
        accountId="acct-001",
        asOf="2026-04-18",
        modelName="default-regime",
        modelVersion=3,
        benchmarkSymbol="spy",
        horizon="3M",
        assumption="current",
        costDragOverrideBps=12,
        expectedReturnPct=4.2,
        expectedActiveReturnPct=1.1,
        downsidePct=-2.3,
        upsidePct=7.6,
        confidence="medium",
        confidenceLabel="Medium confidence",
        sampleSize=11,
        sampleMode="regime-conditioned",
        appliedRegimeCode="trending_up",
        notes=["Regime sample is moderately deep."],
    )
    rebalance = PortfolioNextRebalanceResponse(
        accountId="acct-001",
        asOf="2026-04-18",
        rebalanceCadence="weekly",
        anchorText="Monday close",
        nextDate="2026-04-20",
        inferred=False,
        basis="anchor",
        reason="Weekly cadence is anchored to the parsed weekday in the rebalance anchor.",
    )

    assert forecast.benchmarkSymbol == "SPY"
    assert forecast.confidence == "medium"
    assert rebalance.anchorText == "Monday close"
    assert rebalance.nextDate is not None


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


def test_symbol_identity_contracts_expose_v1_massive_market_aliases() -> None:
    alias_by_provider_symbol = {
        (rule.provider, rule.domain, rule.providerSymbol): rule.canonicalSymbol
        for rule in SYMBOL_ALIAS_RULES
    }

    assert SYMBOL_ALIAS_RULESET_VERSION == "symbol-alias-v1"
    assert alias_by_provider_symbol[("massive", "market", "I:VIX")] == "^VIX"
    assert alias_by_provider_symbol[("massive", "market", "I:VIX3M")] == "^VIX3M"
    assert ("massive", "finance", "I:VIX") not in alias_by_provider_symbol
    assert ("massive", "market", "VIX") not in alias_by_provider_symbol


def test_symbol_identity_resolution_result_supports_strict_error_states() -> None:
    resolved = SymbolResolutionResult(
        status="resolved",
        provider="massive",
        domain="market",
        inputSymbol="I:VIX",
        canonicalSymbol="^VIX",
        providerSymbol="I:VIX",
    )
    unsupported = SymbolResolutionResult(
        status="unsupported",
        provider="massive",
        domain="market",
        inputSymbol="VIX",
        error={
            "code": "unsupported",
            "message": "Bare VIX is not a supported Massive market alias.",
            "provider": "massive",
            "domain": "market",
            "inputSymbol": "VIX",
        },
    )
    ambiguous = SymbolResolutionResult(
        status="ambiguous",
        provider="massive",
        domain="market",
        inputSymbol="VIX",
        error={"code": "ambiguous", "message": "Multiple canonical symbols matched."},
    )
    invalid = SymbolResolutionResult(
        status="invalid",
        provider="massive",
        domain="market",
        inputSymbol="-",
        error={"code": "invalid", "message": "Symbol is blank or placeholder."},
    )

    assert resolved.mappingVersion == SYMBOL_ALIAS_RULESET_VERSION
    assert unsupported.error is not None and unsupported.error.code == "unsupported"
    assert ambiguous.status == "ambiguous"
    assert invalid.status == "invalid"


def test_broker_account_contracts_capture_normalized_operations_surface() -> None:
    summary = BrokerAccountSummary(
        accountId=" alpaca-core ",
        broker="alpaca",
        name=" Core Long Only ",
        accountNumberMasked=" ****1234 ",
        baseCurrency="usd",
        overallStatus="warning",
        tradeReadiness="blocked",
        tradeReadinessReason="Auth refresh is required.",
        highestAlertSeverity="critical",
        connectionHealth={
            "overallStatus": "warning",
            "authStatus": "reauth_required",
            "connectionState": "reconnect_required",
            "syncStatus": "stale",
            "lastSuccessfulSyncAt": "2026-04-20T13:30:00Z",
            "staleReason": "Positions are older than the freshness threshold.",
            "syncPaused": False,
        },
        equity=250000.0,
        cash=42000.0,
        buyingPower=180000.0,
        openPositionCount=12,
        openOrderCount=3,
        lastSyncedAt="2026-04-20T13:30:00Z",
        snapshotAsOf="2026-04-20T13:29:00Z",
        activePortfolioName="growth-core",
        strategyLabel="Quality / Momentum",
        alertCount=2,
    )
    detail = BrokerAccountDetail(
        account=summary,
        capabilities=BrokerCapabilityFlags(
            canReadBalances=True,
            canReadPositions=True,
            canReadOrders=True,
            canTrade=True,
            canReconnect=True,
            canPauseSync=True,
            canRefresh=True,
            canAcknowledgeAlerts=True,
        ),
        accountType="margin",
        tradingBlocked=True,
        tradingBlockedReason="Manual reconnect required before trading resumes.",
        dayTradeBuyingPower=95000.0,
        maintenanceExcess=32000.0,
        alerts=[
            {
                "alertId": "alert-1",
                "accountId": "alpaca-core",
                "severity": "critical",
                "code": "auth_expired",
                "title": "Broker token expired",
                "message": "Reconnect the broker account.",
                "observedAt": "2026-04-20T13:31:00Z",
            }
        ],
        syncRuns=[
            BrokerSyncRun(
                runId="sync-1",
                accountId="alpaca-core",
                trigger="manual",
                scope="full",
                status="failed",
                requestedAt="2026-04-20T13:31:00Z",
                completedAt="2026-04-20T13:32:00Z",
                warningCount=1,
                errorMessage="Token refresh failed.",
            )
        ],
        recentActivity=[
            {
                "activityId": "activity-1",
                "accountId": "alpaca-core",
                "activityType": "acknowledge_alert",
                "status": "completed",
                "requestedAt": "2026-04-20T13:40:00Z",
                "completedAt": "2026-04-20T13:40:02Z",
                "actor": "ops@example.com",
                "summary": "Acknowledged token-expiry alert.",
                "relatedAlertId": "alert-1",
            }
        ],
    )
    reconnect = ReconnectBrokerAccountRequest(reason="Operator initiated reconnect.")
    pause = PauseBrokerSyncRequest(paused=False, reason="Resume after token refresh.")
    refresh = RefreshBrokerAccountRequest(scope="full", force=True)
    acknowledge = AcknowledgeBrokerAlertRequest(note="Connector rerouted to manual follow-up.")
    action_response = BrokerAccountActionResponse(
        actionId="action-1",
        accountId="alpaca-core",
        action="refresh",
        status="accepted",
        requestedAt="2026-04-20T13:45:00Z",
        message="Refresh queued.",
        resultingConnectionHealth=BrokerConnectionHealth(
            overallStatus="warning",
            authStatus="reauth_required",
            connectionState="reconnect_required",
            syncStatus="syncing",
        ),
        tradeReadiness="review",
        syncPaused=False,
    )
    listing = BrokerAccountListResponse(accounts=[summary], generatedAt="2026-04-20T13:45:00Z")

    assert summary.accountId == "alpaca-core"
    assert summary.name == "Core Long Only"
    assert summary.accountNumberMasked == "****1234"
    assert summary.highestAlertSeverity == "critical"
    assert detail.capabilities.canReconnect is True
    assert detail.alerts[0].severity == "critical"
    assert detail.syncRuns[0].status == "failed"
    assert reconnect.reason == "Operator initiated reconnect."
    assert pause.paused is False
    assert refresh.force is True
    assert acknowledge.note == "Connector rerouted to manual follow-up."
    assert action_response.resultingConnectionHealth is not None
    assert action_response.resultingConnectionHealth.syncStatus == "syncing"
    assert listing.accounts[0].tradeReadiness == "blocked"


def test_broker_account_onboarding_contracts_capture_discovery_and_create_response() -> None:
    candidate = BrokerAccountOnboardingCandidate(
        candidateId="alpaca:paper:acct-paper",
        provider="alpaca",
        environment="paper",
        suggestedAccountId="alpaca-paper-acct-paper",
        displayName="Alpaca Paper",
        accountNumberMasked="****1234",
        baseCurrency="usd",
        state="available",
        allowedExecutionPostures=["monitor_only", "paper"],
        blockedExecutionPostureReasons={
            "sandbox": "Sandbox execution is only available for sandbox accounts.",
            "live": "Live execution requires live account approval.",
        },
        canOnboard=True,
    )
    candidate_list = BrokerAccountOnboardingCandidateListResponse(
        candidates=[candidate],
        discoveryStatus="completed",
        message="Broker account discovery completed.",
        generatedAt="2026-05-03T20:00:00Z",
    )
    request = BrokerAccountOnboardingRequest(
        candidateId=candidate.candidateId,
        provider="alpaca",
        environment="paper",
        displayName="Alpaca Paper",
        readiness="review",
        executionPosture="paper",
        initialRefresh=True,
        reason="Initial account onboarding for paper trading.",
    )
    account = BrokerAccountSummary(
        accountId=candidate.suggestedAccountId,
        broker="alpaca",
        name="Alpaca Paper",
        baseCurrency="USD",
        tradeReadiness="review",
    )
    audit = BrokerAccountConfigurationAuditRecord(
        auditId="audit-1",
        accountId=account.accountId,
        category="onboarding",
        outcome="saved",
        requestedAt="2026-05-03T20:00:01Z",
        actor="ops@example.com",
        summary="Onboarded broker account.",
        after={"executionPosture": request.executionPosture},
    )
    response = BrokerAccountOnboardingResponse(
        account=account,
        created=True,
        reenabled=False,
        audit=audit,
        message="Broker account onboarded.",
        generatedAt="2026-05-03T20:00:02Z",
    )

    assert candidate.baseCurrency == "USD"
    assert candidate_list.candidates[0].allowedExecutionPostures == ["monitor_only", "paper"]
    assert candidate_list.discoveryStatus == "completed"
    assert request.reason == "Initial account onboarding for paper trading."
    assert response.audit is not None
    assert response.audit.category == "onboarding"
    assert response.account.accountId == "alpaca-paper-acct-paper"


def test_broker_account_configuration_contracts_capture_policy_and_allocation() -> None:
    configuration = BrokerAccountConfiguration(
        accountId="alpaca-core",
        accountName="Core Long Only",
        baseCurrency="usd",
        configurationVersion=4,
        requestedPolicy=BrokerTradingPolicy(
            maxOpenPositions=12,
            maxSinglePositionExposure={"mode": "pct_of_allocatable_capital", "value": 8.5},
            allowedSides=["long"],
            allowedAssetClasses=["equity", "option"],
            requireOrderConfirmation=True,
        ),
        effectivePolicy=BrokerTradingPolicy(
            maxOpenPositions=10,
            maxSinglePositionExposure={"mode": "pct_of_allocatable_capital", "value": 8.0},
            allowedSides=["long"],
            allowedAssetClasses=["equity", "option"],
            requireOrderConfirmation=True,
        ),
        capabilities={
            "canReadBalances": True,
            "canReadPositions": True,
            "canReadOrders": True,
            "canTrade": True,
            "canReadTradingPolicy": True,
            "canWriteTradingPolicy": True,
            "canReadAllocation": True,
            "canWriteAllocation": True,
            "canReleaseTradeConfirmation": True,
        },
        allocation=BrokerStrategyAllocationSummary(
            portfolioName="growth-core",
            portfolioVersion=7,
            allocationMode="percent",
            allocatableCapital=250000.0,
            allocatedPercent=100.0,
            remainingPercent=0.0,
            items=[
                {
                    "sleeveId": "quality-core",
                    "sleeveName": "Quality Core",
                    "strategy": {"strategyName": "quality-trend", "strategyVersion": 4},
                    "allocationMode": "percent",
                    "targetWeightPct": 60.0,
                },
                {
                    "sleeveId": "defensive",
                    "sleeveName": "Defensive",
                    "strategy": {"strategyName": "defensive-value", "strategyVersion": 2},
                    "allocationMode": "percent",
                    "targetWeightPct": 40.0,
                },
            ],
        ),
        warnings=["Current holdings exceed the tighter max-open-position policy."],
        updatedAt="2026-04-24T14:00:00Z",
        updatedBy="desk-op",
        audit=[
            {
                "auditId": "audit-1",
                "accountId": "alpaca-core",
                "category": "trading_policy",
                "outcome": "warning",
                "requestedAt": "2026-04-24T14:00:00Z",
                "actor": "desk-op",
                "requestId": "req-1",
                "grantedRoles": ["AssetAllocation.AccountPolicy.Write"],
                "summary": "Saved tighter trading policy with out-of-policy warning.",
                "before": {"maxOpenPositions": 15},
                "after": {"maxOpenPositions": 12},
            }
        ],
    )
    policy_request = BrokerTradingPolicyUpdateRequest(
        expectedConfigurationVersion=4,
        requestedPolicy=configuration.requestedPolicy,
    )
    allocation_request = BrokerAccountAllocationUpdateRequest(
        expectedConfigurationVersion=4,
        allocationMode="notional_base_ccy",
        allocatableCapital=250000.0,
        items=[
            {
                "sleeveId": "quality-core",
                "strategy": {"strategyName": "quality-trend", "strategyVersion": 4},
                "allocationMode": "notional_base_ccy",
                "targetNotionalBaseCcy": 150000.0,
            },
            {
                "sleeveId": "defensive",
                "strategy": {"strategyName": "defensive-value", "strategyVersion": 2},
                "allocationMode": "notional_base_ccy",
                "targetNotionalBaseCcy": 100000.0,
            },
        ],
    )

    assert configuration.baseCurrency == "USD"
    assert configuration.requestedPolicy.maxSinglePositionExposure is not None
    assert configuration.requestedPolicy.maxSinglePositionExposure.value == 8.5
    assert configuration.allocation.items[0].strategy.strategyName == "quality-trend"
    assert configuration.audit[0].grantedRoles == ["AssetAllocation.AccountPolicy.Write"]
    assert policy_request.expectedConfigurationVersion == 4
    assert allocation_request.items[1].targetNotionalBaseCcy == 100000.0
