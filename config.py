"""Central project configuration.

All paths are resolved relative to the project root, so the project runs from
VS Code, terminal, and Streamlit Cloud without hardcoded local-machine paths.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
DATABASE_DIR = PROJECT_ROOT / "database"
REPORTS_DIR = PROJECT_ROOT / "reports"

RAW_DATA_PATH = RAW_DATA_DIR / "brand_dirty_dataset.csv"
API_DATA_PATH = RAW_DATA_DIR / "api_products.csv"
CLEAN_DATA_PATH = PROCESSED_DATA_DIR / "cleaned_products.csv"
QUALITY_REPORT_PATH = PROCESSED_DATA_DIR / "data_quality_report.json"
DB_PATH = DATABASE_DIR / "brand_visibility.db"

PRODUCT_TABLE = "products"

REQUIRED_BASE_COLUMNS = [
    "keyword",
    "title",
    "price",
    "rating",
    "reviews",
    "platform",
    "delivery",
]

FINAL_COLUMNS = [
    "product_id",
    "keyword",
    "title",
    "brand",
    "price",
    "raw_price",
    "discount_amount",
    "discount_pct",
    "rating",
    "reviews",
    "platform",
    "position",
    "visibility_score",
    "price_range",
    "rating_category",
    "review_category",
    "delivery",
    "delivery_category",
    "is_top_10",
    "is_popular",
    "link",
    "thumbnail",
    "source_type",
]


def ensure_directories() -> None:
    """Create all writable project directories if they do not exist."""
    for path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, DATABASE_DIR, REPORTS_DIR]:
        path.mkdir(parents=True, exist_ok=True)
