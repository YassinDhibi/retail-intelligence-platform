# Project Summary

Retail Intelligence Platform is a complete analytics portfolio project that
demonstrates how to move from local CSV datasets to a modeled warehouse,
business marts, an API, a forecasting workflow, and BI-ready documentation.

## What It Demonstrates

- Python data cleaning and loading.
- PostgreSQL raw, staging, warehouse, and marts schemas.
- Source-aware dimensional modeling.
- dbt project structure, documentation, and tests.
- FastAPI service for analytics and prediction endpoints.
- Baseline machine learning workflow.
- Airflow orchestration.
- Dockerized PostgreSQL and API services.
- Power BI dashboard specification with DAX measures.

## Current Verified State

- Raw tables loaded into PostgreSQL.
- Staging tables rebuilt successfully.
- Warehouse star schema rebuilt successfully.
- Business marts rebuilt successfully.
- Python syntax checks pass for project scripts.
- Docker Compose configuration validates.

## Best Portfolio Talking Point

The strongest part of the project is the realistic warehouse design: it combines
two retail datasets without forcing fake joins, keeps source lineage explicit,
and exposes clean marts for downstream BI, API, and ML use cases.
