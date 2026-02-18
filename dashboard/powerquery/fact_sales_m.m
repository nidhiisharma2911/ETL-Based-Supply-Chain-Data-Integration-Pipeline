/* Power Query M: fact_sales.csv
   Replace the File.Contents path with the path to your local repo CSV (or use Parameter). */
let
    Source = Csv.Document(File.Contents("C:\\path\\to\\repo\\data\\processed\\fact_sales.csv"),[Delimiter="," , Columns=7, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    TrimmedText = Table.TransformColumns(PromotedHeaders, List.Transform(Table.ColumnNames(PromotedHeaders), each {_, Text.Trim, type text})),
    RemovedDuplicates = Table.Distinct(TrimmedText, {"SaleID"}),
    ReplacedNulls = Table.ReplaceValue(RemovedDuplicates,null, "",Replacer.ReplaceValue, Table.ColumnNames(RemovedDuplicates)),
    ChangedTypes = Table.TransformColumnTypes(ReplacedNulls,
        {
            {"SaleID", type text},
            {"Date", type text},
            {"CustomerID", type text},
            {"ProductID", type text},
            {"Quantity", Int64.Type},
            {"Price", type number},
            {"Total", type number}
        }, "en-US"),
    // Parse Date robustly using try/otherwise fallbacks
    ParseDate = Table.TransformColumns(ChangedTypes, {"Date", each try Date.FromText(_) otherwise try Date.From(DateTime.FromText(_)) otherwise null, type nullable date}),
    // Ensure numeric nulls become zeros where appropriate
    FillNums = Table.TransformColumns(ParseDate, {"Quantity", each if _ = null then 0 else _, Int64.Type}, {"Price", each if _ = null then 0.0 else _, type number}),
    // Add Total if missing or recalc to ensure correctness
    HasTotal = List.Contains(Table.ColumnNames(FillNums), "Total"),
    EnsureTotal = if HasTotal then Table.TransformColumns(FillNums,{"Total", each if _ = null then Number.From([Quantity])*Number.From([Price]) else _, type number}) else Table.AddColumn(FillNums, "Total", each Number.From([Quantity])*Number.From([Price]), type number)
in
    EnsureTotal
