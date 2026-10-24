"""Validated instrument identity contract used between Dhan adapters and storage.

This deliberately does not parse undocumented vendor payloads. The Dhan adapter
must map official payload fields into this contract after validating the
instrument master and exchange-segment values.
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Final

SUPPORTED_SEGMENTS: Final[frozenset[str]] = frozenset({
    "NSE_EQ", "NSE_FNO", "BSE_EQ", "BSE_FNO", "MCX_COMM",
})


@dataclass(frozen=True, slots=True)
class InstrumentIdentity:
    provider: str
    security_id: str
    exchange_segment: str
    trading_symbol: str
    instrument_type: str
    underlying_symbol: str | None = None
    expiry_date: date | None = None
    strike_price: Decimal | None = None
    option_type: str | None = None
    lot_size: int | None = None
    tick_size: Decimal | None = None

    def __post_init__(self) -> None:
        for field_name in ("provider", "security_id", "exchange_segment",
                           "trading_symbol", "instrument_type"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} is required")

        if self.provider.upper() != "DHAN":
            raise ValueError("provider must be DHAN for this adapter contract")
        if self.exchange_segment not in SUPPORTED_SEGMENTS:
            raise ValueError(f"unsupported exchange_segment: {self.exchange_segment}")
        if self.lot_size is not None and self.lot_size <= 0:
            raise ValueError("lot_size must be positive")
        if self.tick_size is not None and self.tick_size <= 0:
            raise ValueError("tick_size must be positive")
        if self.strike_price is not None and self.strike_price < 0:
            raise ValueError("strike_price cannot be negative")
        if self.option_type is not None and self.option_type not in {"CE", "PE"}:
            raise ValueError("option_type must be CE or PE")
        if self.option_type is not None and self.strike_price is None:
            raise ValueError("option instruments require strike_price")
