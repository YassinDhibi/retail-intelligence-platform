from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.train_forecasting_model import (
    FEATURE_COLUMNS,
    MODEL_PATH,
    calculate_metrics,
    load_forecasting_base,
    prepare_features,
    train_test_split_by_date,
)


def evaluate_model() -> dict[str, float]:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}. Run ml/train_forecasting_model.py first.")

    artifact = joblib.load(MODEL_PATH)
    model = artifact["model"]

    raw_df = load_forecasting_base()
    model_df = prepare_features(raw_df)
    _, test_df = train_test_split_by_date(model_df)
    predictions = model.predict(test_df[FEATURE_COLUMNS])
    return calculate_metrics(test_df["revenue"], predictions)


def main() -> None:
    print(json.dumps(evaluate_model(), indent=2))


if __name__ == "__main__":
    main()
