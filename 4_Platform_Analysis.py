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

page_header("Platform Analysis", "Compare e-commerce platforms by product count, price, rating, and ranking.")

if df.empty:
    st.warning("No products match selected filters.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Platforms", df["platform"].nunique())
c2.metric("Best Platform by Rating", best_platform_by_rating(df))
c3.metric("Cheapest Platform", cheapest_platform(df))
c4.metric("Platform with Most Products", df["platform"].value_counts().idxmax())

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(charts.platform_product_count(df), use_container_width=True)
with col2:
    st.plotly_chart(charts.platform_avg_price(df), use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(charts.platform_avg_rating(df), use_container_width=True)
with col2:
    st.plotly_chart(charts.platform_share(df), use_container_width=True)

st.subheader("Platform Summary Table")
st.dataframe(grouped_summary(df, "platform"), use_container_width=True, hide_index=True)
