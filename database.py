"""SQLite database layer for Streamlit and analysis scripts."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import CLEAN_DATA_PATH, DB_PATH, PRODUCT_TABLE, ensure_directories


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection."""
    ensure_directories()
    return sqlite3.connect(DB_PATH)




def _restore_boolean_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """Convert SQLite 0/1 flag columns back to pandas Boolean dtype."""
    for column in ("is_top_10", "is_popular"):
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce").fillna(0).eq(1)
    return frame

def initialize_database(frame: pd.DataFrame | None = None) -> None:
    """Create or refresh SQLite tables from the cleaned DataFrame."""
    ensure_directories()

    if frame is None:
        if not CLEAN_DATA_PATH.exists():
            from src.preprocessing.pipeline import run_pipeline

            frame = run_pipeline(save_database=False)
        else:
            frame = pd.read_csv(CLEAN_DATA_PATH)

    with get_connection() as conn:
        frame.to_sql(PRODUCT_TABLE, conn, if_exists="replace", index=False)

        conn.execute(f"CREATE INDEX IF NOT EXISTS idx_products_brand ON {PRODUCT_TABLE}(brand);")
        conn.execute(f"CREATE INDEX IF NOT EXISTS idx_products_platform ON {PRODUCT_TABLE}(platform);")
        conn.execute(f"CREATE INDEX IF NOT EXISTS idx_products_keyword ON {PRODUCT_TABLE}(keyword);")
        conn.execute(f"CREATE INDEX IF NOT EXISTS idx_products_position ON {PRODUCT_TABLE}(position);")

        conn.execute("DROP VIEW IF EXISTS brand_summary;")
        conn.execute(
            f"""
            CREATE VIEW brand_summary AS
            SELECT
                brand,
                COUNT(*) AS product_count,
                ROUND(AVG(price), 2) AS avg_price,
                ROUND(AVG(rating), 2) AS avg_rating,
                ROUND(AVG(visibility_score), 2) AS avg_visibility_score,
                SUM(CASE WHEN is_top_10 = 1 THEN 1 ELSE 0 END) AS top_10_count
            FROM {PRODUCT_TABLE}
            GROUP BY brand;
            """
        )

        conn.execute("DROP VIEW IF EXISTS platform_summary;")
        conn.execute(
            f"""
            CREATE VIEW platform_summary AS
            SELECT
                platform,
                COUNT(*) AS product_count,
                ROUND(AVG(price), 2) AS avg_price,
                ROUND(AVG(rating), 2) AS avg_rating,
                ROUND(AVG(position), 2) AS avg_position
            FROM {PRODUCT_TABLE}
            GROUP BY platform;
            """
        )


def ensure_database_ready() -> None:
    """Create cleaned CSV and database automatically if missing."""
    if not CLEAN_DATA_PATH.exists() or not DB_PATH.exists():
        from src.preprocessing.pipeline import run_pipeline

        run_pipeline(save_database=True)


def read_table(table_name: str = PRODUCT_TABLE) -> pd.DataFrame:
    """Read a full SQLite table or view."""
    ensure_database_ready()
    with get_connection() as conn:
        frame = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    return _restore_boolean_columns(frame)


def _add_in_filter(where: list[str], params: list[Any], column: str, values: list[str] | tuple[str, ...] | None) -> None:
    clean_values = [value for value in (values or []) if value and value != "All"]
    if clean_values:
        placeholders = ", ".join(["?"] * len(clean_values))
        where.append(f"{column} IN ({placeholders})")
        params.extend(clean_values)


def build_filter_clause(filters: dict | None = None) -> tuple[str, list[Any]]:
    """Create a safe SQL WHERE clause from Streamlit filters."""
    filters = filters or {}
    where: list[str] = []
    params: list[Any] = []

    _add_in_filter(where, params, "brand", filters.get("brand"))
    _add_in_filter(where, params, "platform", filters.get("platform"))
    _add_in_filter(where, params, "keyword", filters.get("keyword"))
    _add_in_filter(where, params, "price_range", filters.get("price_range"))

    rating_range = filters.get("rating_range")
    if rating_range and len(rating_range) == 2:
        where.append("rating BETWEEN ? AND ?")
        params.extend([float(rating_range[0]), float(rating_range[1])])

    price_range_numeric = filters.get("price_range_numeric")
    if price_range_numeric and len(price_range_numeric) == 2:
        where.append("price BETWEEN ? AND ?")
        params.extend([float(price_range_numeric[0]), float(price_range_numeric[1])])

    position_range = filters.get("position_range")
    if position_range and len(position_range) == 2:
        where.append("position BETWEEN ? AND ?")
        params.extend([int(position_range[0]), int(position_range[1])])

    search = str(filters.get("search", "")).strip()
    if search:
        where.append("(LOWER(title) LIKE ? OR LOWER(brand) LIKE ? OR LOWER(keyword) LIKE ?)")
        pattern = f"%{search.lower()}%"
        params.extend([pattern, pattern, pattern])

    clause = f"WHERE {' AND '.join(where)}" if where else ""
    return clause, params


def query_products(filters: dict | None = None, limit: int | None = None) -> pd.DataFrame:
    """Read products using optional dynamic SQL filters."""
    ensure_database_ready()

    where_clause, params = build_filter_clause(filters)
    query = f"SELECT * FROM {PRODUCT_TABLE} {where_clause} ORDER BY visibility_score DESC, rating DESC"

    if limit is not None:
        query += " LIMIT ?"
        params.append(int(limit))

    with get_connection() as conn:
        frame = pd.read_sql_query(query, conn, params=params)
    return _restore_boolean_columns(frame)


def get_filter_options() -> dict:
    """Return distinct values and numeric ranges for dashboard filters."""
    ensure_database_ready()

    with get_connection() as conn:
        products = pd.read_sql_query(
            f"""
            SELECT brand, platform, keyword, price_range, rating, price, position
            FROM {PRODUCT_TABLE};
            """,
            conn,
        )

    if products.empty:
        return {
            "brands": [],
            "platforms": [],
            "keywords": [],
            "price_ranges": [],
            "rating_min": 0.0,
            "rating_max": 5.0,
            "price_min": 0.0,
            "price_max": 0.0,
            "position_min": 1,
            "position_max": 1,
        }

    return {
        "brands": sorted(products["brand"].dropna().unique().tolist()),
        "platforms": sorted(products["platform"].dropna().unique().tolist()),
        "keywords": sorted(products["keyword"].dropna().unique().tolist()),
        "price_ranges": sorted(products["price_range"].dropna().unique().tolist()),
        "rating_min": float(products["rating"].min()),
        "rating_max": float(products["rating"].max()),
        "price_min": float(products["price"].min()),
        "price_max": float(products["price"].max()),
        "position_min": int(products["position"].min()),
        "position_max": int(products["position"].max()),
    }


def run_sql_query(query: str) -> pd.DataFrame:
    """Run a read-only SQL query for analysis pages."""
    ensure_database_ready()
    normalized = query.strip().lower()
    if not normalized.startswith("select"):
        raise ValueError("Only SELECT queries are allowed from the dashboard.")

    with get_connection() as conn:
        return pd.read_sql_query(query, conn)
