"""ETL pipeline: Extract -> Clean -> Transform -> Load

Reads raw CSVs from `data/raw/`, cleans and normalizes data,
and writes processed CSVs to `data/processed/`:

- fact_sales.csv
- inventory_summary.csv
- logistics_kpi.csv
"""
from pathlib import Path
from typing import Optional

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"


def extract(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def _normalize_dates(series: pd.Series) -> pd.Series:
    # Try default parsing, then try dayfirst as fallback
    s = pd.to_datetime(series.astype(str).replace({"nan": None, "": None}), errors="coerce")
    if s.isna().sum() > 0:
        s2 = pd.to_datetime(series.astype(str), dayfirst=True, errors="coerce")
        s = s.fillna(s2)
    return s


def clean_sales(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.drop_duplicates()
    # Normalize column names
    df.columns = [c.strip() for c in df.columns]
    # Parse date
    if "Date" in df.columns:
        df["Date"] = _normalize_dates(df["Date"])
    # Numeric conversions
    df["Quantity"] = pd.to_numeric(df.get("Quantity"), errors="coerce").fillna(0).astype(int)
    df["Price"] = pd.to_numeric(df.get("Price"), errors="coerce").fillna(0.0)
    return df


def transform_sales(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Total"] = df["Quantity"] * df["Price"]
    # Keep canonical columns
    cols = [c for c in ["SaleID", "Date", "CustomerID", "ProductID", "Quantity", "Price", "Total"] if c in df.columns]
    return df[cols]


def clean_inventory(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.drop_duplicates()
    df.columns = [c.strip() for c in df.columns]
    if "Date" in df.columns:
        df["Date"] = _normalize_dates(df["Date"])
    df["StockLevel"] = pd.to_numeric(df.get("StockLevel"), errors="coerce").fillna(0).astype(int)
    return df


def transform_inventory(df: pd.DataFrame) -> pd.DataFrame:
    # Summary per ProductID: total stock and latest inventory date and locations
    grp = df.groupby("ProductID").agg(
        total_stock=("StockLevel", "sum"),
        last_inventory_date=("Date", "max"),
        locations=("Location", lambda x: ",".join(sorted(x.dropna().unique())))
    ).reset_index()
    return grp


def clean_logistics(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.drop_duplicates()
    df.columns = [c.strip() for c in df.columns]
    # Try common date column names
    date_cols = [c for c in df.columns if "date" in c.lower()]
    if date_cols:
        df[date_cols[0]] = _normalize_dates(df[date_cols[0]])
        df = df.rename(columns={date_cols[0]: "ShipDate"})
    return df


def transform_logistics(df: pd.DataFrame) -> pd.DataFrame:
    # Simple KPIs: counts by status and overall totals
    df = df.copy()
    total = len(df)
    status_counts = df["Status"].fillna("Unknown").value_counts().to_dict()
    kpis = {
        "total_shipments": total,
    }
    for k, v in status_counts.items():
        key = f"status_{k.lower().replace(' ', '_')}"
        kpis[key] = int(v)
    # Percent delivered if present
    delivered = status_counts.get("Delivered", 0)
    kpis["percent_delivered"] = round(100 * delivered / total, 2) if total else 0.0
    return pd.DataFrame([kpis])


def load_df(df: pd.DataFrame, path: Path, index: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=index)


def run_pipeline(source_dir: Optional[Path] = None, output_dir: Optional[Path] = None) -> None:
    src = Path(source_dir) if source_dir else RAW_DIR
    out = Path(output_dir) if output_dir else PROCESSED_DIR

    # Sales
    sales_path = src / "sales_raw.csv"
    if sales_path.exists():
        print(f"Processing {sales_path}")
        sales = extract(sales_path)
        sales_clean = clean_sales(sales)
        fact_sales = transform_sales(sales_clean)
        load_df(fact_sales, out / "fact_sales.csv")
        print(f"Wrote {out / 'fact_sales.csv'}")
    else:
        print(f"Missing {sales_path}, skipping sales")

    # Inventory
    inv_path = src / "inventory_raw.csv"
    if inv_path.exists():
        print(f"Processing {inv_path}")
        inv = extract(inv_path)
        inv_clean = clean_inventory(inv)
        inv_summary = transform_inventory(inv_clean)
        load_df(inv_summary, out / "inventory_summary.csv")
        print(f"Wrote {out / 'inventory_summary.csv'}")
    else:
        print(f"Missing {inv_path}, skipping inventory")

    # Logistics
    log_path = src / "logistics_raw.csv"
    if log_path.exists():
        print(f"Processing {log_path}")
        log = extract(log_path)
        log_clean = clean_logistics(log)
        kpis = transform_logistics(log_clean)
        load_df(kpis, out / "logistics_kpi.csv", index=False)
        print(f"Wrote {out / 'logistics_kpi.csv'}")
    else:
        print(f"Missing {log_path}, skipping logistics")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run ETL pipeline to produce processed CSVs")
    parser.add_argument("--source_dir", help="Path to raw data directory", default=None)
    parser.add_argument("--output_dir", help="Path to processed output directory", default=None)
    args = parser.parse_args()
    run_pipeline(args.source_dir, args.output_dir)
