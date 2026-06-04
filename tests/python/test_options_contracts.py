from __future__ import annotations

from datetime import datetime, timezone

from asset_allocation_contracts.backtest import BacktestSummary
from asset_allocation_contracts.options import (
    OUT_OF_V1_OPTION_STRATEGY_IDS,
    REQUIRED_OPTION_OBSERVABILITY_METRICS,
    OptionBacktestEvent,
    OptionBacktestResult,
    OptionBrokerCapability,
    OptionBrokerConstraintProfile,
    OptionChainSnapshot,
    OptionContractIdentity,
    OptionDataQualityGateSet,
    OptionLifecycleEvent,
    OptionLifecycleGateSet,
    OptionLeg,
    OptionLegGroup,
    OptionPayoffProfile,
    OptionQuoteSnapshot,
    OptionRiskEvaluation,
    OptionRiskGateResult,
    OptionRiskLimitSet,
    OptionStrategySupportFlags,
    canonical_option_strategy_ladder,
    canonical_option_strategy_templates,
)
from asset_allocation_contracts.trade_desk import (
    TradeCapabilityFlags,
    TradeOrder,
    TradeOrderPreviewRequest,
    TradeRiskLimit,
)


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _contract(right: str = "call", strike: float = 450.0) -> OptionContractIdentity:
    return OptionContractIdentity(
        underlyingSymbol=" msft ",
        optionSymbol=f" msft260619{'c' if right == 'call' else 'p'}{int(strike * 1000):08d} ",
        expirationDate="2026-06-19",
        strikePrice=strike,
        right=right,
    )


def _support() -> OptionStrategySupportFlags:
    return OptionStrategySupportFlags(researchBacktestSupported=True, brokerPreviewSupported=True)


def test_option_contract_and_leg_models_normalize_and_validate() -> None:
    contract = _contract()
    leg = OptionLeg(
        legId=" short-call ",
        contract=contract,
        side="short",
        role="short_call",
        premium=5.25,
    )
    group = OptionLegGroup(groupId="covered-call-1", strategyId="covered_call", underlyingSymbol="MSFT", legs=[leg])

    assert contract.underlyingSymbol == "MSFT"
    assert contract.optionSymbol == "MSFT260619C00450000"
    assert contract.multiplier == 100
    assert leg.legId == "short-call"
    assert group.legs[0].contract.right == "call"

    try:
        OptionLeg(legId="bad", contract=contract, side="long", role="short_call")
    except Exception as exc:
        assert "Short leg roles require side='short'" in str(exc)
    else:
        raise AssertionError("Expected inconsistent option leg side and role to fail validation.")


def test_canonical_option_ladder_pins_research_only_v1_support_flags() -> None:
    ladder = canonical_option_strategy_ladder()
    templates = {template.strategyId: template for template in ladder.templates}

    assert set(OUT_OF_V1_OPTION_STRATEGY_IDS) == {exclusion.strategyId for exclusion in ladder.exclusions}
    assert all(template.support.liveSubmitSupported is False for template in ladder.templates)
    assert all(exclusion.stage == "out_of_v1" for exclusion in ladder.exclusions)

    core = {
        "covered_call",
        "cash_secured_put",
        "long_call",
        "long_put",
        "protective_put",
        "collar",
        "bull_call_spread",
        "bear_put_spread",
        "bull_put_spread",
        "bear_call_spread",
    }
    experimental = {"long_straddle", "long_strangle", "iron_condor", "iron_butterfly", "long_butterfly"}
    blocked = {"calendar_spread", "diagonal_spread", "pmcc", "covered_straddle", "covered_combination", "covered_strangle"}

    assert core.issubset(templates)
    assert experimental.issubset(templates)
    assert blocked.issubset(templates)
    assert all(templates[strategy_id].support.researchBacktestSupported for strategy_id in core)
    assert all(templates[strategy_id].stage == "experimental_research" for strategy_id in experimental)
    assert all(templates[strategy_id].support.researchBacktestSupported is False for strategy_id in blocked)
    assert templates["covered_straddle"].definedRisk is False


def test_option_quote_chain_and_payoff_models_capture_data_quality() -> None:
    now = _now()
    contract = _contract()
    quote = OptionQuoteSnapshot(
        snapshotId="quote-1",
        contract=contract,
        asOf=now,
        bid=5.0,
        ask=5.4,
        impliedVolatility=0.31,
        delta=0.52,
        gamma=0.03,
        theta=-0.07,
        vega=0.12,
        openInterest=1200,
        volume=80,
        quoteAgeSeconds=15,
        feed="opra",
    )
    chain = OptionChainSnapshot(
        snapshotId="chain-1",
        underlyingSymbol="MSFT",
        asOf=now,
        quotes=[quote],
        totalContractCount=1,
        paginationComplete=True,
        chainComplete=True,
        missingGreeksCount=0,
        feed="opra",
    )
    payoff = OptionPayoffProfile(
        strategyId="long_call",
        maxLoss=525.0,
        maxLossDescription="Premium paid.",
        profitWindowLower=455.25,
        profitWindowDescription="Profitable above strike plus premium paid.",
        deltaSign="positive",
        thetaSign="negative",
        vegaSign="positive",
        idealIvEnvironment="cheap",
        support=_support(),
    )

    assert quote.mid == 5.2
    assert quote.bidAskWidth == 0.40000000000000036
    assert chain.chainComplete is True
    assert payoff.profitWindowLower == 455.25

    try:
        OptionQuoteSnapshot(snapshotId="bad", contract=contract, asOf=now, bid=6.0, ask=5.0)
    except Exception as exc:
        assert "ask must be greater than or equal to bid" in str(exc)
    else:
        raise AssertionError("Expected inverted option quote to fail validation.")


def test_option_broker_constraints_block_v1_live_submit_and_invalid_alpaca_shapes() -> None:
    capability = OptionBrokerCapability(
        provider="alpaca",
        environment="paper",
        approvalLevel=3,
        supportsOptionAccounts=True,
        supportsOptionChains=True,
        supportsOptionQuotes=True,
        supportsOptionGreeks=True,
        supportsMultiLegOrders=True,
        maxLegsPerOrder=4,
    )
    profile = OptionBrokerConstraintProfile(
        provider="alpaca",
        environment="paper",
        capability=capability,
        allowedFamilies=["covered_call", "bull_call_spread"],
        blockedFamilies=["calendar_spread"],
        brokerPreviewSupported=True,
    )

    assert profile.orderQuantityMode == "whole_contracts"
    assert profile.liveSubmitSupported is False
    assert capability.supportsNotionalOptionOrders is False
    assert capability.supportsExtendedHoursOptions is False

    for invalid_capability in (
        {"supportsNotionalOptionOrders": True},
        {"supportsExtendedHoursOptions": True},
    ):
        try:
            OptionBrokerCapability(**invalid_capability)
        except Exception as exc:
            assert "not supported" in str(exc)
        else:
            raise AssertionError("Expected unsupported Alpaca option capability to fail validation.")

    try:
        OptionBrokerConstraintProfile(
            provider="alpaca",
            environment="paper",
            capability=capability,
            liveSubmitSupported=True,
        )
    except Exception as exc:
        assert "liveSubmitSupported must remain false" in str(exc)
    else:
        raise AssertionError("Expected v1 live option submit profile to fail validation.")


def test_option_risk_evaluation_requires_limits_gates_metrics_and_support_alignment() -> None:
    now = _now()
    payoff = OptionPayoffProfile(
        strategyId="covered_call",
        maxProfitDescription="Strike less stock basis plus premium.",
        maxLoss=42_000,
        maxLossDescription="Stock can go to zero less premium received.",
        profitWindowLower=395.0,
        profitWindowDescription="Profitable above stock basis less premium received.",
        deltaSign="positive",
        thetaSign="positive",
        vegaSign="negative",
        idealIvEnvironment="rich",
        support=_support(),
    )
    gate = OptionRiskGateResult(
        code="quote_age",
        status="pass",
        message="Quote age is within threshold.",
        observedValue=12,
        limitValue=60,
    )
    evaluation = OptionRiskEvaluation(
        evaluationId="eval-1",
        strategyId="covered_call",
        generatedAt=now,
        support=_support(),
        payoff=payoff,
        riskLimits=OptionRiskLimitSet(maxPremiumAtRisk=1_000, maxDefinedMaxLoss=5_000),
        dataQualityGates=OptionDataQualityGateSet(maxQuoteAgeSeconds=60, maxBidAskWidthPct=0.2),
        lifecycleGates=OptionLifecycleGateSet(),
        gateResults=[gate],
        metrics=list(REQUIRED_OPTION_OBSERVABILITY_METRICS),
        approvedForResearchBacktest=True,
        approvedForBrokerPreview=True,
    )

    assert evaluation.approvedForLiveSubmit is False
    assert evaluation.metrics[-1] == "option_backtest_model_quality"

    try:
        OptionRiskEvaluation(
            **{
                **evaluation.model_dump(mode="python"),
                "evaluationId": "eval-missing-metric",
                "metrics": ["option_chain_snapshot_count"],
            }
        )
    except Exception as exc:
        assert "Missing required option observability metrics" in str(exc)
    else:
        raise AssertionError("Expected missing observability metrics to fail validation.")


def test_option_backtest_result_and_summary_include_lifecycle_and_observability_payloads() -> None:
    now = _now()
    template = canonical_option_strategy_templates()[0]
    payoff = OptionPayoffProfile(
        strategyId=template.strategyId,
        maxProfitDescription="Capped at short call strike less stock basis plus premium.",
        maxLoss=39_500,
        profitWindowLower=395,
        profitWindowDescription="Profitable above adjusted stock basis.",
        support=template.support,
    )
    lifecycle = OptionLifecycleEvent(
        eventId="assignment-1",
        eventType="assignment",
        occurredAt=now,
        strategyId=template.strategyId,
        contract=_contract(),
        quantity=1,
        stockQuantityImpact=-100,
    )
    event = OptionBacktestEvent(
        eventId="block-1",
        runId="run-1",
        eventType="research_only_block",
        occurredAt=now,
        strategyId=template.strategyId,
        blocking=True,
        message="Live submission is blocked in v1.",
    )
    result = OptionBacktestResult(
        resultId="option-result-1",
        runId="run-1",
        strategyTemplate=template,
        payoff=payoff,
        modelQuality="fixture_backed",
        lifecycleEvents=[lifecycle],
        events=[event],
    )
    summary = BacktestSummary(
        option_strategy_id=template.strategyId,
        option_chain_snapshot_count=2,
        greeks_missing_count=0,
        assignment_event_count=1,
        research_only_block_count=1,
        option_backtest_model_quality="fixture_backed",
    )

    assert result.lifecycleEvents[0].eventType == "assignment"
    assert result.events[0].eventType == "research_only_block"
    assert summary.option_backtest_model_quality == "fixture_backed"


def test_trade_desk_contracts_represent_option_capabilities_and_block_invalid_option_orders() -> None:
    flags = TradeCapabilityFlags(
        supportsOptions=True,
        optionApprovalLevel=3,
        supportsOptionChains=True,
        supportsOptionGreeks=True,
        supportsOptionMultiLegOrders=True,
    )
    limits = TradeRiskLimit(
        allowedAssetClasses=["option"],
        allowedOptionStrategies=["covered_call"],
        maxOptionContracts=10,
        maxOptionPremiumAtRisk=1_000,
        liveOptionSubmitAllowed=False,
    )
    request = TradeOrderPreviewRequest(
        accountId="acct-1",
        environment="paper",
        clientRequestId="client-1",
        symbol="msft260619c00450000",
        assetClass="option",
        side="buy",
        orderType="limit",
        quantity=1,
        limitPrice=5.25,
        optionStrategyId="long_call",
        exitPolicyName="desk-exit",
        exitPolicyVersion=2,
    )
    order = TradeOrder(
        orderId="order-1",
        accountId="acct-1",
        provider="alpaca",
        environment="paper",
        status="previewed",
        symbol="MSFT260619C00450000",
        assetClass="option",
        side="buy",
        orderType="limit",
        quantity=1,
        optionStrategyId="long_call",
    )

    assert flags.optionApprovalLevel == 3
    assert limits.allowedOptionStrategies == ["covered_call"]
    assert request.symbol == "MSFT260619C00450000"
    assert order.optionStrategyId == "long_call"

    invalid_payloads = (
        {"quantity": None, "notional": 500},
        {"quantity": 1.5, "notional": None},
        {"quantity": 1, "notional": None, "allowExtendedHours": True},
    )
    for overrides in invalid_payloads:
        payload = {
            "accountId": "acct-1",
            "environment": "paper",
            "clientRequestId": "client-1",
            "symbol": "MSFT260619C00450000",
            "assetClass": "option",
            "side": "buy",
            "orderType": "limit",
            "quantity": 1,
            "notional": None,
            "limitPrice": 5.25,
            "exitPolicyName": "desk-exit",
            "exitPolicyVersion": 2,
            **overrides,
        }
        try:
            TradeOrderPreviewRequest.model_validate(payload)
        except Exception as exc:
            assert "Option" in str(exc) or "option" in str(exc) or "quantity" in str(exc)
        else:
            raise AssertionError("Expected invalid option order preview request to fail validation.")
