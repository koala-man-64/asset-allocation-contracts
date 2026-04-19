from __future__ import annotations

import types
from datetime import date, datetime
from pathlib import Path
from typing import Any, get_args, get_origin, get_type_hints

from pydantic import BaseModel

from asset_allocation_contracts import backtest, ranking, regime, strategy, ui_config


SCHEMA_EXPORTS: list[tuple[str, type[BaseModel]]] = [
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
]

TS_ALIAS_EXPORTS: list[tuple[str, Any]] = [
    ("ExitRuleType", strategy.ExitRuleType),
    ("ExitRuleScope", strategy.ExitScope),
    ("ExitRuleAction", strategy.ExitAction),
    ("ExitRulePriceField", strategy.PriceField),
    ("ExitRuleReference", strategy.ExitReference),
    ("IntrabarConflictPolicy", strategy.IntrabarConflictPolicy),
    ("RegimeCode", regime.RegimeCode),
    ("RegimeBlockedAction", regime.RegimeBlockedAction),
    ("UniverseSource", strategy.UniverseSource),
    ("UniverseGroupOperator", strategy.UniverseGroupOperator),
    ("UniverseConditionOperator", strategy.UniverseConditionOperator),
    ("UniverseFieldId", strategy.UniverseFieldId),
    ("UniverseValue", strategy.UniverseValue),
    ("UniverseValueKind", strategy.UniverseValueKind),
    ("RankingTransformType", ranking.RankingTransformType),
    ("RankingDirection", ranking.RankingDirection),
    ("RankingMissingValuePolicy", ranking.RankingMissingValuePolicy),
    ("RegimeStatus", regime.RegimeStatus),
    ("TrendState", regime.TrendState),
    ("CurveState", regime.CurveState),
    ("RunStatus", backtest.RunStatus),
    ("BacktestLookupState", backtest.BacktestLookupState),
    ("BacktestStreamEventType", backtest.BacktestStreamEventType),
    ("TradeRole", backtest.TradeRole),
    ("UniverseNode", strategy.UniverseGroup | strategy.UniverseCondition),
]

TS_INTERFACE_EXPORTS: list[type[BaseModel]] = [
    strategy.ExitRule,
    strategy.UniverseCondition,
    strategy.UniverseFieldDefinition,
    strategy.UniverseCatalogResponse,
    strategy.UniversePreviewResponse,
    strategy.UniverseGroup,
    strategy.UniverseDefinition,
    regime.TargetGrossExposureByRegime,
    regime.RegimePolicy,
    strategy.StrategyConfig,
    ranking.RankingTransform,
    ranking.RankingFactor,
    ranking.RankingGroup,
    ranking.RankingSchemaConfig,
    ranking.RankingPreviewRow,
    ranking.RankingMaterializationSummary,
    regime.RegimeModelConfig,
    regime.RegimeSnapshot,
    regime.RegimeInputRow,
    regime.RegimeTransitionRow,
    regime.RegimeModelSummary,
    regime.RegimeModelRevision,
    regime.RegimeModelDetailResponse,
    ui_config.UiRuntimeConfig,
    ui_config.AuthSessionStatus,
    backtest.RunRecordResponse,
    backtest.RunListResponse,
    backtest.RunPinsResponse,
    backtest.RunStatusResponse,
    backtest.StrategyReferenceInput,
    backtest.BacktestResultLinks,
    backtest.BacktestLookupRequest,
    backtest.BacktestLookupResponse,
    backtest.BacktestRunRequest,
    backtest.BacktestRunResponse,
    backtest.BacktestSummary,
    backtest.BacktestResultMetadata,
    backtest.BacktestStreamEvent,
    backtest.TimeseriesPointResponse,
    backtest.TimeseriesResponse,
    backtest.RollingMetricPointResponse,
    backtest.RollingMetricsResponse,
    backtest.TradeResponse,
    backtest.TradeListResponse,
    backtest.ClosedPositionResponse,
    backtest.ClosedPositionListResponse,
    backtest.BacktestClaimRequest,
    backtest.BacktestStartRequest,
    backtest.BacktestCompleteRequest,
    backtest.BacktestFailRequest,
    backtest.BacktestReconcileResponse,
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

    for model in TS_INTERFACE_EXPORTS:
        lines.append("")
        lines.extend(_render_interface(model))

    return "\n".join(lines) + "\n"


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
