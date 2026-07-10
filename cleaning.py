"""Data cleaning utilities for the Brand Visibility project."""

from __future__ import annotations

import hashlib
import re
from typing import Any

import numpy as np
import pandas as pd

INVALID_TOKENS = {
    "",
    "nan",
    "none",
    "null",
    "n/a",
    "na",
    "not available",
    "not_available",
    "many",
    "-",
    "--",
    "unknown",
}


def to_snake_case(value: str) -> str:
    """Convert a column name to snake_case."""
    text = str(value).strip()
    text = re.sub(r"[^0-9A-Za-z]+", "_", text)
    text = re.sub(r"_+", "_", text)
    return text.strip("_").lower()


def standardize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with normalized column names."""
    df = frame.copy()
    df.columns = [to_snake_case(col) for col in df.columns]
    return df


def parse_numeric(value: Any) -> float:
    """Safely parse a messy numeric value.

    Examples
    --------
    "$1,299.99" -> 1299.99
    "Not Available" -> NaN
    "many" -> NaN
    """
    if pd.isna(value):
        return np.nan

    text = str(value).strip()
    if text.lower() in INVALID_TOKENS:
        return np.nan

    text = text.replace(",", "")
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    if not match:
        return np.nan

    try:
        return float(match.group(0))
    except ValueError:
        return np.nan


def clean_title(value: Any) -> str:
    """Remove visual noise from product titles while preserving readable words."""
    if pd.isna(value):
        return "Unknown Product"

    text = str(value)
    text = re.sub(r"[!#@$%^*_=~`|\\<>{}\[\]]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.title() if text else "Unknown Product"


def clean_keyword(value: Any) -> str:
    """Normalize search keywords."""
    if pd.isna(value):
        return "Unknown"
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text.title() if text else "Unknown"


def standardize_platform(value: Any) -> str:
    """Normalize platform names."""
    if pd.isna(value):
        return "Unknown"

    text = re.sub(r"\s+", " ", str(value)).strip().lower()

    mapping = {
        "amazon": "Amazon",
        "flipkart": "Flipkart",
        "croma": "Croma",
        "reliance digital": "Reliance Digital",
        "reliancedigital": "Reliance Digital",
        "walmart": "Walmart",
        "apple": "Apple",
        "samsung": "Samsung",
    }

    return mapping.get(text, text.title() if text else "Unknown")


def standardize_delivery(value: Any) -> str:
    """Normalize delivery labels."""
    if pd.isna(value):
        return "Unknown"

    text = re.sub(r"\s+", " ", str(value)).strip().lower()

    mapping = {
        "free delivery": "Free Delivery",
        "free": "Free Delivery",
        "2 days": "2 Days",
        "2 day": "2 Days",
        "5 days": "5 Days",
        "5 day": "5 Days",
        "prime": "Prime",
        "paid": "Paid Delivery",
    }

    return mapping.get(text, text.title() if text else "Unknown")


def delivery_category(value: Any) -> str:
    """Create a simplified delivery-speed category."""
    text = str(value).lower()
    if "free" in text or "prime" in text or "2" in text:
        return "Fast / Preferred"
    if "5" in text:
        return "Standard"
    if "paid" in text:
        return "Paid"
    return "Unknown"


def fill_with_group_median(df: pd.DataFrame, column: str, group_columns: list[str]) -> pd.Series:
    """Fill missing numeric values using group median, then global median."""
    series = df[column].copy()

    for group_col in group_columns:
        series = series.fillna(df.groupby(group_col)[column].transform("median"))

    global_median = series.median()
    if pd.isna(global_median):
        global_median = 0

    return series.fillna(global_median)


def make_product_id(row: pd.Series) -> str:
    """Create a stable product identifier from core fields."""
    key = f"{row.get('keyword', '')}|{row.get('title', '')}|{row.get('platform', '')}|{row.get('price', '')}"
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]


def clean_dataset(raw_frame: pd.DataFrame) -> pd.DataFrame:
    """Clean raw product data and return an analysis-ready DataFrame.

    The function is intentionally defensive: missing optional columns are created,
    invalid values are converted safely, and machine-specific paths are avoided.
    """
    if raw_frame.empty:
        raise ValueError("The input dataset is empty.")

    df = standardize_columns(raw_frame)

    # Required / optional columns for a unified schema.
    for column in [
        "keyword",
        "title",
        "price",
        "raw_price",
        "rating",
        "reviews",
        "platform",
        "position",
        "delivery",
        "link",
        "thumbnail",
        "source_type",
    ]:
        if column not in df.columns:
            df[column] = np.nan

    df["source_type"] = df["source_type"].fillna("provided_csv")

    df["keyword"] = df["keyword"].apply(clean_keyword)
    df["title"] = df["title"].apply(clean_title)
    df["platform"] = df["platform"].apply(standardize_platform)
    df["delivery"] = df["delivery"].apply(standardize_delivery)
    df["delivery_category"] = df["delivery"].apply(delivery_category)

    df["price"] = df["price"].apply(parse_numeric)
    df.loc[df["price"] <= 0, "price"] = np.nan

    df["raw_price"] = df["raw_price"].apply(parse_numeric)
    df["raw_price"] = df["raw_price"].fillna(df["price"])
    df.loc[df["raw_price"] < df["price"], "raw_price"] = df.loc[df["raw_price"] < df["price"], "price"]

    df["rating"] = df["rating"].apply(parse_numeric)
    df.loc[(df["rating"] < 0) | (df["rating"] > 5), "rating"] = np.nan

    df["reviews"] = df["reviews"].apply(parse_numeric)
    df.loc[df["reviews"] < 0, "reviews"] = np.nan

    # Position: API data may have it; provided CSV may not. Use keyword-wise row
    # order as a deterministic ranking proxy when position is unavailable.
    df["position"] = df["position"].apply(parse_numeric)
    missing_position = df["position"].isna()
    fallback_position = df.groupby("keyword").cumcount() + 1
    df.loc[missing_position, "position"] = fallback_position.loc[missing_position]
    df["position"] = df["position"].clip(lower=1)

    # Drop records without meaningful titles, then deduplicate.
    df = df[df["title"].notna() & (df["title"].str.len() > 0)].copy()
    df = df.drop_duplicates(subset=["keyword", "title", "platform", "price"], keep="first")

    # Imputation strategy.
    df["price"] = fill_with_group_median(df, "price", ["keyword", "platform"])
    df["raw_price"] = df["raw_price"].fillna(df["price"])
    df.loc[df["raw_price"] < df["price"], "raw_price"] = df.loc[df["raw_price"] < df["price"], "price"]

    df["rating"] = fill_with_group_median(df, "rating", ["keyword", "platform"]).clip(0, 5)
    df["reviews"] = df["reviews"].fillna(0).round().astype(int)

    df["position"] = df["position"].round().astype(int)
    df["price"] = df["price"].round(2)
    df["raw_price"] = df["raw_price"].round(2)
    df["rating"] = df["rating"].round(2)

    df["link"] = df["link"].fillna("Not Available").replace("", "Not Available").astype(str)
    df["thumbnail"] = df["thumbnail"].fillna("Not Available").replace("", "Not Available").astype(str)
    df["product_id"] = df.apply(make_product_id, axis=1)

    return df.reset_index(drop=True)


def data_quality_summary(raw_frame: pd.DataFrame, cleaned_frame: pd.DataFrame) -> dict:
    """Generate a compact data-quality summary for reporting."""
    raw = standardize_columns(raw_frame)

    return {
        "raw_shape": {"rows": int(raw_frame.shape[0]), "columns": int(raw_frame.shape[1])},
        "cleaned_shape": {"rows": int(cleaned_frame.shape[0]), "columns": int(cleaned_frame.shape[1])},
        "raw_columns": list(raw.columns),
        "cleaned_columns": list(cleaned_frame.columns),
        "missing_values_before": {k: int(v) for k, v in raw.isna().sum().to_dict().items()},
        "missing_values_after": {k: int(v) for k, v in cleaned_frame.isna().sum().to_dict().items()},
        "duplicates_removed_estimate": int(raw_frame.shape[0] - cleaned_frame.shape[0]),
        "platforms": sorted(cleaned_frame["platform"].dropna().unique().tolist()),
        "keywords": sorted(cleaned_frame["keyword"].dropna().unique().tolist()),
    }
