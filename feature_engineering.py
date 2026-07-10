"""Feature engineering for the Brand Visibility project."""

from __future__ import annotations

import numpy as np
import pandas as pd

KNOWN_BRANDS = [
    "Samsung",
    "Apple",
    "Dell",
    "HP",
    "Lenovo",
    "Sony",
    "LG",
    "Boat",
    "Puma",
    "Philips",
    "Nike",
    "Adidas",
    "OnePlus",
    "Mi",
    "Realme",
    "Croma",
]


def extract_brand(title: str) -> str:
    """Extract a likely brand from a product title."""
    if not isinstance(title, str) or not title.strip():
        return "Unknown"

    words = title.replace("-", " ").split()
    normalized = {word.lower(): word for word in words}

    for brand in KNOWN_BRANDS:
        if brand.lower() in normalized:
            return brand

    # Dataset titles generally start with brand; use first token as fallback.
    first = words[0].strip()
    if first.lower() == "hp":
        return "HP"
    if first.lower() == "lg":
        return "LG"
    return first.title() if first else "Unknown"


def create_price_range(price: float, q1: float, q2: float, q3: float) -> str:
    """Assign a quartile-based price range."""
    if pd.isna(price):
        return "Unknown"
    if price <= q1:
        return "Budget"
    if price <= q2:
        return "Mid Range"
    if price <= q3:
        return "Premium"
    return "Luxury"


def rating_category(rating: float) -> str:
    """Convert a numeric rating into a business-friendly category."""
    if pd.isna(rating):
        return "Unknown"
    if rating >= 4.5:
        return "Excellent"
    if rating >= 4.0:
        return "Good"
    if rating >= 3.0:
        return "Average"
    return "Poor"


def review_category(reviews: int) -> str:
    """Convert review count into engagement category."""
    if pd.isna(reviews):
        return "Unknown"
    if reviews >= 3000:
        return "Very High"
    if reviews >= 1000:
        return "High"
    if reviews >= 250:
        return "Medium"
    return "Low"


def add_features(clean_frame: pd.DataFrame) -> pd.DataFrame:
    """Add project-specific analytical features."""
    if clean_frame.empty:
        raise ValueError("Cannot engineer features for an empty DataFrame.")

    df = clean_frame.copy()

    df["brand"] = df["title"].apply(extract_brand)

    max_position = df.groupby("keyword")["position"].transform("max").replace(0, np.nan)
    df["visibility_score"] = (1 - ((df["position"] - 1) / max_position)) * 100
    df["visibility_score"] = df["visibility_score"].fillna(0).clip(0, 100).round(2)

    df["discount_amount"] = (df["raw_price"] - df["price"]).clip(lower=0).round(2)
    df["discount_pct"] = np.where(
        df["raw_price"] > 0,
        (df["discount_amount"] / df["raw_price"]) * 100,
        0,
    )
    df["discount_pct"] = pd.Series(df["discount_pct"]).fillna(0).round(2)

    q1, q2, q3 = df["price"].quantile([0.25, 0.50, 0.75]).tolist()
    df["price_range"] = df["price"].apply(lambda value: create_price_range(value, q1, q2, q3))

    df["rating_category"] = df["rating"].apply(rating_category)
    df["review_category"] = df["reviews"].apply(review_category)
    df["is_top_10"] = df["position"] <= 10
    df["is_popular"] = (df["rating"] >= 4.3) & (df["reviews"] >= 1000)

    # Keep columns ordered where possible.
    preferred_order = [
        "product_id",
        "keyword",
        "title",
        "brand",
        "price",
        "raw_price",
        "discount_amount",
        "discount_pct",
        "rating",
        "reviews",
        "platform",
        "position",
        "visibility_score",
        "price_range",
        "rating_category",
        "review_category",
        "delivery",
        "delivery_category",
        "is_top_10",
        "is_popular",
        "link",
        "thumbnail",
        "source_type",
    ]

    ordered = [column for column in preferred_order if column in df.columns]
    extra = [column for column in df.columns if column not in ordered]
    return df[ordered + extra].reset_index(drop=True)
