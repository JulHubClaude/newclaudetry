"""SQL-basierte Analysen für das Dashboard.

Alle Funktionen geben pandas-Objekte zurück, damit Streamlit sie direkt
anzeigen oder plotten kann.
"""
from __future__ import annotations

import sqlite3

import pandas as pd


def load_all_transactions(conn: sqlite3.Connection) -> pd.DataFrame:
    """Alle Transaktionen, sortiert nach Datum (neueste oben)."""
    sql = """
        SELECT id, date, transaction_type, asset_class, asset_name, ticker,
               broker, currency, quantity, price_per_unit, gross_amount,
               fees, taxes, net_amount, notes
        FROM transactions
        ORDER BY date DESC, id DESC;
    """
    df = pd.read_sql_query(sql, conn, parse_dates=["date"])
    return df


def total_invested(conn: sqlite3.Connection) -> float:
    """Summe aller Käufe als positiver Betrag (was insgesamt investiert wurde)."""
    sql = """
        SELECT COALESCE(SUM(-net_amount), 0) AS invested
        FROM transactions
        WHERE transaction_type = 'buy';
    """
    return float(conn.execute(sql).fetchone()["invested"])


def current_cash_flow(conn: sqlite3.Connection) -> float:
    """Summe aller net_amount = aktueller Cashflow über alle Typen."""
    sql = "SELECT COALESCE(SUM(net_amount), 0) AS cash FROM transactions;"
    return float(conn.execute(sql).fetchone()["cash"])


def total_dividends(conn: sqlite3.Connection) -> float:
    """Summe aller Dividenden-Nettoeingänge."""
    sql = """
        SELECT COALESCE(SUM(net_amount), 0) AS dividends
        FROM transactions
        WHERE transaction_type = 'dividend';
    """
    return float(conn.execute(sql).fetchone()["dividends"])


def realized_pnl_simple(conn: sqlite3.Connection) -> pd.DataFrame:
    """Vereinfachte realisierte Gewinne/Verluste pro Asset.

    Annahme: Wer verkauft hat, bekommt als PnL die Summe der sell-Nettobeträge
    minus die Summe der buy-Nettobeträge desselben Tickers / Asset-Namens.
    Das ist keine FIFO-Logik – nur eine grobe Näherung.
    """
    sql = """
        SELECT
            COALESCE(ticker, asset_name) AS asset,
            SUM(CASE WHEN transaction_type = 'sell' THEN net_amount ELSE 0 END)
              + SUM(CASE WHEN transaction_type = 'buy'  THEN net_amount ELSE 0 END)
              AS realized_pnl
        FROM transactions
        WHERE transaction_type IN ('buy', 'sell')
        GROUP BY asset
        HAVING SUM(CASE WHEN transaction_type = 'sell' THEN 1 ELSE 0 END) > 0
        ORDER BY realized_pnl DESC;
    """
    return pd.read_sql_query(sql, conn)


def transactions_by_asset_class(conn: sqlite3.Connection) -> pd.DataFrame:
    """Anzahl und Nettosumme der Transaktionen pro Asset-Klasse."""
    sql = """
        SELECT asset_class,
               COUNT(*)                AS num_transactions,
               SUM(net_amount)         AS net_total
        FROM transactions
        GROUP BY asset_class
        ORDER BY num_transactions DESC;
    """
    return pd.read_sql_query(sql, conn)


def portfolio_allocation(conn: sqlite3.Connection) -> pd.DataFrame:
    """Allocation pro Asset-Klasse anhand Netto-Käufe (vereinfacht, ohne Marktwert).

    invested = Summe der Käufe minus Summe der Verkäufe pro Klasse.
    """
    sql = """
        SELECT asset_class,
               SUM(CASE WHEN transaction_type = 'buy'  THEN -net_amount ELSE 0 END)
             - SUM(CASE WHEN transaction_type = 'sell' THEN  net_amount ELSE 0 END)
               AS invested
        FROM transactions
        WHERE asset_class NOT IN ('cash')
        GROUP BY asset_class
        HAVING invested > 0
        ORDER BY invested DESC;
    """
    return pd.read_sql_query(sql, conn)


def monthly_cash_flow(conn: sqlite3.Connection) -> pd.DataFrame:
    """Monatliche Summe aller net_amount für ein Liniendiagramm."""
    sql = """
        SELECT strftime('%Y-%m', date) AS month,
               SUM(net_amount)         AS net_amount
        FROM transactions
        GROUP BY month
        ORDER BY month;
    """
    return pd.read_sql_query(sql, conn)
