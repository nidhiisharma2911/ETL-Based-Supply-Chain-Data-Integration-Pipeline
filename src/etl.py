"""Minimal ETL entrypoint and helpers."""
from pathlib import Path
from typing import Optional

import pandas as pd


def extract(path: Path) -> pd.DataFrame:
    """Extract data from a CSV file at `path`.

    This is a placeholder extractor; replace with DB/API reads as needed.
    """
    return pd.read_csv(path)


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Basic transformation: trim string columns and drop fully-empty rows."""
    str_cols = df.select_dtypes(include=["object"]).columns
    for c in str_cols:
        df[c] = df[c].astype(str).str.strip()
    df = df.dropna(how="all")
    return df


def load(df: pd.DataFrame, out_path: Path) -> None:
    """Load dataframe to parquet at `out_path`."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_path, index=False)


def run_pipeline(source: Optional[str], target: Optional[str]) -> None:
    source = source or "data/sample_input.csv"
    target = target or "outputs/processed.parquet"
    src = Path(source)
    tgt = Path(target)

    print(f"Extracting from {src}")
    df = extract(src)
    print(f"Transforming ({len(df)} rows)")
    df = transform(df)
    print(f"Loading to {tgt}")
    load(df, tgt)
    print("ETL complete")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run basic ETL pipeline")
    parser.add_argument("--source", help="Path to source CSV", default=None)
    parser.add_argument("--target", help="Path to output parquet", default=None)
    args = parser.parse_args()
    run_pipeline(args.source, args.target)
