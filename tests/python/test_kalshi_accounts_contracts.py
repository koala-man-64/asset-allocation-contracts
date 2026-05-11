from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from asset_allocation_contracts.kalshi_accounts import (
    KalshiAccountLimits,
    KalshiAccountSnapshot,
    KalshiBalance,
    KalshiFillsPage,
    KalshiHistoricalCutoff,
    KalshiLineage,
    KalshiOrdersPage,
    KalshiPositionsPage,
)
from asset_allocation_contracts.trade_desk import TradeBlotterRow, TradeOrder, TradePosition


def _now() -> datetime:
    return datetime(2026, 5, 10, 18, 15, tzinfo=timezone.utc)


def _lineage(endpoint: str, *, tier: str = "live", page_number: int = 0) -> KalshiLineage:
    return KalshiLineage(
        sync_run_id="sync-AB155-001",
        source_observed_at=_now(),
        ingested_at=_now(),
        source_payload_hash=f"sha256:{endpoint}:abc",
        endpoint=endpoint,
        request_id="req-001",
        cursor_in=None,
        cursor_out="cursor-next" if page_number == 0 else None,
        page_number=page_number,
        tier=tier,
    )


def test_kalshi_account_snapshot_preserves_provider_native_units_and_fixed_point_strings() -> None:
    balance = KalshiBalance(
        balance=12_345,
        portfolio_value=23_456,
        updated_ts=1_772_999_100,
        balance_breakdown=[{"exchange_index": 0, "balance": "123.4500"}],
        subaccount=0,
        lineage=_lineage("/portfolio/balance"),
    )
    positions = KalshiPositionsPage(
        market_positions=[
            {
                "ticker": "kxnyc-26may10-t75",
                "total_traded_dollars": "12.3400",
                "position_fp": "10.50",
                "market_exposure_dollars": "6.1700",
                "realized_pnl_dollars": "-1.2500",
                "resting_orders_count": 2,
                "fees_paid_dollars": "0.0500",
                "last_updated_ts": "2026-05-10T18:00:00Z",
                "subaccount_number": 0,
                "lineage": _lineage("/portfolio/positions"),
            }
        ],
        event_positions=[
            {
                "event_ticker": "kxnyc-26may10",
                "total_cost_dollars": "12.3400",
                "total_cost_shares_fp": "10.50",
                "event_exposure_dollars": "6.1700",
                "realized_pnl_dollars": "0.0000",
                "fees_paid_dollars": "0.0500",
            }
        ],
        cursor="cursor-next",
        page={"cursor": "cursor-next", "limit": 100, "page_number": 0, "tier": "live", "exhausted": False},
        lineage=_lineage("/portfolio/positions"),
    )
    orders = KalshiOrdersPage(
        orders=[
            {
                "order_id": "order-001",
                "user_id": "user-001",
                "client_order_id": "client-001",
                "ticker": "KXNYC-26MAY10-T75",
                "side": "yes",
                "action": "buy",
                "outcome_side": "yes",
                "book_side": "bid",
                "type": "limit",
                "status": "resting",
                "yes_price_dollars": "0.5600",
                "no_price_dollars": "0.4400",
                "fill_count_fp": "1.00",
                "remaining_count_fp": "9.00",
                "initial_count_fp": "10.00",
                "taker_fill_cost_dollars": "0.5600",
                "maker_fill_cost_dollars": "0.0000",
                "taker_fees_dollars": "0.0100",
                "maker_fees_dollars": "0.0000",
                "expiration_time": "2026-05-10T19:00:00Z",
                "created_time": "2026-05-10T18:00:00Z",
                "last_update_time": "2026-05-10T18:05:00Z",
                "self_trade_prevention_type": "taker_at_cross",
                "order_group_id": "group-001",
                "cancel_order_on_pause": True,
                "subaccount_number": 0,
                "lineage": _lineage("/portfolio/orders"),
            }
        ],
        cursor=None,
        page={"cursor": None, "limit": 100, "page_number": 0, "tier": "live", "exhausted": True},
        lineage=_lineage("/portfolio/orders"),
    )
    fills = KalshiFillsPage(
        fills=[
            {
                "fill_id": "fill-001",
                "trade_id": "trade-001",
                "order_id": "order-001",
                "ticker": "KXNYC-26MAY10-T75",
                "market_ticker": "KXNYC-26MAY10-T75",
                "side": "yes",
                "action": "buy",
                "outcome_side": "yes",
                "book_side": "bid",
                "count_fp": "1.00",
                "yes_price_dollars": "0.5600",
                "no_price_dollars": "0.4400",
                "is_taker": True,
                "fee_cost": "0.0100",
                "created_time": "2026-05-10T18:02:00Z",
                "subaccount_number": 0,
                "ts": 1_772_999_120,
                "lineage": _lineage("/portfolio/fills"),
            }
        ],
        cursor=None,
        page={"cursor": None, "limit": 100, "page_number": 0, "tier": "live", "exhausted": True},
        lineage=_lineage("/portfolio/fills"),
    )
    account_limits = KalshiAccountLimits(
        usage_tier="basic",
        read={"refill_rate": 100, "bucket_capacity": 500},
        write={"refill_rate": 10, "bucket_capacity": 100},
        lineage=_lineage("/account/limits"),
    )
    cutoff = KalshiHistoricalCutoff(
        market_settled_ts="2026-04-01T00:00:00Z",
        trades_created_ts="2026-04-02T00:00:00Z",
        orders_updated_ts="2026-04-03T00:00:00Z",
        observed_at=_now(),
        lineage=_lineage("/historical/cutoff"),
    )

    snapshot = KalshiAccountSnapshot(
        account_id="kalshi-live-subaccount-0",
        environment="live",
        subaccount=0,
        generated_at=_now(),
        balance=balance,
        positions=positions,
        orders=orders,
        fills=fills,
        account_limits=account_limits,
        historical_cutoff=cutoff,
        freshness={
            "balance": {"state": "fresh", "as_of": _now(), "row_count": 1, "cursor_exhausted": True},
            "positions": {"state": "partial", "as_of": _now(), "row_count": 2, "cursor_exhausted": False},
            "orders": {"state": "fresh", "as_of": _now(), "row_count": 1, "cursor_exhausted": True},
            "fills": {"state": "fresh", "as_of": _now(), "row_count": 1, "cursor_exhausted": True},
            "account_limits": {"state": "fresh", "as_of": _now(), "row_count": 1, "cursor_exhausted": True},
            "historical_cutoff": {"state": "fresh", "as_of": _now(), "row_count": 1, "cursor_exhausted": True},
        },
        warnings=[
            {
                "code": "partial_positions_page",
                "message": "A cursor remained after the page cap.",
                "severity": "warning",
                "domain": "positions",
            }
        ],
    )

    dumped = snapshot.model_dump(mode="json")
    assert dumped["balance"]["balance"] == 12_345
    assert dumped["balance"]["portfolio_value"] == 23_456
    assert dumped["positions"]["market_positions"][0]["ticker"] == "KXNYC-26MAY10-T75"
    assert dumped["positions"]["market_positions"][0]["position_fp"] == "10.50"
    assert dumped["orders"]["orders"][0]["outcome_side"] == "yes"
    assert dumped["orders"]["orders"][0]["book_side"] == "bid"
    assert dumped["fills"]["fills"][0]["fee_cost"] == "0.0100"
    assert dumped["historical_cutoff"]["orders_updated_ts"] == "2026-04-03T00:00:00Z"
    assert dumped["warnings"][0]["domain"] == "positions"


def test_kalshi_fixed_point_fields_reject_floats_and_invalid_side_values() -> None:
    with pytest.raises(ValidationError, match="position_fp"):
        KalshiPositionsPage(
            market_positions=[
                {
                    "ticker": "KXNYC-26MAY10-T75",
                    "total_traded_dollars": "12.3400",
                    "position_fp": 10.5,
                    "market_exposure_dollars": "6.1700",
                    "realized_pnl_dollars": "0.0000",
                    "fees_paid_dollars": "0.0500",
                }
            ]
        )

    with pytest.raises(ValidationError, match="outcome_side"):
        KalshiFillsPage(
            fills=[
                {
                    "fill_id": "fill-001",
                    "ticker": "KXNYC-26MAY10-T75",
                    "outcome_side": "maybe",
                    "book_side": "bid",
                    "count_fp": "1.00",
                }
            ]
        )


def test_kalshi_pagination_and_historical_tier_metadata_are_contractual() -> None:
    orders = KalshiOrdersPage(
        orders=[
            {
                "order_id": "historical-order-001",
                "ticker": "KXNYC-26MAY10-T75",
                "outcome_side": "no",
                "book_side": "ask",
                "type": "limit",
                "status": "executed",
                "fill_count_fp": "10.00",
                "remaining_count_fp": "0.00",
                "initial_count_fp": "10.00",
                "tier": "historical",
                "lineage": _lineage("/historical/orders", tier="historical"),
            }
        ],
        cursor=None,
        page={"cursor": None, "limit": 100, "page_number": 1, "tier": "historical", "exhausted": True},
        lineage=_lineage("/historical/orders", tier="historical", page_number=1),
    )

    assert orders.orders[0].tier == "historical"
    assert orders.page is not None
    assert orders.page.exhausted is True
    assert orders.lineage is not None
    assert orders.lineage.endpoint == "/historical/orders"


def test_generic_trade_desk_contracts_accept_long_kalshi_tickers_as_secondary_views() -> None:
    ticker = "KXINFLATION-26DEC31-CPIYOY-3_25-YES-PREDICTION-MARKET-LONG"
    now = _now()

    position = TradePosition(
        accountId="kalshi-live-subaccount-0",
        symbol=ticker,
        assetClass="prediction_market",
        providerInstrumentId=ticker,
        outcomeSide="yes",
        quantity=1.5,
        marketValue=75,
        sourceObservedAt=now,
        ingestedAt=now,
    )
    order = TradeOrder(
        orderId="order-001",
        accountId="kalshi-live-subaccount-0",
        provider="kalshi",
        environment="live",
        status="unknown_reconcile_required",
        symbol=ticker,
        side="buy",
        orderType="limit",
        assetClass="prediction_market",
        quantity=1,
        limitPrice=56,
        createdAt=now,
    )
    row = TradeBlotterRow(
        rowId="fill-001",
        accountId="kalshi-live-subaccount-0",
        provider="kalshi",
        environment="live",
        eventType="fill",
        occurredAt=now,
        symbol=ticker,
        assetClass="prediction_market",
        quantity=1,
        price=56,
    )

    assert position.symbol == ticker
    assert order.symbol == ticker
    assert row.symbol == ticker
