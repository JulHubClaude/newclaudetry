"""CSV-Import von Transaktionen nach SQLite."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import pandas as pd

from src.db import DEFAULT_DB_PATH, get_connection, init_schema
from src.validation import REQUIRED_COLUMNS, validate


def read_csv(csv_path: Path | str) -> pd.DataFrame:
    """Liest die CSV ohne Typkonvertierung; Validierung übernimmt das."""
    return pd.read_csv(csv_path, dtype=str, keep_default_na=False, na_values=[""])


def insert_transactions(conn: sqlite3.Connection, df: pd.DataFrame) -> int:
    """Fügt Zeilen in die Tabelle 'transactions' ein. Gibt Anzahl Zeilen zurück."""
    cols = ", ".join(REQUIRED_COLUMNS)
    placeholders = ", ".join(["?"] * len(REQUIRED_COLUMNS))
    sql = f"INSERT INTO transactions ({cols}) VALUES ({placeholders})"

    rows = [tuple(row) for row in df[REQUIRED_COLUMNS].itertuples(index=False, name=None)]
    conn.executemany(sql, rows)
    conn.commit()
    return len(rows)


def import_csv(csv_path: Path | str, db_path: Path | str = DEFAULT_DB_PATH) -> int:
    """End-to-end: CSV einlesen, validieren, in SQLite schreiben."""
    df = read_csv(csv_path)
    df = validate(df)
    with get_connection(db_path) as conn:
        init_schema(conn)
        return insert_transactions(conn, df)


def _main() -> None:
    parser = argparse.ArgumentParser(description="Import transactions CSV into SQLite.")
    parser.add_argument("csv", type=Path, help="Pfad zur CSV-Datei")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH, help="Pfad zur SQLite-DB")
    args = parser.parse_args()

    n = import_csv(args.csv, args.db)
    print(f"Imported {n} transactions into {args.db}")


if __name__ == "__main__":
    _main()
