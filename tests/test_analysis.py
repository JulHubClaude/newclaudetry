from pathlib import Path

import pytest

from src import analysis
from src.db import get_connection, init_schema
from src.importer import import_csv


@pytest.fixture
def conn(tmp_path: Path):
    db = tmp_path / "test.db"
    import_csv("data/sample_transactions.csv", db)
    c = get_connection(db)
    init_schema(c)
    yield c
    c.close()


def test_load_all_transactions(conn):
    df = analysis.load_all_transactions(conn)
    assert not df.empty
    # neueste zuerst
    assert df["date"].is_monotonic_decreasing


def test_total_invested_is_positive(conn):
    assert analysis.total_invested(conn) > 0


def test_dividends_nonnegative(conn):
    assert analysis.total_dividends(conn) >= 0


def test_allocation_has_expected_classes(conn):
    alloc = analysis.portfolio_allocation(conn)
    assert {"etf", "stock", "crypto", "precious_metal"}.issubset(set(alloc["asset_class"]))


def test_monthly_cash_flow_sums_to_total(conn):
    monthly = analysis.monthly_cash_flow(conn)
    total = analysis.current_cash_flow(conn)
    assert round(monthly["net_amount"].sum(), 2) == round(total, 2)
