"""Validate that the project can run cleanly.

Usage:
    python scripts/validate_project.py
"""

from __future__ import annotations

import py_compile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import CLEAN_DATA_PATH, DB_PATH, FINAL_COLUMNS, RAW_DATA_PATH
from src.database.database import query_products
from src.preprocessing.pipeline import run_pipeline


def compile_python_files() -> None:
    for path in ROOT.rglob("*.py"):
        if ".venv" in path.parts or "__pycache__" in path.parts:
            continue
        py_compile.compile(str(path), doraise=True)


def main() -> None:
    assert RAW_DATA_PATH.exists(), f"Missing raw dataset: {RAW_DATA_PATH}"

    compile_python_files()
    frame = run_pipeline(include_api=True, save_database=True)

    missing_columns = [column for column in FINAL_COLUMNS if column not in frame.columns]
    assert not missing_columns, f"Missing final columns: {missing_columns}"

    critical_columns = ["price", "rating", "reviews", "platform", "brand", "visibility_score"]
    missing_counts = frame[critical_columns].isna().sum()
    assert missing_counts.sum() == 0, f"Critical missing values remain: {missing_counts.to_dict()}"

    assert CLEAN_DATA_PATH.exists(), "Cleaned CSV was not created."
    assert DB_PATH.exists(), "SQLite database was not created."

    sample = query_products(limit=5)
    assert len(sample) > 0, "Database query returned zero rows."

    print("Validation successful.")
    print(f"Rows validated: {len(frame):,}")
    print(f"Database path: {DB_PATH}")


if __name__ == "__main__":
    main()
