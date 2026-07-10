"""Business insight generation from the filtered dataset."""

from __future__ import annotations

import pandas as pd


def _safe_first(series: pd.Series, default: str = "N/A") -> str:
    return str(series.index[0]) if len(series) else default


def generate_insights(frame: pd.DataFrame) -> list[str]:
    """Generate concise business insights from product data."""
    if frame.empty:
        return ["No products match the selected filters. Try widening your filter selection."]

    insights: list[str] = []

    brand_counts = frame["brand"].value_counts()
    if not brand_counts.empty:
        top_brand = brand_counts.index[0]
        share = brand_counts.iloc[0] / len(frame) * 100
        insights.append(f"{top_brand} has the largest product presence in the current view with {share:.1f}% of listings.")

    platform_counts = frame["platform"].value_counts()
    if not platform_counts.empty:
        top_platform = platform_counts.index[0]
        share = platform_counts.iloc[0] / len(frame) * 100
        insights.append(f"{top_platform} contributes the highest number of listed products with {share:.1f}% share.")

    visibility_by_brand = frame.groupby("brand")["visibility_score"].mean().sort_values(ascending=False)
    if not visibility_by_brand.empty:
        insights.append(f"{visibility_by_brand.index[0]} has the strongest average visibility score among selected brands.")

    rating_by_platform = frame.groupby("platform")["rating"].mean().sort_values(ascending=False)
    if not rating_by_platform.empty:
        insights.append(f"{rating_by_platform.index[0]} has the highest average customer rating among selected platforms.")

    if frame["discount_pct"].gt(0).any():
        discounted_pct = frame["discount_pct"].gt(0).mean() * 100
        insights.append(f"{discounted_pct:.1f}% of products have an active discount in the selected view.")
    else:
        insights.append("The current dataset has no measurable discount values because raw price is equal to selling price for provided CSV rows.")

    top_10_share = frame["is_top_10"].mean() * 100
    insights.append(f"{top_10_share:.1f}% of selected products appear in top-10 ranking positions.")

    return insights[:6]
