# dbt Analytics Engineering Layer

## Purpose

The dbt project in `dbt/retail_analytics/` adds an analytics-engineering layer
for documentation, tests, and repeatable mart validation.

This project intentionally uses a hybrid approach:

- The verified PostgreSQL SQL scripts remain the source of truth for raw,
  staging, warehouse, and mart creation.
- dbt reads those verified objects as sources and materializes dbt-managed
  copies into `dbt_staging`, `dbt_warehouse`, and `dbt_marts`.
- dbt tests validate important keys, accepted values, and non-null metrics
  without replacing the manually reviewed SQL models.

This avoids destructive changes while still demonstrating dbt structure,
documentation, and testing.

## Project Structure

```text
dbt/retail_analytics/
|-- dbt_project.yml
|-- profiles.yml.example
|-- macros/
|   `-- generate_schema_name.sql
`-- models/
    |-- sources.yml
    |-- staging/
    |-- warehouse/
    `-- marts/
```

## Setup

Install dbt dependencies:

```powershell
pip install dbt-core dbt-postgres
```

Create a dbt profile from the included example:

```powershell
copy dbt\retail_analytics\profiles.yml.example %USERPROFILE%\.dbt\profiles.yml
```

The profile reads the same environment variables as the rest of the project:

```text
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

## Commands

Run from `dbt/retail_analytics/`:

```powershell
dbt debug
dbt run
dbt test
dbt docs generate
dbt docs serve
```

## Models Created

Staging wrappers:

- `stg_online_retail_transactions`
- `stg_walmart_sales`
- `stg_walmart_stores`
- `stg_walmart_features`

Warehouse wrappers:

- `dim_date`
- `dim_product`
- `dim_customer`
- `dim_store`
- `fact_sales`

Mart wrappers:

- `sales_overview`
- `product_performance`
- `customer_performance`
- `store_performance`
- `forecasting_base`

## Tests Added

- `not_null` tests for primary keys and important metrics.
- `unique` tests for dimension and mart keys where the grain is one row per key.
- `accepted_values` tests for source systems, dataset splits, store types, and
  customer segments.

## Verification

The dbt files were added and their SQL/YAML structure was checked locally. The
live `dbt run` and `dbt test` commands require `dbt-core` and `dbt-postgres` to
be installed in the active Python environment.
