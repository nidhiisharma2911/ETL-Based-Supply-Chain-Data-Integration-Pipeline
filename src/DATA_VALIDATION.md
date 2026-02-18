# Data Validation & Cleaning Rules

This document outlines the data quality checks and cleaning transformations applied by the ETL pipeline (`src/etl_pipeline.py`).

## Raw Data Issues Detected

The raw CSVs under `data/raw/` contain:
- **Missing values**: empty fields in Quantity, Price, Date, StockLevel, ShipDate
- **Duplicates**: exact row duplicates (e.g., SaleID 1004, InventoryID I103, ShipmentID S503)
- **Inconsistent date formats**: "2024-01-05", "01/06/2024", "2024.01.07", "Jan 8 2024", "11-01-2024"
- **Invalid dates**: "2024-13-01" (month 13), "2024/02/30" (day 30 in February)
- **Inconsistent delimiters**: "/" vs "-" vs "." in dates
- **Type mismatches**: text in numeric fields, blank numeric values

## Cleaning Transformations

### Sales (fact_sales.csv)
1. **Remove duplicates**: drop_duplicates() by all columns
2. **Parse dates**: normalize date strings to YYYY-MM-DD format
   - Try ISO parse first: `2024-01-05` → date
   - Fallback to dayfirst=True: `11-01-2024` → 2024-01-11 (if day-first locale)
   - Coerce failures to NaT (NaT = missing)
3. **Numeric fill**: replace missing Quantity and Price with 0
4. **Type conversion**: 
   - SaleID, CustomerID, ProductID → text
   - Quantity → integer
   - Price, Total → decimal
5. **Derived column**: Total = Quantity × Price (recalculated to ensure consistency)

### Inventory (inventory_summary.csv)
1. **Remove duplicates**: drop_duplicates() 
2. **Parse dates**: same as sales (normalize and dayfirst fallback)
3. **Numeric fill**: missing StockLevel → 0
4. **Type conversion**:
   - ProductID → text
   - total_stock → integer
   - locations → text (comma-separated warehouse codes)
5. **Aggregation**: group by ProductID
   - SUM(StockLevel) → total_stock
   - MAX(Date) → last_inventory_date
   - Unique locations → comma-separated string

### Logistics (logistics_kpi.csv)
1. **Remove duplicates**: drop_duplicates()
2. **Parse dates**: normalize ShipDate (same fallback logic)
3. **Type conversion**: status columns → integer (count of shipments)
4. **KPI calculation**:
   - total_shipments = SUM all status counts
   - percent_delivered = (status_delivered / total_shipments) × 100
   - Other statuses: in_transit, shipped, delayed, cancelled, unknown

## Data Quality Metrics

**Sample run metrics** (from `data/raw/` → `data/processed/`):
- Sales: 11 raw rows → 10 rows (1 duplicate removed)
- Inventory: 10 raw rows → 9 rows (1 duplicate removed)
- Logistics: 9 raw rows → 1 KPI row (aggregated)

**Missing value handling**:
- Date fields: coerced to NaT (null) if parse fails
- Numeric fields: filled with 0
- Character fields: trimmed of whitespace

## Validation Checks

Post-load validation performed:
- ✓ No duplicate SaleIDs (if duplicates exist, log warning)
- ✓ Date fields are valid dates (no month > 12 or day > 31)
- ✓ Numeric fields are in valid range (Quantity ≥ 0, Price ≥ 0)
- ✓ ProductID consistency across fact_sales and inventory_summary
- ✓ Status counts sum to total_shipments in logistics_kpi

## Configuration & Tuning

To adjust cleaning behavior, edit `src/etl_pipeline.py`:
- Line ~30: Date parsing logic — modify `_normalize_dates()` for different locale/format rules
- Line ~50+: Filling missing values — change `.fillna(0)` to alternative value
- Line ~100+: Aggregation logic — edit groupby keys or aggregation functions

## Testing & Debugging

Run the pipeline with verbose output:
```bash
python3 src/etl_pipeline.py --source_dir data/raw --output_dir data/processed
```

To inspect intermediate stages, add print statements or debug code in `clean_sales()`, `transform_sales()`, etc.

## Known Limitations

- **Date ambiguity**: Formats like "11-01-2024" are ambiguous (Nov 1 vs Jan 11). The dayfirst=True heuristic may not match your locale.
- **Timezone**: No timezone handling; all dates are treated as date-only (no time component).
- **Validation only**: The pipeline does not reject invalid rows; missing/invalid values are coerced. If stricter validation is needed, add a filter step.

## Future Enhancements

- Add configurable data quality thresholds before/after transformations
- Generate data quality reports (null %, duplicates %, out-of-range values)
- Implement row-level lineage tracking (which raw row produced which output row)
- Add schema enforcement (validate column names, types at load time)
