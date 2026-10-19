# PostgreSQL Warehouse Models

## Purpose

The warehouse layer builds a readable retail star schema from verified staging
tables. It supports reusable analytics without forcing the Online Retail and
Walmart datasets into relationships that the source data cannot support.

Run the warehouse build from the repository root:

```powershell
psql -h localhost -p 5432 -U postgres -d retail_warehouse -f sql/03_create_warehouse_tables.sql
```

## Verified Row Counts

Verified on 2026-06-18 after rebuilding the warehouse from the staging layer.

| Warehouse table | Row count |
| --- | ---: |
| `warehouse.dim_date` | 1,268 |
| `warehouse.dim_product` | 3,746 |
| `warehouse.dim_customer` | 4,347 |
| `warehouse.dim_store` | 46 |
| `warehouse.fact_sales` | 812,977 |

## Model Overview

```text
warehouse.dim_date
        |
warehouse.dim_product -- warehouse.fact_sales -- warehouse.dim_customer
        |
warehouse.dim_store
```

### `warehouse.dim_date`

Purpose:

- Provides a shared continuous calendar for reporting and time-series analysis.

Source staging tables:

- `staging.stg_online_retail_transactions`
- `staging.stg_walmart_sales`
- `staging.stg_walmart_features`

Key columns:

- `date_key`: primary key in `YYYYMMDD` integer format.
- `date`: unique calendar date.
- `week_of_year`, `month`, `quarter`, `year`: reporting attributes.
- `is_weekend`: calendar weekend flag.

Business use:

- Daily, weekly, monthly, quarterly, and yearly sales trends.
- Seasonality analysis and filtering.

### `warehouse.dim_product`

Purpose:

- Provides a source-aware product dimension for online SKUs and Walmart
  departments.

Source staging tables:

- `staging.stg_online_retail_transactions`
- `staging.stg_walmart_sales`

Key columns:

- `product_key`: surrogate primary key.
- `product_code`: source product code or Walmart department identifier.
- `product_name`: canonical product description or generated department label.
- `department_id`: populated for Walmart department-level records.
- `product_level`: identifies `product` or `department` grain.
- `source_system`: prevents accidental cross-source joins.

Business use:

- Product performance, department performance, and product-mix analysis.

Notes:

- Some Online Retail stock codes have multiple observed descriptions. The model
  selects the most frequently observed description, with alphabetical ordering
  as a deterministic tie-breaker.
- Walmart data does not contain SKU-level product detail. Its fact records join
  to department-level dimension rows.

### `warehouse.dim_customer`

Purpose:

- Provides customer profiles where the source contains customer-level data.

Source staging tables:

- `staging.stg_online_retail_transactions`

Key columns:

- `customer_key`: surrogate primary key.
- `customer_id`: Online Retail customer identifier where available.
- `customer_reference`: source-safe join reference.
- `country`: observed customer transaction country.
- `is_unknown`: indicates a controlled fallback member.
- `source_system`: prevents accidental cross-source joins.

Business use:

- Customer sales, repeat purchase, and geography analysis for Online Retail.

Notes:

- A small number of Online Retail customers appear in more than one country.
  The dimension therefore uses one customer-country profile per source.
- Walmart weekly sales do not include customer identifiers. Walmart fact rows
  join to one controlled unknown customer record.

### `warehouse.dim_store`

Purpose:

- Provides physical-store attributes where available and a controlled channel
  record where physical store detail is absent.

Source staging tables:

- `staging.stg_walmart_stores`

Key columns:

- `store_key`: surrogate primary key.
- `store_id`: Walmart store identifier where available.
- `store_reference`: source-safe store or channel reference.
- `store_type`, `store_size`: Walmart store attributes.
- `is_physical_store`, `is_unknown`: clarify the meaning of each row.
- `source_system`: prevents accidental cross-source joins.

Business use:

- Walmart store comparison, store-type reporting, and store-size analysis.

Notes:

- Online Retail does not provide a physical store identifier. Online fact rows
  join to the controlled `ONLINE_CHANNEL` record instead of an invented store.

### `warehouse.fact_sales`

Purpose:

- Stores measurable sales observations at the lowest reliable source grain.

Source staging tables:

- `staging.stg_online_retail_transactions`
- `staging.stg_walmart_sales`

Key columns:

- `sales_key`: surrogate primary key.
- `source_record_id`, `source_system`: source lineage and uniqueness.
- `sales_grain`: identifies `invoice_line` or `weekly_store_department`.
- `date_key`, `product_key`, `customer_key`, `store_key`: dimension foreign keys.
- `invoice_no`: available for Online Retail invoice-line facts.
- `dataset_split`, `is_holiday`: available for Walmart weekly facts.

Business metrics:

- `quantity`: available for Online Retail invoice lines.
- `unit_price`: available for Online Retail invoice lines.
- `sales_amount`: standardized sales amount for analysis.
- `revenue`: standardized revenue metric, equal to the supported sales amount.
- `source_sales_amount`: source value retained for reconciliation.
- `weekly_sales_amount`: Walmart weekly sales value retained explicitly.

Business use:

- Revenue trends, product and department performance, customer analysis, store
  analysis, and later mart construction.

## Limitations

- The two source datasets are analytically compatible but are not transactionally
  connected. The warehouse preserves separate source grains and lineage.
- Walmart test observations are excluded from `warehouse.fact_sales` because
  they have no sales target. They remain available in staging for forecasting.
- Walmart feature markdown columns are promotional feature values, not proven
  transaction discounts. They are not modeled as `discount`.
- Neither dataset supplies product cost or profit. The warehouse does not invent
  a `profit` metric.
- Marts are built from the accepted warehouse layer in `sql/marts/` and refreshed
  through `sql/04_create_marts.sql`.
