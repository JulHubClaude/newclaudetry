"""Validierung von Transaktions-DataFrames vor dem Import."""
from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = [
    "date", "transaction_type", "asset_class", "asset_name",
    "ticker", "broker", "currency", "quantity", "price_per_unit",
    "gross_amount", "fees", "taxes", "net_amount", "notes",
]

ALLOWED_TYPES = {
    "buy", "sell", "dividend", "deposit", "withdrawal", "fee", "tax",
}
ALLOWED_ASSET_CLASSES = {
    "stock", "etf", "crypto", "precious_metal",
    "private_equity", "cash", "other",
}

# Bei diesen Typen muss net_amount negativ sein (Geld fließt raus).
OUTFLOW_TYPES = {"buy", "withdrawal", "fee", "tax"}
# Bei diesen Typen muss net_amount positiv sein (Geld fließt rein).
INFLOW_TYPES = {"sell", "dividend", "deposit"}


class ValidationError(Exception):
    """Wird geworfen, wenn ein DataFrame nicht importiert werden kann."""


def validate(df: pd.DataFrame) -> pd.DataFrame:
    """Prüft das DataFrame und gibt eine bereinigte Kopie zurück.

    Wirft `ValidationError` mit einer aggregierten Fehlerliste.
    """
    errors: list[str] = []

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValidationError(f"Fehlende Spalten: {missing}")

    df = df.copy()

    # Datum parsen
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    if df["date"].isna().any():
        bad = df.index[df["date"].isna()].tolist()
        errors.append(f"Ungültige Daten in Zeilen: {bad}")

    # Numerische Felder
    numeric_cols = ["quantity", "price_per_unit", "gross_amount",
                    "fees", "taxes", "net_amount"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        if df[col].isna().any():
            bad = df.index[df[col].isna()].tolist()
            errors.append(f"Nicht-numerische Werte in '{col}' Zeilen: {bad}")

    # Strings normalisieren
    for col in ["transaction_type", "asset_class", "currency"]:
        df[col] = df[col].astype(str).str.strip().str.lower()
    df["currency"] = df["currency"].str.upper()

    # Erlaubte Werte
    bad_types = df[~df["transaction_type"].isin(ALLOWED_TYPES)]
    if not bad_types.empty:
        errors.append(
            f"Unbekannte transaction_type Werte: "
            f"{bad_types['transaction_type'].unique().tolist()}"
        )
    bad_classes = df[~df["asset_class"].isin(ALLOWED_ASSET_CLASSES)]
    if not bad_classes.empty:
        errors.append(
            f"Unbekannte asset_class Werte: "
            f"{bad_classes['asset_class'].unique().tolist()}"
        )

    # Pflichtfelder
    if df["asset_name"].isna().any() or (df["asset_name"].astype(str).str.strip() == "").any():
        errors.append("Leere asset_name Werte gefunden")
    if df["currency"].str.len().ne(3).any():
        errors.append("currency muss ein 3-stelliger ISO-Code sein")

    # Plausibilität Mengen
    if (df["quantity"] < 0).any():
        errors.append("quantity darf nicht negativ sein")
    if (df["fees"] < 0).any() or (df["taxes"] < 0).any():
        errors.append("fees und taxes dürfen nicht negativ sein")

    # Vorzeichen von net_amount
    out_mask = df["transaction_type"].isin(OUTFLOW_TYPES) & (df["net_amount"] > 0)
    in_mask = df["transaction_type"].isin(INFLOW_TYPES) & (df["net_amount"] < 0)
    if out_mask.any():
        errors.append(
            f"Outflow-Typen mit positivem net_amount in Zeilen: "
            f"{df.index[out_mask].tolist()}"
        )
    if in_mask.any():
        errors.append(
            f"Inflow-Typen mit negativem net_amount in Zeilen: "
            f"{df.index[in_mask].tolist()}"
        )

    if errors:
        raise ValidationError("; ".join(errors))

    # Optionale Strings sauber als None speichern (statt NaN)
    for col in ["ticker", "broker", "notes"]:
        df[col] = df[col].where(df[col].notna(), None)
        df[col] = df[col].apply(lambda v: None if v in ("", "nan", None) else str(v).strip())

    return df[REQUIRED_COLUMNS]
