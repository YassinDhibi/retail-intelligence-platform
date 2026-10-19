# Docker Setup

## Purpose

Docker is used for local PostgreSQL and the FastAPI service. Airflow is
documented separately and kept out of Docker Compose to avoid making the local
portfolio setup unnecessarily heavy.

## Services

| Service | Purpose | Port |
| --- | --- | --- |
| `postgres` | PostgreSQL warehouse database | `5432` |
| `api` | FastAPI analytics and prediction service | `8000` |

## Files

| File | Purpose |
| --- | --- |
| `Dockerfile` | Builds the API image |
| `docker-compose.yml` | Runs PostgreSQL and API together |
| `.dockerignore` | Keeps local data, secrets, and large artifacts out of the image |

## Build And Run

Create `.env` from `.env.example`, then run:

```powershell
docker compose up --build
```

Open the API docs:

```text
http://127.0.0.1:8000/docs
```

## Database Initialization

The compose file starts PostgreSQL but does not automatically load local
datasets. After the database is running, execute the pipeline commands from the
host machine or from an environment with access to the data:

```powershell
python src/load_to_postgres.py
psql -h localhost -p 5432 -U postgres -d retail_warehouse -f sql/02_create_staging_tables.sql
psql -h localhost -p 5432 -U postgres -d retail_warehouse -f sql/03_create_warehouse_tables.sql
psql -h localhost -p 5432 -U postgres -d retail_warehouse -f sql/04_create_marts.sql
```

## Model Artifact

The API container mounts `./ml/models` into `/app/ml/models`. Train the model
locally first if you want `/predict-sales` to return predictions:

```powershell
python ml/train_forecasting_model.py
```

## Known Limitations

- Raw and processed datasets are intentionally excluded from Docker images.
- Airflow is not included in Compose; use the local DAG setup in
  `docs/airflow_pipeline.md`.
- The API depends on PostgreSQL marts being loaded before analytics endpoints
  return business data.
