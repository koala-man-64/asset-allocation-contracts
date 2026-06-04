from __future__ import annotations

from datetime import datetime, timedelta, timezone

from asset_allocation_contracts.trade_desk import (
    TradeAccountBalanceHistoryPoint,
    TradeAccountBalanceHistoryResponse,
    TradeAccountDetail,
    TradeAccountSummary,
    TradeBlotterResponse,
    TradeBlotterRow,
    TradeCapabilityFlags,
    TradeDeskAlert,
    TradeDeskAuditEvent,
    TradeMetricFeedResponse,
    TradeOrder,
    TradeOrderCancelRequest,
    TradeOrderPlaceRequest,
    TradeOrderPreviewRequest,
    TradeOrderPreviewResponse,
    TradePnlSnapshot,
    TradePosition,
    TradeRiskCheck,
)

import pytest
from pydantic import ValidationError


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def test_trade_account_contracts_capture_readiness_and_capabilities() -> None:
    now = _now()
    account = TradeAccountSummary(
        accountId=" alpaca-core ",
        name=" Core Long Only ",
        provider="alpaca",
        environment="paper",
        accountNumberMasked=" ****1234 ",
        baseCurrency="usd",
        readiness="blocked",
        readinessReason="Position snapshot is stale.",
        capabilities=TradeCapabilityFlags(
            canReadAccount=True,
            canReadPositions=True,
            canReadOrders=True,
            canReadHistory=True,
            canPreview=True,
            canSubmitPaper=True,
            canCancel=True,
            supportsMarketOrders=True,
            supportsLimitOrders=True,
            supportsEquities=True,
            readOnly=False,
        ),
        cash=42_000,
        buyingPower=180_000,
        equity=44_200,
        openOrderCount=2,
        positionCount=12,
        pnl={
            "realizedPnl": 1_250.5,
            "unrealizedPnl": 840.25,
            "dayPnl": -120.75,
            "grossExposure": 185_000,
            "netExposure": 163_500,
            "asOf": now,
        },
        lastTradeAt=now,
    )
    detail = TradeAccountDetail(
        account=account,
        restrictions=["stale_positions"],
        unresolvedAlerts=["Refresh required before trading."],
        alerts=[
            TradeDeskAlert(
                alertId="alert-1",
                accountId="alpaca-core",
                severity="critical",
                status="open",
                code="freshness_block",
                title="Snapshot refresh required",
                message="Position freshness exceeded the trading threshold.",
                blocking=True,
                observedAt=now,
            )
        ],
    )

    assert account.accountId == "alpaca-core"
    assert account.name == "Core Long Only"
    assert account.accountNumberMasked == "****1234"
    assert account.baseCurrency == "USD"
    assert account.pnl is not None
    assert account.pnl.realizedPnl == 1_250.5
    assert detail.account.capabilities.canSubmitPaper is True
    assert detail.restrictions == ["stale_positions"]
    assert detail.alerts[0].blocking is True


def test_trade_account_contracts_accept_kalshi_provider() -> None:
    account = TradeAccountSummary(
        accountId="kalshi-live-subaccount-0",
        name="Kalshi Live Subaccount 0",
        provider="kalshi",
        environment="live",
        accountNumberMasked="GEN-0001",
        readiness="ready",
        capabilities=TradeCapabilityFlags(
            canReadAccount=True,
            canReadPositions=True,
            canReadOrders=True,
            canReadHistory=True,
            readOnly=True,
            unsupportedReason="Kalshi trade desk execution is not supported in v1.",
        ),
        cash=0,
        buyingPower=0,
        equity=0,
        freshness={
            "balancesState": "unknown",
            "positionsState": "unknown",
            "ordersState": "unknown",
            "staleReason": "Seeded account; provider refresh has not completed.",
        },
    )

    assert account.provider == "kalshi"
    assert account.environment == "live"
    assert account.freshness.balancesState == "unknown"


def test_trade_account_balance_history_contract_normalizes_currency_and_metadata() -> None:
    observed_at = _now()
    point = TradeAccountBalanceHistoryPoint(
        accountId=" acct-paper ",
        provider="alpaca",
        environment="paper",
        asOf=observed_at,
        balance=201_125.25,
        equity=201_125.25,
        cash=-250.75,
        buyingPower=402_250.50,
        currency="usd",
        sourceObservedAt=observed_at,
        syncRunId=" sync-001 ",
    )
    response = TradeAccountBalanceHistoryResponse(
        accountId=" acct-paper ",
        points=[point],
        totalPoints=3,
        truncated=True,
        generatedAt=observed_at,
    )

    assert point.accountId == "acct-paper"
    assert point.currency == "USD"
    assert point.syncRunId == "sync-001"
    assert response.accountId == "acct-paper"
    assert response.points[0].balance == response.points[0].equity
    assert response.totalPoints == 3
    assert response.truncated is True


def test_trade_metric_feed_accepts_extensible_metric_ids_and_v1_rows() -> None:
    now = _now()
    feed = TradeMetricFeedResponse(
        scope=" global ",
        generatedAt=now,
        coverage={
            "accountCount": 2,
            "includedAccountCount": 2,
            "environments": ["paper", "live"],
            "currencies": ["usd"],
            "mixedEnvironment": True,
            "mixedCurrency": False,
        },
        metrics=[
            {
                "metricId": "open_positions",
                "label": "Open Positions",
                "value": 2,
                "valueType": "count",
                "status": "available",
                "asOf": now,
                "segments": [
                    {
                        "segmentId": "paper",
                        "environment": "paper",
                        "accountCount": 1,
                        "value": 1,
                        "status": "available",
                        "asOf": now,
                    },
                    {
                        "segmentId": "live",
                        "environment": "live",
                        "accountCount": 1,
                        "value": 1,
                        "status": "available",
                        "asOf": now,
                    },
                ],
            },
            {
                "metricId": "buying_power",
                "label": "Buying Power",
                "value": 350_000,
                "valueType": "currency",
                "currency": "usd",
                "status": "available",
                "asOf": now,
                "segments": [
                    {
                        "segmentId": "paper",
                        "environment": "paper",
                        "accountCount": 1,
                        "value": 200_000,
                        "status": "available",
                        "asOf": now,
                        "currency": "usd",
                    },
                ],
            },
            {
                "metricId": "total_pnl",
                "label": "Total P/L",
                "value": 4_260,
                "valueType": "currency",
                "currency": "USD",
                "status": "available",
                "asOf": now,
            },
            {
                "metricId": "day_pnl",
                "label": "Daily P/L",
                "value": -15,
                "valueType": "currency",
                "currency": "USD",
                "status": "available",
                "asOf": now,
            },
            {
                "metricId": "realized_pnl",
                "label": "Realized P/L",
                "value": 4_400,
                "valueType": "currency",
                "currency": "USD",
                "status": "available",
                "asOf": now,
            },
            {
                "metricId": "unrealized_pnl",
                "label": "Unrealized P/L",
                "value": -140,
                "valueType": "currency",
                "currency": "USD",
                "status": "available",
                "asOf": now,
            },
            {
                "metricId": "desk.custom.future_metric",
                "label": "Future Metric",
                "value": None,
                "valueType": "count",
                "status": "unavailable",
                "warnings": ["Builder not deployed."],
            },
        ],
        warnings=["Mixed execution environments are segmented."],
    )

    assert feed.scope == "global"
    assert feed.coverage.currencies == ["USD"]
    assert [metric.metricId for metric in feed.metrics[:6]] == [
        "open_positions",
        "buying_power",
        "total_pnl",
        "day_pnl",
        "realized_pnl",
        "unrealized_pnl",
    ]
    assert feed.metrics[-1].metricId == "desk.custom.future_metric"


def test_trade_order_preview_request_validates_manual_intent() -> None:
    request = TradeOrderPreviewRequest(
        accountId="acct-001",
        environment="paper",
        clientRequestId="client-001",
        symbol=" msft ",
        side="buy",
        orderType="limit",
        quantity=10,
        limitPrice=100.50,
    )

    assert request.symbol == "MSFT"
    assert request.quantity == 10
    assert request.notional is None

    invalid_payloads = (
        {"quantity": 10, "notional": 500},
        {},
        {"quantity": 10, "orderType": "limit"},
        {"quantity": 10, "orderType": "stop"},
    )
    for overrides in invalid_payloads:
        payload = {
            "accountId": "acct-001",
            "environment": "paper",
            "clientRequestId": "client-001",
            "symbol": "MSFT",
            "side": "buy",
            "orderType": "market",
            **overrides,
        }
        try:
            TradeOrderPreviewRequest.model_validate(payload)
        except Exception as exc:
            assert "quantity" in str(exc) or "limitPrice" in str(exc) or "stopPrice" in str(exc)
        else:
            raise AssertionError("Expected invalid order preview request to fail validation.")


def test_trade_order_place_and_cancel_require_idempotency() -> None:
    confirmed_at = _now()
    place = TradeOrderPlaceRequest(
        accountId="acct-001",
        environment="paper",
        clientRequestId="client-001",
        idempotencyKey="idem-000000000001",
        previewId="preview-001",
        confirmedAt=confirmed_at,
        symbol="AAPL",
        side="buy",
        orderType="market",
        quantity=5,
    )
    cancel = TradeOrderCancelRequest(
        accountId="acct-001",
        orderId="order-001",
        clientRequestId="client-002",
        idempotencyKey="idem-000000000002",
        reason="Operator cancel.",
    )

    assert place.confirmedAt == confirmed_at
    assert cancel.reason == "Operator cancel."

    for model, payload in (
        (
            TradeOrderPlaceRequest,
            {
                "accountId": "acct-001",
                "environment": "paper",
                "clientRequestId": "client-001",
                "idempotencyKey": "short",
                "previewId": "preview-001",
                "confirmedAt": confirmed_at,
                "symbol": "AAPL",
                "side": "buy",
                "orderType": "market",
                "quantity": 5,
            },
        ),
        (
            TradeOrderCancelRequest,
            {
                "accountId": "acct-001",
                "orderId": "order-001",
                "clientRequestId": "client-002",
                "idempotencyKey": "short",
            },
        ),
    ):
        try:
            model.model_validate(payload)
        except Exception as exc:
            assert "idempotencyKey" in str(exc)
        else:
            raise AssertionError("Expected short idempotency key to fail validation.")


def test_trade_order_and_audit_contracts_capture_reconciliation_state() -> None:
    now = _now()
    risk = TradeRiskCheck(
        checkId="freshness",
        code="stale_orders",
        label="Open orders freshness",
        status="fail",
        severity="critical",
        blocking=True,
        message="Open orders must be refreshed before submission.",
    )
    order = TradeOrder(
        orderId="order-001",
        accountId="acct-001",
        provider="alpaca",
        environment="paper",
        status="unknown_reconcile_required",
        symbol="aapl",
        side="buy",
        orderType="market",
        quantity=3,
        idempotencyKey="idem-000000000001",
        riskChecks=[risk],
        reconciliationRequired=True,
        createdAt=now,
    )
    response = TradeOrderPreviewResponse(
        previewId="preview-001",
        accountId="acct-001",
        provider="alpaca",
        environment="paper",
        order={**order.model_dump(mode="python"), "status": "previewed", "reconciliationRequired": False},
        generatedAt=now,
        expiresAt=now + timedelta(minutes=5),
        blocked=True,
        blockReason="Open orders are stale.",
        riskChecks=[risk],
    )
    event = TradeDeskAuditEvent(
        eventId="audit-001",
        accountId="acct-001",
        provider="alpaca",
        environment="paper",
        eventType="reconcile",
        severity="critical",
        occurredAt=now,
        orderId=order.orderId,
        statusAfter=order.status,
        summary="Network failure after submit; reconciliation required.",
        sanitizedError="Provider timeout.",
    )
    position = TradePosition(accountId="acct-001", symbol="msft", quantity=10, marketValue=1_000)

    assert order.symbol == "AAPL"
    assert order.status == "unknown_reconcile_required"
    assert response.blocked is True
    assert response.riskChecks[0].blocking is True
    assert event.statusAfter == "unknown_reconcile_required"
    assert position.symbol == "MSFT"


def test_trade_order_preview_and_place_support_policy_confirmation_payloads() -> None:
    now = _now()
    preview = TradeOrderPreviewResponse(
        previewId="preview-001",
        accountId="acct-001",
        provider="alpaca",
        environment="paper",
        order={
            "orderId": "preview-001",
            "accountId": "acct-001",
            "provider": "alpaca",
            "environment": "paper",
            "status": "previewed",
            "symbol": "AAPL",
            "side": "buy",
            "orderType": "market",
            "quantity": 5,
            "createdAt": now,
            "updatedAt": now,
        },
        generatedAt=now,
        expiresAt=now + timedelta(minutes=5),
        estimatedPriceSource="massive_live",
        estimatedPriceObservedAt=now,
        projectedPolicy={
            "maxOpenPositions": 12,
            "maxSinglePositionExposure": {"mode": "pct_of_allocatable_capital", "value": 8.0},
            "allowedSides": ["long"],
            "allowedAssetClasses": ["equity", "option"],
            "requireOrderConfirmation": True,
        },
        policyVersion=7,
        confirmationRequired=True,
        orderHash="hash-123",
        confirmationToken="token-123",
    )
    place = TradeOrderPlaceRequest(
        accountId="acct-001",
        environment="paper",
        clientRequestId="client-001",
        idempotencyKey="idem-000000000001",
        previewId="preview-001",
        confirmedAt=now,
        policyVersion=7,
        orderHash="hash-123",
        confirmationToken="token-123",
        symbol="AAPL",
        side="buy",
        orderType="market",
        quantity=5,
    )

    assert preview.confirmationRequired is True
    assert preview.estimatedPriceSource == "massive_live"
    assert preview.estimatedPriceObservedAt == now
    assert preview.projectedPolicy is not None
    assert preview.projectedPolicy.requireOrderConfirmation is True
    assert place.policyVersion == 7
    assert place.confirmationToken == "token-123"


def test_trade_blotter_contracts_capture_realized_pnl_and_cash_impact() -> None:
    now = _now()
    response = TradeBlotterResponse(
        accountId="acct-001",
        generatedAt=now,
        rows=[
            TradeBlotterRow(
                rowId="blotter-001",
                accountId="acct-001",
                provider="alpaca",
                environment="paper",
                eventType="fill",
                occurredAt=now,
                orderId="order-001",
                providerActivityId=" 202605100001::alpaca-fill-001 ",
                providerActivityType=" FILL ",
                clientRequestId="client-001",
                symbol=" msft ",
                side="sell",
                status="filled",
                quantity=5,
                price=112.5,
                fees=1.25,
                realizedPnl=56.75,
                cashImpact=561.25,
                note="Trim after target hit.",
            )
        ],
    )

    assert response.rows[0].symbol == "MSFT"
    assert response.rows[0].providerActivityId == "202605100001::alpaca-fill-001"
    assert response.rows[0].providerActivityType == "FILL"
    assert response.rows[0].realizedPnl == 56.75
    assert response.rows[0].cashImpact == 561.25


def test_trade_contracts_capture_prediction_market_normalization_metadata() -> None:
    now = _now()
    warning = {
        "code": "unknown_kalshi_order_status",
        "message": "Raw provider status was preserved for reconciliation.",
        "providerField": "status",
        "rawValue": "resting",
    }
    position = TradePosition(
        accountId="kalshi-live-subaccount-0",
        symbol="KXNYC-26MAY10-T75",
        assetClass="prediction_market",
        providerPositionId="pos-123",
        providerInstrumentId="KXNYC-26MAY10-T75",
        instrumentName="NYC high temperature above 75F on May 10",
        outcomeSide="yes",
        rawProviderStatus="active",
        quantity=12,
        marketValue=720,
        asOf=now,
        sourceObservedAt=now,
        ingestedAt=now,
        syncRunId="sync-001",
        sourcePayloadHash="sha256:abc",
        normalizationWarnings=[warning],
    )
    order = TradeOrder(
        orderId="kalshi-order-001",
        accountId="kalshi-live-subaccount-0",
        provider="kalshi",
        environment="live",
        status="unknown_reconcile_required",
        symbol="KXNYC-26MAY10-T75",
        side="buy",
        orderType="limit",
        assetClass="prediction_market",
        providerOrderId="provider-order-001",
        providerInstrumentId="KXNYC-26MAY10-T75",
        instrumentName="NYC high temperature above 75F on May 10",
        outcomeSide="yes",
        rawProviderStatus="resting",
        quantity=10,
        limitPrice=58,
        sourceObservedAt=now,
        ingestedAt=now,
        syncRunId="sync-001",
        normalizationWarnings=[warning],
        reconciliationRequired=True,
    )
    response = TradeBlotterResponse(
        accountId="kalshi-live-subaccount-0",
        generatedAt=now,
        sourceObservedAt=now,
        syncRunId="sync-001",
        normalizationWarnings=[warning],
        quarantinedRowCount=1,
        rows=[
            TradeBlotterRow(
                rowId="kalshi-event-001",
                accountId="kalshi-live-subaccount-0",
                provider="kalshi",
                environment="live",
                eventType="settlement",
                occurredAt=now,
                providerEventId="event-001",
                providerInstrumentId="KXNYC-26MAY10-T75",
                instrumentName="NYC high temperature above 75F on May 10",
                symbol="KXNYC-26MAY10-T75",
                assetClass="prediction_market",
                side="buy",
                outcomeSide="yes",
                status="filled",
                rawProviderStatus="settled",
                quantity=10,
                price=100,
                cashImpact=420,
                sourceObservedAt=now,
                ingestedAt=now,
                syncRunId="sync-001",
                normalizationWarnings=[warning],
            )
        ],
    )

    assert position.assetClass == "prediction_market"
    assert position.outcomeSide == "yes"
    assert order.rawProviderStatus == "resting"
    assert order.reconciliationRequired is True
    assert response.rows[0].eventType == "settlement"
    assert response.rows[0].providerEventId == "event-001"
    assert response.quarantinedRowCount == 1
    assert response.normalizationWarnings[0].code == "unknown_kalshi_order_status"


def test_trade_pnl_snapshot_carries_realized_source_and_ledger_horizon() -> None:
    horizon = datetime(2026, 4, 1, 14, 30, tzinfo=timezone.utc)
    snapshot = TradePnlSnapshot(
        realizedPnl=500.0,
        unrealizedPnl=125.0,
        dayPnl=12.0,
        asOf=horizon,
        realizedSource="ledger",
        ledgerHorizonAt=horizon,
    )

    assert snapshot.realizedSource == "ledger"
    assert snapshot.ledgerHorizonAt == horizon
    # Round-trips cleanly through JSON for storage on the account snapshot payload.
    payload = snapshot.model_dump(mode="json")
    assert payload["realizedSource"] == "ledger"
    assert payload["ledgerHorizonAt"].startswith("2026-04-01T14:30:00")
    assert TradePnlSnapshot.model_validate(payload) == snapshot


def test_trade_pnl_snapshot_realized_source_rejects_unknown_values() -> None:
    with pytest.raises(ValidationError):
        TradePnlSnapshot(realizedSource="estimated")  # type: ignore[arg-type]


def test_trade_pnl_snapshot_defaults_omit_new_optional_fields() -> None:
    """The new fields are additive; legacy payloads must still validate as None."""
    snapshot = TradePnlSnapshot(realizedPnl=42.0, unrealizedPnl=1.0)
    assert snapshot.realizedSource is None
    assert snapshot.ledgerHorizonAt is None
