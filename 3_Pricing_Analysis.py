from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analysis.eda import calculate_kpis, grouped_summary, top_products, top_brand_by_count, best_platform_by_rating, cheapest_platform
from src.analysis.insights import generate_insights
from src.app_components.sidebar import render_sidebar_filters
from src.app_components.ui import clean_display_table, display_kpis, page_header, show_business_insights, format_currency
from src.database.database import ensure_database_ready, query_products
from src.visualization import charts

st.set_page_config(page_title="Brand Visibility Dashboard", page_icon="📊", layout="wide")
ensure_database_ready()
filters = render_sidebar_filters()
df = query_products(filters)

page_header("Pricing Analysis", "Price distribution, price ranges, discount analysis, and price-ranking relationships.")

if df.empty:
    st.warning("No products match selected filters.")
    st.stop()

discounted_pct = df["discount_pct"].gt(0).mean() * 100
c1, c2, c3, c4 = st.columns(4)
c1.metric("Average Price", format_currency(df["price"].mean()))
c2.metric("Maximum Price", format_currency(df["price"].max()))
c3.metric("Minimum Price", format_currency(df["price"].min()))
c4.metric("% Discounted Products", f"{discounted_pct:.1f}%")

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(charts.price_distribution(df), use_container_width=True)
with col2:
    st.plotly_chart(charts.price_range_distribution(df), use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(charts.price_vs_position(df), use_container_width=True)
with col2:
    st.plotly_chart(charts.price_vs_rating(df), use_container_width=True)

st.plotly_chart(charts.discount_by_brand(df), use_container_width=True)

st.subheader("Most Expensive Products")
expensive = df.sort_values("price", ascending=False).head(10)
st.dataframe(clean_display_table(expensive), use_container_width=True, hide_index=True)
