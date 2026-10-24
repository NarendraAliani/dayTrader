from datetime import date
from decimal import Decimal

import pytest

from app.data.dhan_instruments import parse_instrument_master, parse_instrument_row


def test_parses_compact_equity_row():
    row = {
        "SEM_EXM_EXCH_ID": "NSE",
        "SEM_SEGMENT": "E",
        "SEM_SMST_SECURITY_ID": "1333",
        "SEM_INSTRUMENT_NAME": "EQUITY",
        "SEM_TRADING_SYMBOL": "HDFCBANK",
        "SEM_LOT_UNITS": "1",
        "SEM_TICK_SIZE": "0.05",
    }
    item = parse_instrument_row(row)
    assert item is not None
    assert item.security_id == "1333"
    assert item.exchange_segment == "NSE_EQ"
    assert item.trading_symbol == "HDFCBANK"
    assert item.tick_size == Decimal("0.05")


def test_parses_detailed_option_row():
    row = {
        "EXCH_ID": "NSE",
        "SEGMENT": "D",
        "SECURITY_ID": "999999",
        "INSTRUMENT": "OPTIDX",
        "DISPLAY_NAME": "NIFTY 25000 CE",
        "UNDERLYING_SYMBOL": "NIFTY",
        "SM_EXPIRY_DATE": "2026-10-29",
        "STRIKE_PRICE": "25000",
        "OPTION_TYPE": "CE",
        "LOT_SIZE": "65",
        "TICK_SIZE": "0.05",
    }
    item = parse_instrument_row(row)
    assert item is not None
    assert item.exchange_segment == "NSE_FNO"
    assert item.instrument_type == "OPTIDX"
    assert item.underlying_symbol == "NIFTY"
    assert item.expiry_date == date(2026, 10, 29)
    assert item.strike_price == Decimal("25000")
    assert item.option_type == "CE"
    assert item.lot_size == 65


def test_unsupported_segment_is_skipped():
    row = {
        "SEM_EXM_EXCH_ID": "NSE",
        "SEM_SEGMENT": "C",
        "SEM_SMST_SECURITY_ID": "1",
        "SEM_INSTRUMENT_NAME": "FUTCUR",
        "SEM_TRADING_SYMBOL": "USDINR",
    }
    assert parse_instrument_row(row) is None


def test_master_skips_duplicate_security_ids():
    csv_text = (
        "SEM_EXM_EXCH_ID,SEM_SEGMENT,SEM_SMST_SECURITY_ID,"
        "SEM_INSTRUMENT_NAME,SEM_TRADING_SYMBOL\n"
        "NSE,E,1333,EQUITY,HDFCBANK\n"
        "NSE,E,1333,EQUITY,HDFCBANK\n"
    )
    rows = parse_instrument_master(csv_text)
    assert len(rows) == 1


def test_master_reports_bad_supported_row_with_line_number():
    csv_text = (
        "SEM_EXM_EXCH_ID,SEM_SEGMENT,SEM_SMST_SECURITY_ID,"
        "SEM_INSTRUMENT_NAME,SEM_TRADING_SYMBOL\n"
        "NSE,E,,EQUITY,HDFCBANK\n"
    )
    with pytest.raises(ValueError, match="line 2"):
        parse_instrument_master(csv_text)


def test_option_without_strike_is_rejected():
    row = {
        "EXCH_ID": "NSE",
        "SEGMENT": "D",
        "SECURITY_ID": "123",
        "INSTRUMENT": "OPTIDX",
        "DISPLAY_NAME": "NIFTY CE",
        "OPTION_TYPE": "CE",
    }
    with pytest.raises(ValueError, match="strike_price"):
        parse_instrument_row(row)
