import pytest
from app.strategies.iceberg import score_iceberg_evidence

def test_replenishment_and_absorption_raise_score():
    e = score_iceberg_evidence(symbol="NIFTY-FUT", price=25000, side="BUY", replenishments=6, executed_volume=800, price_change=0.02)
    assert e.score >= 70
    assert e.label == "STRONG_PATTERN"

def test_unknown_side_reduces_score():
    args = dict(symbol="NIFTY-FUT", price=25000, replenishments=3, executed_volume=300, price_change=0.01)
    assert score_iceberg_evidence(**args, side="UNKNOWN").score < score_iceberg_evidence(**args, side="BUY").score

def test_rejects_invalid_price():
    with pytest.raises(ValueError):
        score_iceberg_evidence(symbol="NIFTY-FUT", price=0, side="BUY", replenishments=1, executed_volume=10, price_change=0)
