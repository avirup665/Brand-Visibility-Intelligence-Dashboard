"""Reusable EDA calculations."""

from __future__ import annotations

import pandas as pd


def calculate_kpis(frame: pd.DataFrame) -> dict:
    """Calculate high-level dashboard KPIs."""
    if frame.empty:
        return {
            "total_products": 0,
            "avg_price": 0.0,
            "avg_rating": 0.0,
            "total_reviews": 0,
            "avg_visibility_score": 0.0,
            "top_10_pct": 0.0,
        }

    return {
        "total_products": int(len(frame)),
        "avg_price": float(frame["price"].mean()),
        "avg_rating": float(frame["rating"].mean()),
        "total_reviews": int(frame["reviews"].sum()),
        "avg_visibility_score": float(frame["visibility_score"].mean()),
        "top_10_pct": float(frame["is_top_10"].mean() * 100),
    }


def top_brand_by_count(frame: pd.DataFrame) -> str:
    """Return brand with maximum product count."""
    if frame.empty or "brand" not in frame:
        return "N/A"
    counts = frame["brand"].value_counts()
    return counts.index[0] if not counts.empty else "N/A"


def best_platform_by_rating(frame: pd.DataFrame) -> str:
    """Return platform with highest average rating."""
    if frame.empty:
        return "N/A"
    grouped = frame.groupby("platform")["rating"].mean().sort_values(ascending=False)
    return grouped.index[0] if not grouped.empty else "N/A"


def cheapest_platform(frame: pd.DataFrame) -> str:
    """Return platform with lowest average price."""
    if frame.empty:
        return "N/A"
    grouped = frame.groupby("platform")["price"].mean().sort_values()
    return grouped.index[0] if not grouped.empty else "N/A"


def top_products(frame: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Return top products by visibility, rating, and reviews."""
    if frame.empty:
        return frame
    return (
        frame.sort_values(["visibility_score", "rating", "reviews"], ascending=[False, False, False])
        .head(n)
        .reset_index(drop=True)
    )


def grouped_summary(frame: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """Return standard group-level summary."""
    if frame.empty:
        return pd.DataFrame()

    return (
        frame.groupby(group_col, as_index=False)
        .agg(
            product_count=("product_id", "count"),
            avg_price=("price", "mean"),
            avg_rating=("rating", "mean"),
            avg_reviews=("reviews", "mean"),
            avg_position=("position", "mean"),
            avg_visibility_score=("visibility_score", "mean"),
            avg_discount_pct=("discount_pct", "mean"),
        )
        .round(2)
        .sort_values("product_count", ascending=False)
    )
