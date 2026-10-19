# Project Plan

This plan keeps the project focused on a realistic junior data/backend engineering portfolio. The goal is to show repeatable work across Python, SQL, PostgreSQL, BI, and a small API surface without overstating production readiness.

## Completed Foundation

- Repository structure for source code, SQL, docs, dashboards, notebooks, and screenshots.
- Python cleaning pipeline for Online Retail and Walmart datasets.
- Local data policy that keeps raw and processed datasets out of Git.
- PostgreSQL loader for processed CSV files.
- Staging SQL models with typed columns and documented cleaning rules.
- Warehouse, mart, and KPI SQL scripts.
- FastAPI endpoints for selected warehouse metrics.
- Baseline Walmart weekly sales forecasting scripts.
- Docker Compose service for local PostgreSQL.
- Optional Airflow DAG for pipeline orchestration.

## Next Improvements

### 1. Data Quality Checks

- Add row-count checks after each stage.
- Add null and duplicate checks for business keys.
- Store pipeline run metadata in PostgreSQL.

### 2. Power BI Dashboard

- Connect Power BI to the `marts` schema.
- Build pages for sales overview, product performance, store performance, and forecasting.
- Add screenshots to `screenshots/`.

### 3. Modeling Notes

- Compare the baseline model with a simpler benchmark.
- Document features, target variable, train/test split, and model limitations.
- Add a short interpretation of the most important drivers.

### 4. API Hardening

- Add request validation for filters.
- Add pagination for list endpoints.
- Add tests around database query helpers.

### 5. Portfolio Polish

- Add a compact architecture diagram.
- Add final dashboard screenshots.
- Add a short project walkthrough that explains engineering decisions.
