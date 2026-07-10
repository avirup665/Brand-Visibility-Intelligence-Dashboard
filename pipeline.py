"""End-to-end ETL pipeline: load, clean, engineer features, save CSV and SQLite."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pandas as pd

from src.config import (
    API_DATA_PATH,
    CLEAN_DATA_PATH,
    QUALITY_REPORT_PATH,
    RAW_DATA_PATH,
    ensure_directories,
)
from src.preprocessing.cleaning import clean_dataset, data_quality_summary
from src.preprocessing.feature_engineering import add_features
from src.utils.logger import get_logger

logger = get_logger(__name__)


def load_raw_sources(include_api: bool = True) -> tuple[pd.DataFrame, dict]:
    """Load provided CSV and optional API CSV, then combine them."""
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Raw dataset not found at {RAW_DATA_PATH}. "
            "Place brand_dirty_dataset.csv inside data/raw/."
        )

    frames: list[pd.DataFrame] = []
    metadata: dict = {"sources": []}

    provided = pd.read_csv(RAW_DATA_PATH)
    provided["source_type"] = "provided_csv"
    frames.append(provided)
    metadata["sources"].append({"name": "provided_csv", "rows": int(len(provided))})

    if include_api and API_DATA_PATH.exists():
        api = pd.read_csv(API_DATA_PATH)
        if not api.empty:
            api["source_type"] = "api"
            frames.append(api)
            metadata["sources"].append({"name": "api", "rows": int(len(api))})

    combined = pd.concat(frames, ignore_index=True, sort=False)
    metadata["combined_rows"] = int(len(combined))
    return combined, metadata


def run_pipeline(include_api: bool = True, save_database: bool = True) -> pd.DataFrame:
    """Run the complete data pipeline and return the final DataFrame."""
    ensure_directories()

    logger.info("Starting ETL pipeline")
    raw_frame, metadata = load_raw_sources(include_api=include_api)
    cleaned_frame = clean_dataset(raw_frame)
    final_frame = add_features(cleaned_frame)

    final_frame.to_csv(CLEAN_DATA_PATH, index=False)
    logger.info("Saved cleaned dataset to %s", CLEAN_DATA_PATH)

    quality = data_quality_summary(raw_frame, final_frame)
    quality["pipeline_metadata"] = metadata
    quality["generated_at_utc"] = datetime.now(timezone.utc).isoformat()

    with open(QUALITY_REPORT_PATH, "w", encoding="utf-8") as file:
        json.dump(quality, file, indent=2)

    logger.info("Saved data quality report to %s", QUALITY_REPORT_PATH)

    if save_database:
        from src.database.database import initialize_database

        initialize_database(final_frame)

    logger.info("ETL pipeline completed successfully")
    return final_frame
