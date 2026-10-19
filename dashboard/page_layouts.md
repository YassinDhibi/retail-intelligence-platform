# Power BI Page Layouts

## 1. Executive Overview

Purpose: Give the reviewer an immediate understanding of project value.

Layout:

- Top KPI row: Total Revenue, Total Orders, Total Quantity, Average Order Value.
- Center: Monthly Revenue by source system line chart.
- Right: Revenue by source system stacked column.
- Bottom: Top 10 products by revenue.

Filters:

- Source system
- Year
- Month

## 2. Sales Trends

Purpose: Explain revenue movement over time.

Layout:

- Monthly revenue line chart by source system.
- Revenue growth percent column chart.
- Matrix with year, month, source system, total revenue, total orders, AOV.

Filters:

- Source system
- Year

## 3. Product Performance

Purpose: Identify best and worst products or departments.

Layout:

- Top 20 product bar chart by total revenue.
- Product performance band stacked bar.
- Product detail table with product code, name, source, quantity, revenue, rank.

Filters:

- Source system
- Product level
- Performance band

## 4. Customer Analysis

Purpose: Show customer value and repeat behavior.

Layout:

- Customer segment revenue column chart.
- Country revenue bar chart for Online Retail.
- Repeat customer rate card.
- Customer table with revenue, invoice count, AOV, first and last purchase date.

Filters:

- Customer segment
- Country
- Source system

## 5. Store Performance

Purpose: Compare Walmart stores and operational attributes.

Layout:

- Store revenue ranking bar chart.
- Holiday vs non-holiday revenue clustered column.
- Sales per store size scatter plot.
- Store detail table with store type, size, revenue, holiday revenue, rank.

Filters:

- Store type
- Source system

## 6. Forecasting & Recommendations

Purpose: Show that the dataset is prepared for modeling and explain forecast
drivers.

Layout:

- Weekly revenue trend line chart.
- Average weekly revenue card.
- Holiday week revenue card.
- Forecasting base table with date, store, department, revenue, holiday flag,
  temperature, fuel price, CPI, unemployment.
- Text box with model limitations and recommendations.

Recommended notes:

- Use the baseline model as a portfolio demonstration.
- Recommend adding richer product, inventory, and promotion data before
  production forecasting.
- Treat holiday and markdown variables as useful modeling features, not causal
  proof.
