from datetime import date
from decimal import Decimal

import pytest

from app.data.instrument_contract import InstrumentIdentity


def test_valid_equity_instrument_identity():
    item = InstrumentIdentity(
        provider="DHAN",
        security_id="1333",
        exchange_segment="NSE_EQ",
        trading_symbol="HDFCBANK",
        instrument_type="EQUITY",
        tick_size=Decimal("0.05"),
    )
    assert item.security_id == "1333"
    assert item.exchange_segment == "NSE_EQ"


@pytest.mark.parametrize(
    "overrides",
    [
        {"security_id": ""},
        {"exchange_segment": "NSE_UNKNOWN"},
        {"lot_size": 0},
        {"tick_size": Decimal("0")},
        {"option_type": "CALL"},
        {"option_type": "CE"},
    ],
)
def test_invalid_instrument_identity_is_rejected(overrides):
    values = dict(
        provider="DHAN",
        security_id="123",
        exchange_segment="NSE_FNO",
        trading_symbol="NIFTY",
        instrument_type="FUTIDX",
    )
    values.update(overrides)
    if overrides.get("option_type") == "CE":
        values["strike_price"] = Decimal("25000")
    with pytest.raises(ValueError):
        InstrumentIdentity(**values)


def test_option_contract_requires_strike():
    with pytest.raises(ValueError, match="strike_price"):
        InstrumentIdentity(
            provider="DHAN",
            security_id="123",
            exchange_segment="NSE_FNO",
            trading_symbol="NIFTY",
            instrument_type="OPTIDX",
            option_type="PE",
        )
