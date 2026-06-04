from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from pydantic import TypeAdapter

from asset_allocation_contracts.ai_chat import AiChatRequest, AiChatStreamEvent
from asset_allocation_contracts.backtest import (
    BacktestBenchmarkAttribution,
    BacktestClaimRequest,
    BacktestCompleteRequest,
    BacktestDataQualityEvent,
    BacktestDataQualityEventListResponse,
    BacktestExecutionSettings,
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
    ExitRuleAttributionResponse,
    BacktestReconcileResponse,
    BacktestResultMetadata,
    RollingMetricPointResponse,
    RollingMetricsResponse,
    RunRecordResponse,
    RunPinsResponse,
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
    BrokerAccountActionType,
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
    BrokerTradeApprovalPolicy,
    BrokerTradingPolicy,
    BrokerTradingPolicyUpdateRequest,
    BrokerSyncRun,
    PauseBrokerSyncRequest,
    ReconnectBrokerAccountRequest,
    RemoveBrokerAccountRequest,
    RemoveBrokerAccountResponse,
    RefreshBrokerAccountRequest,
)
from asset_allocation_contracts.deployment_provenance import (
    DeploymentProvenanceSummary,
    DeploymentProvenanceView,
    PipelineRunSummary,
    ResourceDeploymentVersion,
)
from asset_allocation_contracts.pull_request_sync import (
    PullRequestCommitSummary,
    PullRequestSyncRow,
    PullRequestSyncSummary,
    PullRequestSyncView,
    PullRequestWorkItemRef,
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
    CurrencyIntradayBar,
    CurrencyIntradayBarInterval,
    CurrencyIntradayBarsResponse,
    LiveCurrencyPriceSnapshot,
    LiveCurrencyPriceTick,
    LiveMarketPriceStatus,
    LiveStockAggregateSnapshot,
    LiveStockTradeSnapshot,
    LiveStockTradeTick,
    IntradayMonitorClaimResponse,
    IntradayMonitorCompleteRequest,
    IntradayMonitorEvent,
    IntradayMonitorRunSummary,
    IntradayOnDemandEnqueueSummary,
    IntradayOnDemandSymbolConfig,
    IntradayOnDemandSymbolListResponse,
    IntradayOnDemandSymbolUpsertRequest,
    IntradayRefreshClaimRequest,
    IntradayRefreshRequest,
    IntradaySymbolStatus,
    IntradayWatchlistDetail,
    IntradayWatchlistSymbolAppendRequest,
    IntradayWatchlistSymbolAppendResponse,
    IntradayWatchlistUpsertRequest,
    StockAggregateBar,
    StockAggregateBarsResponse,
    StockAggregateInterval,
    StockAggregateStreamEventType,
    StockTradeStreamEventType,
)
from asset_allocation_contracts.job_metadata import RuntimeJobMetadata
from asset_allocation_contracts.notifications import (
    NotificationActionDetailResponse,
    NotificationStatusResponse,
    TradeApprovalCreateRequest,
    TradeApprovalCreateResponse,
    TradeApprovalPayload,
)
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
    StrategySliceAttribution,
)
from asset_allocation_contracts.paths import DataPaths, bucket_letter
from asset_allocation_contracts.ranking import (
    RankingFieldReference,
    RankingGroup,
    RankingSchemaConfig,
)
from asset_allocation_contracts.regime import (
    CANONICAL_DEFAULT_REGIME_VERSION,
    RegimeActivationDecision,
    RegimeGate,
    RegimePolicy,
    RegimeSourceRef,
    RegimeSignal,
    RegimeSnapshot,
    canonical_default_regime_config_errors,
    canonical_default_regime_model_config,
    validate_canonical_default_regime_config,
)
from asset_allocation_contracts.results import ResultsReconcileResponse
from asset_allocation_contracts.strategy_publication import (
    RegimePublicationReconcileMetadata,
    StrategyPublicationReconcileSignalRequest,
)
from asset_allocation_contracts.symbol_enrichment import (
    SymbolCleanupRunReviewResponse,
    SymbolCleanupRunSummary,
    SymbolCleanupWorkReviewItem,
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
from asset_allocation_contracts.stock_screener import (
    StockScreenerPresetListResponse,
    StockScreenerPresetSummary,
    StockScreenerPresetUpsertRequest,
    StockScreenerPresetWorkspace,
    StockScreenerRequest,
    StockScreenerResponse,
    StockScreenerRow,
    StockScreenerSourceCatalogResponse,
    StockScreenerSourceDescriptor,
    StockScreenerSortClause,
)
from asset_allocation_contracts.strategy import (
    ConfigIdentity,
    ConfigReference,
    ConfigRevisionReference,
    ExitPolicyPinImpactRequest,
    ExitPolicyPinImpactResponse,
    ExitPolicyPreset,
    ExitRuleDiagnostic,
    ExitRulePinImpact,
    ExitRulePreviewCandidate,
    ExitRulePreviewRequest,
    ExitRulePreviewResponse,
    ExitRuleSetConfig,
    ExitRuleSetDetailResponse,
    ExitRuleSetRevision,
    ExitRuleSetSummary,
    GeneratedStrategyBacktestHandoff,
    GeneratedStrategyProvenance,
    GeneratedStrategySaveRequest,
    GeneratedStrategySaveResponse,
    RankingSchemaDraftGenerationRequest,
    RankingSchemaDraftGenerationResponse,
    RankingSchemaPreset,
    RankingSchemaSummary,
    RebalancePolicy,
    RebalancePolicyPreset,
    RiskPolicyConfig,
    RiskPolicyConfigDetailResponse,
    RiskPolicyConfigRevision,
    RiskPolicyConfigSummary,
    RegimeStrategyPredicate,
    StrategyComponentRefs,
    StrategyRiskExposureLimits,
    StrategyRiskExposurePolicy,
    StrategyRiskOverlaySet,
    StrategyRiskPolicy,
    StrategyRiskPolicyPreset,
    StrategyRiskVixSpikeHaltPolicy,
    StrategyRegimeAllocation,
    StrategyRegimeGatePlan,
    StrategyRiskTradingPermissions,
    StrategyPositionPolicy,
    StrategyRiskProfileConfig,
    StrategyRiskProfileDetail,
    StrategyRiskProfileSummary,
    StrategyConfig,
    UniverseConfigDraftGenerationRequest,
    UniverseConfigDraftGenerationResponse,
    UniverseConfigPreset,
    UniverseCatalogResponse,
    UNIVERSE_FIELD_DEFINITION_BY_ID,
    UNIVERSE_FIELD_DEFINITIONS,
    UniverseCondition,
    UniverseDefinition,
    UniverseGroup,
    UniversePreviewResponse,
    UniversePreviewRequest,
)
from asset_allocation_contracts.trade_desk import TradeOrderPreviewRequest
from asset_allocation_contracts.ui_config import (
    AuthSessionStatus,
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
    assert payload.regimeSource is not None
    assert payload.regimeSource.modelName == "default-regime"


def test_strategy_config_accepts_pinned_configuration_references_with_resolved_snapshots() -> (
    None
):
    payload = StrategyConfig(
        universeConfigName="large-cap-quality",
        universeConfigVersion=4,
        rankingSchemaName="quality-momentum",
        rankingSchemaVersion=7,
        regimePolicyConfigName="observe-default",
        regimePolicyConfigVersion=2,
        regimePolicy={
            "modelName": "default-regime",
            "modelVersion": 3,
            "mode": "observe_only",
        },
        riskPolicyName="balanced-risk",
        riskPolicyVersion=5,
        strategyRiskPolicy={
            "scope": "strategy",
            "drawdown": {
                "stopLoss": {
                    "thresholdPct": 8,
                    "action": "reduce_exposure",
                    "reductionPct": 50,
                },
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
        raise AssertionError(
            "Expected pinned version without config name to fail validation."
        )


def test_config_revision_reference_normalizes_name() -> None:
    ref = ConfigRevisionReference(name="  core-risk  ", version=3)

    assert ref.name == "core-risk"
    assert ref.version == 3


def test_strategy_config_accepts_component_refs_as_canonical_pins() -> None:
    payload = StrategyConfig(
        regimeSource={"modelName": "default-regime", "modelVersion": 3},
        componentRefs={
            "universe": {"name": "us-large-liquid", "version": 1},
            "ranking": {"name": "quality-momentum", "version": 2},
            "rebalance": {"name": "monthly-last-trading-day", "version": 1},
            "riskPolicy": {"name": "balanced-long-only", "version": 1},
            "exitPolicy": {"name": "rank-decay-exit", "version": 1},
        },
    )

    assert isinstance(payload.componentRefs, StrategyComponentRefs)
    assert payload.componentRefs.universe is not None
    assert payload.componentRefs.universe.name == "us-large-liquid"
    assert payload.componentRefs.ranking is not None
    assert payload.componentRefs.ranking.version == 2
    assert payload.regimeSource is not None
    assert payload.regimeSource.modelVersion == 3


def test_strategy_config_rejects_mismatched_component_ref_and_legacy_pin() -> None:
    try:
        StrategyConfig(
            componentRefs={"universe": {"name": "us-large-liquid", "version": 1}},
            universeConfigName="different-universe",
        )
    except Exception as exc:
        assert "componentRefs.universe" in str(exc)
        assert "config name" in str(exc)
    else:
        raise AssertionError(
            "Expected mismatched componentRefs.universe and universeConfigName to fail validation."
        )

    try:
        StrategyConfig(
            componentRefs={"ranking": {"name": "quality-momentum", "version": 2}},
            universeConfigName="us-large-liquid",
            rankingSchemaName="quality-momentum",
            rankingSchemaVersion=3,
        )
    except Exception as exc:
        assert "componentRefs.ranking" in str(exc)
        assert "config version" in str(exc)
    else:
        raise AssertionError(
            "Expected mismatched componentRefs.ranking and rankingSchemaVersion to fail validation."
        )


def test_strategy_config_accepts_legacy_regime_policy_component_ref_for_compatibility() -> (
    None
):
    payload = StrategyConfig(
        componentRefs={
            "universe": {"name": "us-large-liquid", "version": 1},
            "regimePolicy": {"name": "observe-only-default", "version": 1},
        }
    )

    assert payload.componentRefs is not None
    assert payload.componentRefs.regimePolicy is not None
    assert payload.componentRefs.regimePolicy.name == "observe-only-default"


def test_regime_source_ref_requires_model_name() -> None:
    source = RegimeSourceRef(modelName="  default-regime  ", modelVersion=3)

    assert source.modelName == "default-regime"
    assert source.modelVersion == 3

    try:
        RegimeSourceRef(modelName="   ")
    except Exception as exc:
        assert "modelName" in str(exc)
    else:
        raise AssertionError(
            "Expected blank regime source model name to fail validation."
        )


def test_regime_gate_normalizes_blocked_lists_and_rejects_legacy_active_shape() -> None:
    gate = RegimeGate(
        blockedRegimes=["liquidity_stress", "liquidity_stress", "high_volatility"],
    )

    assert gate.blockedRegimes == ["liquidity_stress", "high_volatility"]

    legacy_inactive = RegimeGate(
        inactiveInRegimes=["liquidity_stress", "liquidity_stress"]
    )
    assert legacy_inactive.blockedRegimes == ["liquidity_stress"]

    try:
        RegimeGate(activeInRegimes=["trending_up"])
    except Exception as exc:
        assert "blockedRegimes only" in str(exc)
    else:
        raise AssertionError(
            "Expected legacy activeInRegimes gates to fail validation."
        )


def test_ranking_schema_rejects_legacy_regime_gate_authoring() -> None:
    try:
        RankingSchemaConfig.model_validate(
            {
                "universeConfigName": "us-large-liquid",
                "regimeGate": {"blockedRegimes": ["liquidity_stress"]},
                "groups": [
                    {
                        "name": "momentum",
                        "factors": [
                            {
                                "name": "return_126d",
                                "table": "market",
                                "column": "return_126d",
                                "direction": "desc",
                                "weight": 1,
                            }
                        ],
                    }
                ],
            }
        )
    except Exception as exc:
        assert "regimeGate" in str(exc)
    else:
        raise AssertionError(
            "Expected ranking schema regimeGate authoring to fail validation."
        )


def test_component_configs_accept_regime_gates() -> None:
    ranking = RankingSchemaConfig(
        universeConfigName="us-large-liquid",
        groups=[
            {
                "name": "momentum",
                "factors": [
                    {
                        "name": "return_126d",
                        "table": "market",
                        "column": "return_126d",
                        "direction": "desc",
                        "weight": 1,
                    }
                ],
            }
        ],
    )
    rebalance = RebalancePolicy(regimeGate={"blockedRegimes": ["high_volatility"]})
    risk = RiskPolicyConfig(
        policy={
            "scope": "strategy",
            "drawdown": {
                "stopLoss": {
                    "thresholdPct": 8,
                    "action": "reduce_exposure",
                    "reductionPct": 50,
                },
            },
            "marketStress": {
                "regimeGate": {"blockedRegimes": ["liquidity_stress"]},
            },
        },
    )
    exits = ExitRuleSetConfig(
        regimeGate={"blockedRegimes": ["liquidity_stress"]},
        exits=[{"id": "stop-8", "type": "stop_loss_fixed", "value": 0.08}],
    )
    position = StrategyPositionPolicy(regimeGate={"blockedRegimes": ["trending_down"]})

    assert ranking.universeConfigName == "us-large-liquid"
    assert rebalance.regimeGate is not None
    assert rebalance.regimeGate.blockedRegimes == ["high_volatility"]
    assert position.regimeGate is not None
    assert position.regimeGate.blockedRegimes == ["trending_down"]
    assert risk.policy.marketStress is not None
    assert risk.policy.marketStress.regimeGate is not None
    assert risk.policy.marketStress.regimeGate.blockedRegimes == ["liquidity_stress"]
    assert exits.regimeGate is not None
    assert exits.regimeGate.blockedRegimes == ["liquidity_stress"]


def test_strategy_config_accepts_weighted_regime_strategy_playbook() -> None:
    payload = StrategyConfig(
        universe=UniverseDefinition(
            root=UniverseGroup(
                clauses=[
                    UniverseCondition(field="market.close", operator="gt", value=0),
                ]
            )
        ),
        regimeSource={"modelName": "default-regime", "modelVersion": 3},
        regimeGates={
            "risk-on": {
                "when": {
                    "requiredRegimes": ["trending_up", "trending_up"],
                    "blockedRegimes": ["liquidity_stress"],
                },
                "allocations": [
                    {
                        "strategyRef": {"name": "quality-momentum", "version": 7},
                        "weight": 2,
                    },
                    {
                        "strategyRef": {"name": "defensive-value", "version": 3},
                        "weight": 1,
                    },
                ],
            }
        },
    )

    assert isinstance(payload.regimeGates["risk-on"], StrategyRegimeGatePlan)
    assert payload.regimeGates["risk-on"].when.requiredRegimes == ["trending_up"]
    assert (
        payload.regimeGates["risk-on"].allocations[0].strategyRef.name
        == "quality-momentum"
    )
    assert payload.regimeGates["risk-on"].allocations[0].weight == 2


def test_strategy_config_requires_regime_source_for_weighted_regime_playbook() -> None:
    try:
        StrategyConfig(
            universe=UniverseDefinition(
                root=UniverseGroup(
                    clauses=[
                        UniverseCondition(field="market.close", operator="gt", value=0),
                    ]
                )
            ),
            regimeGates={
                "risk-on": {
                    "when": {"requiredRegimes": ["trending_up"]},
                    "allocations": [
                        {
                            "strategyRef": {"name": "quality-momentum", "version": 7},
                            "weight": 1,
                        },
                    ],
                }
            },
        )
    except Exception as exc:
        assert "regimeGates requires regimeSource" in str(exc)
    else:
        raise AssertionError(
            "Expected regimeGates without regimeSource to fail validation."
        )


def test_weighted_regime_playbook_rejects_invalid_entries() -> None:
    try:
        RegimeStrategyPredicate(
            requiredRegimes=["trending_up"], blockedRegimes=["trending_up"]
        )
    except Exception as exc:
        assert "both require and block" in str(exc)
    else:
        raise AssertionError(
            "Expected overlapping required and blocked regimes to fail validation."
        )

    try:
        StrategyRegimeAllocation(
            strategyRef={"name": "quality-momentum", "version": 7}, weight=0
        )
    except Exception as exc:
        assert "weight" in str(exc)
    else:
        raise AssertionError(
            "Expected non-positive allocation weight to fail validation."
        )

    try:
        StrategyRegimeGatePlan(
            when={"requiredRegimes": ["trending_up"]},
            allocations=[],
        )
    except Exception as exc:
        assert "allocations" in str(exc)
    else:
        raise AssertionError(
            "Expected empty regime gate allocations to fail validation."
        )


def test_strategy_config_requires_regime_source_for_inline_component_gates() -> None:
    base_payload = {
        "universe": {
            "root": {
                "clauses": [{"field": "market.close", "operator": "gt", "value": 0}],
            }
        }
    }

    for payload in (
        {
            **base_payload,
            "rebalancePolicy": {"regimeGate": {"blockedRegimes": ["liquidity_stress"]}},
        },
        {
            **base_payload,
            "positionPolicy": {
                "regimeGate": {"blockedRegimes": ["liquidity_stress"]},
                "targetPositionSize": {
                    "mode": "pct_of_allocatable_capital",
                    "value": 5,
                },
                "maxPositionSize": {"mode": "pct_of_allocatable_capital", "value": 8},
                "maxOpenPositions": 10,
            },
        },
        {
            **base_payload,
            "strategyRiskPolicy": {
                "marketStress": {"regimeGate": {"blockedRegimes": ["liquidity_stress"]}}
            },
        },
        {**base_payload, "exitRegimeGate": {"blockedRegimes": ["liquidity_stress"]}},
    ):
        try:
            StrategyConfig.model_validate(payload)
        except Exception as exc:
            assert "regimeSource" in str(exc)
        else:
            raise AssertionError(
                f"Expected missing regime source to fail for {payload!r}"
            )

    resolved = StrategyConfig.model_validate(
        {
            **base_payload,
            "regimeSource": {"modelName": "default-regime", "modelVersion": 3},
            "rebalancePolicy": {"regimeGate": {"blockedRegimes": ["liquidity_stress"]}},
            "positionPolicy": {
                "regimeGate": {"blockedRegimes": ["trending_down"]},
                "targetPositionSize": {
                    "mode": "pct_of_allocatable_capital",
                    "value": 5,
                },
                "maxPositionSize": {"mode": "pct_of_allocatable_capital", "value": 8},
                "maxOpenPositions": 10,
            },
            "strategyRiskPolicy": {
                "marketStress": {"regimeGate": {"blockedRegimes": ["liquidity_stress"]}}
            },
            "exitRegimeGate": {"blockedRegimes": ["liquidity_stress"]},
        }
    )

    assert resolved.regimeSource is not None
    assert resolved.rebalancePolicy is not None
    assert resolved.rebalancePolicy.regimeGate is not None
    assert resolved.positionPolicy is not None
    assert resolved.positionPolicy.regimeGate is not None
    assert resolved.strategyRiskPolicy is not None
    assert resolved.strategyRiskPolicy.marketStress is not None
    assert resolved.strategyRiskPolicy.marketStress.regimeGate is not None
    assert resolved.exitRegimeGate is not None


def test_config_reference_requires_integer_version() -> None:
    try:
        ConfigReference(name="us-large-liquid", version="v1")
    except Exception as exc:
        assert "version" in str(exc)
    else:
        raise AssertionError("Expected non-integer config version to fail validation.")


def test_stock_screener_contracts_normalize_filters_and_capture_facets() -> None:
    request = StockScreenerRequest(
        q="  ms ",
        as_of="2026-05-04",
        sectors="Technology, Healthcare, technology",
        countries=[" US ", "CA", "US"],
        has_silver=True,
        has_gold=False,
        min_return_5d=0.01,
        max_return_5d=0.08,
        sort="ranking_score",
        sorts=[
            {"key": "ranking_score", "direction": "desc"},
            {"key": "return_5d", "direction": "desc"},
        ],
        strategy_name="quality-trend",
        ranking_schema_name="  quality-momentum  ",
        ranking_schema_version=2,
    )
    response = StockScreenerResponse(
        asOf="2026-05-04",
        total=1,
        limit=250,
        offset=0,
        filters=request,
        summary={
            "universeCount": 3,
            "totalResultCount": 1,
            "returnedCount": 1,
            "coverage": {
                "total": 3,
                "withSilver": 2,
                "withGold": 1,
                "missingSilver": 1,
                "missingGold": 2,
            },
        },
        facets={
            "sectors": [{"value": "Technology", "count": 1}],
            "industries": [{"value": "Software", "count": 1}],
            "countries": [{"value": "US", "count": 1}],
        },
        ranking={
            "schemaName": "quality-momentum",
            "schemaVersion": 2,
            "componentNames": ["Momentum", "Quality"],
        },
        rows=[
            StockScreenerRow(
                symbol=" msft ",
                name="Microsoft Corp.",
                sector="Technology",
                industry="Software",
                close=421.03,
                return1d=-0.004,
                return5d=0.012,
                vol20d=0.18,
                drawdown1y=-0.05,
                atr14d=5.3,
                compressionScore=0.35,
                volumePctRank252d=0.8,
                hasSilver=True,
                hasGold=1,
                rankingRank=3,
                rankingOverallScore=0.91,
                rankingComponents=[
                    {"name": "Momentum", "score": 0.87},
                    {"name": "Quality", "score": None},
                ],
            )
        ],
    )

    assert request.q == "ms"
    assert request.ranking_schema_name == "quality-momentum"
    assert request.ranking_schema_version == 2
    assert request.sorts is not None
    assert [clause.key for clause in request.sorts] == ["ranking_score", "return_5d"]
    assert request.sectors == ["Technology", "Healthcare"]
    assert request.countries == ["US", "CA"]
    assert response.rows[0].symbol == "MSFT"
    assert response.rows[0].rankingRank == 3
    assert response.rows[0].rankingComponents is not None
    assert response.rows[0].rankingComponents[0].name == "Momentum"
    assert response.ranking is not None
    assert response.ranking.componentNames == ["Momentum", "Quality"]
    assert response.summary is not None
    assert response.summary.coverage.missingGold == 2
    assert response.facets is not None
    assert response.facets.sectors[0].value == "Technology"


def test_stock_screener_source_descriptor_migrates_legacy_layer_and_dynamic_fields() -> None:
    request = StockScreenerRequest(
        source_layer="gold",
        selected_columns=["symbol", "return_5d", "symbol", "  volume  ", ""],
        dynamic_filters=[
            {"column_name": "volume_pct_rank_252d", "operator": "gte", "value": 0.8},
            {"column_name": "sector", "operator": "contains", "value": "Tech"},
        ],
        dynamic_sorts=[{"column_name": "volume_pct_rank_252d", "direction": "desc"}],
    )

    assert request.source is not None
    assert request.source.kind == "layer"
    assert request.source.source_layer == "gold"
    assert request.selected_columns == ["symbol", "return_5d", "volume"]
    assert request.dynamic_filters is not None
    assert request.dynamic_filters[0].column_name == "volume_pct_rank_252d"
    assert request.dynamic_sorts is not None
    assert request.dynamic_sorts[0].column_name == "volume_pct_rank_252d"

    workspace = StockScreenerPresetWorkspace.model_validate(
        {
            "source_layer": "platinum",
            "sort": "volume",
            "direction": "desc",
            "visible_column_ids": ["symbol"],
        }
    )
    assert workspace.source is not None
    assert workspace.source.kind == "layer"
    assert workspace.source.source_layer == "platinum"


def test_stock_screener_table_source_catalog_and_response_dynamic_columns() -> None:
    source = StockScreenerSourceDescriptor(
        kind="table",
        schema_name="gold",
        table_name="finance_data",
        symbol_column="symbol",
        as_of_column="date",
        selected_columns=["market_cap", "pe_ratio", "market_cap"],
    )
    catalog = StockScreenerSourceCatalogResponse(
        sources=[
            {
                "source": source,
                "label": "Finance Data",
                "description": "Gold finance factors.",
                "capabilities": ["stock_identity", "as_of_date", "screening"],
                "default_column_names": ["market_cap", "pe_ratio"],
                "columns": [
                    {
                        "name": "market_cap",
                        "label": "Market Cap",
                        "data_type": "numeric",
                        "value_kind": "number",
                        "operators": ["eq", "gte", "lte"],
                        "default_visible": True,
                    }
                ],
            }
        ]
    )
    response = StockScreenerResponse(
        asOf="2026-05-04",
        total=1,
        limit=250,
        offset=0,
        source=source,
        sourceColumns=catalog.sources[0].columns,
        rows=[
            {
                "symbol": "MSFT",
                "values": {
                    "market_cap": 3_100_000_000_000,
                    "pe_ratio": 34.2,
                    "as_of": "2026-05-04",
                },
            }
        ],
    )

    assert source.selected_columns == ["market_cap", "pe_ratio"]
    assert catalog.sources[0].capabilities == ["stock_identity", "as_of_date", "screening"]
    assert response.source is not None
    assert response.source.table_name == "finance_data"
    assert response.sourceColumns[0].name == "market_cap"
    assert response.rows[0].values["market_cap"] == 3_100_000_000_000


def test_stock_screener_source_descriptor_rejects_invalid_sources() -> None:
    invalid_payloads = (
        {"kind": "table", "schema_name": "gold"},
        {"kind": "table", "schema_name": "gold", "table_name": "market_data", "source_layer": "gold"},
        {"kind": "layer", "source_layer": "gold", "schema_name": "gold", "table_name": "market_data"},
    )
    for payload in invalid_payloads:
        try:
            StockScreenerSourceDescriptor.model_validate(payload)
        except Exception:
            continue
        raise AssertionError(f"Expected source descriptor validation to reject {payload!r}.")


def test_stock_screener_sort_stack_deduplicates_first_clause() -> None:
    request = StockScreenerRequest(
        sort="return_5d",
        sorts=[
            StockScreenerSortClause(key="return_5d", direction="desc"),
            StockScreenerSortClause(key="volume_pct_rank_252d", direction="desc"),
            StockScreenerSortClause(key="return_5d", direction="asc"),
        ],
    )

    assert request.sorts is not None
    assert [(clause.key, clause.direction) for clause in request.sorts] == [
        ("return_5d", "desc"),
        ("volume_pct_rank_252d", "desc"),
    ]


def test_stock_screener_sort_stack_rejects_invalid_clause_values() -> None:
    try:
        StockScreenerRequest(sorts=[{"key": "not_a_factor", "direction": "desc"}])
    except Exception as exc:
        assert "not_a_factor" in str(exc)
    else:
        raise AssertionError("Expected invalid screener sort key to fail validation.")

    try:
        StockScreenerRequest(sorts=[{"key": "return_5d", "direction": "sideways"}])
    except Exception as exc:
        assert "sideways" in str(exc)
    else:
        raise AssertionError(
            "Expected invalid screener sort direction to fail validation."
        )


def test_stock_screener_sort_stack_rejects_ranking_sort_without_schema() -> None:
    try:
        StockScreenerRequest(sorts=[{"key": "ranking_score", "direction": "desc"}])
    except Exception as exc:
        assert "ranking_score" in str(exc)
        assert "ranking_schema_name" in str(exc)
    else:
        raise AssertionError(
            "Expected ranking sort without ranking schema to fail validation."
        )


def test_stock_screener_contract_rejects_inverted_numeric_ranges() -> None:
    try:
        StockScreenerRequest(min_volume_pct_rank_252d=0.9, max_volume_pct_rank_252d=0.2)
    except Exception as exc:
        assert "min_volume_pct_rank_252d" in str(exc)
        assert "max_volume_pct_rank_252d" in str(exc)
    else:
        raise AssertionError(
            "Expected inverted screener numeric range to fail validation."
        )


def test_stock_screener_contract_rejects_ranking_version_without_name() -> None:
    try:
        StockScreenerRequest(ranking_schema_version=2)
    except Exception as exc:
        assert "ranking_schema_version" in str(exc)
        assert "ranking_schema_name" in str(exc)
    else:
        raise AssertionError(
            "Expected ranking schema version without name to fail validation."
        )


def test_stock_screener_contract_rejects_ranking_without_strategy_context() -> None:
    try:
        StockScreenerRequest(ranking_schema_name="quality", ranking_schema_version=2)
    except Exception as exc:
        assert "ranking_schema_name" in str(exc)
        assert "strategy_name" in str(exc)
    else:
        raise AssertionError(
            "Expected ranking schema selection without strategy context to fail validation."
        )


def test_stock_screener_preset_workspace_normalizes_saved_state() -> None:
    workspace = StockScreenerPresetWorkspace(
        q="  ms ",
        as_of="2026-05-04",
        source_layer="platinum",
        sort="ranking_score",
        direction="desc",
        sorts=[
            {"key": "ranking_score", "direction": "desc"},
            {"key": "return_5d", "direction": "desc"},
            {"key": "ranking_score", "direction": "asc"},
        ],
        strategy_name=" quality-trend ",
        ranking_schema_name=" quality-momentum ",
        ranking_schema_version=2,
        sectors="Technology, Healthcare, technology",
        countries=[" US ", "CA", "US"],
        min_return_5d=0.01,
        max_return_5d=0.08,
        visible_column_ids=["symbol", "return_5d", "symbol", "  volume  ", ""],
    )
    upsert = StockScreenerPresetUpsertRequest(
        name="  Momentum desk ",
        description="  Active quality/momentum view  ",
        workspace=workspace,
    )
    summary = StockScreenerPresetSummary(
        preset_id="preset-1",
        name=upsert.name,
        description=upsert.description,
        workspace=upsert.workspace,
    )
    listing = StockScreenerPresetListResponse(presets=[summary])

    assert workspace.q == "ms"
    assert workspace.source_layer == "platinum"
    assert workspace.source is not None
    assert workspace.source.source_layer == "platinum"
    assert workspace.strategy_name == "quality-trend"
    assert workspace.ranking_schema_name == "quality-momentum"
    assert workspace.sectors == ["Technology", "Healthcare"]
    assert workspace.countries == ["US", "CA"]
    assert workspace.sorts is not None
    assert [(clause.key, clause.direction) for clause in workspace.sorts] == [
        ("ranking_score", "desc"),
        ("return_5d", "desc"),
    ]
    assert workspace.visible_column_ids == ["symbol", "return_5d", "volume"]
    assert upsert.name == "Momentum desk"
    assert upsert.description == "Active quality/momentum view"
    assert listing.presets[0].preset_id == "preset-1"


def test_stock_screener_preset_workspace_rejects_invalid_payloads() -> None:
    for payload, expected in (
        ({"source_layer": "silver"}, "source_layer"),
        ({"min_volume": 100, "max_volume": 10}, "min_volume"),
        ({"ranking_schema_version": 2}, "ranking_schema_name"),
        (
            {"sorts": [{"key": "ranking_score", "direction": "desc"}]},
            "ranking_schema_name",
        ),
        ({"visible_column_ids": "symbol,volume"}, "visible_column_ids"),
        ({"unknown_field": True}, "unknown_field"),
    ):
        try:
            StockScreenerPresetWorkspace.model_validate(payload)
        except Exception as exc:
            assert expected in str(exc)
        else:
            raise AssertionError(
                f"Expected StockScreenerPresetWorkspace to reject {payload!r}."
            )


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
                "factors": [
                    {
                        "name": "return_126d",
                        "table": "market_data",
                        "column": "return_126d",
                    }
                ],
            }
        ]
    }
    reusable_rebalance = {
        "cadence": "monthly",
        "dayRule": "last_trading_day",
        "anchor": "next_open",
    }
    risk_policy = {
        "scope": "strategy",
        "drawdown": {
            "stopLoss": {
                "thresholdPct": 8,
                "action": "reduce_exposure",
                "reductionPct": 50,
            },
        },
    }
    exit_policy = {
        "exits": [{"id": "rank-decay", "type": "rank_decay", "rankThreshold": 40}]
    }
    cases = [
        (UniverseConfigPreset, {"identity": identity, "config": universe}),
        (RankingSchemaPreset, {"identity": identity, "config": ranking}),
        (RebalancePolicyPreset, {"identity": identity, "config": reusable_rebalance}),
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


def test_strategy_position_policy_defaults_to_equity_without_changing_legacy_configs() -> (
    None
):
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
            "positionVolatilityTolerance": {
                "metric": "atr_14d_pct_of_close",
                "maxPct": 12,
            },
            "requireOrderConfirmation": True,
        },
    )

    assert payload.positionPolicy is not None
    assert payload.positionPolicy.targetPositionSize is not None
    assert payload.positionPolicy.targetPositionSize.value == 5
    assert payload.positionPolicy.allowedAssetClasses == ["equity", "option"]
    assert payload.positionPolicy.positionVolatilityTolerance is not None
    assert (
        payload.positionPolicy.positionVolatilityTolerance.metric
        == "atr_14d_pct_of_close"
    )
    assert payload.positionPolicy.requireOrderConfirmation is True


def test_strategy_position_policy_rejects_invalid_percentage_limit() -> None:
    try:
        StrategyPositionPolicy(
            targetPositionSize={"mode": "pct_of_allocatable_capital", "value": 101}
        )
    except Exception as exc:
        assert "cannot exceed 100" in str(exc)
    else:
        raise AssertionError(
            "Expected validation failure for oversized percentage position limit."
        )


def test_strategy_position_policy_rejects_non_positive_volatility_tolerance() -> None:
    try:
        StrategyPositionPolicy(
            positionVolatilityTolerance={
                "metric": "realized_vol_20d",
                "maxPct": 0,
            }
        )
    except Exception as exc:
        assert "maxPct" in str(exc)
    else:
        raise AssertionError(
            "Expected validation failure for non-positive volatility tolerance."
        )


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
            positionPolicy={
                "targetPositionSize": {
                    "mode": "pct_of_allocatable_capital",
                    "value": 40,
                }
            },
        )
    except Exception as exc:
        assert "cannot allocate more than 100%" in str(exc)
    else:
        raise AssertionError(
            "Expected validation failure for long-only over-allocation."
        )


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
                "targetPositionSize": {
                    "mode": "pct_of_allocatable_capital",
                    "value": 5,
                },
                "maxPositionSize": {"mode": "notional_base_ccy", "value": 25_000},
                "maxOpenPositions": 20,
            },
        },
        {
            "presetClass": "balanced",
            "positionPolicy": {
                "targetPositionSize": {
                    "mode": "pct_of_allocatable_capital",
                    "value": 8,
                },
                "maxPositionSize": {"mode": "pct_of_allocatable_capital", "value": 5},
                "maxOpenPositions": 20,
            },
        },
    ):
        try:
            StrategyRiskProfileConfig.model_validate(invalid_payload)
        except Exception as exc:
            assert (
                "Strategy risk profiles require targetPositionSize" in str(exc)
                or "share a mode" in str(exc)
                or "greater than or equal" in str(exc)
            )
        else:
            raise AssertionError(
                "Expected validation failure for incomplete or invalid risk profile policy."
            )


def test_strategy_risk_profile_summary_and_detail_support_usage_metadata() -> None:
    summary = StrategyRiskProfileSummary(
        name="balanced",
        description="Default balanced posture.",
        presetClass="balanced",
        version=2,
        isSystem=True,
        usageCount=14,
        regimeGate={"blockedRegimes": ["high_volatility"]},
    )
    detail = StrategyRiskProfileDetail(
        **summary.model_dump(),
        config={
            "presetClass": "balanced",
            "positionPolicy": {
                "targetPositionSize": {
                    "mode": "pct_of_allocatable_capital",
                    "value": 5,
                },
                "maxPositionSize": {"mode": "pct_of_allocatable_capital", "value": 8},
                "maxOpenPositions": 20,
                "positionVolatilityTolerance": {
                    "metric": "realized_vol_20d",
                    "maxPct": 18,
                },
            },
        },
    )

    assert detail.name == "balanced"
    assert detail.isSystem is True
    assert detail.regimeGate is not None
    assert detail.regimeGate.blockedRegimes == ["high_volatility"]
    assert detail.config.positionPolicy.maxOpenPositions == 20
    assert detail.config.positionPolicy.positionVolatilityTolerance is not None
    assert detail.config.positionPolicy.positionVolatilityTolerance.maxPct == 18


def test_strategy_config_requires_position_policy_snapshot_when_risk_profile_name_is_set() -> (
    None
):
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
        raise AssertionError(
            "Expected validation failure for incomplete risk profile strategy config."
        )


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
            "positionVolatilityTolerance": {
                "metric": "realized_vol_60d",
                "maxPct": 22,
            },
        },
    )

    assert payload.riskProfileName == "balanced"
    assert payload.positionPolicy is not None
    assert payload.positionPolicy.positionVolatilityTolerance is not None
    assert (
        payload.positionPolicy.positionVolatilityTolerance.metric == "realized_vol_60d"
    )


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
            "drawdown": {
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
            "exposure": {
                "volatilityTolerance": {
                    "metric": "realized_vol_20d",
                    "maxPct": 16,
                },
                "limits": {
                    "drawdownReducePct": 8,
                    "drawdownBlockPct": 12,
                },
            },
        },
    )

    assert payload.rebalancePolicy is not None
    assert payload.rebalancePolicy.intervalBars == 3
    assert payload.strategyRiskPolicy is not None
    assert payload.strategyRiskPolicy.drawdown is not None
    assert payload.strategyRiskPolicy.drawdown.stopLoss is not None
    assert payload.strategyRiskPolicy.drawdown.stopLoss.thresholdPct == 8
    assert payload.strategyRiskPolicy.exposure is not None
    assert payload.strategyRiskPolicy.exposure.volatilityTolerance is not None
    assert (
        payload.strategyRiskPolicy.exposure.volatilityTolerance.metric
        == "realized_vol_20d"
    )
    assert payload.strategyRiskPolicy.drawdown.reentry.cooldownBars == 12


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
    for cadence in ("daily", "weekly", "monthly", "quarterly"):
        policy = RebalancePolicy(
            cadence=cadence,
            dayRule="last_trading_day",
            anchor="next_open",
            tradeDelayBars=1,
            driftThresholdBps=50,
            maxTurnoverPerRebalance=0.35,
        )

        assert policy.cadence == cadence
        assert policy.dayRule == "last_trading_day"
        assert policy.anchor == "next_open"

    try:
        RebalancePolicy(cadence="monthly")
    except Exception as exc:
        assert "cadence, dayRule, and anchor together" in str(exc)
    else:
        raise AssertionError(
            "Expected partial reusable rebalance fields to fail validation."
        )


def test_reusable_rebalance_policy_rejects_invalid_turnover_and_presets_require_calendar_fields() -> (
    None
):
    try:
        RebalancePolicy(
            cadence="annual", dayRule="last_trading_day", anchor="next_open"
        )
    except Exception as exc:
        assert "cadence" in str(exc)
    else:
        raise AssertionError(
            "Expected unsupported reusable rebalance cadence to fail validation."
        )

    try:
        RebalancePolicy(
            cadence="monthly", dayRule="middle_trading_day", anchor="next_open"
        )
    except Exception as exc:
        assert "dayRule" in str(exc)
    else:
        raise AssertionError(
            "Expected unsupported reusable rebalance dayRule to fail validation."
        )

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
        raise AssertionError(
            "Expected maxTurnoverPerRebalance above 1.0 to fail validation."
        )

    try:
        RebalancePolicyPreset(
            identity={"name": "monthly-last-trading-day", "version": 1},
            config={"frequency": "monthly"},
        )
    except Exception as exc:
        assert "cadence, dayRule, and anchor" in str(exc)
    else:
        raise AssertionError(
            "Expected reusable rebalance preset to require calendar fields."
        )


def test_strategy_risk_policy_rejects_ambiguous_enabled_empty_policy() -> None:
    try:
        StrategyRiskPolicy()
    except Exception as exc:
        assert "drawdown stopLoss, takeProfit, or reentry control" in str(exc)
    else:
        raise AssertionError(
            "Expected enabled empty strategy risk policy to fail validation."
        )


def test_strategy_risk_policy_rejects_flat_v1_payload_keys() -> None:
    for field_name in (
        "stopLoss",
        "takeProfit",
        "reentry",
        "exposureLimits",
        "strategyVolatilityTolerance",
        "tradingPermissions",
        "liquidityLimits",
        "overlays",
        "vixSpikeHalt",
        "dataQualityGates",
    ):
        try:
            StrategyRiskPolicy.model_validate({field_name: {}})
        except Exception as exc:
            assert field_name in str(exc)
            assert "extra" in str(exc).lower()
        else:
            raise AssertionError(
                f"Expected flat v1 key {field_name!r} to fail validation."
            )


def test_strategy_risk_policy_accepts_reentry_only_controls() -> None:
    policy = StrategyRiskPolicy(
        drawdown={"reentry": {"cooldownBars": 3, "requireApproval": True}}
    )

    assert policy.drawdown is not None
    assert policy.drawdown.stopLoss is None
    assert policy.drawdown.takeProfit is None
    assert policy.drawdown.reentry.cooldownBars == 3
    assert policy.drawdown.reentry.requireApproval is True


def test_strategy_risk_policy_accepts_complete_policy_envelope() -> None:
    policy = StrategyRiskPolicy(
        operatingMode="balanced_long_short",
        drawdown={
            "stopLoss": {
                "thresholdPct": 6,
                "action": "reduce_exposure",
                "reductionPct": 35,
            },
        },
        exposure={
            "limits": {
                "maxGrossExposurePct": 135,
                "maxNetExposurePct": 65,
                "maxSingleNamePct": 6,
                "maxSectorPct": 25,
                "maxCorrelatedClusterPct": 35,
                "maxFactorBetaAbs": 1.4,
                "dailyLossLimitPct": 2.5,
                "weeklyLossLimitPct": 5,
                "drawdownReducePct": 6,
                "drawdownBlockPct": 9,
            },
            "volatilityTolerance": {
                "metric": "realized_vol_60d",
                "maxPct": 14,
            },
        },
        trading={
            "allowedSides": ["long", "short"],
            "allowedAssetClasses": ["equity", "option"],
            "optionsMode": "defined_risk_only",
            "allowLiveOrders": False,
            "requireOrderConfirmation": True,
            "requireDifferentApprover": True,
            "requireBorrowLocate": True,
        },
        liquidity={
            "maxAdvParticipationPct": 7.5,
            "minLiquidityScore": 60,
            "maxExitHorizonDays": 3,
            "maxBidAskSpreadBps": 50,
            "maxSlippageBps": 35,
        },
        marketStress={
            "vixSpikeHalt": {
                "threshold": 32,
                "streakBars": 2,
                "cooldownBars": 2,
            },
            "overlays": {
                "regime": [
                    {
                        "id": "high-vol-de-risk",
                        "trigger": "regime=high_volatility",
                        "action": "reduce_exposure",
                        "exposureReductionPct": 35,
                    }
                ],
                "event": [
                    {
                        "id": "earnings-blackout",
                        "trigger": "earnings_within=2d",
                        "action": "block_new_orders",
                        "requireApproval": True,
                    }
                ],
            },
        },
        dataQuality={
            "maxQuoteAgeSeconds": 900,
            "maxSecurityMasterAgeSeconds": 86400,
            "minVendorQuorum": 2,
            "requireSymbolIdentityLock": True,
            "corporateActionPolicy": "freeze",
            "requiredAdjustmentStatuses": ["split_adjusted"],
            "minCoveragePct": 95,
        },
        audit={"auditRetentionDays": 2555},
    )

    assert policy.operatingMode == "balanced_long_short"
    assert policy.drawdown is not None
    assert policy.drawdown.stopLoss is not None
    assert policy.drawdown.stopLoss.thresholdPct == 6
    assert policy.exposure is not None
    assert policy.exposure.limits is not None
    assert policy.exposure.limits.maxGrossExposurePct == 135
    assert policy.exposure.volatilityTolerance is not None
    assert policy.exposure.volatilityTolerance.metric == "realized_vol_60d"
    assert policy.trading is not None
    assert policy.trading.allowedSides == ["long", "short"]
    assert policy.trading.optionsMode == "defined_risk_only"
    assert policy.liquidity is not None
    assert policy.liquidity.maxAdvParticipationPct == 7.5
    assert policy.marketStress is not None
    assert policy.marketStress.vixSpikeHalt is not None
    assert policy.marketStress.vixSpikeHalt.threshold == 32
    assert policy.marketStress.vixSpikeHalt.streakBars == 2
    assert policy.marketStress.vixSpikeHalt.cooldownBars == 2
    assert policy.marketStress.overlays is not None
    assert policy.marketStress.overlays.regime[0].id == "high-vol-de-risk"
    assert policy.dataQuality is not None
    assert policy.dataQuality.requiredAdjustmentStatuses == ["split_adjusted"]


def test_complete_strategy_risk_policy_rejects_unsafe_or_ambiguous_controls() -> None:
    invalid_payloads = (
        (
            StrategyRiskExposureLimits,
            {"dailyLossLimitPct": 6, "weeklyLossLimitPct": 3},
            "weeklyLossLimitPct",
        ),
        (
            StrategyRiskTradingPermissions,
            {"allowedSides": ["long", "short"], "requireBorrowLocate": False},
            "borrow/locate",
        ),
        (
            StrategyRiskTradingPermissions,
            {"allowLiveOrders": True, "requireOrderConfirmation": False},
            "order confirmation",
        ),
        (
            StrategyRiskTradingPermissions,
            {"allowedAssetClasses": ["equity"], "optionsMode": "defined_risk_only"},
            "option in allowedAssetClasses",
        ),
        (
            StrategyRiskOverlaySet,
            {
                "regime": [
                    {
                        "id": "duplicate",
                        "trigger": "regime=high_volatility",
                        "action": "warn",
                    }
                ],
                "event": [
                    {
                        "id": "duplicate",
                        "trigger": "earnings_within=2d",
                        "action": "warn",
                    }
                ],
            },
            "Duplicate risk overlay id",
        ),
        (
            StrategyRiskVixSpikeHaltPolicy,
            {"threshold": 0, "streakBars": 2, "cooldownBars": 2},
            "greater than 0",
        ),
        (
            StrategyRiskVixSpikeHaltPolicy,
            {"threshold": 32, "streakBars": 0, "cooldownBars": 2},
            "greater than or equal to 1",
        ),
        (
            StrategyRiskVixSpikeHaltPolicy,
            {"threshold": 32, "streakBars": 2, "cooldownBars": 0},
            "greater than or equal to 1",
        ),
        (
            StrategyRiskExposurePolicy,
            {
                "volatilityTolerance": {
                    "metric": "atr_14d_pct_of_close",
                    "maxPct": 12,
                }
            },
            "exposure.volatilityTolerance.metric",
        ),
        (
            StrategyRiskPolicy,
            {
                "drawdown": {
                    "stopLoss": {
                        "thresholdPct": 8,
                        "action": "reduce_exposure",
                        "reductionPct": 50,
                    },
                },
                "exposure": {
                    "limits": {
                        "drawdownReducePct": 6,
                        "drawdownBlockPct": 9,
                    },
                },
            },
            "drawdownReducePct",
        ),
    )

    for model, payload, expected in invalid_payloads:
        try:
            model.model_validate(payload)
        except Exception as exc:
            assert expected in str(exc)
        else:
            raise AssertionError(f"Expected {model.__name__} to reject {payload!r}.")


def test_risk_policy_library_contracts_wrap_strategy_risk_policy() -> None:
    summary = RiskPolicyConfigSummary(
        name="balanced-risk", description="Desk balanced risk.", version=2, usageCount=4
    )
    revision = RiskPolicyConfigRevision(
        name="balanced-risk",
        version=2,
        description="Desk balanced risk.",
        config={
            "policy": {
                "scope": "strategy",
                "drawdown": {
                    "stopLoss": {
                        "thresholdPct": 8,
                        "action": "reduce_exposure",
                        "reductionPct": 50,
                    },
                },
            }
        },
        configHash="hash-1",
    )
    detail = RiskPolicyConfigDetailResponse(
        policy=summary, activeRevision=revision, revisions=[revision]
    )

    assert detail.policy.version == 2
    assert detail.activeRevision is not None
    assert detail.activeRevision.config.policy.drawdown is not None
    assert detail.activeRevision.config.policy.drawdown.stopLoss is not None


def test_strategy_risk_policy_accepts_vix_spike_halt_control() -> None:
    policy = StrategyRiskPolicy(
        marketStress={
            "vixSpikeHalt": {"threshold": 32, "streakBars": 2, "cooldownBars": 2}
        }
    )

    assert policy.marketStress is not None
    assert policy.marketStress.vixSpikeHalt is not None
    assert policy.marketStress.vixSpikeHalt.threshold == 32
    assert policy.marketStress.vixSpikeHalt.streakBars == 2
    assert policy.marketStress.vixSpikeHalt.cooldownBars == 2


def test_strategy_risk_policy_requires_reduction_percentage_for_reduce_exposure() -> (
    None
):
    try:
        StrategyRiskPolicy(
            drawdown={"stopLoss": {"thresholdPct": 8, "action": "reduce_exposure"}}
        )
    except Exception as exc:
        assert "reduce_exposure" in str(exc)
        assert "reductionPct" in str(exc)
    else:
        raise AssertionError(
            "Expected reduce_exposure stop-loss policy to require reductionPct."
        )


def test_exit_rule_set_contracts_normalize_priorities_and_metadata() -> None:
    config = ExitRuleSetConfig(
        intrabarConflictPolicy="priority_order",
        exits=[
            {
                "id": "profit-10",
                "type": "take_profit_fixed",
                "description": "Exit the position when upside capture reaches the configured profit target.",
                "visualKey": "take_profit_fixed",
                "value": 0.10,
            },
            {"id": "stop-5", "type": "stop_loss_fixed", "value": 0.05},
        ],
    )
    summary = ExitRuleSetSummary(
        name="standard-exits", version=3, ruleCount=len(config.exits)
    )
    revision = ExitRuleSetRevision(name="standard-exits", version=3, config=config)
    detail = ExitRuleSetDetailResponse(
        ruleSet=summary, activeRevision=revision, revisions=[revision]
    )

    assert detail.ruleSet.ruleCount == 2
    assert detail.activeRevision is not None
    assert detail.activeRevision.config.exits[0].priority == 0
    assert detail.activeRevision.config.exits[1].priority == 1
    assert (
        detail.activeRevision.config.exits[0].description
        == "Exit the position when upside capture reaches the configured profit target."
    )
    assert detail.activeRevision.config.exits[0].visualKey == "take_profit_fixed"
    assert detail.activeRevision.config.exits[1].description == ""
    assert detail.activeRevision.config.exits[1].visualKey == "stop_loss_fixed"


def test_exit_rule_visual_key_accepts_null_and_rejects_unknown_keys() -> None:
    config = ExitRuleSetConfig(
        exits=[
            {
                "id": "stop-8",
                "type": "stop_loss_fixed",
                "value": 0.08,
                "visualKey": None,
            }
        ]
    )

    assert config.exits[0].visualKey is None

    try:
        ExitRuleSetConfig(
            exits=[
                {
                    "id": "stop-8",
                    "type": "stop_loss_fixed",
                    "value": 0.08,
                    "visualKey": "custom-uploaded-image",
                }
            ]
        )
    except Exception as exc:
        assert "visualKey" in str(exc)
    else:
        raise AssertionError("Expected unknown exit rule visualKey to fail validation.")


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


def test_rank_decay_exit_requires_rank_threshold_and_rejects_price_stop_fields() -> (
    None
):
    config = ExitRuleSetConfig(
        exits=[{"id": "rank-decay", "type": "rank_decay", "rankThreshold": 40}]
    )

    assert config.exits[0].rankThreshold == 40
    assert config.exits[0].value is None

    invalid_payloads = [
        {"id": "missing-threshold", "type": "rank_decay"},
        {
            "id": "value-not-supported",
            "type": "rank_decay",
            "rankThreshold": 40,
            "value": 0.1,
        },
        {
            "id": "reference-not-supported",
            "type": "rank_decay",
            "rankThreshold": 40,
            "reference": "entry_price",
        },
        {
            "id": "atr-not-supported",
            "type": "rank_decay",
            "rankThreshold": 40,
            "atrColumn": "atr_14",
        },
        {
            "id": "price-not-supported",
            "type": "rank_decay",
            "rankThreshold": 40,
            "priceField": "close",
        },
    ]

    for payload in invalid_payloads:
        try:
            ExitRuleSetConfig(exits=[payload])
        except Exception as exc:
            assert "rank_decay" in str(exc)
        else:
            raise AssertionError(
                f"Expected invalid rank_decay payload to fail validation: {payload['id']}"
            )


def test_exit_rule_preview_diagnostics_contracts_are_typed() -> None:
    config = ExitRuleSetConfig(
        exits=[
            {
                "id": "atr-stop",
                "type": "trailing_stop_atr",
                "value": 2.0,
                "atrColumn": "atr_14",
            },
            {"id": "rank-decay", "type": "rank_decay", "rankThreshold": 40},
        ]
    )
    request = ExitRulePreviewRequest(
        config=config.model_dump(mode="json"),
        sampleBar={"low": 95.0, "close": 100.0},
        samplePosition={"entry_price": 100.0, "highest_since_entry": 110.0},
    )
    diagnostic = ExitRuleDiagnostic(
        code="unsupported_evaluator",
        severity="warning",
        ruleId="rank-decay",
        field="type",
        message="rank_decay is contract-valid but not supported by the evaluator.",
        details={"ruleType": "rank_decay"},
    )
    candidate = ExitRulePreviewCandidate(
        ruleId="atr-stop",
        ruleType="trailing_stop_atr",
        priority=0,
        triggered=False,
        priceField="low",
        observedValue=95.0,
        thresholdValue=96.0,
    )
    response = ExitRulePreviewResponse(
        verdict="warning",
        normalizedConfig=config,
        diagnostics=[diagnostic],
        candidates=[candidate],
    )

    dumped = response.model_dump(mode="json")

    assert request.config["exits"][0]["atrColumn"] == "atr_14"
    assert dumped["diagnostics"][0]["code"] == "unsupported_evaluator"
    assert dumped["candidates"][0]["ruleType"] == "trailing_stop_atr"


def test_exit_policy_pin_impact_contract_captures_rule_revision_diff() -> None:
    current_config = ExitRuleSetConfig(
        exits=[{"id": "stop-5", "type": "stop_loss_fixed", "value": 0.05}]
    )
    proposed_config = ExitRuleSetConfig(
        exits=[
            {"id": "stop-5", "type": "stop_loss_fixed", "value": 0.08},
            {"id": "target-15", "type": "take_profit_fixed", "value": 0.15},
        ]
    )
    request = ExitPolicyPinImpactRequest(
        strategyName="quality-trend",
        strategyVersion=4,
        currentExitPolicyName="lifecycle-exits",
        currentExitPolicyVersion=2,
        proposedExitPolicyName="lifecycle-exits",
        proposedExitPolicyVersion=3,
        currentConfig=current_config,
        proposedConfig=proposed_config,
    )
    response = ExitPolicyPinImpactResponse(
        strategyName=request.strategyName,
        strategyVersion=request.strategyVersion,
        currentExitPolicyName=request.currentExitPolicyName,
        currentExitPolicyVersion=request.currentExitPolicyVersion,
        proposedExitPolicyName=request.proposedExitPolicyName,
        proposedExitPolicyVersion=request.proposedExitPolicyVersion,
        ruleImpacts=[
            ExitRulePinImpact(
                ruleId="stop-5",
                changeType="modified",
                ruleType="stop_loss_fixed",
                visualKey="stop_loss_fixed",
                previousPriority=0,
                proposedPriority=0,
            ),
            ExitRulePinImpact(
                ruleId="target-15",
                changeType="added",
                ruleType="take_profit_fixed",
                visualKey="take_profit_fixed",
                proposedPriority=1,
            ),
        ],
        changedRuleCount=2,
    )

    assert request.proposedConfig.exits[1].priority == 1
    assert response.ruleImpacts[0].changeType == "modified"
    assert response.changedRuleCount == 2


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
        requested_target_weight=0.5,
        executed_target_weight=0.35,
        requested_residual_cash_weight=0.0,
        executed_residual_cash_weight=0.15,
        details={"cooldownBarsRemaining": 11},
    )
    response = BacktestPolicyEventListResponse(
        events=[event], total=1, limit=50, offset=0
    )

    assert response.events[0].reason_code == "cooldown_active"
    assert response.events[0].details["cooldownBarsRemaining"] == 11
    assert response.events[0].executed_target_weight == 0.35


def test_backtest_data_quality_event_contract_captures_strict_mode_diagnostics() -> (
    None
):
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
    response = BacktestDataQualityEventListResponse(
        events=[event], total=1, limit=50, offset=0
    )

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
        exitPolicyName="desk-exit",
        exitPolicyVersion=2,
    )

    assert request.symbol == "AAPL"
    assert request.strategyRef is not None
    assert request.strategyRef.strategyName == "quality-trend"
    assert request.strategyRef.strategyVersion == 3
    assert request.exitPolicyName == "desk-exit"
    assert request.exitPolicyVersion == 2


def test_ranking_schema_requires_groups() -> None:
    try:
        RankingSchemaConfig(groups=[])
    except Exception as exc:
        assert "groups" in str(exc)
    else:
        raise AssertionError("Expected validation failure for empty groups.")


def test_ranking_schema_accepts_missing_legacy_universe_reference() -> None:
    payload = RankingSchemaConfig(
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

    assert payload.universeConfigName is None


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
    assert payload.universeConfigName == "core-universe"


def test_ranking_schema_summary_accepts_compact_profile() -> None:
    payload = RankingSchemaSummary(
        name="quality_momentum",
        version=3,
        status="active",
        description="Quality plus medium-term momentum.",
        intendedUse="validation",
        schemaProfile={
            "groupCount": 2,
            "factorCount": 4,
            "groupNames": ["quality", "momentum"],
            "sourceTables": ["market_data", "fundamentals"],
            "factorColumns": ["market_data.return_126d", "fundamentals.pe_ratio"],
            "transformTypes": ["percentile_rank", "zscore"],
            "directionCounts": {"asc": 1, "desc": 3},
            "missingPolicyCounts": {"exclude": 2, "zero": 2},
        },
    )

    assert payload.schemaProfile is not None
    assert payload.schemaProfile.groupCount == 2
    assert payload.schemaProfile.factorColumns == [
        "market_data.return_126d",
        "fundamentals.pe_ratio",
    ]
    assert payload.schemaProfile.directionCounts["desc"] == 3


def test_universe_condition_uses_governed_field_catalog() -> None:
    condition = UniverseCondition(
        field="security.sector", operator="in", values=["technology"]
    )

    assert condition.field == "security.sector"
    assert any(field.id == "security.sector" for field in UNIVERSE_FIELD_DEFINITIONS)


def test_universe_condition_accepts_security_symbol_filter() -> None:
    definition = UniverseDefinition(
        root={
            "operator": "and",
            "clauses": [
                {"field": "security.symbol", "operator": "eq", "value": "SPY"},
            ],
        }
    )

    clause = definition.root.clauses[0]
    assert isinstance(clause, UniverseCondition)
    assert clause.field == "security.symbol"
    assert clause.value == "SPY"
    assert UNIVERSE_FIELD_DEFINITION_BY_ID["security.symbol"].valueKind == "string"


def test_universe_condition_rejects_numeric_operator_for_security_symbol() -> None:
    try:
        UniverseCondition(field="security.symbol", operator="gt", value="SPY")
    except ValueError as exc:
        assert "gt is not supported for field 'security.symbol'" in str(exc)
    else:
        raise AssertionError(
            "Expected security.symbol to reject numeric comparison operators."
        )


def test_universe_condition_accepts_us_liquid_equity_filter_fields() -> None:
    definition = UniverseDefinition(
        root={
            "operator": "and",
            "clauses": [
                {"field": "security.country", "operator": "eq", "value": "US"},
                {"field": "security.primary_listing", "operator": "eq", "value": True},
                {
                    "field": "security.market_cap",
                    "operator": "gte",
                    "value": 10_000_000_000,
                },
                {
                    "field": "market.dollar_volume_20d",
                    "operator": "gte",
                    "value": 50_000_000,
                },
                {
                    "field": "security.is_price_liquidity_eligible",
                    "operator": "eq",
                    "value": True,
                },
            ],
        }
    )

    used_fields = [
        clause.field
        for clause in definition.root.clauses
        if isinstance(clause, UniverseCondition)
    ]
    assert used_fields == [
        "security.country",
        "security.primary_listing",
        "security.market_cap",
        "market.dollar_volume_20d",
        "security.is_price_liquidity_eligible",
    ]


def test_universe_condition_accepts_qmom_research_fields() -> None:
    definition = UniverseDefinition(
        root={
            "operator": "and",
            "clauses": [
                {"field": "qmom.daily_research_score", "operator": "gte", "value": 70},
                {
                    "field": "qmom.breakout_close_above_20d_high",
                    "operator": "eq",
                    "value": 1,
                },
                {"field": "qmom.trend_filter", "operator": "eq", "value": 1},
            ],
        }
    )

    used_fields = [
        clause.field
        for clause in definition.root.clauses
        if isinstance(clause, UniverseCondition)
    ]
    assert used_fields == [
        "qmom.daily_research_score",
        "qmom.breakout_close_above_20d_high",
        "qmom.trend_filter",
    ]
    assert any(field.id == "qmom.adr_pct_20d" for field in UNIVERSE_FIELD_DEFINITIONS)


def test_universe_condition_accepts_strict_stock_state_fields() -> None:
    definition = UniverseDefinition(
        root={
            "operator": "and",
            "clauses": [
                {"field": "returns.return_60d", "operator": "gte", "value": 0.30},
                {"field": "technical.rsi_14d", "operator": "gte", "value": 75},
                {"field": "technical.bb_width_20d", "operator": "lte", "value": 0.10},
                {
                    "field": "technical.compression_score",
                    "operator": "gte",
                    "value": 0.70,
                },
                {
                    "field": "technical.position_in_20d_range",
                    "operator": "gte",
                    "value": 1.0,
                },
            ],
        }
    )

    used_fields = [
        clause.field
        for clause in definition.root.clauses
        if isinstance(clause, UniverseCondition)
    ]
    assert used_fields == [
        "returns.return_60d",
        "technical.rsi_14d",
        "technical.bb_width_20d",
        "technical.compression_score",
        "technical.position_in_20d_range",
    ]
    assert UNIVERSE_FIELD_DEFINITION_BY_ID["technical.rsi_14d"].label == "14 Day RSI"
    assert all(
        UNIVERSE_FIELD_DEFINITION_BY_ID[field].valueKind == "number"
        for field in used_fields
    )


def test_universe_condition_accepts_runner_discovery_fields() -> None:
    definition = UniverseDefinition(
        root={
            "operator": "and",
            "clauses": [
                {
                    "field": "runner.distance_to_20d_high_pct",
                    "operator": "gte",
                    "value": -0.03,
                },
                {
                    "field": "runner.volume_dryup_10d_50d",
                    "operator": "lte",
                    "value": 0.7,
                },
                {"field": "runner.breakout_hold_1d", "operator": "eq", "value": 1},
            ],
        }
    )

    used_fields = [
        clause.field
        for clause in definition.root.clauses
        if isinstance(clause, UniverseCondition)
    ]
    assert used_fields == [
        "runner.distance_to_20d_high_pct",
        "runner.volume_dryup_10d_50d",
        "runner.breakout_hold_1d",
    ]
    assert any(
        field.id == "runner.failed_breakout_1d" for field in UNIVERSE_FIELD_DEFINITIONS
    )


def test_universe_condition_accepts_alternative_data_observed_fields() -> None:
    definition = UniverseDefinition(
        root={
            "operator": "or",
            "clauses": [
                {
                    "field": "alternative.wall_street_bets_observed_date",
                    "operator": "is_not_null",
                },
                {
                    "field": "alternative.insider_trading_observed_date",
                    "operator": "is_not_null",
                },
                {
                    "field": "alternative.congressional_trading_observed_date",
                    "operator": "is_not_null",
                },
                {
                    "field": "alternative.government_contract_observed_date",
                    "operator": "is_not_null",
                },
                {
                    "field": "alternative.institutional_holding_observed_date",
                    "operator": "is_not_null",
                },
                {
                    "field": "alternative.patent_observed_date",
                    "operator": "is_not_null",
                },
                {
                    "field": "alternative.congress_holding_observed_date",
                    "operator": "is_not_null",
                },
            ],
        }
    )

    used_fields = [
        clause.field
        for clause in definition.root.clauses
        if isinstance(clause, UniverseCondition)
    ]
    assert used_fields == [
        "alternative.wall_street_bets_observed_date",
        "alternative.insider_trading_observed_date",
        "alternative.congressional_trading_observed_date",
        "alternative.government_contract_observed_date",
        "alternative.institutional_holding_observed_date",
        "alternative.patent_observed_date",
        "alternative.congress_holding_observed_date",
    ]
    assert all(
        UNIVERSE_FIELD_DEFINITION_BY_ID[field].valueKind == "date"
        for field in used_fields
    )


def test_universe_condition_rejects_unknown_field() -> None:
    try:
        UniverseCondition(field="market_data.close", operator="gt", value=0)
    except Exception as exc:
        assert "field" in str(exc)
    else:
        raise AssertionError("Expected validation failure for unknown universe field.")


def test_universe_catalog_response_uses_governed_field_definitions() -> None:
    payload = UniverseCatalogResponse(fields=list(UNIVERSE_FIELD_DEFINITIONS[:3]))
    fields_by_id = {field.id: field for field in payload.fields}

    assert payload.source == "postgres_gold"
    assert payload.fields[0].id == "market.close"
    assert fields_by_id["security.symbol"].label == "Security Symbol"
    assert fields_by_id["security.is_active"].label == "Security Active Flag"


def test_universe_preview_response_uses_governed_field_ids() -> None:
    payload = UniversePreviewResponse(
        symbolCount=2,
        sampleSymbols=["AAPL", "MSFT"],
        fieldsUsed=["market.close", "quality.piotroski_f_score"],
        rows=[
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "country": "US",
                "close": 182.31,
                "volume": 1300000,
            }
        ],
        rowCount=2,
        previewLimit=25,
        truncated=False,
        asOf="2026-05-16",
    )

    assert payload.fieldsUsed == ["market.close", "quality.piotroski_f_score"]
    assert payload.warnings == []
    assert payload.rows[0].symbol == "AAPL"
    assert payload.rowCount == 2


def test_universe_preview_request_accepts_as_of_date() -> None:
    payload = UniversePreviewRequest(
        universeName="u26_us_liquid_oversold_dislocation",
        asOfDate="2020-03-20",
        sampleLimit=50,
    )

    assert payload.universeName == "u26_us_liquid_oversold_dislocation"
    assert payload.asOfDate == date(2020, 3, 20)
    assert payload.sampleLimit == 50


def test_universe_preview_request_requires_source() -> None:
    try:
        UniversePreviewRequest(asOfDate="2020-03-20")
    except Exception as exc:
        assert "universeName or universe is required" in str(exc)
    else:
        raise AssertionError("Expected validation failure without universe source.")


def test_universe_preview_response_rejects_unknown_field_ids() -> None:
    try:
        UniversePreviewResponse(
            symbolCount=1,
            sampleSymbols=["AAPL"],
            fieldsUsed=["market_data.close"],
            rowCount=1,
            previewLimit=25,
        )
    except Exception as exc:
        assert "fieldsUsed" in str(exc)
    else:
        raise AssertionError(
            "Expected validation failure for unknown preview field id."
        )


def test_universe_config_draft_generation_request_normalizes_prompt_and_hints() -> None:
    payload = UniverseConfigDraftGenerationRequest(
        plaintext="  US primary listings with strong liquidity  ",
        nameHint="  us-liquid  ",
        descriptionHint="  Liquid US equities.  ",
        intendedUse="validation",
    )

    assert payload.plaintext == "US primary listings with strong liquidity"
    assert payload.nameHint == "us-liquid"
    assert payload.descriptionHint == "Liquid US equities."
    assert payload.intendedUse == "validation"
    assert payload.previewSampleLimit == 25


def test_universe_config_draft_generation_request_rejects_blank_and_oversized_prompt() -> (
    None
):
    for invalid_prompt in ("   ", "x" * 4001):
        try:
            UniverseConfigDraftGenerationRequest(plaintext=invalid_prompt)
        except Exception as exc:
            assert "plaintext" in str(exc)
        else:
            raise AssertionError(
                "Expected invalid universe draft generation prompt to fail validation."
            )


def test_universe_config_draft_generation_response_wraps_valid_draft_and_preview() -> (
    None
):
    payload = UniverseConfigDraftGenerationResponse(
        draft={
            "identity": {
                "name": "generated-us-liquid",
                "version": 1,
                "status": "draft",
                "description": "Generated candidate universe.",
                "intendedUse": "research",
            },
            "config": {
                "source": "postgres_gold",
                "root": {
                    "kind": "group",
                    "operator": "and",
                    "clauses": [
                        {
                            "kind": "condition",
                            "field": "security.country",
                            "operator": "eq",
                            "value": "US",
                        },
                        {
                            "kind": "condition",
                            "field": "market.close",
                            "operator": "gt",
                            "value": 5,
                        },
                    ],
                },
            },
        },
        explanation="  Converted the request into country and price filters.  ",
        assumptions=["  Common stocks are represented by the governed catalog.  ", ""],
        warnings=["Review liquidity threshold before production use."],
        fieldsUsed=["security.country", "market.close"],
        preview={
            "source": "postgres_gold",
            "symbolCount": 2,
            "sampleSymbols": ["AAPL", "MSFT"],
            "fieldsUsed": ["security.country", "market.close"],
            "warnings": [],
        },
    )

    assert payload.draft.identity.status == "draft"
    assert payload.draft.identity.version == 1
    assert (
        payload.explanation == "Converted the request into country and price filters."
    )
    assert payload.assumptions == [
        "Common stocks are represented by the governed catalog."
    ]
    assert payload.fieldsUsed == ["security.country", "market.close"]
    assert payload.preview is not None
    assert payload.preview.symbolCount == 2


def test_universe_config_draft_generation_response_rejects_non_draft_identity() -> None:
    base_payload = {
        "draft": {
            "identity": {
                "name": "generated-us-liquid",
                "version": 1,
                "status": "active",
                "description": "Generated candidate universe.",
                "intendedUse": "research",
            },
            "config": {
                "root": {
                    "clauses": [
                        {"field": "security.country", "operator": "eq", "value": "US"},
                    ],
                },
            },
        },
        "explanation": "Generated a candidate draft.",
        "fieldsUsed": ["security.country"],
    }

    try:
        UniverseConfigDraftGenerationResponse.model_validate(base_payload)
    except Exception as exc:
        assert "draft status" in str(exc)
    else:
        raise AssertionError(
            "Expected generation response to reject active identity status."
        )

    version_payload = dict(base_payload)
    version_payload["draft"] = dict(base_payload["draft"])
    version_payload["draft"]["identity"] = {
        **base_payload["draft"]["identity"],
        "status": "draft",
        "version": 2,
    }

    try:
        UniverseConfigDraftGenerationResponse.model_validate(version_payload)
    except Exception as exc:
        assert "version 1" in str(exc)
    else:
        raise AssertionError("Expected generation response to reject non-v1 drafts.")


def test_ranking_field_reference_normalizes_identifiers_and_label() -> None:
    payload = RankingFieldReference(
        table="  MARKET_DATA  ",
        column="  RETURN_126D  ",
        label="  126 Day Return  ",
        valueKind="number",
    )

    assert payload.table == "market_data"
    assert payload.column == "return_126d"
    assert payload.label == "126 Day Return"
    assert payload.valueKind == "number"


def test_ranking_schema_draft_generation_request_normalizes_prompt_and_hints() -> None:
    payload = RankingSchemaDraftGenerationRequest(
        plaintext="  Rank liquid names by momentum and quality  ",
        nameHint="  quality-momentum  ",
        descriptionHint="  Generated ranking draft.  ",
        universeConfigNameHint="  us-large-liquid  ",
        intendedUse="validation",
        previewStrategyName="  long-only-core  ",
        previewAsOfDate="2026-05-08",
    )

    assert payload.plaintext == "Rank liquid names by momentum and quality"
    assert payload.nameHint == "quality-momentum"
    assert payload.descriptionHint == "Generated ranking draft."
    assert payload.universeConfigNameHint == "us-large-liquid"
    assert payload.previewStrategyName == "long-only-core"
    assert payload.previewAsOfDate is not None
    assert payload.previewSampleLimit == 25


def test_ranking_schema_draft_generation_request_rejects_blank_prompt_and_preview_half_pair() -> (
    None
):
    for invalid_payload in (
        {"plaintext": "   "},
        {"plaintext": "x" * 4001},
        {"plaintext": "rank momentum", "previewStrategyName": "core"},
        {"plaintext": "rank momentum", "previewAsOfDate": "2026-05-08"},
    ):
        try:
            RankingSchemaDraftGenerationRequest.model_validate(invalid_payload)
        except Exception as exc:
            assert "plaintext" in str(exc) or "previewStrategyName" in str(exc)
        else:
            raise AssertionError(
                "Expected invalid ranking draft generation request to fail validation."
            )


def test_ranking_schema_draft_generation_response_wraps_valid_draft_and_preview() -> (
    None
):
    payload = RankingSchemaDraftGenerationResponse(
        draft={
            "identity": {
                "name": "generated-quality-momentum",
                "version": 1,
                "status": "draft",
                "description": "Generated ranking draft.",
                "intendedUse": "research",
            },
            "config": {
                "universeConfigName": "us-large-liquid",
                "groups": [
                    {
                        "name": "momentum",
                        "weight": 1,
                        "factors": [
                            {
                                "name": "return_126d",
                                "table": "market_data",
                                "column": "return_126d",
                                "weight": 1,
                                "direction": "desc",
                                "missingValuePolicy": "zero",
                                "transforms": [
                                    {"type": "percentile_rank", "params": {}}
                                ],
                            }
                        ],
                        "transforms": [],
                    }
                ],
                "overallTransforms": [],
            },
        },
        explanation="  Converted the request into a medium-term momentum factor.  ",
        assumptions=[
            "  Quality is not mapped because no governed field was provided.  ",
            "",
        ],
        warnings=["Review factor coverage before saving."],
        fieldsUsed=[
            {
                "table": "market_data",
                "column": "return_126d",
                "label": "126 Day Return",
                "valueKind": "number",
            }
        ],
        unmappedSignals=["  quality  ", ""],
        preview={
            "strategyName": "long-only-core",
            "asOfDate": "2026-05-08",
            "rowCount": 1,
            "rows": [{"symbol": "AAPL", "rank": 1, "score": 0.98}],
            "warnings": [],
        },
    )

    assert payload.draft.identity.status == "draft"
    assert payload.draft.identity.version == 1
    assert (
        payload.explanation
        == "Converted the request into a medium-term momentum factor."
    )
    assert payload.assumptions == [
        "Quality is not mapped because no governed field was provided."
    ]
    assert payload.fieldsUsed[0].table == "market_data"
    assert payload.unmappedSignals == ["quality"]
    assert payload.preview is not None
    assert payload.preview.rows[0].symbol == "AAPL"


def test_generated_strategy_save_request_normalizes_redacted_provenance() -> None:
    payload = GeneratedStrategySaveRequest(
        name="  generated-quality-momentum  ",
        description="  Human-reviewed generated draft.  ",
        config={
            "universeConfigName": "us-large-liquid",
            "rankingSchemaName": "quality-momentum",
        },
        provenance={
            "generationRequestId": "  genreq-123  ",
            "promptFingerprint": "  sha256:prompt-abcdef1234567890  ",
            "promptSummary": "  Redacted summary of the requested strategy.  ",
            "sourceContext": [
                "  upstream draft  ",
                "",
                "  user-reviewed assumptions  ",
            ],
            "model": "  strategy-draft-v1  ",
            "generatedAt": "2026-05-24T12:00:00Z",
            "outputFingerprint": "  sha256:output-abcdef1234567890  ",
            "assumptions": ["  monthly rebalance  "],
            "warnings": ["  Validate liquidity filters before backtest.  "],
            "unresolvedRequirements": ["  Confirm benchmark.  "],
        },
    )

    assert payload.name == "generated-quality-momentum"
    assert payload.description == "Human-reviewed generated draft."
    assert payload.config.universeConfigName == "us-large-liquid"
    assert payload.provenance.generationRequestId == "genreq-123"
    assert payload.provenance.promptFingerprint == "sha256:prompt-abcdef1234567890"
    assert (
        payload.provenance.promptSummary
        == "Redacted summary of the requested strategy."
    )
    assert payload.provenance.sourceContext == [
        "upstream draft",
        "user-reviewed assumptions",
    ]
    assert payload.provenance.assumptions == ["monthly rebalance"]


def test_generated_strategy_save_request_rejects_invalid_provenance() -> None:
    invalid_payload = {
        "name": "generated-quality-momentum",
        "config": {
            "universeConfigName": "us-large-liquid",
            "rankingSchemaName": "quality-momentum",
        },
        "provenance": {
            "generationRequestId": "genreq-123",
            "promptFingerprint": "too-short",
            "promptSummary": "Redacted summary.",
            "model": "strategy-draft-v1",
            "generatedAt": "2026-05-24T12:00:00Z",
            "outputFingerprint": "sha256:output-abcdef1234567890",
            "raw_generation_text": "not allowed",
        },
    }

    try:
        GeneratedStrategySaveRequest.model_validate(invalid_payload)
    except Exception as exc:
        message = str(exc)
        assert "promptFingerprint" in message
        assert "raw_generation_text" in message
    else:
        raise AssertionError(
            "Expected invalid generated strategy provenance to fail validation."
        )


def test_generated_strategy_save_response_carries_exact_backtest_handoff() -> None:
    provenance = GeneratedStrategyProvenance(
        generationRequestId="genreq-123",
        promptFingerprint="sha256:prompt-abcdef1234567890",
        promptSummary="Redacted summary of the requested strategy.",
        sourceContext=["strategy workspace draft"],
        model="strategy-draft-v1",
        generatedAt="2026-05-24T12:00:00Z",
        outputFingerprint="sha256:output-abcdef1234567890",
        assumptions=["monthly rebalance"],
        warnings=[],
        unresolvedRequirements=[],
    )
    handoff = GeneratedStrategyBacktestHandoff(
        strategyRef={"strategyName": "generated-quality-momentum", "strategyVersion": 7}
    )
    payload = GeneratedStrategySaveResponse(
        message="Generated strategy saved for review.",
        strategyName="generated-quality-momentum",
        strategyVersion=7,
        strategyRef={
            "strategyName": "generated-quality-momentum",
            "strategyVersion": 7,
        },
        provenanceId="generated-quality-momentum-7",
        provenance=provenance,
        backtestHandoff=handoff,
    )

    assert payload.status == "saved"
    assert payload.reviewStatus == "pending_review"
    assert payload.strategyRef.strategyVersion == 7
    assert (
        payload.backtestHandoff.strategyRef.strategyName == "generated-quality-momentum"
    )
    assert payload.backtestHandoff.validationPath == "/api/backtests/validation"
    assert payload.backtestHandoff.runPath == "/api/backtests/runs"


def test_ranking_schema_draft_generation_response_rejects_non_draft_identity() -> None:
    base_payload = {
        "draft": {
            "identity": {
                "name": "generated-quality-momentum",
                "version": 1,
                "status": "active",
                "description": "Generated ranking draft.",
                "intendedUse": "research",
            },
            "config": {
                "universeConfigName": "us-large-liquid",
                "groups": [
                    {
                        "name": "momentum",
                        "factors": [
                            {
                                "name": "return_126d",
                                "table": "market_data",
                                "column": "return_126d",
                            }
                        ],
                    }
                ],
            },
        },
        "explanation": "Generated a candidate draft.",
        "fieldsUsed": [
            {"table": "market_data", "column": "return_126d", "valueKind": "number"}
        ],
    }

    try:
        RankingSchemaDraftGenerationResponse.model_validate(base_payload)
    except Exception as exc:
        assert "draft status" in str(exc)
    else:
        raise AssertionError(
            "Expected generation response to reject active identity status."
        )

    version_payload = dict(base_payload)
    version_payload["draft"] = dict(base_payload["draft"])
    version_payload["draft"]["identity"] = {
        **base_payload["draft"]["identity"],
        "status": "draft",
        "version": 2,
    }

    try:
        RankingSchemaDraftGenerationResponse.model_validate(version_payload)
    except Exception as exc:
        assert "version 1" in str(exc)
    else:
        raise AssertionError("Expected generation response to reject non-v1 drafts.")


def test_ui_runtime_config_defaults_to_api_root() -> None:
    config = UiRuntimeConfig()
    assert config.apiBaseUrl == "/api"
    assert config.authSessionMode == "cookie"
    assert config.authProvider == "oidc"
    assert config.oidcScopes == []
    assert config.oidcAudience == []
    assert config.oidcPostLogoutRedirectUri is None


def test_ui_runtime_config_accepts_cookie_auth_session_mode() -> None:
    config = UiRuntimeConfig(authSessionMode="cookie")

    assert config.authSessionMode == "cookie"


def test_ui_runtime_config_rejects_unknown_auth_session_mode() -> None:
    try:
        UiRuntimeConfig(authSessionMode="local-storage")
    except Exception as exc:
        assert "authSessionMode" in str(exc)
    else:
        raise AssertionError(
            "Expected validation failure for unknown auth session mode."
        )


def test_ui_runtime_config_accepts_password_auth_provider() -> None:
    config = UiRuntimeConfig(authProvider="password")

    assert config.authProvider == "password"


def test_ui_runtime_config_normalizes_string_scopes() -> None:
    config = UiRuntimeConfig(
        oidcScopes="api://asset-allocation-api/user_impersonation openid",
        oidcAudience="asset-allocation-api,asset-allocation-jobs",
    )
    assert config.oidcScopes == [
        "api://asset-allocation-api/user_impersonation",
        "openid",
    ]
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


def test_regime_gate_schema_descriptions_preserve_ownership_boundary() -> None:
    strategy_schema = StrategyConfig.model_json_schema()
    assert "Canonical strategy-level regime playbook" in strategy_schema["properties"]["regimeGates"]["description"]

    position_schema = StrategyPositionPolicy.model_json_schema()
    position_description = position_schema["properties"]["regimeGate"]["description"]
    assert "local operating constraint" in position_description.lower()
    assert "StrategyConfig.regimeGates" in position_description

    rebalance_schema = RebalancePolicy.model_json_schema()
    assert "local operating constraint" in rebalance_schema["properties"]["regimeGate"]["description"].lower()

    exits_schema = ExitRuleSetConfig.model_json_schema()
    assert "local operating constraint" in exits_schema["properties"]["regimeGate"]["description"].lower()


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
        raise AssertionError(
            "Expected RuntimeJobMetadata to reject legacy job categories."
        )


def test_deployment_provenance_view_captures_resource_consistency() -> None:
    latest_run = PipelineRunSummary(
        pipelineId=18,
        pipelineName="asset-allocation-ui-deploy-prod",
        runId=1205,
        runNumber="20260514.5",
        status="completed",
        result="succeeded",
        sourceSha="420db20a1b1a5a3d70f26c8c23e2fa82a283ca82",
        sourceBranch="refs/heads/main",
        finishedAt="2026-05-14T02:00:00Z",
        links=[
            {"label": "Pipeline run", "href": "https://dev.azure.com/example/run/1205"}
        ],
    )
    resource = ResourceDeploymentVersion(
        resourceName="vg-aa-prod-ui",
        resourceType="Microsoft.App/containerApps",
        environment="prod",
        repo="asset-allocation-ui",
        artifactDigest="sha256:abc123",
        sourceSha="420db20a1b1a5a3d70f26c8c23e2fa82a283ca82",
        releaseRun=latest_run,
        deployRun=latest_run,
        latestSuccessfulRun=latest_run,
        status="available",
        result="consistent",
        checkedAt="2026-05-14T02:05:00Z",
    )
    view = DeploymentProvenanceView(
        checkedAt="2026-05-14T02:05:00Z",
        status="available",
        result="consistent",
        summary=DeploymentProvenanceSummary(totalResources=1, consistent=1),
        resources=[resource],
    )
    schema = DeploymentProvenanceView.model_json_schema()

    assert view.resources[0].resourceName == "vg-aa-prod-ui"
    assert view.resources[0].latestSuccessfulRun is not None
    assert view.resources[0].latestSuccessfulRun.runId == 1205
    assert view.summary.consistent == 1
    assert (
        schema["properties"]["resources"]["items"]["$ref"]
        == "#/$defs/ResourceDeploymentVersion"
    )


def test_deployment_provenance_contracts_reject_unknown_result_and_extra_fields() -> (
    None
):
    try:
        ResourceDeploymentVersion(
            resourceName="vg-aa-prod-ui",
            resourceType="Microsoft.App/containerApps",
            environment="prod",
            repo="asset-allocation-ui",
            status="available",
            result="drifted",
            checkedAt="2026-05-14T02:05:00Z",
            unexpected=True,
        )
    except Exception as exc:
        assert "result" in str(exc)
        assert "unexpected" in str(exc)
    else:
        raise AssertionError(
            "Expected deployment provenance to reject invalid result fields."
        )


def test_pull_request_sync_view_captures_commit_and_work_item_lineage() -> None:
    commit = PullRequestCommitSummary(
        commitId="2a954f01717a13765a28b1050ea96997a6c6fab5",
        comment="Add symbol cleanup review panel",
        authorName="rudy",
        authoredAt="2026-05-15T14:34:47Z",
        links=[
            {"label": "Commit", "href": "https://dev.azure.com/example/commit/2a954f0"}
        ],
    )
    row = PullRequestSyncRow(
        repo="asset-allocation-ui",
        repositoryId="5e10a80a-e19e-487d-bd1c-1a18e3b13e1c",
        pullRequestId=280,
        title="AB#178 Add symbol cleanup run review UI",
        status="active",
        isDraft=True,
        sourceRefName="refs/heads/agent/delivery-engineer-agent/AB178/asset-allocation-ui",
        targetRefName="refs/heads/main",
        sourceHeadSha="2a954f01717a13765a28b1050ea96997a6c6fab5",
        targetHeadSha="df3f6ec626b1e2f4a72f71a2b73dab1da5f022bf",
        lastMergeSourceCommit="2a954f01717a13765a28b1050ea96997a6c6fab5",
        lastMergeTargetCommit="df3f6ec626b1e2f4a72f71a2b73dab1da5f022bf",
        lastMergeCommit="7a78f21a7afb10aeb9b3039eb385b18b0c08aef6",
        mergeStatus="succeeded",
        result="synced",
        workItems=[
            PullRequestWorkItemRef(
                id=178,
                title="Review symbol cleanup results and exceptions",
                workItemType="User Story",
                state="Closed",
            )
        ],
        commits=[commit],
    )
    view = PullRequestSyncView(
        checkedAt="2026-05-15T15:00:00Z",
        status="available",
        result="synced",
        summary=PullRequestSyncSummary(totalPullRequests=1, drafts=1, synced=1),
        pullRequests=[row],
    )
    schema = PullRequestSyncView.model_json_schema()

    assert view.pullRequests[0].pullRequestId == 280
    assert view.pullRequests[0].commits[0].commitId.startswith("2a954f0")
    assert view.pullRequests[0].workItems[0].id == 178
    assert (
        schema["properties"]["pullRequests"]["items"]["$ref"]
        == "#/$defs/PullRequestSyncRow"
    )


def test_pull_request_sync_contracts_reject_unknown_result_and_extra_fields() -> None:
    try:
        PullRequestSyncRow(
            repo="asset-allocation-ui",
            pullRequestId=280,
            title="Bad PR",
            sourceRefName="refs/heads/source",
            targetRefName="refs/heads/main",
            mergeStatus="succeeded",
            result="drifted",
            unexpected=True,
        )
    except Exception as exc:
        assert "result" in str(exc)
        assert "unexpected" in str(exc)
    else:
        raise AssertionError(
            "Expected pull request sync to reject invalid result fields."
        )


def test_strategy_publication_reconcile_signal_request_validates_key_and_fingerprint() -> (
    None
):
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
        raise AssertionError(
            "Expected strategy publication signal request validation to reject bad inputs."
        )


def test_results_reconcile_contract_requires_strict_complete_payloads() -> None:
    response = ResultsReconcileResponse(
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

    assert response.publicationSignalsProcessedCount == 6

    bad_payloads = (
        {},
        {
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
        raise AssertionError(
            f"Expected results reconcile response validation to reject {payload!r}."
        )


def test_currency_intraday_bars_contract_normalizes_pair_and_provider_fields() -> None:
    payload = CurrencyIntradayBarsResponse(
        symbol=" btcusd ",
        providerSymbol="x:btcusd",
        quoteCurrency="usd",
        interval="5m",
        from_="2026-05-20T00:00:00Z",
        to="2026-05-20T00:15:00-05:00",
        rowCount=2,
        rows=[
            CurrencyIntradayBar(
                timestamp="2026-05-20T00:00:00Z",
                open=101000.0,
                high=101250.0,
                low=100900.0,
                close=101200.0,
                volume=12.5,
                vwap=101125.25,
                transactions=42,
                providerTimestampMs=1779235200000,
            ),
            {
                "timestamp": "2026-05-20T00:05:00",
                "open": 101200.0,
                "high": 101350.0,
                "low": 101000.0,
                "close": 101250.0,
                "volume": 7.25,
            },
        ],
    )

    assert payload.symbol == "BTCUSD"
    assert payload.baseCurrency == "BTC"
    assert payload.providerSymbol == "X:BTCUSD"
    assert payload.quoteCurrency == "USD"
    assert payload.interval == "5m"
    assert payload.from_.isoformat() == "2026-05-20T00:00:00+00:00"
    assert payload.to.isoformat() == "2026-05-20T05:15:00+00:00"
    assert payload.rows[0].vwap == 101125.25
    assert payload.rows[0].transactions == 42
    assert payload.rows[0].providerTimestampMs == 1779235200000
    assert payload.rows[1].timestamp.isoformat() == "2026-05-20T00:05:00+00:00"
    assert payload.rows[1].vwap is None
    assert payload.rows[1].transactions is None

    dumped = payload.model_dump(mode="json", by_alias=True)
    assert dumped["from"] == "2026-05-20T00:00:00Z"
    assert "from_" not in dumped


def test_currency_intraday_bars_contract_rejects_unsupported_shapes() -> None:
    adapter = TypeAdapter(CurrencyIntradayBarInterval)

    assert adapter.validate_python("1m") == "1m"
    assert adapter.validate_python("5m") == "5m"
    assert adapter.validate_python("15m") == "15m"

    for invalid_interval in ("30m", "1h"):
        try:
            adapter.validate_python(invalid_interval)
        except Exception:
            continue
        raise AssertionError(
            f"Expected interval validation to reject {invalid_interval!r}."
        )

    invalid_payloads = (
        {
            "symbol": "BTCUSD",
            "providerSymbol": "X:ETHUSD",
            "interval": "1m",
            "from": "2026-05-20T00:00:00Z",
            "to": "2026-05-20T00:01:00Z",
            "rowCount": 0,
            "rows": [],
        },
        {
            "symbol": "BTCUSD",
            "providerSymbol": "X:BTCUSD",
            "baseCurrency": "ETH",
            "interval": "1m",
            "from": "2026-05-20T00:00:00Z",
            "to": "2026-05-20T00:01:00Z",
            "rowCount": 0,
            "rows": [],
        },
        {
            "symbol": "BTCUSD",
            "providerSymbol": "BTCUSD",
            "interval": "1m",
            "from": "2026-05-20T00:00:00Z",
            "to": "2026-05-20T00:01:00Z",
            "rowCount": 1,
            "rows": [],
        },
    )
    for payload in invalid_payloads:
        try:
            CurrencyIntradayBarsResponse.model_validate(payload)
        except Exception:
            continue
        raise AssertionError(
            f"Expected currency intraday response validation to reject {payload!r}."
        )


def test_currency_intraday_artifacts_include_schema_and_typescript_exports() -> None:
    root = Path(__file__).resolve().parents[2]
    schema_path = root / "schemas" / "currency-intraday-bars-response.schema.json"
    type_path = root / "ts" / "src" / "contracts.ts"

    response_schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert "CurrencyIntradayBar" in response_schema["$defs"]
    assert response_schema["properties"]["from"]["format"] == "date-time"
    assert response_schema["properties"]["interval"]["enum"] == ["1m", "5m", "15m"]

    generated_types = type_path.read_text(encoding="utf-8")
    assert "export interface CurrencyIntradayBar" in generated_types
    assert "export interface CurrencyIntradayBarsResponse" in generated_types
    assert "interval: CurrencyIntradayBarInterval;" in generated_types
    assert "from: string;" in generated_types


def test_stock_aggregate_bars_contract_normalizes_provider_fields() -> None:
    payload = StockAggregateBarsResponse(
        symbol=" aapl ",
        interval="5M",
        from_="2026-05-20T14:30:00Z",
        to="2026-05-20T14:45:00-05:00",
        rowCount=2,
        rows=[
            StockAggregateBar(
                symbol="AAPL",
                interval="5m",
                timestamp="2026-05-20T14:30:00Z",
                open=191.25,
                high=191.9,
                low=191.1,
                close=191.7,
                volume=1250,
                vwap=191.52,
                transactions=42,
                providerStartTimestampMs=1779287400000,
                providerEndTimestampMs=1779287699999,
                providerDelaySeconds=1.25,
                observedAt="2026-05-20T14:30:02",
                sequence=7,
            ),
            {
                "symbol": "am.aapl",
                "interval": "5m",
                "timestamp": "2026-05-20T14:35:00Z",
                "open": 191.7,
                "high": 192.1,
                "low": 191.45,
                "close": 192.0,
                "volume": 925,
                "providerStartTimestampMs": 1779287700000,
            },
        ],
    )

    assert payload.symbol == "AAPL"
    assert payload.providerSymbol == "AAPL"
    assert payload.interval == "5m"
    assert payload.from_.isoformat() == "2026-05-20T14:30:00+00:00"
    assert payload.to.isoformat() == "2026-05-20T19:45:00+00:00"
    assert payload.rows[0].observedAt is not None
    assert payload.rows[0].observedAt.isoformat() == "2026-05-20T14:30:02+00:00"
    assert payload.rows[1].symbol == "AAPL"
    assert payload.rows[1].vwap is None

    dumped = payload.model_dump(mode="json", by_alias=True)
    assert dumped["from"] == "2026-05-20T14:30:00Z"
    assert "from_" not in dumped


def test_stock_aggregate_bars_contract_rejects_unsupported_shapes() -> None:
    interval_adapter = TypeAdapter(StockAggregateInterval)
    event_adapter = TypeAdapter(StockAggregateStreamEventType)

    assert interval_adapter.validate_python("1s") == "1s"
    assert interval_adapter.validate_python("1m") == "1m"
    assert interval_adapter.validate_python("15m") == "15m"
    assert interval_adapter.validate_python("daily") == "daily"
    assert interval_adapter.validate_python("weekly") == "weekly"
    assert interval_adapter.validate_python("monthly") == "monthly"
    assert event_adapter.validate_python("market_price.stock_aggregate") == (
        "market_price.stock_aggregate"
    )
    assert event_adapter.validate_python("market_price.stock_status") == (
        "market_price.stock_status"
    )

    for invalid_interval in ("30m", "1h", "day"):
        try:
            interval_adapter.validate_python(invalid_interval)
        except Exception:
            continue
        raise AssertionError(
            f"Expected interval validation to reject {invalid_interval!r}."
        )

    invalid_payloads = (
        {
            "symbol": "*",
            "interval": "1m",
            "from": "2026-05-20T14:30:00Z",
            "to": "2026-05-20T14:31:00Z",
            "rowCount": 0,
            "rows": [],
        },
        {
            "symbol": "AAPL",
            "providerSymbol": "MSFT",
            "interval": "1m",
            "from": "2026-05-20T14:30:00Z",
            "to": "2026-05-20T14:31:00Z",
            "rowCount": 0,
            "rows": [],
        },
        {
            "symbol": "AAPL",
            "interval": "1m",
            "from": "2026-05-20T14:31:00Z",
            "to": "2026-05-20T14:30:00Z",
            "rowCount": 0,
            "rows": [],
        },
        {
            "symbol": "AAPL",
            "interval": "1m",
            "from": "2026-05-20T14:30:00Z",
            "to": "2026-05-20T14:31:00Z",
            "rowCount": 1,
            "rows": [],
        },
        {
            "symbol": "AAPL",
            "interval": "1m",
            "from": "2026-05-20T14:30:00Z",
            "to": "2026-05-20T14:31:00Z",
            "rowCount": 1,
            "rows": [
                {
                    "symbol": "MSFT",
                    "interval": "1m",
                    "timestamp": "2026-05-20T14:30:00Z",
                    "open": 1,
                    "high": 1,
                    "low": 1,
                    "close": 1,
                    "volume": 1,
                    "providerStartTimestampMs": 1779287400000,
                }
            ],
        },
    )
    for payload in invalid_payloads:
        try:
            StockAggregateBarsResponse.model_validate(payload)
        except Exception:
            continue
        raise AssertionError(
            f"Expected stock aggregate response validation to reject {payload!r}."
        )


def test_live_stock_aggregate_snapshot_validates_topic_and_last_bar() -> None:
    bar = StockAggregateBar(
        symbol="aapl",
        interval="1m",
        timestamp="2026-05-20T14:30:00Z",
        open=191.25,
        high=191.9,
        low=191.1,
        close=191.7,
        volume=1250,
        providerStartTimestampMs=1779287400000,
        providerEndTimestampMs=1779287459999,
        providerDelaySeconds=1.25,
        observedAt="2026-05-20T14:30:02Z",
        sequence=7,
    )
    snapshot = LiveStockAggregateSnapshot(
        symbol="aapl",
        interval="1m",
        topic="market-prices:massive:stocks:AAPL:1m",
        status="healthy",
        lastBar=bar,
        lastBarAgeSeconds=1.5,
        providerDelaySeconds=1.25,
        connectedAt="2026-05-20T14:00:00Z",
        lastProviderMessageAt="2026-05-20T14:30:02Z",
        lastStatusAt="2026-05-20T14:30:03Z",
        lastError=None,
    )

    assert snapshot.symbol == "AAPL"
    assert snapshot.providerSymbol == "AAPL"
    assert snapshot.lastBar == bar
    assert snapshot.status == "healthy"

    invalid_payloads = (
        {
            "symbol": "AAPL",
            "interval": "1m",
            "topic": "market-prices:massive:stocks:MSFT:1m",
            "status": "healthy",
            "lastStatusAt": "2026-05-20T14:30:03Z",
        },
        {
            "symbol": "AAPL",
            "interval": "5m",
            "topic": "market-prices:massive:stocks:AAPL:5m",
            "status": "healthy",
            "lastBar": bar,
            "lastStatusAt": "2026-05-20T14:30:03Z",
        },
    )
    for payload in invalid_payloads:
        try:
            LiveStockAggregateSnapshot.model_validate(payload)
        except Exception:
            continue
        raise AssertionError(
            f"Expected live stock aggregate snapshot to reject {payload!r}."
        )


def test_stock_aggregate_artifacts_include_schema_and_typescript_exports() -> None:
    root = Path(__file__).resolve().parents[2]
    response_schema_path = root / "schemas" / "stock-aggregate-bars-response.schema.json"
    snapshot_schema_path = root / "schemas" / "live-stock-aggregate-snapshot.schema.json"
    event_schema_path = root / "schemas" / "stock-aggregate-stream-event-type.schema.json"
    type_path = root / "ts" / "src" / "contracts.ts"

    response_schema = json.loads(response_schema_path.read_text(encoding="utf-8"))
    snapshot_schema = json.loads(snapshot_schema_path.read_text(encoding="utf-8"))
    event_schema = json.loads(event_schema_path.read_text(encoding="utf-8"))

    assert "StockAggregateBar" in response_schema["$defs"]
    assert response_schema["properties"]["interval"]["enum"] == [
        "1s",
        "1m",
        "5m",
        "15m",
        "daily",
        "weekly",
        "monthly",
    ]
    assert "StockAggregateBar" in snapshot_schema["$defs"]
    assert event_schema["enum"] == [
        "market_price.stock_aggregate",
        "market_price.stock_status",
    ]

    generated_types = type_path.read_text(encoding="utf-8")
    assert "export type StockAggregateInterval" in generated_types
    assert "export type StockAggregateStreamEventType" in generated_types
    assert "export interface StockAggregateBar" in generated_types
    assert "export interface StockAggregateBarsResponse" in generated_types
    assert "export interface LiveStockAggregateSnapshot" in generated_types
    assert "lastBar?: StockAggregateBar | null;" in generated_types


def test_live_stock_trade_contract_normalizes_massive_trade_shape() -> None:
    event_adapter = TypeAdapter(StockTradeStreamEventType)

    assert event_adapter.validate_python("market_price.stock_trade") == (
        "market_price.stock_trade"
    )
    assert event_adapter.validate_python("market_price.stock_trade_status") == (
        "market_price.stock_trade_status"
    )

    tick = LiveStockTradeTick(
        symbol=" t.aapl ",
        providerChannel="t.aapl",
        price=191.72,
        size=100,
        exchangeId=12,
        conditions=["1", 37],
        tradeId="trade-123",
        tape=3,
        providerSequenceNumber=875,
        providerTimestampMs=1779287400123,
        tradeReportingFacilityId=201,
        tradeReportingFacilityTimestampMs=1779287400124,
        observedAt="2026-05-20T14:30:02",
        sequence=7,
    )

    assert tick.symbol == "AAPL"
    assert tick.providerSymbol == "AAPL"
    assert tick.providerChannel == "T.AAPL"
    assert tick.conditions == [1, 37]
    assert tick.observedAt.isoformat() == "2026-05-20T14:30:02+00:00"

    snapshot = LiveStockTradeSnapshot(
        symbol="aapl",
        providerChannel="T.AAPL",
        topic="market-prices:massive:stocks:AAPL:trades",
        status="healthy",
        lastTrade=tick,
        lastTradeAgeSeconds=1.5,
        connectedAt="2026-05-20T14:00:00Z",
        lastProviderMessageAt="2026-05-20T14:30:02Z",
        lastStatusAt="2026-05-20T14:30:03Z",
        lastError=None,
    )

    assert snapshot.symbol == "AAPL"
    assert snapshot.providerSymbol == "AAPL"
    assert snapshot.lastTrade == tick
    assert snapshot.status == "healthy"


def test_live_stock_trade_contract_rejects_cross_symbol_payloads() -> None:
    matching_tick = LiveStockTradeTick(
        symbol="AAPL",
        providerChannel="T.AAPL",
        price=191.72,
        providerTimestampMs=1779287400123,
        observedAt="2026-05-20T14:30:02Z",
        sequence=1,
    )

    invalid_payloads = (
        {
            "symbol": "AAPL",
            "providerSymbol": "MSFT",
            "providerChannel": "T.AAPL",
            "price": 191.72,
            "providerTimestampMs": 1779287400123,
            "observedAt": "2026-05-20T14:30:02Z",
            "sequence": 1,
        },
        {
            "symbol": "AAPL",
            "providerChannel": "Q.AAPL",
            "price": 191.72,
            "providerTimestampMs": 1779287400123,
            "observedAt": "2026-05-20T14:30:02Z",
            "sequence": 1,
        },
        {
            "symbol": "AAPL",
            "providerChannel": "T.AAPL",
            "price": 0,
            "providerTimestampMs": 1779287400123,
            "observedAt": "2026-05-20T14:30:02Z",
            "sequence": 1,
        },
    )
    for payload in invalid_payloads:
        try:
            LiveStockTradeTick.model_validate(payload)
        except Exception:
            continue
        raise AssertionError(
            f"Expected live stock trade tick validation to reject {payload!r}."
        )

    invalid_snapshots = (
        {
            "symbol": "AAPL",
            "providerChannel": "T.AAPL",
            "topic": "market-prices:massive:stocks:MSFT:trades",
            "status": "healthy",
            "lastStatusAt": "2026-05-20T14:30:03Z",
        },
        {
            "symbol": "MSFT",
            "providerChannel": "T.MSFT",
            "topic": "market-prices:massive:stocks:MSFT:trades",
            "status": "healthy",
            "lastTrade": matching_tick,
            "lastStatusAt": "2026-05-20T14:30:03Z",
        },
    )
    for payload in invalid_snapshots:
        try:
            LiveStockTradeSnapshot.model_validate(payload)
        except Exception:
            continue
        raise AssertionError(
            f"Expected live stock trade snapshot validation to reject {payload!r}."
        )


def test_live_stock_trade_artifacts_include_schema_and_typescript_exports() -> None:
    root = Path(__file__).resolve().parents[2]
    tick_schema_path = root / "schemas" / "live-stock-trade-tick.schema.json"
    snapshot_schema_path = root / "schemas" / "live-stock-trade-snapshot.schema.json"
    event_schema_path = root / "schemas" / "stock-trade-stream-event-type.schema.json"
    type_path = root / "ts" / "src" / "contracts.ts"

    tick_schema = json.loads(tick_schema_path.read_text(encoding="utf-8"))
    snapshot_schema = json.loads(snapshot_schema_path.read_text(encoding="utf-8"))
    event_schema = json.loads(event_schema_path.read_text(encoding="utf-8"))

    assert tick_schema["properties"]["providerChannel"]["maxLength"] == 80
    assert tick_schema["properties"]["price"]["exclusiveMinimum"] == 0
    assert "LiveStockTradeTick" in snapshot_schema["$defs"]
    assert event_schema["enum"] == [
        "market_price.stock_trade",
        "market_price.stock_trade_status",
    ]

    generated_types = type_path.read_text(encoding="utf-8")
    assert "export type StockTradeStreamEventType" in generated_types
    assert "export interface LiveStockTradeTick" in generated_types
    assert "export interface LiveStockTradeSnapshot" in generated_types
    assert "lastTrade?: LiveStockTradeTick | null;" in generated_types


def test_live_currency_price_contract_normalizes_massive_trade_shape() -> None:
    adapter = TypeAdapter(LiveMarketPriceStatus)

    assert adapter.validate_python("healthy") == "healthy"
    assert adapter.validate_python("degraded") == "degraded"
    assert adapter.validate_python("unavailable") == "unavailable"

    tick = LiveCurrencyPriceTick(
        symbol=" x:btcusd ",
        providerPair="btc-usd",
        providerChannel="xt.btc-usd",
        price=101250.25,
        size=0.025,
        exchangeId=3,
        conditions=["1", 2],
        tradeId="trade-123",
        providerTimestampMs=1779235200123,
        providerReceivedTimestampMs=1779235200456,
        observedAt="2026-05-20T00:05:00",
        sequence=7,
    )

    assert tick.symbol == "BTCUSD"
    assert tick.baseCurrency == "BTC"
    assert tick.quoteCurrency == "USD"
    assert tick.providerPair == "BTC-USD"
    assert tick.providerChannel == "XT.BTC-USD"
    assert tick.conditions == [1, 2]
    assert tick.observedAt.isoformat() == "2026-05-20T00:05:00+00:00"

    snapshot = LiveCurrencyPriceSnapshot(
        symbol="BTC/USD",
        providerPair="BTC-USD",
        providerChannel="XT.BTC-USD",
        topic="market-prices:massive:crypto:BTCUSD",
        status="healthy",
        lastTick=tick,
        lastTickAgeSeconds=1.5,
        connectedAt="2026-05-20T00:00:00Z",
        lastProviderMessageAt="2026-05-20T00:05:00Z",
        lastStatusAt="2026-05-20T00:05:01Z",
    )

    assert snapshot.symbol == "BTCUSD"
    assert snapshot.baseCurrency == "BTC"
    assert snapshot.quoteCurrency == "USD"
    assert snapshot.lastTick == tick
    assert snapshot.status == "healthy"


def test_live_currency_price_contract_rejects_cross_pair_payloads() -> None:
    invalid_payloads = (
        {
            "symbol": "BTCUSD",
            "providerPair": "ETH-USD",
            "providerChannel": "XT.BTC-USD",
            "price": 101000,
            "providerTimestampMs": 1779235200000,
            "observedAt": "2026-05-20T00:00:00Z",
            "sequence": 1,
        },
        {
            "symbol": "BTCUSD",
            "providerPair": "BTC-USD",
            "providerChannel": "XA.BTC-USD",
            "price": 101000,
            "providerTimestampMs": 1779235200000,
            "observedAt": "2026-05-20T00:00:00Z",
            "sequence": 1,
        },
        {
            "symbol": "BTCUSD",
            "providerPair": "BTC-USD",
            "providerChannel": "XT.BTC-USD",
            "price": 0,
            "providerTimestampMs": 1779235200000,
            "observedAt": "2026-05-20T00:00:00Z",
            "sequence": 1,
        },
    )
    for payload in invalid_payloads:
        try:
            LiveCurrencyPriceTick.model_validate(payload)
        except Exception:
            continue
        raise AssertionError(
            f"Expected live currency price validation to reject {payload!r}."
        )

    matching_tick = LiveCurrencyPriceTick(
        symbol="BTCUSD",
        providerPair="BTC-USD",
        providerChannel="XT.BTC-USD",
        price=101000,
        providerTimestampMs=1779235200000,
        observedAt="2026-05-20T00:00:00Z",
        sequence=1,
    )
    try:
        LiveCurrencyPriceSnapshot(
            symbol="ETHUSD",
            providerPair="ETH-USD",
            providerChannel="XT.ETH-USD",
            topic="market-prices:massive:crypto:ETHUSD",
            status="healthy",
            lastTick=matching_tick,
            lastStatusAt="2026-05-20T00:00:01Z",
        )
    except Exception:
        return
    raise AssertionError("Expected snapshot validation to reject mismatched lastTick.")


def test_live_currency_price_artifacts_include_schema_and_typescript_exports() -> None:
    root = Path(__file__).resolve().parents[2]
    tick_schema_path = root / "schemas" / "live-currency-price-tick.schema.json"
    snapshot_schema_path = root / "schemas" / "live-currency-price-snapshot.schema.json"
    type_path = root / "ts" / "src" / "contracts.ts"

    tick_schema = json.loads(tick_schema_path.read_text(encoding="utf-8"))
    snapshot_schema = json.loads(snapshot_schema_path.read_text(encoding="utf-8"))

    assert tick_schema["properties"]["providerChannel"]["maxLength"] == 80
    assert tick_schema["properties"]["price"]["exclusiveMinimum"] == 0
    assert "LiveCurrencyPriceTick" in snapshot_schema["$defs"]

    generated_types = type_path.read_text(encoding="utf-8")
    assert "export type LiveMarketPriceStatus" in generated_types
    assert "export interface LiveCurrencyPriceTick" in generated_types
    assert "export interface LiveCurrencyPriceSnapshot" in generated_types
    assert "status: LiveMarketPriceStatus;" in generated_types


def test_currency_intraday_paths_use_shared_domain_root() -> None:
    assert (
        DataPaths.get_bronze_currency_intraday_run_path("run-123")
        == "currency/intraday/runs/run-123"
    )
    assert (
        DataPaths.get_silver_currency_intraday_bucket_path("1m", "b")
        == "currency/intraday/1m/buckets/B"
    )
    assert (
        DataPaths.get_gold_currency_intraday_features_bucket_path("15m", "x")
        == "currency/intraday/features/15m/buckets/X"
    )
    assert (
        DataPaths.get_gold_currency_intraday_features_domain_path("5m")
        == "currency/intraday/features/5m"
    )


def test_intraday_watchlist_upsert_normalizes_and_deduplicates_symbols() -> None:
    payload = IntradayWatchlistUpsertRequest(
        name="Large Cap Momentum",
        description="Operator-managed intraday names.",
        symbols=["aapl", " msft ", "AAPL"],
    )

    assert payload.symbols == ["AAPL", "MSFT"]
    assert payload.pollIntervalMinutes == 5
    assert payload.refreshCooldownMinutes == 15
    assert payload.refreshDomains == ["market"]
    assert payload.marketSession == "us_equities_regular"


def test_intraday_watchlist_upsert_normalizes_refresh_domains() -> None:
    payload = IntradayWatchlistUpsertRequest(
        name="Cross Asset Refresh",
        symbols=["aapl"],
        refreshDomains=["currency", "market", "currency"],
    )

    assert payload.refreshDomains == ["currency", "market"]


def test_intraday_watchlist_symbol_append_contract_normalizes_and_reports_run_state() -> (
    None
):
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


def test_intraday_on_demand_contracts_normalize_symbols_and_report_enqueue_summary() -> (
    None
):
    request = IntradayOnDemandSymbolUpsertRequest(
        symbol=" aapl ",
        enabled=True,
        reason="  earnings desk watch  ",
    )
    config = IntradayOnDemandSymbolConfig(
        symbol="msft",
        enabled=False,
        reason="  operator paused  ",
        requestedBy="  analyst@example.com  ",
    )
    response = IntradayOnDemandSymbolListResponse(total=1, items=[config])
    summary = IntradayOnDemandEnqueueSummary(
        enabledSymbolCount=3,
        enqueuedSymbolCount=2,
        skippedSymbolCount=1,
        batchCount=1,
        queuedSymbols=["aapl", "MSFT", "AAPL"],
        skippedSymbols=[" nvda "],
    )
    run = IntradayMonitorRunSummary(
        runId="run-on-demand-1",
        watchlistId="on-demand",
        triggerKind="on_demand",
        status="queued",
        symbolCount=2,
    )

    assert request.symbol == "AAPL"
    assert request.reason == "earnings desk watch"
    assert response.items[0].symbol == "MSFT"
    assert response.items[0].reason == "operator paused"
    assert response.items[0].requestedBy == "analyst@example.com"
    assert summary.queuedSymbols == ["AAPL", "MSFT"]
    assert summary.skippedSymbols == ["NVDA"]
    assert run.triggerKind == "on_demand"


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
            refreshDomains=["market", "currency"],
            symbols=["AAPL", "MSFT"],
        ),
        currentSymbolStatuses=[
            IntradaySymbolStatus(
                symbol="aapl",
                domain="market",
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
    assert payload.watchlist.refreshDomains == ["market", "currency"]
    assert payload.currentSymbolStatuses[0].symbol == "AAPL"
    assert payload.currentSymbolStatuses[0].domain == "market"


def test_intraday_monitor_complete_request_accepts_statuses_and_events() -> None:
    payload = IntradayMonitorCompleteRequest(
        claimToken="claim-1",
        symbolStatuses=[
            IntradaySymbolStatus(
                symbol="aapl",
                domain="currency",
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
    assert payload.symbolStatuses[0].domain == "currency"
    assert payload.events[0].details["source"] == "massive"
    assert payload.refreshSymbols == ["AAPL", "MSFT"]
    assert payload.refreshRequests == [
        IntradayRefreshRequest(domain="market", symbols=["AAPL", "MSFT"])
    ]


def test_intraday_monitor_complete_request_supports_domain_refresh_requests() -> None:
    payload = IntradayMonitorCompleteRequest(
        claimToken="claim-1",
        refreshRequests=[
            IntradayRefreshRequest(domain="currency", symbols=["eurusd", "GBPUSD"]),
            IntradayRefreshRequest(domain="market", symbols=["aapl", "AAPL"]),
        ],
    )

    assert payload.refreshRequests[0].domain == "currency"
    assert payload.refreshRequests[0].symbols == ["EURUSD", "GBPUSD"]
    assert payload.refreshSymbols == ["AAPL"]


def test_intraday_refresh_claim_request_can_scope_domain() -> None:
    request = IntradayRefreshClaimRequest(executionName="job-1", domain="currency")

    assert request.domain == "currency"


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
                    **canonical.model_dump(mode="python")["signalConfigs"][
                        "trending_up"
                    ],
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
        raise AssertionError(
            "Expected legacy default-regime policy fields to be rejected."
        )


def test_regime_policy_activation_gate_requires_rules_and_revision() -> None:
    policy = RegimePolicy.model_validate(
        {
            "modelName": "default-regime",
            "modelVersion": 3,
            "mode": "activation_gate",
            "activation": {
                "allowedRegimes": ["trending_up", "low_volatility", "trending_up"],
                "blockedRegimes": ["liquidity_stress"],
                "honorModelHalt": True,
                "blockWhenUnclassified": True,
                "inactiveAction": "target_zero",
            },
        }
    )

    assert policy.mode == "activation_gate"
    assert policy.activation is not None
    assert policy.activation.allowedRegimes == ["trending_up", "low_volatility"]
    assert policy.activation.inactiveAction == "target_zero"

    for payload in (
        {
            "mode": "activation_gate",
            "activation": {"blockedRegimes": ["liquidity_stress"]},
        },
        {"modelVersion": 3, "mode": "activation_gate"},
        {
            "mode": "observe_only",
            "activation": {"blockedRegimes": ["liquidity_stress"]},
        },
    ):
        try:
            RegimePolicy.model_validate(payload)
        except Exception:
            continue
        raise AssertionError(
            f"Expected invalid regime policy payload to fail: {payload!r}"
        )


def test_regime_activation_decision_can_be_reported_on_portfolio_slices() -> None:
    decision = RegimeActivationDecision(
        state="inactive",
        reasonCode="blocked_regime",
        inactiveAction="target_zero",
        targetWeightMultiplier=0.0,
        modelName="default-regime",
        modelVersion=3,
        asOfDate="2026-05-15",
        effectiveFromDate="2026-05-15",
        activeRegimes=["liquidity_stress"],
        haltFlag=False,
    )
    slice_payload = StrategySliceAttribution(
        asOf="2026-05-15",
        sleeveId="core-trend",
        strategyName="quality-trend",
        strategyVersion=4,
        targetWeight=0.0,
        actualWeight=0.25,
        marketValue=25_000.0,
        regimeActivation=decision,
    )

    assert slice_payload.regimeActivation is not None
    assert slice_payload.regimeActivation.state == "inactive"
    assert slice_payload.regimeActivation.targetWeightMultiplier == 0.0


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
        raise AssertionError(
            "Expected RunRecordResponse to reject legacy artifact fields."
        )


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
            "regimePolicyName": "default-regime-policy",
            "regimePolicyVersion": 2,
            "riskProfileName": "balanced-long-only",
            "riskPolicyName": "balanced-risk",
            "riskPolicyVersion": 3,
            "exitPolicyName": "lifecycle-exits",
            "exitPolicyVersion": 4,
            "rebalancePolicyName": "monthly-rebalance",
            "rebalancePolicyVersion": 5,
        },
        executionSettings={
            "initialCapital": 1_000_000,
            "executionModel": "simple_bps",
            "commissionBps": 2.5,
            "slippageBps": 4.0,
        },
    )

    assert payload.strategy_version == 4
    assert payload.bar_size == "5m"
    assert payload.results_schema_version == 4
    assert payload.pins is not None
    assert payload.pins.rankingSchemaVersion == 7
    assert payload.pins.riskProfileName == "balanced-long-only"
    assert payload.pins.exitPolicyName == "lifecycle-exits"
    assert payload.pins.rebalancePolicyVersion == 5
    assert payload.executionSettings is not None
    assert payload.executionSettings.executionModel == "simple_bps"
    assert payload.executionSettings.commissionBps == 2.5


def test_run_pin_and_exit_rule_attribution_contracts_are_typed() -> None:
    pins = RunPinsResponse(
        strategyName="quality-trend",
        strategyVersion=4,
        exitPolicyName="lifecycle-exits",
        exitPolicyVersion=3,
        riskPolicyName="balanced-risk",
        riskPolicyVersion=2,
        rebalancePolicyName="monthly-rebalance",
        rebalancePolicyVersion=1,
    )
    attribution = ExitRuleAttributionResponse(
        runId="run-123",
        exitPolicyName=pins.exitPolicyName,
        exitPolicyVersion=pins.exitPolicyVersion,
        exitPolicyConfigHash="sha256:abc",
        rules=[
            {
                "ruleId": "lifecycle-target",
                "ruleType": "take_profit_fixed",
                "description": "Fixed target exit.",
                "visualKey": "take_profit_fixed",
                "priority": 1,
                "closedPositionCount": 3,
                "realizedPnl": 145.5,
                "averageRealizedReturn": 0.08,
                "winRate": 1.0,
                "averageHoldingPeriodBars": 12.3,
                "totalTransactionCost": 4.25,
            }
        ],
        unattributedExitCount=1,
        missingRuleIds=["legacy-stop"],
    )

    assert pins.riskPolicyName == "balanced-risk"
    assert attribution.rules[0].ruleType == "take_profit_fixed"
    assert attribution.unattributedExitCount == 1


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
    assert schema["oneOf"] == [
        {"required": ["strategyRef"]},
        {"required": ["strategyConfig"]},
    ]
    assert "executionSettings" in schema["properties"]
    assert "assumptions" not in schema["properties"]

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
            assert (
                "Exactly one of strategyRef or strategyConfig must be provided"
                in str(exc)
            )
        else:
            raise AssertionError(
                "Expected BacktestLookupRequest to enforce exactly one strategy input."
            )


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
        policyEventsUrl="/api/backtests/run-123/policy-events",
        dataQualityEventsUrl="/api/backtests/run-123/data-quality-events",
    )
    summary = BacktestSummary(
        total_return=0.12,
        requested_residual_cash_weight=0.0,
        executed_residual_cash_weight=0.15,
    )

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
    assert lookup.links.dataQualityEventsUrl is not None
    assert lookup.result is not None
    assert lookup.result.total_return == 0.12
    assert lookup.result.executed_residual_cash_weight == 0.15
    assert run_response.streamUrl.endswith("/events")


def test_backtest_summary_accepts_benchmark_attribution_and_nullable_compatibility() -> (
    None
):
    attribution = BacktestBenchmarkAttribution(
        benchmarkSymbol="SPY",
        strategyTotalReturn=0.12,
        benchmarkTotalReturn=0.08,
        excessTotalReturn=0.04,
        strategyAnnualizedReturn=0.11,
        benchmarkAnnualizedReturn=0.07,
        excessAnnualizedReturn=0.04,
        startTs="2026-03-08T00:00:00Z",
        endTs="2026-03-09T00:00:00Z",
        observationCount=2,
    )

    summary = BacktestSummary(
        total_return=0.12,
        annualized_return=0.11,
        benchmarkAttribution=attribution,
    )
    legacy_summary = BacktestSummary.model_validate({"total_return": 0.12})

    assert summary.benchmarkAttribution is not None
    assert summary.benchmarkAttribution.benchmarkSymbol == "SPY"
    assert summary.benchmarkAttribution.attributionMethod == "simple_total_return"
    assert summary.benchmarkAttribution.dataQualityStatus == "complete"
    assert summary.benchmarkAttribution.excessTotalReturn == 0.04
    assert legacy_summary.benchmarkAttribution is None


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
        executionSettings={
            "initialCapital": 500_000,
            "executionModel": "simple_bps",
            "commissionBps": 1.5,
            "slippageBps": 3.0,
        },
    )
    assert payload.strategyConfig is not None
    assert payload.strategyRef is None
    assert payload.executionSettings is not None
    assert payload.executionSettings.initialCapital == 500_000


def test_backtest_request_accepts_legacy_assumptions_alias_and_normalizes_cost_model() -> (
    None
):
    payload = BacktestLookupRequest.model_validate(
        {
            "strategyRef": {"strategyName": "quality-trend", "strategyVersion": 4},
            "startTs": "2026-03-08T00:00:00Z",
            "endTs": "2026-03-09T00:00:00Z",
            "barSize": "1d",
            "assumptions": {
                "initialCapital": 250000,
                "benchmarkSymbol": "SPY",
                "costModel": "default",
                "commissionBps": 1.0,
            },
        }
    )

    assert payload.executionSettings is not None
    assert payload.assumptions is payload.executionSettings
    assert payload.executionSettings.executionModel == "simple_bps"
    assert payload.executionSettings.benchmarkSymbol == "SPY"


def test_backtest_execution_settings_reject_unsupported_execution_model() -> None:
    try:
        BacktestExecutionSettings(executionModel="high_touch")
    except Exception as exc:
        assert "simple_bps" in str(exc)
    else:
        raise AssertionError(
            "Expected unsupported backtest execution model to fail validation."
        )


def test_backtest_run_request_rejects_unsupported_inline_backtest_fields() -> None:
    invalid_payloads = [
        (
            {
                "strategyConfig": {
                    "universeConfigName": "large-cap-quality",
                    "rankingSchemaName": "quality",
                    "costModel": "high_touch",
                    "exits": [],
                },
                "startTs": "2026-03-08T00:00:00Z",
                "endTs": "2026-03-09T00:00:00Z",
                "barSize": "1d",
            },
            "strategyConfig.costModel='default'",
        ),
        (
            {
                "strategyConfig": {
                    "universeConfigName": "large-cap-quality",
                    "rankingSchemaName": "quality",
                    "rebalancePolicy": {"frequency": "manual"},
                    "exits": [],
                },
                "startTs": "2026-03-08T00:00:00Z",
                "endTs": "2026-03-09T00:00:00Z",
                "barSize": "1d",
            },
            "rebalancePolicy.frequency='manual'",
        ),
        (
            {
                "strategyConfig": {
                    "universeConfigName": "large-cap-quality",
                    "rankingSchemaName": "quality",
                    "regimePolicyConfigName": "observe-default",
                    "regimePolicyConfigVersion": 2,
                    "exits": [],
                },
                "startTs": "2026-03-08T00:00:00Z",
                "endTs": "2026-03-09T00:00:00Z",
                "barSize": "1d",
            },
            "normalize to regimeSource",
        ),
    ]

    for invalid_payload, expected_error in invalid_payloads:
        try:
            BacktestRunRequest.model_validate(invalid_payload)
        except Exception as exc:
            assert expected_error in str(exc)
        else:
            raise AssertionError(
                f"Expected backtest submission to reject unsupported payload: {expected_error}"
            )


def test_backtest_complete_request_rejects_legacy_artifact_manifest_path() -> None:
    try:
        BacktestCompleteRequest(
            summary={"run_id": "run-123"}, artifactManifestPath="backtests/run-123"
        )
    except Exception as exc:
        assert "artifactManifestPath" in str(exc)
    else:
        raise AssertionError(
            "Expected BacktestCompleteRequest to reject artifactManifestPath."
        )


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
        results_schema_version=9,
        bar_size="1d",
        periods_per_year=252,
        strategy_scope="portfolio",
    )
    schema = TimeseriesResponse.model_json_schema()

    assert metadata.results_schema_version == 9
    assert metadata.bar_size == "1d"
    assert schema["properties"]["metadata"]["default"] is None
    assert (
        schema["$defs"]["BacktestResultMetadata"]["properties"][
            "results_schema_version"
        ]["default"]
        == 9
    )


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


def test_timeseries_point_response_supports_period_return_and_daily_return_compatibility() -> (
    None
):
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


def test_rolling_metric_point_response_supports_window_periods_and_legacy_window_days() -> (
    None
):
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


def test_backtest_response_metadata_attaches_to_timeseries_and_rolling_metrics() -> (
    None
):
    metadata = BacktestResultMetadata(
        results_schema_version=4,
        bar_size="1d",
        periods_per_year=252,
        strategy_scope="strategy",
    )
    timeseries = TimeseriesResponse(
        metadata=metadata, points=[], total_points=0, truncated=False
    )
    rolling_metrics = RollingMetricsResponse(
        metadata=metadata, points=[], total_points=0, truncated=True
    )

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


def test_trade_and_closed_position_contracts_support_position_lifecycle_fields() -> (
    None
):
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
            "requested_target_weight": 0.5,
            "executed_target_weight": 0.35,
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
    assert trade.executed_target_weight == 0.35
    assert closed.realized_return == 0.063
    assert closed.exit_rule_id == "tp-1"


def test_shared_path_rules_are_stable() -> None:
    assert (
        DataPaths.get_gold_finance_bucket_path("Balance Sheet", "a")
        == "finance/balance_sheet/buckets/A"
    )
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
        raise AssertionError(
            "Expected revision validation failure when weights do not sum to 1.0."
        )


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


def test_portfolio_account_upsert_request_accepts_optional_rebalance_schedule_overrides() -> (
    None
):
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
        raise AssertionError(
            "Expected fee event validation failure when symbol is provided."
        )


def test_portfolio_snapshot_and_rebalance_proposal_capture_monitoring_contracts() -> (
    None
):
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


def test_portfolio_forecast_and_next_rebalance_contracts_capture_authoritative_monitoring_shapes() -> (
    None
):
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


def test_government_signal_contract_and_summary_models_accept_expected_payloads() -> (
    None
):
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
    payload = GovernmentSignalMappingOverrideRequest(
        action="map", symbol="RTX", reason="Matched issuer"
    )
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
    override = SymbolProfileOverride(
        symbol="AAPL", fieldName="sector_norm", value="Technology", isLocked=True
    )
    run = SymbolCleanupRunSummary(runId="run-1", status="queued")

    assert detail.overrides == []
    assert summary.backlogCount == 0
    assert override.isLocked is True
    assert run.mode == "fill_missing"


def test_symbol_cleanup_run_review_response_captures_work_item_resolution() -> None:
    item = SymbolCleanupWorkReviewItem(
        workId="work-1",
        runId="run-1",
        symbol="AAPL",
        status="completed",
        requestedFields=["sector_norm", "issuer_summary_short"],
        attemptCount=2,
        executionName="symbol-cleanup-worker",
        createdAt="2026-05-14T06:00:00Z",
        claimedAt="2026-05-14T06:01:00Z",
        completedAt="2026-05-14T06:01:45Z",
        updatedAt="2026-05-14T06:01:45Z",
        acceptedUpdateCount=1,
        rejectedUpdateCount=1,
        lockedSkipCount=1,
        overwriteCount=0,
        result={
            "symbol": "AAPL",
            "profile": {
                "sector_norm": "Technology",
                "issuer_summary_short": "Consumer hardware and services company.",
            },
            "model": "gpt-5.4",
            "confidence": 0.91,
            "warnings": ["locked field skipped"],
        },
    )
    response = SymbolCleanupRunReviewResponse(
        run=SymbolCleanupRunSummary(
            runId="run-1",
            status="completed",
            queuedCount=1,
            completedCount=1,
            acceptedUpdateCount=1,
            rejectedUpdateCount=1,
            lockedSkipCount=1,
        ),
        totalCount=1,
        limit=50,
        offset=0,
        items=[item],
    )

    assert response.run.runId == "run-1"
    assert response.totalCount == 1
    assert response.items[0].attemptCount == 2
    assert response.items[0].executionName == "symbol-cleanup-worker"
    assert response.items[0].result is not None
    assert response.items[0].result.profile.sector_norm == "Technology"


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
    acknowledge = AcknowledgeBrokerAlertRequest(
        note="Connector rerouted to manual follow-up."
    )
    remove = RemoveBrokerAccountRequest(reason="Remove duplicate paper account.")
    remove_response = RemoveBrokerAccountResponse(
        accountId=" alpaca-core ",
        removed=True,
        message="Broker account removed.",
        generatedAt="2026-04-20T13:46:00Z",
    )
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
    listing = BrokerAccountListResponse(
        accounts=[summary], generatedAt="2026-04-20T13:45:00Z"
    )

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
    assert remove.reason == "Remove duplicate paper account."
    assert remove_response.accountId == "alpaca-core"
    assert remove_response.removed is True
    assert (
        TypeAdapter(BrokerAccountActionType).validate_python("remove_account")
        == "remove_account"
    )
    assert action_response.resultingConnectionHealth is not None
    assert action_response.resultingConnectionHealth.syncStatus == "syncing"
    assert listing.accounts[0].tradeReadiness == "blocked"


def test_broker_account_contracts_accept_kalshi_vendor() -> None:
    summary = BrokerAccountSummary(
        accountId="kalshi-live-subaccount-0",
        broker="kalshi",
        name="Kalshi Live Subaccount 0",
        accountNumberMasked="GEN-0001",
        baseCurrency="USD",
        overallStatus="warning",
        tradeReadiness="ready",
        connectionHealth={
            "overallStatus": "warning",
            "authStatus": "authenticated",
            "connectionState": "degraded",
            "syncStatus": "never_synced",
            "staleReason": "Seeded account; provider refresh has not completed.",
            "syncPaused": False,
        },
    )

    assert summary.broker == "kalshi"
    assert summary.tradeReadiness == "ready"


def test_broker_account_onboarding_contracts_capture_discovery_and_create_response() -> (
    None
):
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
    assert candidate_list.candidates[0].allowedExecutionPostures == [
        "monitor_only",
        "paper",
    ]
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
            maxSinglePositionExposure={
                "mode": "pct_of_allocatable_capital",
                "value": 8.5,
            },
            maxGrossExposurePct=100,
            maxNetExposurePct=80,
            maxDailyLossPct=2.5,
            maxAdvParticipationPct=5,
            allowedSides=["long"],
            allowedAssetClasses=["equity", "option"],
            allowLiveOrders=False,
            requireOrderConfirmation=True,
            reduceOnly=False,
        ),
        effectivePolicy=BrokerTradingPolicy(
            maxOpenPositions=10,
            maxSinglePositionExposure={
                "mode": "pct_of_allocatable_capital",
                "value": 8.0,
            },
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
                    "strategy": {
                        "strategyName": "defensive-value",
                        "strategyVersion": 2,
                    },
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
    assert configuration.requestedPolicy.maxGrossExposurePct == 100
    assert configuration.requestedPolicy.maxAdvParticipationPct == 5
    assert configuration.requestedPolicy.tradeApproval.approvalMode == "disabled"
    assert configuration.allocation.items[0].strategy.strategyName == "quality-trend"
    assert configuration.audit[0].grantedRoles == [
        "AssetAllocation.AccountPolicy.Write"
    ]
    assert policy_request.expectedConfigurationVersion == 4
    assert allocation_request.items[1].targetNotionalBaseCcy == 100000.0

    for invalid_policy, expected in (
        (
            {"allowedSides": ["short"], "requireBorrowLocate": False},
            "borrow/locate",
        ),
        (
            {"allowLiveOrders": True, "requireOrderConfirmation": False},
            "order confirmation",
        ),
    ):
        try:
            BrokerTradingPolicy.model_validate(invalid_policy)
        except Exception as exc:
            assert expected in str(exc)
        else:
            raise AssertionError(
                f"Expected BrokerTradingPolicy to reject {invalid_policy!r}."
            )


def test_broker_trade_approval_policy_contracts_gate_live_bearer_release() -> None:
    policy = BrokerTradeApprovalPolicy(
        approvalMode="required",
        releaseMode="live_bearer",
        enabledEnvironments=["paper", "live", "live"],
        recipientGroupId="desk-reviewers",
        maxLiveBearerNotional=2500.0,
        tokenTtlSeconds=300,
    )

    assert policy.enabledEnvironments == ["paper", "live"]
    assert policy.maxLiveBearerNotional == 2500.0
    assert policy.requireDistinctRequester is True

    for invalid_policy, expected in (
        (
            {
                "approvalMode": "required",
                "releaseMode": "live_bearer",
                "enabledEnvironments": ["live"],
                "recipientEmails": ["desk@example.com"],
            },
            "maxLiveBearerNotional",
        ),
        (
            {
                "approvalMode": "required",
                "releaseMode": "paper_sandbox_bearer",
                "enabledEnvironments": ["paper"],
            },
            "recipient group",
        ),
    ):
        try:
            BrokerTradeApprovalPolicy.model_validate(invalid_policy)
        except Exception as exc:
            assert expected in str(exc)
        else:
            raise AssertionError(
                f"Expected BrokerTradeApprovalPolicy to reject {invalid_policy!r}."
            )


def test_trade_approval_review_context_contracts_are_structured_and_optional() -> None:
    order = {
        "accountId": "acct-live",
        "environment": "live",
        "clientRequestId": "client-approval-1",
        "symbol": "SPY",
        "side": "buy",
        "orderType": "market",
        "timeInForce": "day",
        "assetClass": "etf",
        "quantity": 1.0,
        "optionLegs": [],
        "allowExtendedHours": False,
        "source": "rebalance_preview",
        "strategyRef": {"strategyName": "quality-trend", "strategyVersion": 4},
        "exitPolicyName": "desk-exit",
        "exitPolicyVersion": 4,
    }
    review_context = {
        "source": "rebalance_proposal",
        "accountLabel": "Core Live",
        "provider": "alpaca",
        "proposalId": "proposal-1",
        "proposalTradeIndex": 0,
        "sleeveId": "quality-core",
        "sleeveName": "Quality Core",
        "strategyRef": {"strategyName": "quality-trend", "strategyVersion": 4},
        "policyVersion": 7,
        "estimatedCost": 525.0,
        "estimatedFees": 1.25,
        "cashAfter": 9475.0,
        "buyingPowerAfter": 9475.0,
        "riskChecks": [
            {
                "checkId": "approval-live-bearer-cap",
                "code": "max_live_bearer_notional",
                "label": "Live bearer release cap",
                "status": "pass",
                "severity": "info",
                "blocking": False,
                "message": "Within live bearer cap.",
            }
        ],
        "warnings": ["Live release requires one-time approval link."],
        "confirmationRequired": True,
        "releaseMode": "live_bearer",
    }

    payload = TradeApprovalPayload(
        accountId="acct-live",
        previewId="preview-1",
        orderHash="hash-1",
        placeIdempotencyKey="place-idempotency-1",
        exitPolicyName="desk-exit",
        exitPolicyVersion=4,
        order=order,
        reviewContext=review_context,
    )
    status = NotificationStatusResponse(
        requestId="notification-1",
        kind="trade_approval",
        status="delivered",
        sourceRepo="asset-allocation-control-plane",
        clientRequestId="client-approval-1",
        title="Approve SPY buy",
        description="Approve one SPY buy order.",
        createdAt="2026-05-28T15:00:00Z",
        updatedAt="2026-05-28T15:00:00Z",
        decisionStatus="pending",
        executionStatus="pending_approval",
        tradeApproval={
            "accountId": "acct-live",
            "previewId": "preview-1",
            "orderHash": "hash-1",
            "environment": "live",
            "symbol": "SPY",
            "side": "buy",
            "orderType": "market",
            "timeInForce": "day",
            "quantity": 1.0,
            "exitPolicyName": "desk-exit",
            "exitPolicyVersion": 4,
            "reviewContext": review_context,
        },
    )
    action = NotificationActionDetailResponse(
        requestId=status.requestId,
        tokenId="token-1",
        kind=status.kind,
        title=status.title,
        description=status.description,
        createdAt=status.createdAt,
        decisionStatus=status.decisionStatus,
        executionStatus=status.executionStatus,
        tradeApproval=status.tradeApproval,
    )
    legacy_payload = TradeApprovalPayload(
        accountId="acct-live",
        previewId="preview-2",
        orderHash="hash-2",
        placeIdempotencyKey="place-idempotency-2",
        order={**order, "clientRequestId": "client-approval-2", "source": "manual"},
    )

    assert payload.reviewContext is not None
    assert payload.reviewContext.source == "rebalance_proposal"
    assert payload.reviewContext.riskChecks[0].code == "max_live_bearer_notional"
    assert payload.exitPolicyName == "desk-exit"
    assert payload.exitPolicyVersion == 4
    assert action.tradeApproval is not None
    assert action.tradeApproval.exitPolicyName == "desk-exit"
    assert action.tradeApproval.exitPolicyVersion == 4
    assert action.tradeApproval.reviewContext is not None
    assert action.tradeApproval.reviewContext.releaseMode == "live_bearer"
    assert legacy_payload.exitPolicyName == "desk-exit"
    assert legacy_payload.exitPolicyVersion == 4
    assert legacy_payload.reviewContext is None


def test_trade_approval_create_request_routes_manual_and_rebalance_sources() -> None:
    manual_request = TradeApprovalCreateRequest(
        source="manual_preview",
        clientRequestId="approval-client-1",
        idempotencyKey="approval-idempotency-1",
        previewId="preview-1",
        targetUrl="https://example.com/trade-desk",
        reason="Desk review requested.",
        exitPolicyName="desk-exit",
        exitPolicyVersion=4,
    )
    rebalance_request = TradeApprovalCreateRequest(
        source="rebalance_proposal",
        clientRequestId="approval-client-2",
        idempotencyKey="approval-idempotency-2",
        proposalId="proposal-1",
        proposalTradeIndexes=[2, 0, 2],
        exitPolicyName="desk-exit",
        exitPolicyVersion=4,
        releaseMode="paper_sandbox_bearer",
    )
    response = TradeApprovalCreateResponse(
        accountId="acct-live",
        approvals=[],
    )

    assert manual_request.previewId == "preview-1"
    assert rebalance_request.proposalTradeIndexes == [0, 2]
    assert response.accountId == "acct-live"
    assert rebalance_request.exitPolicyName == "desk-exit"
    assert rebalance_request.exitPolicyVersion == 4

    for invalid_request, expected in (
        (
            {
                "source": "manual_preview",
                "clientRequestId": "client",
                "idempotencyKey": "approval-idempotency-3",
                "exitPolicyName": "desk-exit",
                "exitPolicyVersion": 4,
            },
            "previewId",
        ),
        (
            {
                "source": "rebalance_proposal",
                "clientRequestId": "client",
                "idempotencyKey": "approval-idempotency-4",
                "proposalId": "proposal-1",
                "exitPolicyName": "desk-exit",
                "exitPolicyVersion": 4,
            },
            "proposalTradeIndexes",
        ),
        (
            {
                "source": "manual_preview",
                "clientRequestId": "client",
                "idempotencyKey": "approval-idempotency-5",
                "previewId": "preview-1",
                "exitPolicyName": "desk-exit",
            },
            "exitPolicyVersion",
        ),
    ):
        try:
            TradeApprovalCreateRequest.model_validate(invalid_request)
        except Exception as exc:
            assert expected in str(exc)
        else:
            raise AssertionError(
                f"Expected TradeApprovalCreateRequest to reject {invalid_request!r}."
            )
