from datetime import date

import pytest

from asset_allocation_contracts.market_signals import (
    MARKET_SIGNAL_EXCLUDED_QUIVER_TABLES,
    MARKET_SIGNAL_SUPPORTED_SOURCES,
    SignalActivityEvent,
    SignalActivityPlotPoint,
    SignalActivityScreenRequest,
    SignalActivityScreenResponse,
)


def test_market_signal_sources_and_exclusions_document_v1_scope() -> None:
    assert MARKET_SIGNAL_SUPPORTED_SOURCES == (
        "congressional_trading",
        "insider_trading",
        "wall_street_bets",
    )
    assert "quiver_congress_holdings_daily" in MARKET_SIGNAL_EXCLUDED_QUIVER_TABLES


def test_congressional_activity_preserves_amount_range_and_flags_midpoint_proxy() -> None:
    event = SignalActivityEvent.model_validate(
        {
            "event_id": "congress-1",
            "source": "congressional_trading",
            "activity_date": "2026-04-18",
            "date_basis": "filed_at",
            "symbol": "AAPL",
            "issuer_name": "Example Corp",
            "actor_name": "Jane Doe",
            "activity_type": "purchase",
            "activity_label": "Purchase",
            "size_value": 8000.5,
            "size_unit": "usd_midpoint_proxy",
            "amount_lower_usd": 1001,
            "amount_upper_usd": 15000,
            "amount_bucket_label": "$1,001 - $15,000",
            "mapping_status": "mapped",
            "quality_flags": ["amount_range_midpoint_proxy"],
        }
    )

    assert event.amount_lower_usd == 1001
    assert event.amount_upper_usd == 15000
    assert event.size_unit == "usd_midpoint_proxy"


def test_wall_street_bets_rejects_dollar_sized_points() -> None:
    with pytest.raises(ValueError, match="wall_street_bets size"):
        SignalActivityPlotPoint.model_validate(
            {
                "source": "wall_street_bets",
                "activity_date": "2026-04-18",
                "date_basis": "event_time",
                "activity_count": 5,
                "size_value": 250000,
                "size_unit": "usd_notional_proxy",
                "quality_flags": ["notional_proxy", "mentions_not_dollars"],
            }
        )


def test_proxy_units_require_visible_quality_flags() -> None:
    with pytest.raises(ValueError, match="notional_proxy"):
        SignalActivityEvent.model_validate(
            {
                "event_id": "insider-1",
                "source": "insider_trading",
                "activity_date": "2026-04-18",
                "date_basis": "uploaded",
                "activity_type": "purchase",
                "activity_label": "Insider buy",
                "size_value": 50000,
                "size_unit": "usd_notional_proxy",
            }
        )


def test_signal_activity_response_shape_supports_plots_events_freshness_and_quality() -> None:
    response = SignalActivityScreenResponse.model_validate(
        {
            "plots": [
                {
                    "source": "wall_street_bets",
                    "label": "WallStreetBets",
                    "size_unit": "mentions",
                    "points": [
                        {
                            "source": "wall_street_bets",
                            "activity_date": "2026-04-18",
                            "date_basis": "event_time",
                            "activity_count": 4,
                            "size_value": 12,
                            "size_unit": "mentions",
                            "mention_count": 12,
                            "quality_flags": ["mentions_not_dollars"],
                        }
                    ],
                }
            ],
            "events": [],
            "freshness": [{"source": "wall_street_bets", "latest_activity_date": "2026-04-18"}],
            "data_quality": [
                {
                    "source": "wall_street_bets",
                    "row_count": 1,
                    "excluded_tables": list(MARKET_SIGNAL_EXCLUDED_QUIVER_TABLES),
                    "quality_flags": ["mentions_not_dollars"],
                }
            ],
            "total_events": 0,
            "limit": 250,
            "offset": 0,
        }
    )

    assert response.plots[0].points[0].activity_date == date(2026, 4, 18)
    assert response.freshness[0].source == "wall_street_bets"


def test_signal_activity_request_rejects_inverted_dates() -> None:
    with pytest.raises(ValueError, match="from_date"):
        SignalActivityScreenRequest.model_validate(
            {
                "from_date": "2026-04-19",
                "to_date": "2026-04-18",
            }
        )
