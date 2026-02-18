# ETL-Based Supply Chain Data Integration Pipeline

This repository contains a sample ETL pipeline for supply-chain data (sales,
inventory, logistics). It includes extraction, cleaning, transformation,
loading into CSV and SQLite, a Streamlit monitoring dashboard, unit tests,
and GitHub Actions workflows for validation and automated release.

**Status**
- **Tests**: 4 passed (pytest)
- **Release**: `etl_submission.zip` uploaded to GitHub Releases

## Quickstart

1. Create a Python environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the ETL pipeline (reads `data/raw/`, writes `data/processed/`):

```bash
python -m src.etl_pipeline run --source data/raw --output data/processed
```

3. Load processed CSVs into the supplied SQLite DB:

```bash
python src/load_to_sqlite.py --processed-dir data/processed --db supply_chain.db
```

4. Run unit tests:

```bash
pytest
```

5. Start the Streamlit monitoring app:

```bash
streamlit run dashboard/app.py
```

## Repository layout

- `data/raw/` — sample raw CSVs
- `data/processed/` — ETL outputs (`fact_sales.csv`, `inventory_summary.csv`, `logistics_kpi.csv`)
- `src/` — ETL implementation and loader (`src/etl_pipeline.py`, `src/load_to_sqlite.py`, `src/etl.py`)
- `dashboard/` — Streamlit app and Power BI specs + Power Query M / DAX snippets
- `tests/` — pytest tests
- `.github/workflows/` — CI, scheduled ETL, release automation

## CI / Releases

- Validation workflow runs `flake8` + `pytest` and uploads coverage.
- A release workflow creates a zip and uploads `etl_submission.zip` as a release asset when `.github/release-trigger` is pushed.

## Notes & Next Steps

- Branch protection automation requires an admin PAT if you want programmatic enforcement.
- Outbound uploads (e.g., transfer.sh) are blocked from the runner environment; releases are produced via GitHub Releases.

If you'd like, I can:
- Add a short `CONTRIBUTING.md` and `CHANGELOG.md`.
- Remove the release trigger after you're done.
