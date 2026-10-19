from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Query

from api.schemas import (
    HealthResponse,
    PredictionRequest,
    PredictionResponse,
    ProjectStatus,
)
from api.services import (
    fetch_all,
    fetch_one,
    get_prediction,
    verify_database_connection,
)


app = FastAPI(
    title="Retail Intelligence API",
    description="Analytics and prediction API for the Retail Intelligence Platform.",
    version="1.0.0",
)


@app.get("/", response_model=ProjectStatus)
def root() -> ProjectStatus:
    return ProjectStatus(
        project="Retail Intelligence Platform",
        status="ready",
        layers=["raw", "staging", "warehouse", "marts", "ml"],
        docs=["README.md", "docs/api.md", "docs/business_marts.md"],
    )


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    verify_database_connection()
    return HealthResponse(status="ok", database="connected")


@app.get("/sales-overview")
def sales_overview() -> dict[str, Any]:
    return fetch_one(
        """
        SELECT
            ROUND(SUM(total_revenue), 2) AS total_revenue,
            SUM(total_orders)::integer AS total_orders,
            ROUND(SUM(total_quantity), 2) AS total_quantity,
            ROUND(SUM(total_revenue) / NULLIF(SUM(total_orders), 0), 2) AS average_order_value,
            COUNT(*)::integer AS monthly_rows
        FROM marts.sales_overview
        """
    )


@app.get("/sales-overview/monthly")
def monthly_sales() -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT
            month_start_date,
            year,
            month,
            month_name,
            source_system,
            total_revenue,
            total_orders,
            total_quantity,
            average_order_value,
            revenue_growth_pct
        FROM marts.sales_overview
        ORDER BY month_start_date, source_system
        """
    )


@app.get("/top-products")
def top_products(limit: int = Query(default=10, ge=1, le=50)) -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT
            product_key,
            product_code,
            product_name,
            department_id,
            product_level,
            source_system,
            sales_rows,
            quantity_sold,
            total_revenue,
            revenue_rank,
            performance_band
        FROM marts.product_performance
        ORDER BY total_revenue DESC, product_name
        LIMIT :limit
        """,
        {"limit": limit},
    )


@app.get("/store-performance")
def store_performance(limit: int = Query(default=20, ge=1, le=100)) -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT
            store_key,
            store_id,
            store_name,
            store_type,
            store_size,
            source_system,
            sales_rows,
            total_revenue,
            holiday_revenue,
            non_holiday_revenue,
            sales_per_store_size,
            store_revenue_rank
        FROM marts.store_performance
        ORDER BY total_revenue DESC, store_reference
        LIMIT :limit
        """,
        {"limit": limit},
    )


@app.post("/predict-sales", response_model=PredictionResponse)
def predict_sales(request: PredictionRequest) -> PredictionResponse:
    try:
        prediction = get_prediction(request)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return PredictionResponse(predicted_weekly_sales=round(prediction, 2), model="LinearRegression")


# Backward-compatible aliases from the earlier API draft.
app.add_api_route("/metrics/sales-overview", sales_overview, methods=["GET"])
app.add_api_route("/metrics/monthly-sales", monthly_sales, methods=["GET"])
app.add_api_route("/metrics/top-products", top_products, methods=["GET"])
