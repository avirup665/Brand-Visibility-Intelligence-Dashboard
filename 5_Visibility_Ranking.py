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

page_header("Visibility & Ranking Analysis", "Understand ranking distribution and how rating, reviews, and price relate to visibility.")

if df.empty:
    st.warning("No products match selected filters.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Average Position", f"{df['position'].mean():.1f}")
c2.metric("Best Ranked Product", df.sort_values("position").iloc[0]["title"])
c3.metric("Average Visibility", f"{df['visibility_score'].mean():.1f}")
c4.metric("Top 10 Products %", f"{df['is_top_10'].mean() * 100:.1f}%")

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(charts.ranking_distribution(df), use_container_width=True)
with col2:
    st.plotly_chart(charts.visibility_by_brand(df), use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(charts.rating_vs_ranking(df), use_container_width=True)
with col2:
    st.plotly_chart(charts.reviews_vs_ranking(df), use_container_width=True)

st.subheader("Highest Visibility Products")
visible = df.sort_values(["visibility_score", "rating", "reviews"], ascending=[False, False, False]).head(15)
st.dataframe(clean_display_table(visible), use_container_width=True, hide_index=True)
