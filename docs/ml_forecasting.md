# ML Forecasting

## Purpose

The ML module trains a baseline weekly sales forecasting model from
`marts.forecasting_base`. It is intentionally simple and explainable: the goal
is to demonstrate a complete modeling workflow, not to claim production-grade
forecasting accuracy.

## Files

| File | Purpose |
| --- | --- |
| `ml/train_forecasting_model.py` | Loads `marts.forecasting_base`, trains a baseline model, saves metrics and artifact |
| `ml/model_evaluation.py` | Reloads the saved model and evaluates it on the same chronological test window |
| `ml/predict_sales.py` | Scores one store-department-week input from command-line arguments |
| `ml/models/.gitkeep` | Keeps the local model artifact folder in Git |

The generated model artifact is saved locally as:

```text
ml/models/sales_forecasting_model.pkl
```

Model binaries are ignored by Git through the existing `*.pkl` rule.

## Input Data

The model reads:

```sql
SELECT * FROM marts.forecasting_base;
```

Important fields:

- `date`
- `store_id`
- `department_id`
- `revenue`
- `holiday_flag`
- `store_type`
- `store_size`
- `temperature`
- `fuel_price`
- `markdown_1` through `markdown_5`
- `cpi`
- `unemployment_rate`

## Model

- Baseline model: `LinearRegression`
- Split strategy: chronological 80 percent train, 20 percent test
- Metrics: MAE, RMSE, MAPE

The linear baseline is intentionally fast, transparent, and safe to run on a
portfolio laptop. A later improvement could compare it with Random Forest or
gradient boosting.

## Commands

Run after PostgreSQL marts are built:

```powershell
python ml/train_forecasting_model.py
python ml/model_evaluation.py
python ml/predict_sales.py --store-id 1 --department-id 1 --store-type A
```

## Verification Notes

The forecasting base contains 420,285 training rows. Live model training
requires `pandas`, `SQLAlchemy`, `psycopg2-binary`, `scikit-learn`, and `joblib`
in the active Python environment.

## Known Limitations

- Walmart sales are weekly department-level records, not SKU transactions.
- The dataset does not include product prices, margins, or stockouts.
- The baseline model uses tabular date features rather than a dedicated
  time-series model.
- Predictions should be treated as demonstration outputs, not business-ready
  forecasts.
