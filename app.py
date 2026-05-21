import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Brand Visibility Intelligence Dashboard",
    layout="wide"
)    

# DATABASE CONNECTION
os.makedirs("database", exist_ok=True)

conn = sqlite3.connect(
    "database/brand_visibility.db"
)

# LOAD DATASET
df = pd.read_csv("data/brand_data.csv")

# Clean column names
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
)

# CHECK REQUIRED COLUMNS
required_columns = [
    "keyword",
    "title",
    "price",
    "rating",
    "reviews",
    "platform",
    "delivery"
]

for col in required_columns:
    if col not in df.columns:
        st.error(f"Missing column in CSV file: {col}")
        st.stop()

# DATA CLEANING

# Remove duplicates
df.drop_duplicates(inplace=True)

# Fill missing values
df.fillna(0, inplace=True)

# Convert numeric columns safely
df["price"] = pd.to_numeric(
    df["price"],
    errors="coerce"
).fillna(0)

df["rating"] = pd.to_numeric(
    df["rating"],
    errors="coerce"
).fillna(0)

df["reviews"] = pd.to_numeric(
    df["reviews"],
    errors="coerce"
).fillna(0)

# STORE DATA INTO DATABASE
df.to_sql(
    "brands",
    conn,
    if_exists="replace",
    index=False
)

# KPI CALCULATIONS
average_price = round(
    df["price"].mean(),
    2
)

average_rating = round(
    df["rating"].mean(),
    2
)

total_reviews = int(
    df["reviews"].sum()
)

top_platform = (
    df["platform"]
    .mode()[0]
)

# DASHBOARD TITLE
st.title(
    "Brand Visibility Intelligence Dashboard"
)

# PROJECT DESCRIPTION
st.markdown("""
### Real-Time Brand Visibility & Market Intelligence Dashboard

This dashboard analyzes:
- Product ratings
- Platform-wise pricing
- Review distribution
- Market trends
- Brand visibility insights
""")

# SIDEBAR FILTER
st.sidebar.header("Filter Data")

selected_platform = st.sidebar.multiselect(
    "Select Platform",
    options=df["platform"].unique(),
    default=df["platform"].unique()
)

filtered_df = df[
    df["platform"].isin(selected_platform)
]

# SEARCH PRODUCT
search_product = st.text_input(
    "Search Product"
)

if search_product:
    filtered_df = filtered_df[
        filtered_df["title"]
        .str.contains(
            search_product,
            case=False,
            na=False
        )
    ]

# SHOW DATASET
st.subheader("Dataset")

st.dataframe(filtered_df)

# DOWNLOAD CSV
csv = filtered_df.to_csv(index=False)

st.download_button(
    label="Download Filtered Data",
    data=csv,
    file_name="filtered_data.csv",
    mime="text/csv"
)

# KPI CARDS
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Average Price",
    average_price
)

col2.metric(
    "Average Rating",
    average_rating
)

col3.metric(
    "Total Reviews",
    total_reviews
)

col4.metric(
    "Top Platform",
    top_platform
)

# PRICE ANALYSIS BAR CHART
st.subheader("Price Analysis")

fig1 = px.bar(
    filtered_df,
    x="platform",
    y="price",
    color="platform",
    title="Platform vs Price"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# RATING ANALYSIS SCATTER PLOT
st.subheader("Rating Analysis")

fig2 = px.scatter(
    filtered_df,
    x="price",
    y="rating",
    color="platform",
    size="reviews",
    hover_data=["title"],
    title="Price vs Rating"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# REVIEW DISTRIBUTION PIE CHART

st.subheader("Review Distribution")

fig3 = px.pie(
    filtered_df,
    names="platform",
    values="reviews",
    title="Reviews by Platform"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# PRICE DISTRIBUTION HISTOGRAM
st.subheader("Price Distribution")

fig4 = px.histogram(
    filtered_df,
    x="price",
    nbins=20,
    title="Product Price Distribution"
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

# TOP PRODUCTS TABLE
st.subheader("Top Rated Products")

top_products = filtered_df.sort_values(
    by="rating",
    ascending=False
)

st.dataframe(
    top_products[
        [
            "title",
            "platform",
            "price",
            "rating",
            "reviews"
        ]
    ].head(10)
)

# BUSINESS INSIGHTS
st.subheader("Business Insights")

st.write(f"""
- Average product price is {average_price}
- Average product rating is {average_rating}
- Total reviews collected are {total_reviews}
- Most active platform is {top_platform}
- Dashboard helps analyze market visibility and customer engagement
""")

# FOOTER
st.markdown("---")

st.markdown(
    "Developed using Python, Streamlit, Plotly, Pandas, and SQLite"
)

# CLOSE DATABASE CONNECTION
conn.close()