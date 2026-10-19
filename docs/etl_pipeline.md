# ETL Pipeline: Cleaned CSVs to PostgreSQL

## Purpose

This ETL pipeline loads locally cleaned CSV files into PostgreSQL so the project can move from file-based analysis into a structured warehouse workflow.

The current implementation focuses on the first database landing layer: the `raw` schema.

## Flow

```text
data/processed/*.csv
        |
        v
pandas DataFrame
        |
        v
SQLAlchemy engine
        |
        v
PostgreSQL raw schema
```

## Source

The loader automatically detects CSV files in:

```text
data/processed/
```

Each CSV file is loaded into PostgreSQL using a table name derived from the file name.

Examples:

- `online_retail_clean.csv` -> `raw.online_retail_clean`
- `walmart_train_clean.csv` -> `raw.walmart_train_clean`
- `walmart_train_model_ready.csv` -> `raw.walmart_train_model_ready`

## Target Layer

The `raw` schema is the database landing zone for cleaned but source-aligned data.

This layer is intentionally simple:

- One table per CSV file.
- Table names are generated from CSV filenames.
- Tables are replaced on each run with `if_exists="replace"`.
- No business aggregation is applied during loading.

## Configuration

Database credentials are loaded from environment variables.

Create a local `.env` file using `.env.example` as a template:

```text
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=retail_warehouse
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
```

The `.env` file must stay local and should not be committed to GitHub.

## Run Commands

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the loader:

```bash
python src/load_to_postgres.py
```

## Operational Notes

- The loader creates the `raw` schema if it does not already exist.
- The script uses clear logging for discovery, loading, row counts, and failures.
- Failed file loads raise an error so the pipeline does not silently hide data problems.
- When pandas or SQLAlchemy are not installed, the loader falls back to PostgreSQL
  `psql` and `COPY` with normalized text columns.
- This phase is designed for development. Later phases can add incremental loads,
  audit columns, and persisted data quality checks.

## Verified Raw Load

Verified on 2026-06-18 against the local PostgreSQL database
`retail_warehouse`.

| Raw table | Row count |
| --- | ---: |
| `raw.online_retail_clean` | 392,692 |
| `raw.walmart_features_clean` | 8,190 |
| `raw.walmart_stores_clean` | 45 |
| `raw.walmart_test_clean` | 115,064 |
| `raw.walmart_test_model_ready` | 115,064 |
| `raw.walmart_train_clean` | 420,285 |
| `raw.walmart_train_model_ready` | 420,285 |

No load warnings were observed beyond the expected fallback to `psql` because
the local virtual environment did not include optional pandas and SQLAlchemy
dependencies at verification time.
