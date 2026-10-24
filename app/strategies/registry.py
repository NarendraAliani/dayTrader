from app.strategies.base import Strategy


class StrategyRegistry:
    """In-memory registry; strategy discovery/config loading will be added next."""

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
        return [
            {
                "strategy_id": strategy.strategy_id,
                "name": strategy.name,
                "version": strategy.version,
                "enabled_by_default": strategy.enabled_by_default,
            }
            for strategy in self._strategies.values()
        ]


registry = StrategyRegistry()
