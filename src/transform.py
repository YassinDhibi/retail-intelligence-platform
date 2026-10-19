from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORT_DIR = PROJECT_ROOT / "data" / "processed" / "reports"


@dataclass(frozen=True)
class CleaningResult:
    dataset: str
    raw_rows: int
    clean_rows: int
    raw_missing_cells: int
    clean_missing_cells: int
    duplicate_rows_removed: int
    invalid_rows_removed: int
    output_path: Path


def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.str.strip()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
        .str.lower()
    )
    return df


def _write_quality_report(results: list[CleaningResult]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / "data_quality_report.csv"
    pd.DataFrame(
        [
            {
                "dataset": result.dataset,
                "raw_rows": result.raw_rows,
                "clean_rows": result.clean_rows,
                "rows_removed": result.raw_rows - result.clean_rows,
                "raw_missing_cells": result.raw_missing_cells,
                "clean_missing_cells": result.clean_missing_cells,
                "duplicate_rows_removed": result.duplicate_rows_removed,
                "invalid_rows_removed": result.invalid_rows_removed,
                "output_path": str(result.output_path.relative_to(PROJECT_ROOT)),
            }
            for result in results
        ]
    ).to_csv(report_path, index=False)


def _clean_online_retail() -> CleaningResult:
    source_path = RAW_DIR / "archive" / "OnlineRetail.csv"
    output_path = PROCESSED_DIR / "online_retail_clean.csv"

    raw = pd.read_csv(source_path, encoding="ISO-8859-1")
    raw_rows = len(raw)
    raw_missing_cells = int(raw.isna().sum().sum())
    duplicate_rows = int(raw.duplicated().sum())

    df = _standardize_columns(raw).rename(
        columns={
            "invoiceno": "invoice_no",
            "stockcode": "stock_code",
            "invoicedate": "invoice_date",
            "unitprice": "unit_price",
            "customerid": "customer_id",
        }
    )
    df = df.drop_duplicates()
    df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")
    df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce").astype("Int64")

    required_fields = ["invoice_no", "stock_code", "description", "invoice_date", "customer_id", "country"]
    valid_mask = (
        df[required_fields].notna().all(axis=1)
        & (df["quantity"] > 0)
        & (df["unit_price"] > 0)
        & ~df["invoice_no"].astype(str).str.startswith("C")
    )
    invalid_rows_removed = int((~valid_mask).sum())

    df = df.loc[valid_mask].copy()
    df["description"] = df["description"].str.strip().str.title()
    df["country"] = df["country"].str.strip()
    df["total_sales"] = df["quantity"] * df["unit_price"]

    ordered_columns = [
        "invoice_no",
        "stock_code",
        "description",
        "quantity",
        "invoice_date",
        "unit_price",
        "customer_id",
        "country",
        "total_sales",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df[ordered_columns].to_csv(output_path, index=False)

    return CleaningResult(
        dataset="online_retail",
        raw_rows=raw_rows,
        clean_rows=len(df),
        raw_missing_cells=raw_missing_cells,
        clean_missing_cells=int(df.isna().sum().sum()),
        duplicate_rows_removed=duplicate_rows,
        invalid_rows_removed=invalid_rows_removed,
        output_path=output_path,
    )


def _clean_walmart() -> list[CleaningResult]:
    source_dir = RAW_DIR / "walmart-recruiting-store-sales-forecasting"
    paths = {
        "stores": source_dir / "stores.csv",
        "features": source_dir / "features.csv" / "features.csv",
        "train": source_dir / "train.csv" / "train.csv",
        "test": source_dir / "test.csv" / "test.csv",
    }

    raw_frames = {name: pd.read_csv(path) for name, path in paths.items()}
    clean_frames: dict[str, pd.DataFrame] = {}
    results: list[CleaningResult] = []

    for name, raw in raw_frames.items():
        df = _standardize_columns(raw)
        raw_rows = len(raw)
        raw_missing_cells = int(raw.isna().sum().sum())
        duplicate_rows = int(df.duplicated().sum())
        df = df.drop_duplicates()

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")

        if name == "features":
            markdown_columns = [column for column in df.columns if column.startswith("markdown")]
            df[markdown_columns] = df[markdown_columns].fillna(0)
            df = df.sort_values(["store", "date"])
            df[["cpi", "unemployment"]] = df.groupby("store")[["cpi", "unemployment"]].ffill().bfill()

        valid_mask = df.notna().all(axis=1)
        if name == "stores":
            valid_mask &= df["size"].gt(0)
        if name == "train":
            valid_mask &= df["weekly_sales"].ge(0)

        invalid_rows_removed = int((~valid_mask).sum())
        df = df.loc[valid_mask].copy()
        clean_frames[name] = df

        output_path = PROCESSED_DIR / f"walmart_{name}_clean.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)

        results.append(
            CleaningResult(
                dataset=f"walmart_{name}",
                raw_rows=raw_rows,
                clean_rows=len(df),
                raw_missing_cells=raw_missing_cells,
                clean_missing_cells=int(df.isna().sum().sum()),
                duplicate_rows_removed=duplicate_rows,
                invalid_rows_removed=invalid_rows_removed,
                output_path=output_path,
            )
        )

    _write_walmart_model_tables(clean_frames)
    return results


def _write_walmart_model_tables(clean_frames: dict[str, pd.DataFrame]) -> None:
    stores = clean_frames["stores"]
    features = clean_frames["features"]

    for split in ["train", "test"]:
        merged = (
            clean_frames[split]
            .merge(stores, on="store", how="left")
            .merge(features, on=["store", "date", "isholiday"], how="left")
        )
        merged = merged.dropna().copy()
        merged.to_csv(PROCESSED_DIR / f"walmart_{split}_model_ready.csv", index=False)


def clean_all() -> list[CleaningResult]:
    results = [_clean_online_retail()]
    results.extend(_clean_walmart())
    _write_quality_report(results)
    return results


def main() -> None:
    results = clean_all()
    for result in results:
        print(
            f"{result.dataset}: {result.raw_rows:,} raw rows -> "
            f"{result.clean_rows:,} clean rows | "
            f"missing cells {result.raw_missing_cells:,} -> {result.clean_missing_cells:,} | "
            f"saved {result.output_path.relative_to(PROJECT_ROOT)}"
        )
    print(f"quality report: {(REPORT_DIR / 'data_quality_report.csv').relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
