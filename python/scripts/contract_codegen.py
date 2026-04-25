from __future__ import annotations

import json
import types
from datetime import date, datetime
from pathlib import Path
from typing import Any, get_args, get_origin, get_type_hints

from pydantic import BaseModel, TypeAdapter

from asset_allocation_contracts import (
    ai_chat,
    backtest,
    broker_accounts,
    government_signals,
    intraday,
    job_metadata,
    portfolio,
    ranking,
    regime,
    strategy,
    strategy_publication,
    symbol_enrichment,
    trade_desk,
    ui_config,
)


SCHEMA_EXPORTS: list[tuple[str, Any]] = [
    ("strategy-config.schema.json", strategy.StrategyConfig),
    ("universe-definition.schema.json", strategy.UniverseDefinition),
    ("universe-catalog.schema.json", strategy.UniverseCatalogResponse),
    ("universe-preview.schema.json", strategy.UniversePreviewResponse),
    ("ranking-schema.schema.json", ranking.RankingSchemaConfig),
    ("regime-policy.schema.json", regime.RegimePolicy),
    ("regime-model-config.schema.json", regime.RegimeModelConfig),
    ("regime-snapshot.schema.json", regime.RegimeSnapshot),
    ("regime-input-row.schema.json", regime.RegimeInputRow),
    ("regime-transition-row.schema.json", regime.RegimeTransitionRow),
    ("regime-model-summary.schema.json", regime.RegimeModelSummary),
    ("regime-model-revision.schema.json", regime.RegimeModelRevision),
    ("regime-model-detail.schema.json", regime.RegimeModelDetailResponse),
    ("ui-runtime-config.schema.json", ui_config.UiRuntimeConfig),
    ("auth-session-status.schema.json", ui_config.AuthSessionStatus),
    ("runtime-job-metadata.schema.json", job_metadata.RuntimeJobMetadata),
    (
        "strategy-publication-reconcile-signal-request.schema.json",
        strategy_publication.StrategyPublicationReconcileSignalRequest,
    ),
    (
        "strategy-publication-reconcile-signal-response.schema.json",
        strategy_publication.StrategyPublicationReconcileSignalResponse,
    ),
    ("backtest-run-record.schema.json", backtest.RunRecordResponse),
    ("backtest-run-list.schema.json", backtest.RunListResponse),
    ("backtest-lookup-request.schema.json", backtest.BacktestLookupRequest),
    ("backtest-lookup-response.schema.json", backtest.BacktestLookupResponse),
    ("backtest-run-request.schema.json", backtest.BacktestRunRequest),
    ("backtest-run-response.schema.json", backtest.BacktestRunResponse),
    ("backtest-summary.schema.json", backtest.BacktestSummary),
    ("backtest-stream-event.schema.json", backtest.BacktestStreamEvent),
    ("backtest-timeseries.schema.json", backtest.TimeseriesResponse),
    ("backtest-rolling-metrics.schema.json", backtest.RollingMetricsResponse),
    ("backtest-trade-list.schema.json", backtest.TradeListResponse),
    ("backtest-closed-position-list.schema.json", backtest.ClosedPositionListResponse),
    ("backtest-claim-request.schema.json", backtest.BacktestClaimRequest),
    ("backtest-start-request.schema.json", backtest.BacktestStartRequest),
    ("backtest-complete-request.schema.json", backtest.BacktestCompleteRequest),
    ("backtest-fail-request.schema.json", backtest.BacktestFailRequest),
    ("backtest-reconcile-response.schema.json", backtest.BacktestReconcileResponse),
    ("broker-account-detail.schema.json", broker_accounts.BrokerAccountDetail),
    ("broker-account-list.schema.json", broker_accounts.BrokerAccountListResponse),
    ("broker-account-action-response.schema.json", broker_accounts.BrokerAccountActionResponse),
    ("broker-account-alert.schema.json", broker_accounts.BrokerAccountAlert),
    ("broker-account-summary.schema.json", broker_accounts.BrokerAccountSummary),
    ("broker-account-configuration.schema.json", broker_accounts.BrokerAccountConfiguration),
    ("broker-trading-policy.schema.json", broker_accounts.BrokerTradingPolicy),
    ("broker-position-size-limit.schema.json", broker_accounts.BrokerPositionSizeLimit),
    ("broker-allocation-update-request.schema.json", broker_accounts.BrokerAccountAllocationUpdateRequest),
    ("broker-trading-policy-update-request.schema.json", broker_accounts.BrokerTradingPolicyUpdateRequest),
    ("broker-capability-flags.schema.json", broker_accounts.BrokerCapabilityFlags),
    ("broker-connection-health.schema.json", broker_accounts.BrokerConnectionHealth),
    ("broker-sync-run.schema.json", broker_accounts.BrokerSyncRun),
    ("reconnect-broker-account-request.schema.json", broker_accounts.ReconnectBrokerAccountRequest),
    ("pause-broker-sync-request.schema.json", broker_accounts.PauseBrokerSyncRequest),
    ("refresh-broker-account-request.schema.json", broker_accounts.RefreshBrokerAccountRequest),
    ("acknowledge-broker-alert-request.schema.json", broker_accounts.AcknowledgeBrokerAlertRequest),
    ("trade-account-summary.schema.json", trade_desk.TradeAccountSummary),
    ("trade-account-detail.schema.json", trade_desk.TradeAccountDetail),
    ("trade-account-list.schema.json", trade_desk.TradeAccountListResponse),
    ("trade-capability-flags.schema.json", trade_desk.TradeCapabilityFlags),
    ("trade-position.schema.json", trade_desk.TradePosition),
    ("trade-position-list.schema.json", trade_desk.TradePositionListResponse),
    ("trade-order.schema.json", trade_desk.TradeOrder),
    ("trade-order-history-response.schema.json", trade_desk.TradeOrderHistoryResponse),
    ("trade-order-preview-request.schema.json", trade_desk.TradeOrderPreviewRequest),
    ("trade-order-preview-response.schema.json", trade_desk.TradeOrderPreviewResponse),
    ("trade-order-place-request.schema.json", trade_desk.TradeOrderPlaceRequest),
    ("trade-order-place-response.schema.json", trade_desk.TradeOrderPlaceResponse),
    ("trade-order-cancel-request.schema.json", trade_desk.TradeOrderCancelRequest),
    ("trade-order-cancel-response.schema.json", trade_desk.TradeOrderCancelResponse),
    ("trade-risk-check.schema.json", trade_desk.TradeRiskCheck),
    ("trade-desk-audit-event.schema.json", trade_desk.TradeDeskAuditEvent),
    ("trade-desk-audit-event-list.schema.json", trade_desk.TradeDeskAuditEventListResponse),
    ("portfolio-account.schema.json", portfolio.PortfolioAccount),
    ("portfolio-account-detail.schema.json", portfolio.PortfolioAccountDetailResponse),
    ("portfolio-account-list.schema.json", portfolio.PortfolioAccountListResponse),
    ("portfolio-account-revision.schema.json", portfolio.PortfolioAccountRevision),
    ("portfolio-account-upsert-request.schema.json", portfolio.PortfolioAccountUpsertRequest),
    ("portfolio-alert-list.schema.json", portfolio.PortfolioAlertListResponse),
    ("portfolio-assignment.schema.json", portfolio.PortfolioAssignment),
    ("portfolio-assignment-request.schema.json", portfolio.PortfolioAssignmentRequest),
    ("portfolio-definition.schema.json", portfolio.PortfolioDefinition),
    ("portfolio-definition-detail.schema.json", portfolio.PortfolioDefinitionDetailResponse),
    ("portfolio-history.schema.json", portfolio.PortfolioHistoryResponse),
    ("portfolio-ledger-event.schema.json", portfolio.PortfolioLedgerEvent),
    ("portfolio-ledger-event-request.schema.json", portfolio.PortfolioLedgerEventPayload),
    ("portfolio-list.schema.json", portfolio.PortfolioListResponse),
    ("portfolio-position-list.schema.json", portfolio.PortfolioPositionListResponse),
    ("portfolio-rebalance-apply-request.schema.json", portfolio.PortfolioRebalanceApplyRequest),
    ("portfolio-rebalance-preview-request.schema.json", portfolio.PortfolioRebalancePreviewRequest),
    ("portfolio-rebalance-proposal.schema.json", portfolio.RebalanceProposal),
    ("portfolio-revision.schema.json", portfolio.PortfolioRevision),
    ("portfolio-snapshot.schema.json", portfolio.PortfolioSnapshot),
    ("portfolio-upsert-request.schema.json", portfolio.PortfolioUpsertRequest),
    ("government-signal-congress-event.schema.json", government_signals.CongressTradeEvent),
    ("government-signal-congress-event-list.schema.json", government_signals.CongressTradeEventListResponse),
    ("government-signal-congress-version.schema.json", government_signals.CongressTradeVersion),
    ("government-signal-contract-event.schema.json", government_signals.GovernmentContractEvent),
    (
        "government-signal-contract-event-list.schema.json",
        government_signals.GovernmentContractEventListResponse,
    ),
    ("government-signal-contract-version.schema.json", government_signals.GovernmentContractVersion),
    ("government-signal-issuer-daily.schema.json", government_signals.IssuerGovernmentSignalDaily),
    ("government-signal-alert.schema.json", government_signals.GovernmentSignalAlert),
    ("government-signal-alert-list.schema.json", government_signals.GovernmentSignalAlertListResponse),
    ("government-signal-mapping-review.schema.json", government_signals.GovernmentSignalMappingReviewResponse),
    (
        "government-signal-mapping-override-request.schema.json",
        government_signals.GovernmentSignalMappingOverrideRequest,
    ),
    (
        "government-signal-mapping-override-response.schema.json",
        government_signals.GovernmentSignalMappingOverrideResponse,
    ),
    ("government-signal-issuer-summary.schema.json", government_signals.GovernmentSignalIssuerSummaryResponse),
    (
        "government-signal-portfolio-exposure-request.schema.json",
        government_signals.GovernmentSignalPortfolioExposureRequest,
    ),
    (
        "government-signal-portfolio-exposure-response.schema.json",
        government_signals.GovernmentSignalPortfolioExposureResponse,
    ),
    ("ai-chat-request.schema.json", ai_chat.AiChatRequest),
    ("ai-chat-stream-event.schema.json", TypeAdapter(ai_chat.AiChatStreamEvent)),
    ("symbol-cleanup-work-item.schema.json", symbol_enrichment.SymbolCleanupWorkItem),
    ("symbol-cleanup-run-summary.schema.json", symbol_enrichment.SymbolCleanupRunSummary),
    ("symbol-enrichment-resolve-request.schema.json", symbol_enrichment.SymbolEnrichmentResolveRequest),
    ("symbol-enrichment-resolve-response.schema.json", symbol_enrichment.SymbolEnrichmentResolveResponse),
    ("symbol-profile-current.schema.json", symbol_enrichment.SymbolProfileCurrent),
    ("symbol-profile-history-entry.schema.json", symbol_enrichment.SymbolProfileHistoryEntry),
    ("symbol-profile-override.schema.json", symbol_enrichment.SymbolProfileOverride),
    ("symbol-enrichment-summary.schema.json", symbol_enrichment.SymbolEnrichmentSummaryResponse),
    ("symbol-enrichment-symbol-list-item.schema.json", symbol_enrichment.SymbolEnrichmentSymbolListItem),
    ("symbol-enrichment-symbol-detail.schema.json", symbol_enrichment.SymbolEnrichmentSymbolDetailResponse),
    ("symbol-enrichment-enqueue-request.schema.json", symbol_enrichment.SymbolEnrichmentEnqueueRequest),
    ("intraday-watchlist-summary.schema.json", intraday.IntradayWatchlistSummary),
    ("intraday-watchlist-detail.schema.json", intraday.IntradayWatchlistDetail),
    ("intraday-watchlist-upsert-request.schema.json", intraday.IntradayWatchlistUpsertRequest),
    ("intraday-symbol-status.schema.json", intraday.IntradaySymbolStatus),
    ("intraday-monitor-run-summary.schema.json", intraday.IntradayMonitorRunSummary),
    ("intraday-monitor-event.schema.json", intraday.IntradayMonitorEvent),
    ("intraday-monitor-claim-request.schema.json", intraday.IntradayMonitorClaimRequest),
    ("intraday-monitor-claim-response.schema.json", intraday.IntradayMonitorClaimResponse),
    ("intraday-monitor-complete-request.schema.json", intraday.IntradayMonitorCompleteRequest),
    ("intraday-monitor-fail-request.schema.json", intraday.IntradayMonitorFailRequest),
    ("intraday-refresh-batch-summary.schema.json", intraday.IntradayRefreshBatchSummary),
    ("intraday-refresh-claim-request.schema.json", intraday.IntradayRefreshClaimRequest),
    ("intraday-refresh-claim-response.schema.json", intraday.IntradayRefreshClaimResponse),
    ("intraday-refresh-complete-request.schema.json", intraday.IntradayRefreshCompleteRequest),
    ("intraday-refresh-fail-request.schema.json", intraday.IntradayRefreshFailRequest),
]

TS_ALIAS_EXPORTS: list[tuple[str, Any]] = [
    ("AuthSessionMode", ui_config.AuthSessionMode),
    ("JobCategory", job_metadata.JobCategory),
    ("JobMetadataSource", job_metadata.JobMetadataSource),
    ("JobMetadataStatus", job_metadata.JobMetadataStatus),
    ("PublicationReconcileStatus", strategy_publication.PublicationReconcileStatus),
    ("ExitRuleType", strategy.ExitRuleType),
    ("ExitRuleScope", strategy.ExitScope),
    ("ExitRuleAction", strategy.ExitAction),
    ("ExitRulePriceField", strategy.PriceField),
    ("ExitRuleReference", strategy.ExitReference),
    ("IntrabarConflictPolicy", strategy.IntrabarConflictPolicy),
    ("RegimeCode", regime.RegimeCode),
    ("UniverseSource", strategy.UniverseSource),
    ("UniverseGroupOperator", strategy.UniverseGroupOperator),
    ("UniverseConditionOperator", strategy.UniverseConditionOperator),
    ("UniverseFieldId", strategy.UniverseFieldId),
    ("UniverseValue", strategy.UniverseValue),
    ("UniverseValueKind", strategy.UniverseValueKind),
    ("RankingTransformType", ranking.RankingTransformType),
    ("RankingDirection", ranking.RankingDirection),
    ("RankingMissingValuePolicy", ranking.RankingMissingValuePolicy),
    ("RegimeSignalState", regime.RegimeSignalState),
    ("RegimeTransitionType", regime.RegimeTransitionType),
    ("RegimePolicyMode", regime.RegimePolicyMode),
    ("TrendState", regime.TrendState),
    ("CurveState", regime.CurveState),
    ("RunStatus", backtest.RunStatus),
    ("BrokerVendor", broker_accounts.BrokerVendor),
    ("BrokerHealthTone", broker_accounts.BrokerHealthTone),
    ("BrokerConnectionState", broker_accounts.BrokerConnectionState),
    ("BrokerAuthStatus", broker_accounts.BrokerAuthStatus),
    ("BrokerSyncStatus", broker_accounts.BrokerSyncStatus),
    ("BrokerTradeReadiness", broker_accounts.BrokerTradeReadiness),
    ("BrokerAccountType", broker_accounts.BrokerAccountType),
    ("BrokerAlertSeverity", broker_accounts.BrokerAlertSeverity),
    ("BrokerAlertStatus", broker_accounts.BrokerAlertStatus),
    ("BrokerSyncTrigger", broker_accounts.BrokerSyncTrigger),
    ("BrokerSyncScope", broker_accounts.BrokerSyncScope),
    ("BrokerSyncRunStatus", broker_accounts.BrokerSyncRunStatus),
    ("BrokerPolicySide", broker_accounts.BrokerPolicySide),
    ("BrokerPolicyAssetClass", broker_accounts.BrokerPolicyAssetClass),
    ("BrokerPositionSizeMode", broker_accounts.BrokerPositionSizeMode),
    ("BrokerAllocationMode", broker_accounts.BrokerAllocationMode),
    ("BrokerConfigurationAuditCategory", broker_accounts.BrokerConfigurationAuditCategory),
    ("BrokerConfigurationAuditOutcome", broker_accounts.BrokerConfigurationAuditOutcome),
    ("BrokerAccountActionType", broker_accounts.BrokerAccountActionType),
    ("BrokerAccountActionStatus", broker_accounts.BrokerAccountActionStatus),
    ("TradeProvider", trade_desk.TradeProvider),
    ("TradeEnvironment", trade_desk.TradeEnvironment),
    ("TradeReadiness", trade_desk.TradeReadiness),
    ("TradeAssetClass", trade_desk.TradeAssetClass),
    ("TradeOrderSide", trade_desk.TradeOrderSide),
    ("TradeOrderType", trade_desk.TradeOrderType),
    ("TradeTimeInForce", trade_desk.TradeTimeInForce),
    ("TradeOrderStatus", trade_desk.TradeOrderStatus),
    ("TradeRiskCheckStatus", trade_desk.TradeRiskCheckStatus),
    ("TradeAuditEventType", trade_desk.TradeAuditEventType),
    ("TradeDataFreshnessState", trade_desk.TradeDataFreshnessState),
    ("TradeAuditSeverity", trade_desk.TradeAuditSeverity),
    ("PortfolioAllocationMode", portfolio.PortfolioAllocationMode),
    ("BacktestLookupState", backtest.BacktestLookupState),
    ("BacktestStreamEventType", backtest.BacktestStreamEventType),
    ("TradeRole", backtest.TradeRole),
    ("AiChatStreamEvent", ai_chat.AiChatStreamEvent),
    ("UniverseNode", strategy.UniverseGroup | strategy.UniverseCondition),
]

FORCE_OPTIONAL_FIELDS: set[tuple[str, str]] = {
    ("RegimeModelSummary", "description"),
    ("RegimeModelRevision", "description"),
}

DEPRECATED_FIELD_NOTES: dict[tuple[str, str], str] = {
    ("TimeseriesPointResponse", "daily_return"): "Use period_return.",
    ("RollingMetricPointResponse", "window_days"): "Use window_periods.",
}

_ALIAS_NAME_BY_ANNOTATION: dict[Any, str] = {annotation: name for name, annotation in TS_ALIAS_EXPORTS}


def write_schema_exports(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for filename, schema_target in SCHEMA_EXPORTS:
        (path / filename).write_text(_schema_json(schema_target), encoding="utf-8")


def write_typescript_contracts(path: Path) -> None:
    path.write_text(render_typescript_contracts(), encoding="utf-8")


def render_typescript_contracts() -> str:
    lines = [
        "// Generated by python/scripts/export_schemas.py.",
        "// Do not edit by hand.",
        "",
    ]

    for name, annotation in TS_ALIAS_EXPORTS:
        lines.append(f"export type {name} = {_ts_type(annotation, prefer_alias_name=False)};")

    for model in _typescript_interface_exports():
        lines.append("")
        lines.extend(_render_interface(model))

    return "\n".join(lines) + "\n"


def _schema_json(schema_target: Any) -> str:
    if isinstance(schema_target, TypeAdapter):
        schema = schema_target.json_schema()
    elif isinstance(schema_target, type) and issubclass(schema_target, BaseModel):
        schema = schema_target.model_json_schema()
    else:
        raise TypeError(f"Unsupported schema export target: {schema_target!r}")
    return json.dumps(schema, indent=2, sort_keys=True) + "\n"


def _typescript_interface_exports() -> list[type[BaseModel]]:
    seen: dict[type[BaseModel], None] = {}

    for _, schema_target in SCHEMA_EXPORTS:
        if isinstance(schema_target, type) and issubclass(schema_target, BaseModel):
            _collect_model_types(schema_target, seen)

    for _, annotation in TS_ALIAS_EXPORTS:
        _walk_annotation(annotation, seen)

    return list(seen)


def _collect_model_types(model: type[BaseModel], seen: dict[type[BaseModel], None]) -> None:
    if model in seen:
        return

    seen[model] = None
    type_hints = get_type_hints(model, include_extras=True)

    for field_name, field_info in model.model_fields.items():
        _walk_annotation(type_hints.get(field_name, field_info.annotation), seen)


def _walk_annotation(annotation: Any, seen: dict[type[BaseModel], None]) -> None:
    origin = get_origin(annotation)

    if origin is types.GenericAlias:
        origin = annotation.__origin__

    if origin is not None and str(origin) == "typing.Annotated":
        args = get_args(annotation)
        if args:
            _walk_annotation(args[0], seen)
        return

    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        _collect_model_types(annotation, seen)
        return

    if origin in {list, set, frozenset, tuple}:
        for arg in get_args(annotation):
            if arg is not Ellipsis:
                _walk_annotation(arg, seen)
        return

    if origin is dict:
        args = get_args(annotation)
        if len(args) == 2:
            _walk_annotation(args[1], seen)
        return

    if origin in {types.UnionType, getattr(types, "UnionType", None)} or str(origin) == "typing.Union":
        for arg in get_args(annotation):
            _walk_annotation(arg, seen)


def _render_interface(model: type[BaseModel]) -> list[str]:
    lines = [f"export interface {model.__name__} {{"]
    schema_properties = model.model_json_schema().get("properties", {})
    type_hints = get_type_hints(model, include_extras=True)

    for field_name, field_info in model.model_fields.items():
        property_schema = schema_properties.get(field_name, {})
        annotation = type_hints.get(field_name, field_info.annotation)
        ts_type = _ts_type(annotation)
        is_optional = _field_is_optional(model.__name__, field_name, field_info)
        note = DEPRECATED_FIELD_NOTES.get((model.__name__, field_name))

        if property_schema.get("deprecated"):
            lines.append(f"  /** @deprecated{f' {note}' if note else ''} */")

        lines.append(f"  {field_name}{'?' if is_optional else ''}: {ts_type};")

    if model.model_config.get("extra") == "allow":
        lines.append("  [key: string]: unknown;")

    lines.append("}")
    return lines


def _field_is_optional(model_name: str, field_name: str, field_info: Any) -> bool:
    if (model_name, field_name) in FORCE_OPTIONAL_FIELDS:
        return True
    return (not field_info.is_required()) and field_info.default is None


def _ts_type(annotation: Any, *, prefer_alias_name: bool = True) -> str:
    alias_name = _ALIAS_NAME_BY_ANNOTATION.get(annotation) if prefer_alias_name else None
    if alias_name:
        return alias_name

    origin = get_origin(annotation)

    if origin is types.GenericAlias:
        origin = annotation.__origin__

    if origin is not None and str(origin) == "typing.Annotated":
        return _ts_type(get_args(annotation)[0], prefer_alias_name=prefer_alias_name)

    if annotation is Any:
        return "unknown"
    if annotation in {str, date, datetime}:
        return "string"
    if annotation in {int, float}:
        return "number"
    if annotation is bool:
        return "boolean"
    if annotation is type(None):
        return "null"
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return annotation.__name__

    if origin in {list, set, frozenset}:
        item_type = _ts_type(
            get_args(annotation)[0] if get_args(annotation) else Any,
            prefer_alias_name=prefer_alias_name,
        )
        if " | " in item_type and not item_type.startswith("("):
            item_type = f"({item_type})"
        return f"{item_type}[]"

    if origin is dict:
        args = get_args(annotation)
        value_type = _ts_type(args[1] if len(args) == 2 else Any, prefer_alias_name=prefer_alias_name)
        return f"Record<string, {value_type}>"

    if origin is tuple:
        args = get_args(annotation)
        if len(args) == 2 and args[1] is Ellipsis:
            item_type = _ts_type(args[0], prefer_alias_name=prefer_alias_name)
            if " | " in item_type and not item_type.startswith("("):
                item_type = f"({item_type})"
            return f"{item_type}[]"
        return "[" + ", ".join(_ts_type(arg, prefer_alias_name=prefer_alias_name) for arg in args) + "]"

    if origin in {types.UnionType, getattr(types, "UnionType", None)} or str(origin) == "typing.Union":
        members: list[str] = []
        for arg in get_args(annotation):
            member = _ts_type(arg, prefer_alias_name=prefer_alias_name)
            if member not in members:
                members.append(member)
        return " | ".join(members)

    if str(origin) == "typing.Literal":
        return " | ".join(_literal_to_ts(value) for value in get_args(annotation))

    raise TypeError(f"Unsupported annotation for TS generation: {annotation!r}")


def _literal_to_ts(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace("'", "\\'")
        return f"'{escaped}'"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)
