# Power BI Dashboard Plan

## Goal

Build a recruiter-ready Power BI dashboard that explains retail performance
from executive KPIs down to product, customer, store, and forecasting insights.

## Data Connection

Connect Power BI to PostgreSQL:

```text
Server: localhost:5432
Database: retail_warehouse
Schema: marts
```

Import these views:

- `marts.sales_overview`
- `marts.product_performance`
- `marts.customer_performance`
- `marts.store_performance`
- `marts.forecasting_base`

Optional supporting warehouse tables:

- `warehouse.dim_date`
- `warehouse.fact_sales`

## Dashboard Pages

| Page | Purpose | Primary marts |
| --- | --- | --- |
| Executive Overview | Show headline revenue, order, quantity, and monthly trend | `sales_overview` |
| Sales Trends | Analyze monthly sales by source and growth | `sales_overview` |
| Product Performance | Rank products and Walmart departments | `product_performance` |
| Customer Analysis | Analyze customer value, segments, and geography | `customer_performance` |
| Store Performance | Compare Walmart stores and holiday impact | `store_performance` |
| Forecasting & Recommendations | Show ML base data and explain forecast drivers | `forecasting_base` |

## Filters And Slicers

Use these slicers where relevant:

- Source system
- Year
- Month
- Product level
- Customer segment
- Store type
- Holiday flag
- Department ID

## Storytelling Flow

1. Start with total revenue and the split between Online Retail and Walmart.
2. Explain monthly trend and growth changes.
3. Identify products and departments that drive most revenue.
4. Show customer concentration and geography for Online Retail.
5. Compare Walmart stores by revenue, size, and holiday behavior.
6. Finish with forecasting readiness and practical recommendations.

## Recommended Visuals

| Insight | Visual |
| --- | --- |
| Total revenue, total orders, AOV | Card visuals |
| Monthly revenue by source | Line chart |
| Revenue growth percent | Line chart or column chart |
| Top products | Bar chart |
| Product performance bands | Treemap or stacked bar |
| Customer segment revenue | Donut or stacked column |
| Country revenue | Map or bar chart |
| Store revenue ranking | Bar chart |
| Holiday vs non-holiday revenue | Clustered column |
| Forecasting base trend | Line chart by date |

## Manual Build Steps

1. Refresh PostgreSQL marts using `sql/04_create_marts.sql`.
2. Open Power BI Desktop.
3. Connect to PostgreSQL and import the marts schema views.
4. Create DAX measures from `dashboard/measures_dax.md`.
5. Build pages using `dashboard/page_layouts.md`.
6. Save the `.pbix` locally. Do not commit `.pbix` files to Git.
7. Export screenshots to `screenshots/` for the README.

## Known Limitations

- Online Retail and Walmart are displayed as separate source systems.
- Walmart product detail is department-level only.
- Profit and margin are not available in the source data.
- Forecasting is a baseline demo, not a production planning model.
