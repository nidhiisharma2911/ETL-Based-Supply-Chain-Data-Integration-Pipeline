/* Power Query M: Unpivot logistics status_* columns for Delivery Delays visual
   Replace the File.Contents path with your local CSV path or parameterize it in Power BI. */
let
    Source = Csv.Document(File.Contents("C:\\path\\to\\repo\\data\\processed\\logistics_kpi.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    // Trim whitespace from all text columns
    Trimmed = Table.TransformColumns(PromotedHeaders, List.Transform(Table.ColumnNames(PromotedHeaders), each {_, Text.Trim, type text})),
    Cols = Table.ColumnNames(Trimmed),
    // Identify status_ columns
    StatusCols = List.Select(Cols, each Text.StartsWith(_, "status_")),
    // If no status columns exist, return the table with percent_delivered typed if present
    ConvertStatusOrReturn = if List.Count(StatusCols) = 0 then
        (if List.Contains(Cols, "percent_delivered") then Table.TransformColumnTypes(Trimmed, {{"percent_delivered", type number}}) else Trimmed)
    else
        let
            // Convert status cols to integers
            Converted = List.Accumulate(StatusCols, Trimmed, (state, current) => Table.TransformColumnTypes(state, {{current, Int64.Type}})),
            // Columns to keep as-is when unpivoting
            OtherCols = List.RemoveItems(Cols, StatusCols),
            // Unpivot status columns into rows: Status, Count
            Unpivoted = Table.UnpivotOtherColumns(Converted, OtherCols, "Status", "Count"),
            // Clean status names: remove prefix
            StatusClean = Table.TransformColumns(Unpivoted, {{"Status", each Text.Replace(_, "status_", ""), type text}}),
            // Ensure Count is numeric and percent_delivered is numeric if present
            Typed = if List.Contains(Cols, "percent_delivered") then Table.TransformColumnTypes(StatusClean, {{"Count", Int64.Type}, {"percent_delivered", type number}}) else Table.TransformColumnTypes(StatusClean, {{"Count", Int64.Type}})
        in
            Typed,
    Result = ConvertStatusOrReturn
in
    Result
