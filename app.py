"""Streamlit-Dashboard für investment-transaction-analyzer."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src import analysis
from src.db import DEFAULT_DB_PATH, get_connection, init_schema
from src.importer import import_csv

st.set_page_config(page_title="Investment Transaction Analyzer", layout="wide")


@st.cache_data(ttl=10)
def _load(db_path: str):
    with get_connection(db_path) as conn:
        init_schema(conn)
        return {
            "transactions": analysis.load_all_transactions(conn),
            "total_invested": analysis.total_invested(conn),
            "cash_flow": analysis.current_cash_flow(conn),
            "dividends": analysis.total_dividends(conn),
            "realized_pnl": analysis.realized_pnl_simple(conn),
            "by_class": analysis.transactions_by_asset_class(conn),
            "allocation": analysis.portfolio_allocation(conn),
            "monthly": analysis.monthly_cash_flow(conn),
        }


st.title("Investment Transaction Analyzer")
st.caption("Lokales Lernprojekt – keine Anlageberatung.")

# Sidebar: Import + DB-Pfad
st.sidebar.header("Daten")
db_path = st.sidebar.text_input("SQLite DB", value=str(DEFAULT_DB_PATH))

uploaded = st.sidebar.file_uploader("CSV importieren", type=["csv"])
if uploaded is not None:
    tmp = Path("data") / "_uploaded.csv"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_bytes(uploaded.getvalue())
    try:
        n = import_csv(tmp, db_path)
        st.sidebar.success(f"{n} Transaktionen importiert.")
        st.cache_data.clear()
    except Exception as exc:  # noqa: BLE001
        st.sidebar.error(f"Import fehlgeschlagen: {exc}")

if st.sidebar.button("Sample-Daten laden"):
    try:
        n = import_csv("data/sample_transactions.csv", db_path)
        st.sidebar.success(f"{n} Sample-Transaktionen importiert.")
        st.cache_data.clear()
    except Exception as exc:  # noqa: BLE001
        st.sidebar.error(f"Import fehlgeschlagen: {exc}")

data = _load(db_path)
tx = data["transactions"]

if tx.empty:
    st.info("Noch keine Daten. Lade die Sample-Daten in der Sidebar.")
    st.stop()

# Kennzahlen
c1, c2, c3, c4 = st.columns(4)
c1.metric("Gesamtinvestitionen", f"{data['total_invested']:,.2f}")
c2.metric("Aktueller Cashflow",  f"{data['cash_flow']:,.2f}")
c3.metric("Dividenden",          f"{data['dividends']:,.2f}")
realized_total = float(data["realized_pnl"]["realized_pnl"].sum()) if not data["realized_pnl"].empty else 0.0
c4.metric("Realisierte PnL (vereinfacht)", f"{realized_total:,.2f}")

# Charts
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Transaktionen nach Anlageklasse")
    st.dataframe(data["by_class"], hide_index=True, use_container_width=True)

with col_right:
    st.subheader("Portfolio Allocation (Netto-Käufe)")
    alloc = data["allocation"]
    if alloc.empty:
        st.write("Keine Käufe vorhanden.")
    else:
        fig = px.pie(alloc, names="asset_class", values="invested", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

st.subheader("Monatlicher Cashflow")
monthly = data["monthly"]
if not monthly.empty:
    monthly["month"] = pd.to_datetime(monthly["month"])
    fig = px.line(monthly, x="month", y="net_amount", markers=True)
    fig.update_layout(yaxis_title="Net Amount", xaxis_title="Monat")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Realisierte Gewinne/Verluste pro Asset")
st.dataframe(data["realized_pnl"], hide_index=True, use_container_width=True)

st.subheader("Alle Transaktionen")
st.dataframe(tx, hide_index=True, use_container_width=True)
