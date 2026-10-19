# Data Dictionary

This document describes the main cleaned fields used by the Retail Intelligence Platform. Raw datasets are stored locally and are not committed to GitHub.

## Online Retail

Grain: one invoice line per product/customer transaction.

| Column | Type | Description | Cleaning Notes |
| --- | --- | --- | --- |
| `invoice_no` | string | Transaction invoice number | Cancelled invoices removed |
| `stock_code` | string | Product identifier | Required field |
| `description` | string | Product description | Trimmed and standardized |
| `quantity` | integer | Units purchased | Must be positive |
| `invoice_date` | datetime | Transaction timestamp | Parsed to datetime |
| `unit_price` | numeric | Unit selling price | Must be positive |
| `customer_id` | integer | Customer identifier | Missing customers removed |
| `country` | string | Customer country | Required field |
| `total_sales` | numeric | `quantity * unit_price` | Derived during cleaning |

## Walmart Sales

Grain: one weekly sales observation by store, department, and date.

| Column | Type | Description | Cleaning Notes |
| --- | --- | --- | --- |
| `store` | integer | Store identifier | Must be positive |
| `dept` | integer | Department identifier | Must be positive |
| `date` | date | Weekly sales date | Parsed to date |
| `weekly_sales` | numeric | Weekly department sales | Negative training values removed |
| `isholiday` | boolean | Holiday week flag | Standardized to boolean |

## Walmart Stores

Grain: one row per store.

| Column | Type | Description | Cleaning Notes |
| --- | --- | --- | --- |
| `store` | integer | Store identifier | Must be positive |
| `type` | string | Store type category | Kept as `A`, `B`, or `C` |
| `size` | integer | Store size | Must be positive |

## Walmart Features

Grain: one row per store and date.

| Column | Type | Description | Cleaning Notes |
| --- | --- | --- | --- |
| `store` | integer | Store identifier | Must be positive |
| `date` | date | Feature date | Parsed to date |
| `temperature` | numeric | Local temperature value | Cast to numeric |
| `fuel_price` | numeric | Fuel price value | Must be positive |
| `markdown1`-`markdown5` | numeric | Markdown promotion features | Missing values filled with `0` |
| `cpi` | numeric | Consumer price index | Forward/backward filled by store |
| `unemployment` | numeric | Unemployment rate | Forward/backward filled by store |
| `isholiday` | boolean | Holiday week flag | Standardized to boolean |

## Warehouse Entities

| Table | Purpose |
| --- | --- |
| `warehouse.dim_date` | Calendar attributes for reporting and time-series analysis |
| `warehouse.dim_product` | Product and department descriptors |
| `warehouse.dim_customer` | Customer and geography fields where available |
| `warehouse.dim_store` | Store-level attributes for Walmart analysis |
| `warehouse.fact_sales` | Central sales fact table for BI, API, and analytics |

## Marts

| View | Purpose |
| --- | --- |
| `marts.sales_overview` | Monthly sales summary by source |
| `marts.product_performance` | Product and department contribution |
| `marts.customer_performance` | Customer and country-level performance |
| `marts.store_performance` | Store-level sales analysis |
| `marts.forecasting_features` | Walmart feature table for modeling |
