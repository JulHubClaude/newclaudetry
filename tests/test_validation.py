import pandas as pd
import pytest

from src.validation import REQUIRED_COLUMNS, ValidationError, validate


def _row(**overrides):
    base = {
        "date": "2024-01-02",
        "transaction_type": "buy",
        "asset_class": "stock",
        "asset_name": "Apple Inc.",
        "ticker": "AAPL",
        "broker": "Trade Republic",
        "currency": "USD",
        "quantity": "5",
        "price_per_unit": "180",
        "gross_amount": "900",
        "fees": "1",
        "taxes": "0",
        "net_amount": "-901",
        "notes": "",
    }
    base.update(overrides)
    return base


def test_validate_ok():
    df = pd.DataFrame([_row()])
    out = validate(df)
    assert list(out.columns) == REQUIRED_COLUMNS
    assert out.loc[0, "currency"] == "USD"
    assert out.loc[0, "transaction_type"] == "buy"


def test_validate_rejects_unknown_type():
    df = pd.DataFrame([_row(transaction_type="gift")])
    with pytest.raises(ValidationError, match="transaction_type"):
        validate(df)


def test_validate_rejects_wrong_sign():
    # 'buy' soll negativen net_amount haben, hier positiv → Fehler
    df = pd.DataFrame([_row(net_amount="901")])
    with pytest.raises(ValidationError, match="Outflow"):
        validate(df)


def test_validate_rejects_negative_quantity():
    df = pd.DataFrame([_row(quantity="-1")])
    with pytest.raises(ValidationError, match="quantity"):
        validate(df)


def test_validate_requires_columns():
    df = pd.DataFrame([{"date": "2024-01-01"}])
    with pytest.raises(ValidationError, match="Fehlende Spalten"):
        validate(df)
