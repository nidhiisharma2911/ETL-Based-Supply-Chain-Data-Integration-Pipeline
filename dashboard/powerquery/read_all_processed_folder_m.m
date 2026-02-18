/* Power Query M: Read all CSVs from a parameterized processed folder and combine them

Usage:
- Replace the `ProcessedFolder` value with your folder path, or create a Power BI parameter named `ProcessedFolder` and set it here.
- In Power BI: Home → Manage Parameters → New Parameter `ProcessedFolder` (Text). Then in Advanced Editor paste this script and replace the top `ProcessedFolder` assignment with `ProcessedFolder = ParameterName`.

This script:
- Lists CSV files in the folder
- Loads each CSV, promotes headers
- Adds a `SourceFile` column with the filename
- Attempts basic type parsing for common date/number columns
- Combines all tables into one consolidated table
*/
let
    // Set your folder path here (example):
    ProcessedFolder = "C:\\path\\to\\repo\\data\\processed\\",

    // Get files from folder
    Source = Folder.Files(ProcessedFolder),
    CSVFiles = Table.SelectRows(Source, each Text.Lower([Extension]) = ".csv"),

    // Function to load a single CSV file record
    LoadCsv = (fileRecord as record) =>
        let
            filePath = fileRecord[Folder Path] & fileRecord[Name],
            Binary = File.Contents(filePath),
            Csv = Csv.Document(Binary, [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
            TablePromoted = Table.PromoteHeaders(Csv, [PromoteAllScalars=true]),
            // Trim text columns
            Trimmed = Table.TransformColumns(TablePromoted, List.Transform(Table.ColumnNames(TablePromoted), each {_, Text.Trim, type text})),
            // Add SourceFile column
            WithSource = Table.AddColumn(Trimmed, "SourceFile", each fileRecord[Name], type text),
            // Attempt to coerce common date columns to date type
            Cols = Table.ColumnNames(WithSource),
            DateCols = List.Intersect({Cols, {"Date", "last_inventory_date", "ShipDate"}}),
            CoercedDates = List.Accumulate(DateCols, WithSource, (state, c) => Table.TransformColumnTypes(state, {{c, type nullable date}})),
            // Coerce numeric columns if present
            NumCols = List.Intersect({Cols, {"Quantity", "total_stock", "Price", "Total", "Count"}}),
            CoercedNums = List.Accumulate(NumCols, CoercedDates, (state, c) => Table.TransformColumnTypes(state, {{c, type number}}))
        in
            CoercedNums,

    // Load all CSVs into list of tables
    Loaded = Table.AddColumn(CSVFiles, "Table", each LoadCsv(_)),
    TablesList = List.Transform(Table.ToRecords(Loaded), each Record.Field(_, "Table")),

    // Combine tables; if none exist return empty table
    Combined = if List.Count(TablesList) > 0 then Table.Combine(TablesList) else #table({}, {})

in
    Combined
