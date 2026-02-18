"""Load processed CSVs into a SQLite database `supply_chain.db`.

Reads files from `data/processed/` and writes them as tables:
- fact_sales.csv -> fact_sales
- inventory_summary.csv -> inventory_summary
- logistics_kpi.csv -> logistics_kpi
"""
from pathlib import Path
import sys

import pandas as pd
from sqlalchemy import create_engine


ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"
DB_PATH = ROOT / "supply_chain.db"


def load_table(csv_path: Path, table_name: str, engine) -> None:
    print(f"Loading {csv_path} -> {table_name}")
    df = pd.read_csv(csv_path)
    df.to_sql(table_name, engine, if_exists="replace", index=False)


def main():
    if not PROCESSED_DIR.exists():
        print(f"Processed directory not found: {PROCESSED_DIR}")
        sys.exit(1)

    engine = create_engine(f"sqlite:///{DB_PATH}")

    files = {
        "fact_sales.csv": "fact_sales",
        "inventory_summary.csv": "inventory_summary",
        "logistics_kpi.csv": "logistics_kpi",
    }

    for fname, table in files.items():
        path = PROCESSED_DIR / fname
        if path.exists():
            load_table(path, table, engine)
        else:
            print(f"Warning: {path} not found, skipping {table}")

    print(f"Database created at {DB_PATH}")


if __name__ == "__main__":
    main()
