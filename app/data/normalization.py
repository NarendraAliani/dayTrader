"""Vendor-neutral normalization for ticks and order-book snapshots.

Vendor adapters must map source timestamps and fields into these models only
after validating the source packet. This module does not infer missing values.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class DepthLevel:
    price: float
    quantity: int
    orders: int | None = None

    def __post_init__(self) -> None:
        if self.price <= 0:
            raise ValueError("Depth price must be positive")
        if self.quantity < 0:
            raise ValueError("Depth quantity cannot be negative")
        if self.orders is not None and self.orders < 0:
            raise ValueError("Depth order count cannot be negative")


@dataclass(frozen=True)
class MarketTick:
    provider: str
    exchange_segment: str
    security_id: str
    event_time: datetime
    received_at: datetime
    last_price: float
    last_quantity: int | None = None
    cumulative_volume: int | None = None
    open_interest: int | None = None
    raw: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if not self.provider.strip() or not self.exchange_segment.strip() or not self.security_id.strip():
            raise ValueError("Provider, exchange segment and security ID are required")
        if self.last_price <= 0:
            raise ValueError("Last price must be positive")
        if self.last_quantity is not None and self.last_quantity < 0:
            raise ValueError("Last quantity cannot be negative")
        if self.cumulative_volume is not None and self.cumulative_volume < 0:
            raise ValueError("Cumulative volume cannot be negative")
        if self.open_interest is not None and self.open_interest < 0:
            raise ValueError("Open interest cannot be negative")


@dataclass(frozen=True)
class DepthSnapshot:
    provider: str
    exchange_segment: str
    security_id: str
    event_time: datetime
    received_at: datetime
    bids: tuple[DepthLevel, ...]
    asks: tuple[DepthLevel, ...]
    raw: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if not self.provider.strip() or not self.exchange_segment.strip() or not self.security_id.strip():
            raise ValueError("Provider, exchange segment and security ID are required")
        if not self.bids or not self.asks:
            raise ValueError("Both bid and ask sides must contain at least one level")
        if len(self.bids) > 200 or len(self.asks) > 200:
            raise ValueError("Depth snapshots are limited to 200 levels per side")
        if any(self.bids[i].price < self.bids[i + 1].price for i in range(len(self.bids) - 1)):
            raise ValueError("Bid levels must be ordered from highest to lowest price")
        if any(self.asks[i].price > self.asks[i + 1].price for i in range(len(self.asks) - 1)):
            raise ValueError("Ask levels must be ordered from lowest to highest price")
        if self.bids[0].price >= self.asks[0].price:
            raise ValueError("Best bid must be below best ask; crossed/locked data needs review")
