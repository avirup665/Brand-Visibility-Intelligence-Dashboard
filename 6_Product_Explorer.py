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

page_header("Product Explorer", "Search, sort, inspect, and download product-level data.")

if df.empty:
    st.warning("No products match selected filters.")
    st.stop()

display_kpis(calculate_kpis(df))

sort_col = st.selectbox(
    "Sort products by",
    ["visibility_score", "rating", "reviews", "price", "position", "discount_pct"],
    index=0,
)
ascending = st.toggle("Ascending order", value=False)

sorted_df = df.sort_values(sort_col, ascending=ascending)

st.dataframe(clean_display_table(sorted_df), use_container_width=True, hide_index=True, height=560)

csv = sorted_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download Product Explorer Data",
    csv,
    file_name="product_explorer_data.csv",
    mime="text/csv",
    use_container_width=True,
)
