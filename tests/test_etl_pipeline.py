import sys
from pathlib import Path
import pandas as pd
import pytest

# Ensure repo root is on sys.path so `src` package imports work in CI
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import etl_pipeline as etl


def test_clean_sales_dedup_and_types():
    df = pd.DataFrame({
        "SaleID": ["s1", "s1"],
        "Date": ["2024-01-01", "2024-01-01"],
        "CustomerID": ["c1", "c1"],
        "ProductID": ["p1", "p1"],
        "Quantity": ["1", "1"],
        "Price": ["10.0", "10.0"],
    })

    cleaned = etl.clean_sales(df)
    # duplicate removed
    assert len(cleaned) == 1
    # types
    assert cleaned["Quantity"].dtype == int
    assert cleaned["Price"].dtype == float


def test_transform_sales_total_calc():
    df = pd.DataFrame({"SaleID": ["s2"], "Date": ["2024-01-02"], "CustomerID": ["c2"], "ProductID": ["p2"], "Quantity": [2], "Price": [5.0]})
    transformed = etl.transform_sales(df)
    assert "Total" in transformed.columns
    assert transformed.iloc[0]["Total"] == 10.0


def test_inventory_transform_aggregation():
    df = pd.DataFrame({
        "InventoryID": ["i1", "i2"],
        "Date": ["2024-01-01", "2024-01-02"],
        "ProductID": ["pA", "pA"],
        "Location": ["WH1", "WH2"],
        "StockLevel": [10, 5],
    })
    cleaned = etl.clean_inventory(df)
    summary = etl.transform_inventory(cleaned)
    assert len(summary) == 1
    assert summary.iloc[0]["total_stock"] == 15
    assert "WH1" in summary.iloc[0]["locations"]


def test_logistics_kpi_counts_and_percent():
    df = pd.DataFrame({
        "ShipmentID": ["sh1", "sh2", "sh3"],
        "ShipDate": ["2024-01-01", "2024-01-02", "2024-01-03"],
        "Origin": ["A", "B", "C"],
        "Destination": ["D", "E", "F"],
        "Status": ["Delivered", "In Transit", "Delivered"],
    })
    cleaned = etl.clean_logistics(df)
    kpi = etl.transform_logistics(cleaned)
    assert int(kpi.iloc[0]["total_shipments"]) == 3
    # percent_delivered should be 66.67 or similar
    assert pytest.approx(float(kpi.iloc[0]["percent_delivered"]), rel=1e-2) == 100.0 * 2 / 3
