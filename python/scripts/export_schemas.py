from __future__ import annotations

import json
from pathlib import Path

from asset_allocation_contracts.ai_chat import AiChatRequest
from asset_allocation_contracts.ai_chat import AiChatStreamEvent
from asset_allocation_contracts.backtest import (
    BacktestClaimRequest,
    BacktestCompleteRequest,
    BacktestFailRequest,
    BacktestReconcileResponse,
    BacktestStartRequest,
    BacktestSummary,
    ClosedPositionListResponse,
    RollingMetricsResponse,
    RunListResponse,
    RunRecordResponse,
    TimeseriesResponse,
    TradeListResponse,
)
from pydantic import TypeAdapter
from asset_allocation_contracts.ranking import RankingSchemaConfig
from asset_allocation_contracts.regime import (
    RegimeInputRow,
    RegimeModelConfig,
    RegimeModelDetailResponse,
    RegimeModelRevision,
    RegimeModelSummary,
    RegimePolicy,
    RegimeSnapshot,
    RegimeTransitionRow,
)
from asset_allocation_contracts.symbol_enrichment import (
    SymbolCleanupRunSummary,
    SymbolCleanupWorkItem,
    SymbolEnrichmentEnqueueRequest,
    SymbolEnrichmentResolveRequest,
    SymbolEnrichmentResolveResponse,
    SymbolEnrichmentSummaryResponse,
    SymbolEnrichmentSymbolDetailResponse,
    SymbolEnrichmentSymbolListItem,
    SymbolProfileCurrent,
    SymbolProfileHistoryEntry,
    SymbolProfileOverride,
)
from asset_allocation_contracts.strategy import StrategyConfig, UniverseDefinition
from asset_allocation_contracts.strategy import UniverseCatalogResponse, UniversePreviewResponse
from asset_allocation_contracts.ui_config import AuthSessionStatus, UiRuntimeConfig


ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "schemas"


def _write(name: str, model) -> None:
    SCHEMAS.mkdir(parents=True, exist_ok=True)
    path = SCHEMAS / name
    path.write_text(json.dumps(model.model_json_schema(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_adapter(name: str, adapter: TypeAdapter) -> None:
    SCHEMAS.mkdir(parents=True, exist_ok=True)
    path = SCHEMAS / name
    path.write_text(json.dumps(adapter.json_schema(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    _write("ai-chat-request.schema.json", AiChatRequest)
    _write_adapter("ai-chat-stream-event.schema.json", TypeAdapter(AiChatStreamEvent))
    _write("strategy-config.schema.json", StrategyConfig)
    _write("universe-definition.schema.json", UniverseDefinition)
    _write("universe-catalog.schema.json", UniverseCatalogResponse)
    _write("universe-preview.schema.json", UniversePreviewResponse)
    _write("ranking-schema.schema.json", RankingSchemaConfig)
    _write("regime-policy.schema.json", RegimePolicy)
    _write("regime-model-config.schema.json", RegimeModelConfig)
    _write("regime-snapshot.schema.json", RegimeSnapshot)
    _write("regime-input-row.schema.json", RegimeInputRow)
    _write("regime-transition-row.schema.json", RegimeTransitionRow)
    _write("regime-model-summary.schema.json", RegimeModelSummary)
    _write("regime-model-revision.schema.json", RegimeModelRevision)
    _write("regime-model-detail.schema.json", RegimeModelDetailResponse)
    _write("ui-runtime-config.schema.json", UiRuntimeConfig)
    _write("auth-session-status.schema.json", AuthSessionStatus)
    _write("backtest-run-record.schema.json", RunRecordResponse)
    _write("backtest-run-list.schema.json", RunListResponse)
    _write("backtest-summary.schema.json", BacktestSummary)
    _write("backtest-timeseries.schema.json", TimeseriesResponse)
    _write("backtest-rolling-metrics.schema.json", RollingMetricsResponse)
    _write("backtest-trade-list.schema.json", TradeListResponse)
    _write("backtest-closed-position-list.schema.json", ClosedPositionListResponse)
    _write("backtest-claim-request.schema.json", BacktestClaimRequest)
    _write("backtest-start-request.schema.json", BacktestStartRequest)
    _write("backtest-complete-request.schema.json", BacktestCompleteRequest)
    _write("backtest-fail-request.schema.json", BacktestFailRequest)
    _write("backtest-reconcile-response.schema.json", BacktestReconcileResponse)
    _write("symbol-cleanup-work-item.schema.json", SymbolCleanupWorkItem)
    _write("symbol-cleanup-run-summary.schema.json", SymbolCleanupRunSummary)
    _write("symbol-enrichment-resolve-request.schema.json", SymbolEnrichmentResolveRequest)
    _write("symbol-enrichment-resolve-response.schema.json", SymbolEnrichmentResolveResponse)
    _write("symbol-profile-current.schema.json", SymbolProfileCurrent)
    _write("symbol-profile-history-entry.schema.json", SymbolProfileHistoryEntry)
    _write("symbol-profile-override.schema.json", SymbolProfileOverride)
    _write("symbol-enrichment-summary.schema.json", SymbolEnrichmentSummaryResponse)
    _write("symbol-enrichment-symbol-list-item.schema.json", SymbolEnrichmentSymbolListItem)
    _write("symbol-enrichment-symbol-detail.schema.json", SymbolEnrichmentSymbolDetailResponse)
    _write("symbol-enrichment-enqueue-request.schema.json", SymbolEnrichmentEnqueueRequest)


if __name__ == "__main__":
    main()
