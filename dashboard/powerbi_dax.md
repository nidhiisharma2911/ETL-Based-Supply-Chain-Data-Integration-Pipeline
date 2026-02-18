# Power BI DAX Measures

Copy & paste these DAX measures into your report (Modeling → New measure).

-- Basic KPIs
Total Sales =
SUM(fact_sales[Total])

Total Units =
SUM(fact_sales[Quantity])

Inventory On Hand =
SUM(inventory_summary[total_stock])

-- Average daily sales over last 30 days (requires Date table or Date column in fact_sales)
Avg Daily Sales (30d) =
VAR LastDate = MAX(fact_sales[Date])
VAR Units30 = CALCULATE([Total Units], DATESINPERIOD(fact_sales[Date], LastDate, -30, DAY))
RETURN DIVIDE(Units30, 30)

-- Days of Inventory
Days Of Inventory =
DIVIDE([Inventory On Hand], [Avg Daily Sales (30d)])

-- Percent Delivered (from logistics_kpi table)
Percent Delivered =
IF(HASONEVALUE(logistics_kpi[percent_delivered]), VALUES(logistics_kpi[percent_delivered]), AVERAGE(logistics_kpi[percent_delivered]))

-- Shipments Delivered (if status_delivered column exists)
Shipments Delivered =
IF(HASONEVALUE(logistics_kpi[status_delivered]), SUM(logistics_kpi[status_delivered]), SUM(logistics_kpi[status_delivered]))

-- Weekly Total Sales (requires calendar Date table or grouping by week)
Weekly Total Sales =
CALCULATE([Total Sales], DATESINPERIOD('Date'[Date], LASTDATE('Date'[Date]), -7, DAY))

-- 4-week moving average of weekly sales (example)
Sales_MA_4W =
VAR CurrentDate = LASTDATE('Date'[Date])
VAR Window = DATESINPERIOD('Date'[Date], CurrentDate, -28, DAY)
RETURN AVERAGEX(VALUES('Date'[Date]), CALCULATE([Total Sales], Window))

-- Notes:
- Replace `'Date'[Date]` with your Date table's column. If you don't have a Date table, create one and mark it as Date table (recommended).
- If `logistics_kpi` contains status columns (e.g., `status_delivered`), you can also build measures summing those columns directly.
