from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODEL_PATH = PROJECT_ROOT / "models" / "walmart_weekly_sales_model.joblib"
PREDICTION_PATH = PROCESSED_DIR / "walmart_test_predictions.csv"


def prepare_features(df: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["week"] = df["date"].dt.isocalendar().week.astype(int)
    df["isholiday"] = df["isholiday"].astype(bool).astype(int)
    df["type"] = df["type"].astype("category").cat.codes
    return df.dropna(subset=feature_columns)


def predict() -> Path:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}. Run src/train_model.py first.")

    test_path = PROCESSED_DIR / "walmart_test_model_ready.csv"
    if not test_path.exists():
        raise FileNotFoundError(f"Test file not found: {test_path}. Run src/transform.py first.")

    artifact = joblib.load(MODEL_PATH)
    model = artifact["model"]
    feature_columns = artifact["features"]

    df = pd.read_csv(test_path)
    scored = prepare_features(df, feature_columns)
    scored["predicted_weekly_sales"] = model.predict(scored[feature_columns])

    output_columns = ["store", "dept", "date", "predicted_weekly_sales"]
    PREDICTION_PATH.parent.mkdir(parents=True, exist_ok=True)
    scored[output_columns].to_csv(PREDICTION_PATH, index=False)
    return PREDICTION_PATH


def main() -> None:
    output_path = predict()
    print(f"predictions saved to {output_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
