# Business Marts

## Purpose

The `marts` schema contains dashboard-ready and modeling-ready views built from
the warehouse star schema. Power BI, API endpoints, and forecasting scripts
should read from these marts instead of joining raw or staging tables directly.

Run all marts from the repository root:

```powershell
psql -h localhost -p 5432 -U postgres -d retail_warehouse -f sql/04_create_marts.sql
```

## Mart Inventory

| Mart | Grain | Main use |
| --- | --- | --- |
| `marts.sales_overview` | Source system by month | Executive KPIs, monthly trend, revenue growth |
| `marts.product_performance` | Source-aware product or department | Best and worst products, department ranking |
| `marts.customer_performance` | Source-aware customer profile | Customer value, country analysis, repeat purchase behavior |
| `marts.store_performance` | Store or channel | Store ranking, holiday revenue, store-size productivity |
| `marts.forecasting_base` | Walmart store, department, week | ML-ready forecasting dataset |

`marts.forecasting_features` is kept as a compatibility alias for earlier
documentation and exploration.

## KPI Definitions

| KPI | Definition |
| --- | --- |
| `total_revenue` | Sum of standardized warehouse revenue for the mart grain |
| `total_orders` | Online invoices for Online Retail; sales observations for Walmart |
| `total_quantity` | Sum of known item quantities; Walmart weekly sales has no unit quantity |
| `average_order_value` | `total_revenue / total_orders` |
| `monthly_revenue` | Monthly `total_revenue` in `marts.sales_overview` |
| `revenue_growth_pct` | Month-over-month revenue growth by source system |
| `sales_per_store_size` | Store revenue divided by Walmart store size |
| `holiday_revenue` | Walmart sales amount where the holiday flag is true |

## Verified Row Counts

Verified on 2026-06-18 after rebuilding raw, staging, and warehouse layers.

| Mart | Row count |
| --- | ---: |
| `marts.sales_overview` | 46 |
| `marts.product_performance` | 3,746 |
| `marts.customer_performance` | 4,347 |
| `marts.store_performance` | 46 |
| `marts.forecasting_base` | 420,285 |

## Power BI Usage Notes

- Use `marts.sales_overview` for executive cards and monthly trend visuals.
- Use `marts.product_performance` for product ranking and contribution charts.
- Use `marts.customer_performance` for customer and country pages.
- Use `marts.store_performance` for Walmart store comparison and holiday impact.
- Use `marts.forecasting_base` for forecasting visuals and model validation
  pages.

## Known Limitations

- Online Retail and Walmart are separate source systems, not joinable business
  entities.
- Walmart sales are department-level weekly observations, not SKU-level
  transactions.
- The datasets do not provide profit or cost, so margin analysis is not
  invented.
- Walmart markdown fields are promotional features, not confirmed customer
  discounts.
