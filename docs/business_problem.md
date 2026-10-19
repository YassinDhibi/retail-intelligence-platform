# Business Problem

Retail businesses often have sales data spread across transactional systems,
store systems, and external planning datasets. Analysts need a clean and trusted
way to answer performance questions without rebuilding logic in every report.

## Key Questions

- What is total revenue by month and source system?
- Which products and departments drive revenue?
- Which customers and countries matter most?
- Which stores perform best after considering store type and size?
- How do holiday periods affect Walmart weekly sales?
- What data is ready for forecasting and recommendations?

## Analytics Requirements

- Keep raw data reproducible.
- Standardize messy columns and data types.
- Build reusable warehouse dimensions and facts.
- Create business marts with clear KPI definitions.
- Prepare data for Power BI and API consumption.
- Avoid inventing unavailable metrics such as profit or margin.

## Project Response

The platform creates a structured analytics workflow:

```text
CSV data -> Python cleaning -> PostgreSQL -> staging -> warehouse -> marts -> BI/API/ML
```

This gives analysts a repeatable system instead of ad hoc notebooks or manual
dashboard joins.
