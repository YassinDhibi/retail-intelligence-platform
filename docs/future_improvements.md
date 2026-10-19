# Future Improvements

## Data Quality

- Add row-count audit tables after every pipeline step.
- Add null, duplicate, and accepted-value checks in SQL and dbt.
- Add pipeline run metadata with timestamps and status.

## Modeling

- Add more mart-level documentation for each metric.
- Add dbt exposures for Power BI pages and API endpoints.
- Add snapshot logic if slowly changing dimensions become relevant.

## Machine Learning

- Compare the baseline linear model with Random Forest and XGBoost.
- Add feature importance reporting.
- Add backtesting by store and department.
- Store predictions in a PostgreSQL mart for dashboard consumption.

## API

- Add pagination to list endpoints.
- Add filters for source system, date range, product, and store.
- Add pytest coverage with mocked database results.
- Add structured API error responses.

## DevOps

- Add CI checks for SQL parsing and dbt parsing.
- Add a lightweight seed dataset for automated tests.
- Add deployment notes for Render, Railway, or Azure.

## Dashboard

- Build the Power BI report manually from the provided specification.
- Export dashboard screenshots to `screenshots/`.
- Add a short dashboard walkthrough video or GIF.
