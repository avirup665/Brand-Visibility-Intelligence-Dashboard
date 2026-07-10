"""Run the complete ETL pipeline from terminal.

Usage:
    python scripts/run_pipeline.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.preprocessing.pipeline import run_pipeline


def main() -> None:
    frame = run_pipeline(include_api=True, save_database=True)
    print("ETL pipeline completed successfully.")
    print(f"Rows: {len(frame):,}")
    print(f"Columns: {len(frame.columns):,}")
    print("Clean data: data/processed/cleaned_products.csv")
    print("SQLite DB: database/brand_visibility.db")


if __name__ == "__main__":
    main()
