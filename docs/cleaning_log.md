# Cleaning Log

## Current Cleaning Rules

### Online Retail

- Removed duplicate rows.
- Removed rows with missing required business fields.
- Removed cancelled invoices.
- Removed invalid transactions where quantity or unit price is not positive.
- Parsed invoice dates.
- Added `total_sales`.

### Walmart Sales Forecasting

- Removed duplicate rows.
- Converted date fields to datetime.
- Filled missing markdown values with `0`.
- Filled missing CPI and unemployment values by store using forward/backward fill.
- Removed invalid negative weekly sales rows from training data.
- Created model-ready train and test tables by joining sales, stores, and features.

## Outputs

Cleaned files are generated locally under `data/processed/` and are intentionally ignored by Git.
