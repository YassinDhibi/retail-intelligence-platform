# FastAPI Service

## Purpose

The API exposes selected business marts and the baseline sales forecasting model
for local demos, portfolio walkthroughs, and lightweight integration testing.

## Run Locally

Start PostgreSQL and build the database layers first:

```powershell
python src/load_to_postgres.py
psql -h localhost -p 5432 -U postgres -d retail_warehouse -f sql/02_create_staging_tables.sql
psql -h localhost -p 5432 -U postgres -d retail_warehouse -f sql/03_create_warehouse_tables.sql
psql -h localhost -p 5432 -U postgres -d retail_warehouse -f sql/04_create_marts.sql
```

Run the API:

```powershell
uvicorn api.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | Project status |
| `GET` | `/health` | Database health check |
| `GET` | `/sales-overview` | Portfolio-level revenue, order, quantity, and AOV KPIs |
| `GET` | `/sales-overview/monthly` | Monthly KPI trend from `marts.sales_overview` |
| `GET` | `/top-products?limit=10` | Product and department ranking |
| `GET` | `/store-performance?limit=20` | Store and channel performance |
| `POST` | `/predict-sales` | Baseline weekly sales prediction |

Legacy aliases remain available under `/metrics/...`.

## Example Requests

```powershell
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/sales-overview
curl "http://127.0.0.1:8000/top-products?limit=5"
```

Prediction request:

```powershell
curl -X POST http://127.0.0.1:8000/predict-sales `
  -H "Content-Type: application/json" `
  -d "{\"date\":\"2012-10-26\",\"store_id\":1,\"department_id\":1,\"holiday_flag\":false,\"store_type\":\"A\",\"store_size\":151315,\"temperature\":58.85,\"fuel_price\":3.882,\"markdown_1\":0,\"markdown_2\":0,\"markdown_3\":0,\"markdown_4\":0,\"markdown_5\":0,\"cpi\":223.078337,\"unemployment_rate\":6.573}"
```

## Example Responses

Health:

```json
{
  "status": "ok",
  "database": "connected"
}
```

Prediction:

```json
{
  "predicted_weekly_sales": 22412.58,
  "model": "LinearRegression"
}
```

## Notes

- `/predict-sales` requires `ml/models/sales_forecasting_model.pkl`, generated
  by `python ml/train_forecasting_model.py`.
- Database credentials are read from `.env` and should not be committed.
- The API is designed for local portfolio demonstration, not public production
  deployment.
