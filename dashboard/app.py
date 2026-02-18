"""Streamlit ETL monitoring dashboard.

Run: `streamlit run dashboard/app.py`

Shows: data freshness, sales vs inventory, delivery delays, KPI trends.
"""
from pathlib import Path
import os
import sqlite3
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
DB = ROOT / "supply_chain.db"


@st.cache_data
def load_tables():
    if DB.exists():
        conn = sqlite3.connect(DB)
        sales = pd.read_sql_query("SELECT * FROM fact_sales", conn, parse_dates=["Date"]) if "fact_sales" in pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)["name"].values else pd.DataFrame()
        inv = pd.read_sql_query("SELECT * FROM inventory_summary", conn, parse_dates=["last_inventory_date"]) if "inventory_summary" in pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)["name"].values else pd.DataFrame()
        log = pd.read_sql_query("SELECT * FROM logistics_kpi", conn) if "logistics_kpi" in pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)["name"].values else pd.DataFrame()
    else:
        # fallback to CSVs
        sales = pd.read_csv(PROCESSED / "fact_sales.csv", parse_dates=["Date"]) if (PROCESSED / "fact_sales.csv").exists() else pd.DataFrame()
        inv = pd.read_csv(PROCESSED / "inventory_summary.csv", parse_dates=["last_inventory_date"]) if (PROCESSED / "inventory_summary.csv").exists() else pd.DataFrame()
        log = pd.read_csv(PROCESSED / "logistics_kpi.csv") if (PROCESSED / "logistics_kpi.csv").exists() else pd.DataFrame()
    return sales, inv, log


def data_freshness():
    rows = []
    for f in (PROCESSED).glob("*.csv"):
        mtime = datetime.fromtimestamp(f.stat().st_mtime)
        rows.append({"file": f.name, "modified": mtime})
    df = pd.DataFrame(rows)
    return df


def main():
    st.set_page_config(page_title="ETL Monitoring", layout="wide")
    st.title("ETL Monitoring Dashboard")

    sales, inv, log = load_tables()

    st.header("Data Freshness")
    df_fresh = data_freshness()
    if not df_fresh.empty:
        df_fresh = df_fresh.sort_values("modified", ascending=False)
        st.table(df_fresh)
    else:
        st.info("No processed CSVs found in data/processed/")

    st.header("Sales vs Inventory")
    if not sales.empty and not inv.empty:
        # Aggregate recent sales by ProductID
        sales_agg = sales.groupby("ProductID").agg(sold=("Quantity", "sum"), sales_value=("Total", "sum")).reset_index()
        merged = pd.merge(inv, sales_agg, on="ProductID", how="left").fillna(0)
        fig = px.bar(merged.melt(id_vars=["ProductID"], value_vars=["total_stock", "sold"], var_name="metric", value_name="value"), x="ProductID", y="value", color="metric", barmode="group", title="Stock vs Sold by Product")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Require both `fact_sales` and `inventory_summary` to show this chart.")

    st.header("Delivery Delays")
    if not log.empty:
        # If kpi table exists, use status counts
        cols = [c for c in log.columns if c.startswith("status_")]
        if cols:
            data = {"status": [c.replace("status_", "") for c in cols], "count": [int(log.iloc[0][c]) for c in cols]}
            df_status = pd.DataFrame(data)
            fig2 = px.pie(df_status, names="status", values="count", title="Shipment Status Distribution")
            st.plotly_chart(fig2, use_container_width=True)
            st.metric("Percent Delivered", f"{log.iloc[0].get('percent_delivered', 0)}%")
        else:
            st.info("No status columns found in logistics_kpi.")
    else:
        st.info("No logistics KPI data available.")

    st.header("KPI Trends")
    if not sales.empty:
        df_trend = sales.copy()
        if "Date" in df_trend.columns:
            df_trend = df_trend.dropna(subset=["Date"]) 
            df_trend["Date"] = pd.to_datetime(df_trend["Date"]) 
            trend = df_trend.set_index("Date").resample("W").agg(total_sales=("Total", "sum"), total_units=("Quantity", "sum")).reset_index()
            fig3 = px.line(trend, x="Date", y=["total_sales", "total_units"], title="Weekly KPI Trends")
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No `Date` column in sales for trend analysis.")
    else:
        st.info("No sales data for KPI trends.")


if __name__ == "__main__":
    main()
