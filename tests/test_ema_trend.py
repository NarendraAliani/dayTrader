from app.strategies.ema_trend import EmaTrendStrategy

def test_ema_strategy_returns_no_trade_with_insufficient_data():
    result = EmaTrendStrategy().evaluate([{"close": 100.0}] * 10, symbol="NIFTY-FUT", timeframe="5m")
    assert result.action == "NO_TRADE"

def test_ema_strategy_returns_structured_signal():
    candles = [{"close": float(i)} for i in range(1, 31)]
    result = EmaTrendStrategy().evaluate(candles, symbol="NIFTY-FUT", timeframe="5m")
    assert result.action in {"BUY", "SELL", "NO_TRADE"}
    assert result.strategy_id == "ema_trend"
    assert 0 <= result.score <= 100
