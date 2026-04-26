from __future__ import annotations

from datetime import datetime, timedelta, timezone

from asset_allocation_contracts.trade_desk import (
    TradeAccountDetail,
    TradeAccountSummary,
    TradeBlotterResponse,
    TradeBlotterRow,
    TradeCapabilityFlags,
    TradeDeskAlert,
    TradeDeskAuditEvent,
    TradeOrder,
    TradeOrderCancelRequest,
    TradeOrderPlaceRequest,
    TradeOrderPreviewRequest,
    TradeOrderPreviewResponse,
    TradePosition,
    TradeRiskCheck,
)


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
    assert response.rows[0].realizedPnl == 56.75
    assert response.rows[0].cashImpact == 561.25
