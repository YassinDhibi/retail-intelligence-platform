# Airflow Pipeline

## Purpose

The Airflow DAG orchestrates the local analytics workflow from cleaned source
data through marts and baseline model training.

## DAG

File:

```text
airflow/dags/retail_pipeline.py
```

DAG id:

```text
retail_intelligence_pipeline
```

## Tasks

| Task | Command | Purpose |
| --- | --- | --- |
| `clean_data` | `python src/transform.py` | Clean raw CSV files into `data/processed/` |
| `load_raw_tables` | `python src/load_to_postgres.py` | Load processed CSVs into `raw` schema |
| `refresh_staging` | `psql -f sql/02_create_staging_tables.sql` | Build typed staging tables |
| `refresh_warehouse` | `psql -f sql/03_create_warehouse_tables.sql` | Build star schema |
| `refresh_marts` | `psql -f sql/04_create_marts.sql` | Build business marts |
| `train_forecasting_model` | `python ml/train_forecasting_model.py` | Train and save baseline model |

## Dependencies

```text
clean_data
    -> load_raw_tables
    -> refresh_staging
    -> refresh_warehouse
    -> refresh_marts
    -> train_forecasting_model
```

## Environment Variables

The DAG reads the same PostgreSQL variables as the rest of the project:

```text
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

## Run Locally

Install Airflow in your local environment, then place or mount this repository
so Airflow can discover `airflow/dags/retail_pipeline.py`.

Start Airflow and trigger the DAG manually:

```powershell
airflow dags trigger retail_intelligence_pipeline
```

## Verification

The DAG file was syntax-checked locally. Full DAG execution requires an Airflow
environment with access to PostgreSQL, the local datasets, and the Python
dependencies in `requirements.txt`.
