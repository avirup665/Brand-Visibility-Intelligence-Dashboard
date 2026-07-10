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

page_header("Executive Overview", "High-level KPIs, market composition, price distribution, and top products.")

if df.empty:
    st.warning("No products match selected filters.")
    st.stop()

display_kpis(calculate_kpis(df))

col1, col2 = st.columns([2, 1])
with col1:
    st.plotly_chart(charts.price_distribution(df), use_container_width=True)
with col2:
    st.plotly_chart(charts.platform_share(df), use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(charts.products_per_keyword(df), use_container_width=True)
with col2:
    st.plotly_chart(charts.correlation_heatmap(df), use_container_width=True)

show_business_insights(generate_insights(df))

st.subheader("Top 10 Products")
st.dataframe(clean_display_table(top_products(df, 10)), use_container_width=True, hide_index=True)
