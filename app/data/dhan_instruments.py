"""Parse official DhanHQ security-master CSV rows into our normalized contract.

The parser supports the documented compact and detailed CSV column names. It
does not download the master itself; network/retry/scheduling belongs in a
separate ingestion service.
"""
from __future__ import annotations

import csv
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from io import StringIO
from typing import Iterable, Mapping

from app.data.instrument_contract import InstrumentIdentity

_SEGMENTS = {
    ("NSE", "E"): "NSE_EQ",
    ("NSE", "D"): "NSE_FNO",
    ("BSE", "E"): "BSE_EQ",
    ("BSE", "D"): "BSE_FNO",
    ("MCX", "M"): "MCX_COMM",
}
# Dhan's index feed segment is separate from the exchange's CSV E/D segments.
_SPECIAL_SEGMENTS = {("IDX", "I"): "IDX_I", ("NSE", "I"): "IDX_I"}


def _value(row: Mapping[str, str], *keys: str) -> str:
    """Return the first non-empty alias, trimming whitespace and BOM."""
    for key in keys:
        value = row.get(key)
        if value is not None:
            cleaned = str(value).strip().lstrip("\ufeff")
            if cleaned:
                return cleaned
    return ""


def _optional_decimal(value: str, field_name: str) -> Decimal | None:
    if not value:
        return None
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"invalid {field_name}: {value!r}") from exc
    # Dhan master commonly uses 0 for non-option strike prices.
    if field_name == "strike_price" and result == 0:
        return None
    return result


def _optional_int(value: str, field_name: str) -> int | None:
    if not value:
        return None
    try:
        result = int(Decimal(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"invalid {field_name}: {value!r}") from exc
    return result


def _optional_date(value: str) -> date | None:
    if not value or value in {"NA", "N/A", "0000-00-00"}:
        return None
    normalized = value.strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(normalized, fmt).date()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(normalized.replace("Z", "+00:00")).date()
    except ValueError as exc:
        raise ValueError(f"invalid expiry date: {value!r}") from exc


def parse_instrument_row(row: Mapping[str, str]) -> InstrumentIdentity | None:
    """Normalize one compact or detailed Dhan CSV row.

    Returns None for instruments outside supported exchanges/segments. Invalid
    rows inside supported segments raise ValueError so ingestion can report them
    rather than silently storing incorrect security IDs.
    """
    exchange = _value(row, "EXCH_ID", "SEM_EXM_EXCH_ID").upper()
    segment_code = _value(row, "SEGMENT", "SEM_SEGMENT").upper()
    segment = _SEGMENTS.get((exchange, segment_code)) or _SPECIAL_SEGMENTS.get(
        (exchange, segment_code)
    )
    if segment is None:
        return None

    security_id = _value(row, "SECURITY_ID", "SEM_SMST_SECURITY_ID")
    instrument_type = _value(
        row, "INSTRUMENT", "SEM_INSTRUMENT_NAME", "INSTRUMENT_TYPE",
        "SEM_EXCH_INSTRUMENT_TYPE",
    ).upper()
    trading_symbol = _value(
        row, "SEM_TRADING_SYMBOL", "TRADING_SYMBOL", "DISPLAY_NAME",
        "SEM_CUSTOM_SYMBOL", "SYMBOL_NAME", "SM_SYMBOL_NAME",
    )
    # Index feeds may omit a trading symbol in one source; don't invent one.
    if not security_id or not instrument_type or not trading_symbol:
        raise ValueError("supported Dhan row requires security ID, instrument type and symbol")

    is_option = instrument_type.startswith("OPT")
    option_type = _value(row, "OPTION_TYPE", "SEM_OPTION_TYPE").upper() or None
    if not is_option:
        option_type = None

    return InstrumentIdentity(
        provider="DHAN",
        security_id=security_id,
        exchange_segment=segment,
        trading_symbol=trading_symbol,
        instrument_type=instrument_type,
        underlying_symbol=(
            _value(row, "UNDERLYING_SYMBOL", "SEM_UNDERLYING_SYMBOL", "SYMBOL_NAME")
            or None
        ),
        expiry_date=_optional_date(_value(row, "SM_EXPIRY_DATE", "SEM_EXPIRY_DATE")),
        strike_price=_optional_decimal(
            _value(row, "STRIKE_PRICE", "SEM_STRIKE_PRICE"), "strike_price"
        ) if is_option else None,
        option_type=option_type,
        lot_size=_optional_int(_value(row, "LOT_SIZE", "SEM_LOT_UNITS"), "lot_size"),
        tick_size=_optional_decimal(_value(row, "TICK_SIZE", "SEM_TICK_SIZE"), "tick_size"),
    )


def parse_instrument_master(csv_text: str) -> list[InstrumentIdentity]:
    """Parse a CSV snapshot, retaining only supported exchange segments."""
    reader = csv.DictReader(StringIO(csv_text.lstrip("\ufeff")))
    if not reader.fieldnames:
        raise ValueError("Dhan instrument master CSV has no header")
    parsed: list[InstrumentIdentity] = []
    seen: set[tuple[str, str, str]] = set()
    for line_number, row in enumerate(reader, start=2):
        try:
            item = parse_instrument_row(row)
        except ValueError as exc:
            raise ValueError(f"invalid Dhan instrument row at CSV line {line_number}: {exc}") from exc
        if item is None:
            continue
        key = (item.provider, item.security_id, item.exchange_segment)
        if key in seen:
            continue
        seen.add(key)
        parsed.append(item)
    return parsed
