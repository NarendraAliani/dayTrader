"""PostgreSQL persistence for normalized instrument identities."""
from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from app.data.instrument_contract import InstrumentIdentity

UPSERT_INSTRUMENT_SQL = """
INSERT INTO instruments (
    provider, security_id, exchange_segment, trading_symbol, instrument_type,
    underlying_symbol, expiry_date, strike_price, option_type, lot_size,
    tick_size, active, updated_at
) VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE, now()
)
ON CONFLICT (provider, security_id, exchange_segment) DO UPDATE SET
    trading_symbol = EXCLUDED.trading_symbol,
    instrument_type = EXCLUDED.instrument_type,
    underlying_symbol = EXCLUDED.underlying_symbol,
    expiry_date = EXCLUDED.expiry_date,
    strike_price = EXCLUDED.strike_price,
    option_type = EXCLUDED.option_type,
    lot_size = EXCLUDED.lot_size,
    tick_size = EXCLUDED.tick_size,
    active = TRUE,
    updated_at = now()
"""

DEFAULT_BATCH_SIZE = 1_000


def upsert_instruments(
    connection: Any,
    instruments: Iterable[InstrumentIdentity],
    *,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> int:
    """Insert/update instruments in bounded batches within one transaction.

    The caller supplies an open psycopg-compatible connection. The migration
    must be applied first. Re-running a master import updates existing records
    instead of creating duplicates. Any failure rolls the whole import back.
    """
    if batch_size < 1:
        raise ValueError("batch_size must be positive")

    items = list(instruments)
    if not items:
        return 0

    rows = [
        (
            item.provider,
            item.security_id,
            item.exchange_segment,
            item.trading_symbol,
            item.instrument_type,
            item.underlying_symbol,
            item.expiry_date,
            item.strike_price,
            item.option_type,
            item.lot_size,
            item.tick_size,
        )
        for item in items
    ]

    try:
        with connection.cursor() as cursor:
            for start in range(0, len(rows), batch_size):
                cursor.executemany(
                    UPSERT_INSTRUMENT_SQL,
                    rows[start : start + batch_size],
                )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    return len(items)
