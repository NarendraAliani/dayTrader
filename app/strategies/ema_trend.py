"""Simple EMA trend-following plugin; signals are research candidates, not advice."""
from typing import Any
from app.strategies.base import Strategy, StrategySignal


class EmaTrendStrategy(Strategy):
    strategy_id = "ema_trend"
    name = "EMA Trend"
    version = "0.1.0"
    enabled_by_default = False

    def __init__(self, fast_period: int = 9, slow_period: int = 21) -> None:
        if fast_period < 2 or slow_period < 2 or fast_period >= slow_period:
            raise ValueError("Require 2 <= fast_period < slow_period")
        self.fast_period = fast_period
        self.slow_period = slow_period

    @staticmethod
    def _ema(values: list[float], period: int) -> float:
        alpha = 2.0 / (period + 1.0)
        result = values[0]
        for value in values[1:]:
            result = alpha * value + (1.0 - alpha) * result
        return result

    def evaluate(self, candles: list[dict[str, Any]], *, symbol: str, timeframe: str) -> StrategySignal:
        closes = [float(c["close"]) for c in candles if c.get("close") is not None]
        if len(closes) < self.slow_period:
            return StrategySignal(self.strategy_id, symbol, timeframe, "NO_TRADE", 0.0,
                f"Need at least {self.slow_period} closes; received {len(closes)}.",
                {"fast_period": self.fast_period, "slow_period": self.slow_period})
        fast = self._ema(closes[-self.slow_period:], self.fast_period)
        slow = self._ema(closes[-self.slow_period:], self.slow_period)
        action = "BUY" if fast > slow else "SELL" if fast < slow else "NO_TRADE"
        separation = abs(fast - slow) / slow if slow else 0.0
        score = round(min(separation * 1000.0, 100.0), 2)
        return StrategySignal(self.strategy_id, symbol, timeframe, action, score,
            f"EMA({self.fast_period})={fast:.4f}; EMA({self.slow_period})={slow:.4f}.",
            {"fast_ema": fast, "slow_ema": slow, "bars": len(closes)})
