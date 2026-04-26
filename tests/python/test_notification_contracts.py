from __future__ import annotations

from datetime import datetime, timezone

import pytest

from asset_allocation_contracts.notifications import (
    CreateNotificationRequest,
    NotificationDecisionRequest,
    NotificationRecipient,
    NotificationStatusResponse,
    TradeApprovalPayload,
)
from asset_allocation_contracts.trade_desk import TradeOrderPreviewRequest


def _trade_order() -> TradeOrderPreviewRequest:
    return TradeOrderPreviewRequest(
        accountId="acct-paper",
        environment="paper",
        clientRequestId="trade-client-1",
        symbol="msft",
        side="buy",
        orderType="limit",
        timeInForce="day",
        quantity=10,
        limitPrice=100,
    )


def test_message_notification_contract_requires_matching_recipient_addresses() -> None:
    request = CreateNotificationRequest(
        sourceRepo="asset-allocation-jobs",
        clientRequestId="message-1",
        idempotencyKey="notification-idem-1",
        kind="message",
        title="Backtest complete",
        description="Backtest run finished.",
        targetUrl="https://app.example.com/backtests/run-1",
        recipients=[
            NotificationRecipient(
                recipientId="operator",
                email="ops@example.com",
                channels=["email"],
            )
        ],
    )

    assert request.kind == "message"
    assert request.recipients[0].channels == ["email"]

    with pytest.raises(ValueError, match="phoneNumber is required"):
        NotificationRecipient(channels=["sms"], email="ops@example.com")


def test_trade_approval_payload_reuses_trade_order_intent_contract() -> None:
    request = CreateNotificationRequest(
        sourceRepo="asset-allocation-control-plane",
        clientRequestId="approval-1",
        idempotencyKey="notification-idem-2",
        kind="trade_approval",
        title="Approve MSFT buy",
        description="Approve or deny the proposed order.",
        recipients=[
            NotificationRecipient(
                recipientId="operator",
                phoneNumber="+15555550100",
                channels=["sms"],
            )
        ],
        tradeApproval=TradeApprovalPayload(
            accountId="acct-paper",
            previewId="preview-1",
            orderHash="hash-1",
            placeIdempotencyKey="place-idem-000001",
            order=_trade_order(),
        ),
    )

    assert request.tradeApproval is not None
    assert request.tradeApproval.order.symbol == "MSFT"
    assert request.tradeApproval.order.accountId == "acct-paper"

    with pytest.raises(ValueError, match="tradeApproval is required"):
        CreateNotificationRequest(
            sourceRepo="asset-allocation-control-plane",
            clientRequestId="approval-2",
            idempotencyKey="notification-idem-3",
            kind="trade_approval",
            title="Approve trade",
            description="Missing trade payload.",
            recipients=[
                NotificationRecipient(
                    recipientId="operator",
                    email="ops@example.com",
                    channels=["email"],
                )
            ],
        )


def test_notification_status_and_decision_contracts_capture_polling_state() -> None:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    status = NotificationStatusResponse(
        requestId="notification-1",
        kind="trade_approval",
        status="decided",
        sourceRepo="asset-allocation-control-plane",
        clientRequestId="approval-1",
        title="Approve MSFT buy",
        description="Approve or deny the proposed order.",
        createdAt=now,
        updatedAt=now,
        decisionStatus="approved",
        decision="approve",
        decidedAt=now,
        executionStatus="submitted",
        executionOrderId="order-1",
    )
    decision = NotificationDecisionRequest(decision="deny", reason="Risk budget closed.")

    assert status.decisionStatus == "approved"
    assert status.executionStatus == "submitted"
    assert decision.reason == "Risk budget closed."
