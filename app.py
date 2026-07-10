"""Main Streamlit app entry point.

Run locally:
    streamlit run app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analysis.eda import calculate_kpis, top_products
from src.analysis.insights import generate_insights
from src.app_components.sidebar import render_sidebar_filters
from src.app_components.ui import clean_display_table, display_kpis, page_header, show_business_insights
from src.database.database import ensure_database_ready, query_products
from src.visualization import charts

st.set_page_config(
    page_title="Brand Visibility Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

ensure_database_ready()

page_header(
    "Brand Visibility Intelligence Dashboard",
    "End-to-end data science dashboard for brand visibility, pricing, platform comparison, and ranking intelligence.",
)

filters = render_sidebar_filters()
df = query_products(filters)

if df.empty:
    st.warning("No products match the selected filters.")
    st.stop()

kpis = calculate_kpis(df)
display_kpis(kpis)

st.divider()

left, right = st.columns([2, 1])
with left:
    st.plotly_chart(charts.price_distribution(df), use_container_width=True)
with right:
    st.plotly_chart(charts.platform_share(df), use_container_width=True)

left, right = st.columns(2)
with left:
    st.plotly_chart(charts.products_per_keyword(df), use_container_width=True)
with right:
    st.plotly_chart(charts.brand_product_count(df), use_container_width=True)

show_business_insights(generate_insights(df))

st.subheader("Top Products")
st.dataframe(clean_display_table(top_products(df, 10)), use_container_width=True, hide_index=True)

csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Filtered Data as CSV",
    data=csv,
    file_name="filtered_brand_visibility_data.csv",
    mime="text/csv",
    use_container_width=True,
)
