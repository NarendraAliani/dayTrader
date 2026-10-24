import pytest
from app.strategies.base import Strategy, StrategySignal
from app.strategies.registry import StrategyRegistry


class DummyStrategy(Strategy):
    strategy_id = "dummy"
    name = "Dummy strategy"

    def evaluate(self, candles, *, symbol, timeframe):
        return StrategySignal(
            strategy_id=self.strategy_id,
            symbol=symbol,
            timeframe=timeframe,
            action="NO_TRADE",
            score=0.0,
            reason="Test strategy",
            metadata={},
        )


def test_registry_registers_and_lists_strategy():
    registry = StrategyRegistry()
    registry.register(DummyStrategy())
    assert registry.get("dummy").name == "Dummy strategy"
    assert registry.list()[0]["strategy_id"] == "dummy"


def test_registry_rejects_duplicate_strategy():
    registry = StrategyRegistry()
    registry.register(DummyStrategy())
    with pytest.raises(ValueError):
        registry.register(DummyStrategy())
