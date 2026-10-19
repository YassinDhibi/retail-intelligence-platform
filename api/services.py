from __future__ import annotations

from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from api.schemas import PredictionRequest
from src.load_to_postgres import PostgresConfig, load_local_env


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    load_local_env(PROJECT_ROOT / ".env")
    config = PostgresConfig.from_env()
    return create_engine(config.sqlalchemy_url(), pool_pre_ping=True)


@contextmanager
def db_connection():
    try:
        engine = get_engine()
        with engine.connect() as connection:
            yield connection
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {exc}") from exc


def verify_database_connection() -> None:
    with db_connection() as connection:
        connection.execute(text("SELECT 1"))


def fetch_one(query: str, parameters: dict[str, Any] | None = None) -> dict[str, Any]:
    with db_connection() as connection:
        row = connection.execute(text(query), parameters or {}).mappings().first()
    return dict(row or {})


def fetch_all(query: str, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    with db_connection() as connection:
        rows = connection.execute(text(query), parameters or {}).mappings().all()
    return [dict(row) for row in rows]


def get_prediction(request: PredictionRequest) -> float:
    from ml.predict_sales import predict_sales

    payload = request.model_dump()
    payload["date"] = request.date.isoformat()
    return predict_sales(payload)
