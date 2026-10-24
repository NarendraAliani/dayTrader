from app.strategies.base import Strategy
from app.strategies.ema_trend import EmaTrendStrategy


class StrategyRegistry:
    """In-memory registry; config-driven enablement and discovery come next."""

    def __init__(self) -> None:
        self._strategies: dict[str, Strategy] = {}

    def register(self, strategy: Strategy) -> None:
        strategy_id = getattr(strategy, "strategy_id", "").strip()
        if not strategy_id:
            raise ValueError("Strategy must define a non-empty strategy_id.")
        if strategy_id in self._strategies:
            raise ValueError(f"Strategy already registered: {strategy_id}")
        self._strategies[strategy_id] = strategy

    def get(self, strategy_id: str) -> Strategy:
        try:
            return self._strategies[strategy_id]
        except KeyError as exc:
            raise KeyError(f"Unknown strategy: {strategy_id}") from exc

    def list(self) -> list[dict[str, str | bool]]:
        return [{"strategy_id": s.strategy_id, "name": s.name, "version": s.version,
                 "enabled_by_default": s.enabled_by_default}
                for s in self._strategies.values()]


registry = StrategyRegistry()
registry.register(EmaTrendStrategy())
