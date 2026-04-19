from __future__ import annotations

import json
from pathlib import Path

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
from asset_allocation_contracts.portfolio import (
    PortfolioAccount,
    PortfolioAccountDetailResponse,
    PortfolioAccountListResponse,
    PortfolioAccountRevision,
    PortfolioAccountUpsertRequest,
    PortfolioAlertListResponse,
    PortfolioAssignment,
    PortfolioAssignmentRequest,
    PortfolioDefinition,
    PortfolioDefinitionDetailResponse,
    PortfolioHistoryResponse,
    PortfolioLedgerEvent,
    PortfolioLedgerEventPayload,
    PortfolioListResponse,
    PortfolioPositionListResponse,
    PortfolioRebalanceApplyRequest,
    PortfolioRebalancePreviewRequest,
    PortfolioRevision,
    PortfolioSnapshot,
    PortfolioUpsertRequest,
    RebalanceProposal,
)
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
from asset_allocation_contracts.strategy import StrategyConfig, UniverseDefinition
from asset_allocation_contracts.strategy import UniverseCatalogResponse, UniversePreviewResponse
from asset_allocation_contracts.ui_config import AuthSessionStatus, UiRuntimeConfig


ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "schemas"


def _write(name: str, model) -> None:
    SCHEMAS.mkdir(parents=True, exist_ok=True)
    path = SCHEMAS / name
    path.write_text(json.dumps(model.model_json_schema(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
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
    _write("portfolio-account.schema.json", PortfolioAccount)
    _write("portfolio-account-detail.schema.json", PortfolioAccountDetailResponse)
    _write("portfolio-account-list.schema.json", PortfolioAccountListResponse)
    _write("portfolio-account-revision.schema.json", PortfolioAccountRevision)
    _write("portfolio-account-upsert-request.schema.json", PortfolioAccountUpsertRequest)
    _write("portfolio-alert-list.schema.json", PortfolioAlertListResponse)
    _write("portfolio-assignment.schema.json", PortfolioAssignment)
    _write("portfolio-assignment-request.schema.json", PortfolioAssignmentRequest)
    _write("portfolio-definition.schema.json", PortfolioDefinition)
    _write("portfolio-definition-detail.schema.json", PortfolioDefinitionDetailResponse)
    _write("portfolio-history.schema.json", PortfolioHistoryResponse)
    _write("portfolio-ledger-event.schema.json", PortfolioLedgerEvent)
    _write("portfolio-ledger-event-request.schema.json", PortfolioLedgerEventPayload)
    _write("portfolio-list.schema.json", PortfolioListResponse)
    _write("portfolio-position-list.schema.json", PortfolioPositionListResponse)
    _write("portfolio-rebalance-apply-request.schema.json", PortfolioRebalanceApplyRequest)
    _write("portfolio-rebalance-preview-request.schema.json", PortfolioRebalancePreviewRequest)
    _write("portfolio-rebalance-proposal.schema.json", RebalanceProposal)
    _write("portfolio-revision.schema.json", PortfolioRevision)
    _write("portfolio-snapshot.schema.json", PortfolioSnapshot)
    _write("portfolio-upsert-request.schema.json", PortfolioUpsertRequest)


if __name__ == "__main__":
    main()
