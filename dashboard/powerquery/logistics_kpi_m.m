/* Power Query M: logistics_kpi.csv
   Loads KPI CSV, coerces status_* columns to numbers and percent_delivered to number.
   Replace the File.Contents path with your local CSV path. */
let
    Source = Csv.Document(File.Contents("C:\\path\\to\\repo\\data\\processed\\logistics_kpi.csv"),[Delimiter="," , Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Trimmed = Table.TransformColumns(Promoted, List.Transform(Table.ColumnNames(Promoted), each {_, Text.Trim, type text})),
    // Detect status columns dynamically
    Cols = Table.ColumnNames(Trimmed),
    StatusCols = List.Select(Cols, each Text.StartsWith(_, "status_")),
    // Convert status cols to number
    ConvertStatus = List.Accumulate(StatusCols, Trimmed, (state, current) => Table.TransformColumnTypes(state, {{current, Int64.Type}})),
    // Convert percent_delivered if present
    Final = if List.Contains(Cols, "percent_delivered") then Table.TransformColumnTypes(ConvertStatus, {{"percent_delivered", type number}}) else ConvertStatus
in
    Final
