"""Heuristic iceberg-like replenishment scoring over normalized market events.

This does not prove hidden reserve orders exist. It scores patterns consistent with
displayed-liquidity replenishment and absorption. Validate real Dhan payloads first.
"""
from dataclasses import dataclass
from typing import Literal

Side = Literal["BUY", "SELL", "UNKNOWN"]


@dataclass(frozen=True)
class IcebergEvidence:
    symbol: str
    price: float
    side: Side
    replenishments: int
    executed_volume: float
    price_change: float
    score: float
    label: str


def score_iceberg_evidence(*, symbol: str, price: float, side: Side, replenishments: int, executed_volume: float, price_change: float) -> IcebergEvidence:
    """Score normalized evidence; caller must define units and time windows."""
    if not symbol.strip():
        raise ValueError("symbol is required")
    if price <= 0:
        raise ValueError("price must be positive")
    if replenishments < 0 or executed_volume < 0:
        raise ValueError("replenishments and executed_volume cannot be negative")
    if side not in ("BUY", "SELL", "UNKNOWN"):
        raise ValueError("side must be BUY, SELL, or UNKNOWN")
    score = min(replenishments, 10) * 6.0
    score += min(executed_volume, 1000.0) / 1000.0 * 20.0
    if abs(price_change) <= max(price * 0.0002, 0.05):
        score += 20.0
    if side == "UNKNOWN":
        score *= 0.5
    score = round(min(score, 100.0), 2)
    label = "STRONG_PATTERN" if score >= 70 else "POSSIBLE_PATTERN" if score >= 40 else "WEAK_PATTERN"
    return IcebergEvidence(symbol, price, side, replenishments, executed_volume, price_change, score, label)
