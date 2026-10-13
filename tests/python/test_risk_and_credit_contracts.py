from __future__ import annotations

import pytest
from pydantic import ValidationError

from asset_allocation_contracts.backtest import BacktestSummary
from asset_allocation_contracts.strategy import (
    UNIVERSE_FIELD_DEFINITION_BY_ID,
    StrategyRiskExposurePolicy,
    StrategyRiskKellySizingPolicy,
    StrategyRiskPolicy,
    UniverseCondition,
)


def test_backtest_summary_accepts_parametric_and_cornish_fisher_risk() -> None:
    summary = BacktestSummary.model_validate(
        {
            "run_id": "run-1",
            "closed_positions": 42,
            "return_skewness": -0.65,
            "return_excess_kurtosis": 2.4,
            "var_95": 0.02467,
            "es_97_5": 0.03507,
            "var_95_cornish_fisher": 0.02660,
            "es_97_5_cornish_fisher": 0.04973,
            "kelly_fraction": 0.72,
        }
    )

    assert summary.var_95_cornish_fisher == pytest.approx(0.02660)
    assert summary.cornish_fisher_fallback_reason is None
    assert summary.kelly_fraction == pytest.approx(0.72)


def test_backtest_summary_records_cornish_fisher_fallback_reason() -> None:
    summary = BacktestSummary.model_validate(
        {
            "var_95": 0.02467,
            "es_97_5": 0.03507,
            "cornish_fisher_fallback_reason": "non_monotonic_tail",
        }
    )

    assert summary.var_95_cornish_fisher is None
    assert summary.cornish_fisher_fallback_reason == "non_monotonic_tail"


@pytest.mark.parametrize("field", ["var_95", "es_97_5", "var_95_cornish_fisher", "es_97_5_cornish_fisher"])
def test_backtest_summary_rejects_negative_loss_measures(field: str) -> None:
    with pytest.raises(ValidationError):
        BacktestSummary.model_validate({field: -0.01})


def test_backtest_summary_rejects_unknown_fallback_reason() -> None:
    with pytest.raises(ValidationError):
        BacktestSummary.model_validate({"cornish_fisher_fallback_reason": "unknown"})


def test_kelly_sizing_policy_defaults() -> None:
    policy = StrategyRiskKellySizingPolicy.model_validate({"referenceBacktestRunId": "run-1"})

    assert policy.minClosedPositions == 30
    assert policy.fractionMultiplier == pytest.approx(0.25)
    assert policy.floorScalar == pytest.approx(0.25)
    assert policy.capScalar == pytest.approx(1.0)
    assert policy.fallbackScalar == pytest.approx(1.0)


def test_kelly_sizing_policy_never_levers_above_baseline() -> None:
    with pytest.raises(ValidationError):
        StrategyRiskKellySizingPolicy.model_validate(
            {"referenceBacktestRunId": "run-1", "capScalar": 1.5}
        )


def test_kelly_sizing_policy_rejects_floor_above_cap() -> None:
    with pytest.raises(ValidationError, match="floorScalar"):
        StrategyRiskKellySizingPolicy.model_validate(
            {"referenceBacktestRunId": "run-1", "floorScalar": 0.8, "capScalar": 0.5, "fallbackScalar": 0.5}
        )


def test_kelly_sizing_policy_rejects_fallback_outside_band() -> None:
    with pytest.raises(ValidationError, match="fallbackScalar"):
        StrategyRiskKellySizingPolicy.model_validate(
            {"referenceBacktestRunId": "run-1", "floorScalar": 0.25, "capScalar": 0.5, "fallbackScalar": 1.0}
        )


def test_kelly_sizing_policy_requires_reference_run() -> None:
    with pytest.raises(ValidationError):
        StrategyRiskKellySizingPolicy.model_validate({})


def test_strategy_risk_policy_accepts_kelly_sizing_under_exposure() -> None:
    policy = StrategyRiskPolicy.model_validate(
        {"exposure": {"kellySizing": {"referenceBacktestRunId": "run-1", "fractionMultiplier": 0.5}}}
    )

    assert isinstance(policy.exposure, StrategyRiskExposurePolicy)
    assert policy.exposure.kellySizing is not None
    assert policy.exposure.kellySizing.fractionMultiplier == pytest.approx(0.5)


@pytest.mark.parametrize("field_id", ["credit.distance_to_default", "credit.merton_pd"])
def test_credit_universe_fields_are_numeric_and_filterable(field_id: str) -> None:
    definition = UNIVERSE_FIELD_DEFINITION_BY_ID[field_id]

    assert definition.valueKind == "number"
    condition = UniverseCondition.model_validate(
        {"kind": "condition", "field": field_id, "operator": "gte", "value": 1.5}
    )
    assert condition.field == field_id
