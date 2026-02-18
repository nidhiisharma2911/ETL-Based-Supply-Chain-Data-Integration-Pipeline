# Dashboard

Place dashboard code (Streamlit, Dash, or other) here. Example: a `dashboard/app.py` that reads `outputs/processed.parquet` and renders KPIs.

Power BI note: a `.pbix` file (`etl_monitoring.pbix`) is a proprietary binary and cannot be generated here. Instead this repo includes a Streamlit alternative at `dashboard/app.py`.

Run the Streamlit dashboard:

```bash
pip install -r requirements.txt
streamlit run dashboard/app.py
```

The app reads processed CSVs under `data/processed/` or `supply_chain.db` if present and shows:
- Data freshness (file modification times)
- Sales vs Inventory comparison
- Delivery delays (status distribution)
- KPI trends (weekly sales / units)

