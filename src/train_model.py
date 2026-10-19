from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODEL_DIR / "walmart_weekly_sales_model.joblib"
METRICS_PATH = MODEL_DIR / "walmart_weekly_sales_metrics.json"

FEATURE_COLUMNS = [
    "store",
    "dept",
    "isholiday",
    "temperature",
    "fuel_price",
    "markdown1",
    "markdown2",
    "markdown3",
    "markdown4",
    "markdown5",
    "cpi",
    "unemployment",
    "type",
    "size",
    "year",
    "month",
    "week",
]


def load_training_data() -> pd.DataFrame:
    data_path = PROCESSED_DIR / "walmart_train_model_ready.csv"
    if not data_path.exists():
        raise FileNotFoundError(
            f"Training file not found: {data_path}. Run src/transform.py first."
        )

    df = pd.read_csv(data_path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["week"] = df["date"].dt.isocalendar().week.astype(int)
    df["isholiday"] = df["isholiday"].astype(bool).astype(int)
    df["type"] = df["type"].astype("category").cat.codes
    return df.dropna(subset=FEATURE_COLUMNS + ["weekly_sales"])


def train() -> dict[str, float]:
    df = load_training_data()
    x = df[FEATURE_COLUMNS]
    y = df["weekly_sales"]

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
    )

    model = RandomForestRegressor(
        n_estimators=120,
        max_depth=14,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)

    metrics = {
        "mae": float(mean_absolute_error(y_test, predictions)),
        "rmse": float(mean_squared_error(y_test, predictions, squared=False)),
        "r2": float(r2_score(y_test, predictions)),
        "training_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
    }

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "features": FEATURE_COLUMNS}, MODEL_PATH)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


def main() -> None:
    metrics = train()
    print(json.dumps(metrics, indent=2))
    print(f"model saved to {MODEL_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
