/* Power Query M: inventory_summary.csv
   Replace File.Contents path with your local CSV path or parameterize. */
let
    Source = Csv.Document(File.Contents("C:\\path\\to\\repo\\data\\processed\\inventory_summary.csv"),[Delimiter="," , Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Trimmed = Table.TransformColumns(Promoted, List.Transform(Table.ColumnNames(Promoted), each {_, Text.Trim, type text})),
    RemovedDuplicates = Table.Distinct(Trimmed),
    ChangedTypes = Table.TransformColumnTypes(RemovedDuplicates,
        {
            {"ProductID", type text},
            {"total_stock", Int64.Type},
            {"last_inventory_date", type text},
            {"locations", type text}
        }, "en-US"),
    ParsedDate = Table.TransformColumns(ChangedTypes, {"last_inventory_date", each try Date.FromText(_) otherwise try Date.From(DateTime.FromText(_)) otherwise null, type nullable date})
in
    ParsedDate
