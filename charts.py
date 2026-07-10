"""Plotly chart factory functions for Streamlit pages."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def empty_figure(message: str = "No data available") -> go.Figure:
    """Return a clean placeholder figure."""
    fig = go.Figure()
    fig.add_annotation(text=message, x=0.5, y=0.5, showarrow=False, font={"size": 16})
    fig.update_layout(height=380, xaxis={"visible": False}, yaxis={"visible": False})
    return fig


def price_distribution(frame: pd.DataFrame) -> go.Figure:
    if frame.empty:
        return empty_figure()
    fig = px.histogram(frame, x="price", nbins=35, title="Price Distribution")
    fig.update_layout(xaxis_title="Price", yaxis_title="Product Count")
    return fig


def products_per_keyword(frame: pd.DataFrame) -> go.Figure:
    if frame.empty:
        return empty_figure()
    data = frame["keyword"].value_counts().reset_index()
    data.columns = ["keyword", "product_count"]
    fig = px.bar(data, x="keyword", y="product_count", title="Products per Keyword", text_auto=True)
    fig.update_layout(xaxis_title="Keyword", yaxis_title="Product Count")
    return fig


def platform_share(frame: pd.DataFrame) -> go.Figure:
    if frame.empty:
        return empty_figure()
    data = frame["platform"].value_counts().reset_index()
    data.columns = ["platform", "product_count"]
    fig = px.pie(data, names="platform", values="product_count", title="Platform Share")
    return fig


def brand_product_count(frame: pd.DataFrame, top_n: int = 15) -> go.Figure:
    if frame.empty:
        return empty_figure()
    data = frame["brand"].value_counts().head(top_n).reset_index()
    data.columns = ["brand", "product_count"]
    fig = px.bar(data, x="product_count", y="brand", orientation="h", title=f"Top {top_n} Brands by Product Count", text_auto=True)
    fig.update_layout(xaxis_title="Product Count", yaxis_title="Brand", yaxis={"categoryorder": "total ascending"})
    return fig


def brand_avg_rating(frame: pd.DataFrame, top_n: int = 15) -> go.Figure:
    if frame.empty:
        return empty_figure()
    data = (
        frame.groupby("brand", as_index=False)
        .agg(avg_rating=("rating", "mean"), product_count=("product_id", "count"))
        .query("product_count >= 3")
        .sort_values("avg_rating", ascending=False)
        .head(top_n)
    )
    if data.empty:
        return empty_figure("Not enough brand rating data")
    fig = px.bar(data, x="avg_rating", y="brand", orientation="h", title="Highest Rated Brands", text_auto=".2f")
    fig.update_layout(xaxis_title="Average Rating", yaxis_title="Brand", yaxis={"categoryorder": "total ascending"})
    return fig


def top_brands_top10(frame: pd.DataFrame, top_n: int = 15) -> go.Figure:
    if frame.empty:
        return empty_figure()

    # SQLite stores Boolean values as 0/1 integers. Build an explicit
    # Boolean mask so pandas filters rows instead of treating 0/1 as columns.
    top_10_mask = pd.to_numeric(frame["is_top_10"], errors="coerce").fillna(0).eq(1)
    data = (
        frame.loc[top_10_mask]
        .groupby("brand", as_index=False)
        .agg(top_10_count=("product_id", "count"))
    )
    data = data.sort_values("top_10_count", ascending=False).head(top_n)
    if data.empty:
        return empty_figure("No top-10 products in selected data")
    fig = px.bar(data, x="top_10_count", y="brand", orientation="h", title="Brands Appearing Most in Top 10 Positions", text_auto=True)
    fig.update_layout(xaxis_title="Top 10 Count", yaxis_title="Brand", yaxis={"categoryorder": "total ascending"})
    return fig


def visibility_by_brand(frame: pd.DataFrame, top_n: int = 15) -> go.Figure:
    if frame.empty:
        return empty_figure()
    data = (
        frame.groupby("brand", as_index=False)
        .agg(avg_visibility_score=("visibility_score", "mean"), product_count=("product_id", "count"))
        .query("product_count >= 3")
        .sort_values("avg_visibility_score", ascending=False)
        .head(top_n)
    )
    fig = px.bar(data, x="avg_visibility_score", y="brand", orientation="h", title="Average Visibility Score by Brand", text_auto=".1f")
    fig.update_layout(xaxis_title="Average Visibility Score", yaxis_title="Brand", yaxis={"categoryorder": "total ascending"})
    return fig


def price_vs_position(frame: pd.DataFrame) -> go.Figure:
    if frame.empty:
        return empty_figure()
    fig = px.scatter(
        frame,
        x="price",
        y="position",
        color="platform",
        hover_data=["title", "brand", "rating", "reviews"],
        title="Price vs Ranking Position",
    )
    fig.update_layout(xaxis_title="Price", yaxis_title="Position / Ranking")
    return fig


def price_vs_rating(frame: pd.DataFrame) -> go.Figure:
    if frame.empty:
        return empty_figure()
    fig = px.scatter(
        frame,
        x="price",
        y="rating",
        color="brand",
        hover_data=["title", "platform", "reviews"],
        title="Price vs Rating",
    )
    fig.update_layout(xaxis_title="Price", yaxis_title="Rating")
    return fig


def price_range_distribution(frame: pd.DataFrame) -> go.Figure:
    if frame.empty:
        return empty_figure()
    order = ["Budget", "Mid Range", "Premium", "Luxury"]
    data = frame["price_range"].value_counts().reindex(order).fillna(0).reset_index()
    data.columns = ["price_range", "product_count"]
    fig = px.bar(data, x="price_range", y="product_count", title="Product Distribution by Price Range", text_auto=True)
    fig.update_layout(xaxis_title="Price Range", yaxis_title="Product Count")
    return fig


def discount_by_brand(frame: pd.DataFrame, top_n: int = 15) -> go.Figure:
    if frame.empty:
        return empty_figure()
    data = (
        frame.groupby("brand", as_index=False)
        .agg(avg_discount_pct=("discount_pct", "mean"), product_count=("product_id", "count"))
        .sort_values("avg_discount_pct", ascending=False)
        .head(top_n)
    )
    fig = px.bar(data, x="avg_discount_pct", y="brand", orientation="h", title="Average Discount % by Brand", text_auto=".1f")
    fig.update_layout(xaxis_title="Average Discount %", yaxis_title="Brand", yaxis={"categoryorder": "total ascending"})
    return fig


def platform_product_count(frame: pd.DataFrame) -> go.Figure:
    if frame.empty:
        return empty_figure()
    data = frame["platform"].value_counts().reset_index()
    data.columns = ["platform", "product_count"]
    fig = px.bar(data, x="platform", y="product_count", title="Platform vs Product Count", text_auto=True)
    fig.update_layout(xaxis_title="Platform", yaxis_title="Product Count")
    return fig


def platform_avg_price(frame: pd.DataFrame) -> go.Figure:
    if frame.empty:
        return empty_figure()
    data = frame.groupby("platform", as_index=False).agg(avg_price=("price", "mean")).sort_values("avg_price")
    fig = px.bar(data, x="platform", y="avg_price", title="Platform vs Average Price", text_auto=".0f")
    fig.update_layout(xaxis_title="Platform", yaxis_title="Average Price")
    return fig


def platform_avg_rating(frame: pd.DataFrame) -> go.Figure:
    if frame.empty:
        return empty_figure()
    data = frame.groupby("platform", as_index=False).agg(avg_rating=("rating", "mean")).sort_values("avg_rating", ascending=False)
    fig = px.bar(data, x="platform", y="avg_rating", title="Platform vs Average Rating", text_auto=".2f")
    fig.update_layout(xaxis_title="Platform", yaxis_title="Average Rating")
    return fig


def ranking_distribution(frame: pd.DataFrame) -> go.Figure:
    if frame.empty:
        return empty_figure()
    fig = px.histogram(frame, x="position", nbins=40, title="Ranking Position Distribution")
    fig.update_layout(xaxis_title="Position", yaxis_title="Product Count")
    return fig


def rating_vs_ranking(frame: pd.DataFrame) -> go.Figure:
    if frame.empty:
        return empty_figure()
    fig = px.scatter(
        frame,
        x="rating",
        y="position",
        color="platform",
        hover_data=["title", "brand", "price", "reviews"],
        title="Rating vs Ranking Position",
    )
    fig.update_layout(xaxis_title="Rating", yaxis_title="Position / Ranking")
    return fig


def reviews_vs_ranking(frame: pd.DataFrame) -> go.Figure:
    if frame.empty:
        return empty_figure()
    fig = px.scatter(
        frame,
        x="reviews",
        y="position",
        size="price",
        color="brand",
        hover_data=["title", "platform", "rating"],
        title="Reviews vs Ranking Position",
    )
    fig.update_layout(xaxis_title="Reviews", yaxis_title="Position / Ranking")
    return fig


def correlation_heatmap(frame: pd.DataFrame) -> go.Figure:
    if frame.empty:
        return empty_figure()
    numeric = frame[["price", "raw_price", "discount_pct", "rating", "reviews", "position", "visibility_score"]]
    corr = numeric.corr(numeric_only=True).round(2)
    fig = px.imshow(corr, text_auto=True, title="Correlation Heatmap")
    return fig
