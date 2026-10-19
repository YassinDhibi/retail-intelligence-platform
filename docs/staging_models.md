# PostgreSQL Staging Models

## Purpose

The staging layer transforms raw text-loaded CSV tables into typed, business-ready PostgreSQL tables. These models prepare the data for future warehouse dimensions, fact tables, marts, Power BI reporting, and machine learning workflows.

The staging layer does not create final warehouse tables. It keeps source-specific entities clean, typed, and ready for dimensional modeling.

Run all staging models from the repository root:

```powershell
psql -h localhost -p 5432 -U postgres -d retail_warehouse -f sql/02_create_staging_tables.sql
```

## Verified Row Counts

Verified on 2026-06-18 after loading the cleaned CSV files into the `raw`
schema.

| Staging table | Row count |
| --- | ---: |
| `staging.stg_online_retail_transactions` | 392,692 |
| `staging.stg_walmart_sales` | 535,349 |
| `staging.stg_walmart_features` | 8,190 |
| `staging.stg_walmart_stores` | 45 |

## Flow

```text
raw tables
    |
    v
staging SQL transformations
    |
    v
staging tables
```

## Models

### `staging.stg_online_retail_transactions`

Source raw table:

- `raw.online_retail_clean`

Purpose:

- Creates a clean invoice-line transaction table from the Online Retail dataset.
- Provides typed transaction fields for future sales facts and product/customer dimensions.

Main columns:

- `transaction_line_id`
- `invoice_no`
- `stock_code`
- `product_description`
- `quantity`
- `invoice_timestamp`
- `invoice_date`
- `unit_price`
- `customer_id`
- `country`
- `sales_amount`
- `source_total_sales`
- `source_system`

Cleaning rules applied:

- Removes rows with missing required transaction identifiers.
- Casts `quantity` to integer.
- Casts `invoice_date` to timestamp and date fields.
- Casts `unit_price` and sales values to numeric.
- Keeps only positive quantities and unit prices.
- Recalculates `sales_amount` from `quantity * unit_price`.
- Adds a stable transaction-line hash key from all cleaned invoice-line attributes so repeated product purchases remain distinct.

### `staging.stg_walmart_sales`

Source raw tables:

- `raw.walmart_train_clean`
- `raw.walmart_test_clean`

Purpose:

- Creates a clean weekly Walmart sales observation table.
- Preserves both training and test observations with a `dataset_split` column.
- Keeps `weekly_sales_amount` nullable for test records because test data does not include the target value.

Main columns:

- `walmart_sales_id`
- `dataset_split`
- `store_id`
- `department_id`
- `sales_date`
- `weekly_sales_amount`
- `is_holiday`
- `source_system`

Cleaning rules applied:

- Casts store and department identifiers to integers.
- Casts sales date to date.
- Casts weekly sales to numeric for training rows.
- Casts holiday flags to boolean.
- Removes invalid store or department identifiers.
- Removes negative weekly sales from training data.
- Adds a stable sales observation hash key.

### `staging.stg_walmart_stores`

Source raw table:

- `raw.walmart_stores_clean`

Purpose:

- Creates a typed store reference table for Walmart store-level analysis.
- Provides clean store attributes for future `dim_store` modeling.

Main columns:

- `store_id`
- `store_type`
- `store_size`
- `source_system`

Cleaning rules applied:

- Casts store identifiers to integers.
- Standardizes store type to uppercase.
- Keeps valid store types `A`, `B`, and `C`.
- Casts store size to integer.
- Removes invalid or non-positive store sizes.

### `staging.stg_walmart_features`

Source raw table:

- `raw.walmart_features_clean`

Purpose:

- Creates a typed weekly feature table for Walmart stores.
- Provides clean exogenous variables for analysis and future forecasting features.

Main columns:

- `walmart_feature_id`
- `store_id`
- `feature_date`
- `temperature`
- `fuel_price`
- `markdown_1`
- `markdown_2`
- `markdown_3`
- `markdown_4`
- `markdown_5`
- `cpi`
- `unemployment_rate`
- `is_holiday`
- `source_system`

Cleaning rules applied:

- Casts store identifiers to integers.
- Casts feature date to date.
- Casts temperature, fuel price, markdowns, CPI, and unemployment to numeric values.
- Replaces missing markdown values with `0`.
- Floors markdown values at `0`.
- Casts holiday flags to boolean.
- Removes invalid fuel price, CPI, and unemployment values.

## Run Commands

From the repository root:

```powershell
$env:PGPASSWORD="your_password"
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -h localhost -p 5432 -U postgres -d retail_warehouse -f sql\02_create_staging_tables.sql
Remove-Item Env:PGPASSWORD
```

Verification:

```powershell
$env:PGPASSWORD="your_password"
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -h localhost -p 5432 -U postgres -d retail_warehouse -c "SELECT schemaname, tablename FROM pg_tables WHERE schemaname = 'staging' ORDER BY tablename;"
Remove-Item Env:PGPASSWORD
```
