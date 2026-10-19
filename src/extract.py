from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

EXPECTED_FILES = [
    RAW_DIR / "archive" / "OnlineRetail.csv",
    RAW_DIR / "walmart-recruiting-store-sales-forecasting" / "stores.csv",
    RAW_DIR / "walmart-recruiting-store-sales-forecasting" / "features.csv" / "features.csv",
    RAW_DIR / "walmart-recruiting-store-sales-forecasting" / "train.csv" / "train.csv",
    RAW_DIR / "walmart-recruiting-store-sales-forecasting" / "test.csv" / "test.csv",
]


def validate_raw_files() -> list[Path]:
    missing = [path for path in EXPECTED_FILES if not path.exists()]
    if missing:
        missing_text = "\n".join(str(path.relative_to(PROJECT_ROOT)) for path in missing)
        raise FileNotFoundError(
            "Missing raw dataset files. Download the Kaggle datasets locally and place them at:\n"
            f"{missing_text}"
        )
    return EXPECTED_FILES


def main() -> None:
    files = validate_raw_files()
    for path in files:
        print(f"found {path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
