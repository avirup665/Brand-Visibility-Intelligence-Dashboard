"""Reusable Streamlit UI helpers."""

from __future__ import annotations

import pandas as pd
import streamlit as st


def page_header(title: str, subtitle: str) -> None:
    """Render a consistent page heading."""
    st.title(title)
    st.caption(subtitle)


def format_currency(value: float) -> str:
    """Format a numeric price in Indian rupee style."""
    try:
        return f"₹{value:,.0f}"
    except Exception:
        return "₹0"


def display_kpis(metrics: dict) -> None:
    """Display standard KPI cards."""
    columns = st.columns(5)

    with columns[0]:
        st.metric("Total Products", f"{metrics.get('total_products', 0):,}")

    with columns[1]:
        st.metric("Avg Price", format_currency(metrics.get("avg_price", 0)))

    with columns[2]:
        st.metric("Avg Rating", f"{metrics.get('avg_rating', 0):.2f}")

    with columns[3]:
        st.metric("Total Reviews", f"{metrics.get('total_reviews', 0):,}")

    with columns[4]:
        st.metric("Avg Visibility", f"{metrics.get('avg_visibility_score', 0):.1f}")


def show_business_insights(insights: list[str]) -> None:
    """Render business insights in a neat container."""
    st.subheader("Business Insights")
    for insight in insights:
        st.info(insight)


def clean_display_table(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a user-facing product table with readable columns."""
    if frame.empty:
        return frame

    columns = [
        "title",
        "brand",
        "keyword",
        "platform",
        "price",
        "rating",
        "reviews",
        "position",
        "visibility_score",
        "price_range",
        "discount_pct",
        "delivery",
    ]
    selected = [column for column in columns if column in frame.columns]
    output = frame[selected].copy()

    rename_map = {
        "title": "Title",
        "brand": "Brand",
        "keyword": "Keyword",
        "platform": "Platform",
        "price": "Price",
        "rating": "Rating",
        "reviews": "Reviews",
        "position": "Position",
        "visibility_score": "Visibility Score",
        "price_range": "Price Range",
        "discount_pct": "Discount %",
        "delivery": "Delivery",
    }
    return output.rename(columns=rename_map)
