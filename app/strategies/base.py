from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class StrategySignal:
    strategy_id: str
    symbol: str
    timeframe: str
    action: str
    score: float
    reason: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class Strategy(ABC):
    strategy_id: str
    name: str
    version: str = "1.0.0"
    enabled_by_default: bool = False

    @abstractmethod
    def evaluate(self, candles: list[dict[str, Any]], *, symbol: str, timeframe: str) -> StrategySignal:
        """Evaluate normalized OHLCV candles and return a signal."""
        raise NotImplementedError
