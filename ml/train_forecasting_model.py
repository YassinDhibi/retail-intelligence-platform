from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sqlalchemy import create_engine


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.load_to_postgres import PostgresConfig

MODEL_DIR = PROJECT_ROOT / "ml" / "models"
MODEL_PATH = MODEL_DIR / "sales_forecasting_model.pkl"
METRICS_PATH = MODEL_DIR / "sales_forecasting_metrics.json"

FORECASTING_QUERY = """
SELECT
    date,
    store_id,
    department_id,
    revenue,
    holiday_flag,
    store_type,
    store_size,
    temperature,
    fuel_price,
    markdown_1,
    markdown_2,
    markdown_3,
    markdown_4,
    markdown_5,
    cpi,
    unemployment_rate
FROM marts.forecasting_base
WHERE revenue IS NOT NULL
"""

FEATURE_COLUMNS = [
    "store_id",
    "department_id",
    "holiday_flag",
    "store_size",
    "temperature",
    "fuel_price",
    "markdown_1",
    "markdown_2",
    "markdown_3",
    "markdown_4",
    "markdown_5",
    "cpi",
    "unemployment_rate",
    "year",
    "month",
    "week_of_year",
    "store_type_A",
    "store_type_B",
    "store_type_C",
]


def load_forecasting_base() -> pd.DataFrame:
    config = PostgresConfig.from_env()
    engine = create_engine(config.sqlalchemy_url(), pool_pre_ping=True)
    return pd.read_sql(FORECASTING_QUERY, engine)


def prepare_features(dataframe: pd.DataFrame) -> pd.DataFrame:
    df = dataframe.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["week_of_year"] = df["date"].dt.isocalendar().week.astype("Int64")
    df["holiday_flag"] = df["holiday_flag"].astype(bool).astype(int)

    df = pd.get_dummies(df, columns=["store_type"], prefix="store_type")
    for column in FEATURE_COLUMNS:
        if column not in df.columns:
            df[column] = 0

    numeric_columns = FEATURE_COLUMNS + ["revenue"]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    return df.dropna(subset=numeric_columns)


def train_test_split_by_date(dataframe: pd.DataFrame, test_fraction: float = 0.2) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = dataframe.sort_values("date").reset_index(drop=True)
    split_index = int(len(df) * (1 - test_fraction))
    return df.iloc[:split_index].copy(), df.iloc[split_index:].copy()


def calculate_metrics(actual: pd.Series, predicted: np.ndarray) -> dict[str, float]:
    mae = mean_absolute_error(actual, predicted)
    rmse = mean_squared_error(actual, predicted) ** 0.5
    non_zero_mask = actual != 0
    mape = np.mean(np.abs((actual[non_zero_mask] - predicted[non_zero_mask]) / actual[non_zero_mask])) * 100
    return {
        "mae": float(mae),
        "rmse": float(rmse),
        "mape": float(mape),
    }


def train_model() -> dict[str, Any]:
    raw_df = load_forecasting_base()
    model_df = prepare_features(raw_df)
    train_df, test_df = train_test_split_by_date(model_df)

    x_train = train_df[FEATURE_COLUMNS]
    y_train = train_df["revenue"]
    x_test = test_df[FEATURE_COLUMNS]
    y_test = test_df["revenue"]

    model = LinearRegression()
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)

    metrics = calculate_metrics(y_test, predictions)
    metrics.update(
        {
            "model_type": "LinearRegression",
            "training_rows": int(len(train_df)),
            "test_rows": int(len(test_df)),
            "feature_count": len(FEATURE_COLUMNS),
            "trained_at_utc": datetime.now(UTC).isoformat(),
        }
    )

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    artifact = {
        "model": model,
        "feature_columns": FEATURE_COLUMNS,
        "metrics": metrics,
    }
    joblib.dump(artifact, MODEL_PATH)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


def main() -> None:
    metrics = train_model()
    print(json.dumps(metrics, indent=2))
    print(f"model saved to {MODEL_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
