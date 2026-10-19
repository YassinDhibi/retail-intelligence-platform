from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.train_forecasting_model import FEATURE_COLUMNS, MODEL_PATH, prepare_features


def predict_sales(input_record: dict[str, Any]) -> float:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}. Run ml/train_forecasting_model.py first.")

    artifact = joblib.load(MODEL_PATH)
    model = artifact["model"]
    dataframe = pd.DataFrame([input_record])
    prepared = prepare_features(dataframe)
    if prepared.empty:
        raise ValueError("Input record could not be converted into model features.")

    return float(model.predict(prepared[FEATURE_COLUMNS])[0])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Predict Walmart weekly sales for one store and department.")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--store-id", type=int, default=1)
    parser.add_argument("--department-id", type=int, default=1)
    parser.add_argument("--holiday-flag", action="store_true")
    parser.add_argument("--store-type", choices=["A", "B", "C"], default="A")
    parser.add_argument("--store-size", type=int, default=151315)
    parser.add_argument("--temperature", type=float, default=45.0)
    parser.add_argument("--fuel-price", type=float, default=3.0)
    parser.add_argument("--markdown-1", type=float, default=0.0)
    parser.add_argument("--markdown-2", type=float, default=0.0)
    parser.add_argument("--markdown-3", type=float, default=0.0)
    parser.add_argument("--markdown-4", type=float, default=0.0)
    parser.add_argument("--markdown-5", type=float, default=0.0)
    parser.add_argument("--cpi", type=float, default=211.0)
    parser.add_argument("--unemployment-rate", type=float, default=8.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_record = {
        "date": args.date,
        "store_id": args.store_id,
        "department_id": args.department_id,
        "holiday_flag": args.holiday_flag,
        "store_type": args.store_type,
        "store_size": args.store_size,
        "temperature": args.temperature,
        "fuel_price": args.fuel_price,
        "markdown_1": args.markdown_1,
        "markdown_2": args.markdown_2,
        "markdown_3": args.markdown_3,
        "markdown_4": args.markdown_4,
        "markdown_5": args.markdown_5,
        "cpi": args.cpi,
        "unemployment_rate": args.unemployment_rate,
    }
    prediction = predict_sales(input_record)
    print(json.dumps({"predicted_weekly_sales": round(prediction, 2)}, indent=2))


if __name__ == "__main__":
    main()
