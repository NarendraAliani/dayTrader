from datetime import datetime, timezone

import pytest

from app.data.normalization import DepthLevel, DepthSnapshot, MarketTick


NOW = datetime(2026, 10, 24, 9, 30, tzinfo=timezone.utc)


def test_market_tick_accepts_valid_minimal_data():
    tick = MarketTick("DHAN", "NSE_FNO", "12345", NOW, NOW, 25123.5)
    assert tick.last_price == 25123.5
    assert tick.cumulative_volume is None


def test_market_tick_rejects_negative_volume():
    with pytest.raises(ValueError):
        MarketTick("DHAN", "NSE_FNO", "12345", NOW, NOW, 100.0, cumulative_volume=-1)


def test_depth_snapshot_accepts_sorted_book():
    book = DepthSnapshot(
        "DHAN", "NSE_FNO", "12345", NOW, NOW,
        bids=(DepthLevel(100.0, 20, 2), DepthLevel(99.5, 30, 3)),
        asks=(DepthLevel(100.5, 15, 1), DepthLevel(101.0, 10, 2)),
    )
    assert len(book.bids) == 2


def test_depth_snapshot_rejects_unsorted_bids():
    with pytest.raises(ValueError):
        DepthSnapshot(
            "DHAN", "NSE_FNO", "12345", NOW, NOW,
            bids=(DepthLevel(99.5, 20), DepthLevel(100.0, 30)),
            asks=(DepthLevel(100.5, 15),),
        )


def test_depth_snapshot_rejects_crossed_book():
    with pytest.raises(ValueError):
        DepthSnapshot(
            "DHAN", "NSE_FNO", "12345", NOW, NOW,
            bids=(DepthLevel(101.0, 20),),
            asks=(DepthLevel(100.5, 15),),
        )
