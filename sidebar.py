"""Streamlit sidebar filters connected to SQL-backed product data."""

from __future__ import annotations

import streamlit as st

from src.database.database import get_filter_options
from src.preprocessing.pipeline import run_pipeline


def render_sidebar_filters() -> dict:
    """Render sidebar controls and return a filter dictionary."""
    options = get_filter_options()

    st.sidebar.header("Dashboard Filters")

    if st.sidebar.button("Run / Refresh ETL Pipeline", use_container_width=True):
        with st.spinner("Running ETL pipeline and refreshing SQLite database..."):
            run_pipeline(save_database=True)
        st.cache_data.clear()
        st.success("Pipeline completed successfully.")
        st.rerun()

    brand = st.sidebar.multiselect("Brand", options["brands"])
    platform = st.sidebar.multiselect("Platform", options["platforms"])
    keyword = st.sidebar.multiselect("Keyword", options["keywords"])
    price_range = st.sidebar.multiselect("Price Range", options["price_ranges"])

    rating_min = float(options["rating_min"])
    rating_max = float(options["rating_max"])
    if rating_min == rating_max:
        rating_range = (rating_min, rating_max)
        st.sidebar.caption(f"Rating range: {rating_min:.1f}")
    else:
        rating_range = st.sidebar.slider(
            "Rating Range",
            min_value=round(rating_min, 1),
            max_value=round(rating_max, 1),
            value=(round(rating_min, 1), round(rating_max, 1)),
            step=0.1,
        )

    position_min = int(options["position_min"])
    position_max = int(options["position_max"])
    if position_min == position_max:
        position_range = (position_min, position_max)
        st.sidebar.caption(f"Position range: {position_min}")
    else:
        position_range = st.sidebar.slider(
            "Position Range",
            min_value=position_min,
            max_value=position_max,
            value=(position_min, position_max),
            step=1,
        )

    search = st.sidebar.text_input("Search Product / Brand / Keyword")

    st.sidebar.divider()
    st.sidebar.caption("Tip: leaving a multiselect empty means All.")

    return {
        "brand": brand,
        "platform": platform,
        "keyword": keyword,
        "price_range": price_range,
        "rating_range": rating_range,
        "position_range": position_range,
        "search": search,
    }
