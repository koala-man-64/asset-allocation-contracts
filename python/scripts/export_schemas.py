from __future__ import annotations

import json
from pathlib import Path

from asset_allocation_contracts.backtest import (
    BacktestClaimRequest,
    BacktestCompleteRequest,
    BacktestFailRequest,
    BacktestStartRequest,
    BacktestSummary,
    RollingMetricsResponse,
    RunListResponse,
    RunRecordResponse,
    TimeseriesResponse,
    TradeListResponse,
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
from asset_allocation_contracts.ui_config import UiRuntimeConfig


ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "schemas"


def _write(name: str, model) -> None:
    SCHEMAS.mkdir(parents=True, exist_ok=True)
    path = SCHEMAS / name
    path.write_text(json.dumps(model.model_json_schema(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    _write("strategy-config.schema.json", StrategyConfig)
    _write("universe-definition.schema.json", UniverseDefinition)
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
    _write("backtest-run-record.schema.json", RunRecordResponse)
    _write("backtest-run-list.schema.json", RunListResponse)
    _write("backtest-summary.schema.json", BacktestSummary)
    _write("backtest-timeseries.schema.json", TimeseriesResponse)
    _write("backtest-rolling-metrics.schema.json", RollingMetricsResponse)
    _write("backtest-trade-list.schema.json", TradeListResponse)
    _write("backtest-claim-request.schema.json", BacktestClaimRequest)
    _write("backtest-start-request.schema.json", BacktestStartRequest)
    _write("backtest-complete-request.schema.json", BacktestCompleteRequest)
    _write("backtest-fail-request.schema.json", BacktestFailRequest)


if __name__ == "__main__":
    main()
