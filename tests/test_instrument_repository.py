from datetime import date
from decimal import Decimal

import pytest

from app.data.instrument_contract import InstrumentIdentity
from app.data.instrument_repository import upsert_instruments


class FakeCursor:
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, query, params):
        if self.connection.fail:
            raise RuntimeError("simulated database failure")
        self.connection.executed.append((query, params))


class FakeConnection:
    def __init__(self, fail=False):
        self.fail = fail
        self.executed = []
        self.commits = 0
        self.rollbacks = 0

    def cursor(self):
        return FakeCursor(self)

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


def sample_instrument():
    return InstrumentIdentity(
        provider="DHAN",
        security_id="999999",
        exchange_segment="NSE_FNO",
        trading_symbol="NIFTY 25000 CE",
        instrument_type="OPTIDX",
        underlying_symbol="NIFTY",
        expiry_date=date(2026, 10, 29),
        strike_price=Decimal("25000"),
        option_type="CE",
        lot_size=65,
        tick_size=Decimal("0.05"),
    )


def test_upsert_writes_expected_fields_and_commits():
    connection = FakeConnection()
    count = upsert_instruments(connection, [sample_instrument()])
    assert count == 1
    assert connection.commits == 1
    assert connection.rollbacks == 0
    query, params = connection.executed[0]
    assert "ON CONFLICT (provider, security_id, exchange_segment)" in query
    assert params[1:4] == ("999999", "NSE_FNO", "NIFTY 25000 CE")
    assert params[7:9] == (Decimal("25000"), "CE")


def test_empty_batch_does_not_touch_database():
    connection = FakeConnection()
    assert upsert_instruments(connection, []) == 0
    assert connection.commits == 0
    assert connection.rollbacks == 0
    assert connection.executed == []


def test_database_failure_rolls_back_and_reraises():
    connection = FakeConnection(fail=True)
    with pytest.raises(RuntimeError, match="simulated database failure"):
        upsert_instruments(connection, [sample_instrument()])
    assert connection.commits == 0
    assert connection.rollbacks == 1
