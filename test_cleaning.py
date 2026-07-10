from __future__ import annotations

import pandas as pd

from src.preprocessing.cleaning import clean_dataset, parse_numeric
from src.preprocessing.feature_engineering import add_features


def test_parse_numeric_handles_messy_values():
    assert parse_numeric("₹1,299.50") == 1299.50
    assert pd.isna(parse_numeric("Not Available"))
    assert pd.isna(parse_numeric("many"))


def test_clean_dataset_and_features():
    raw = pd.DataFrame(
        {
            "keyword": ["phone", "phone"],
            "title": ["Samsung Phone !!!", "SAMSUNG Phone !!!"],
            "price": ["₹10,000", "Not Available"],
            "rating": [4.5, None],
            "reviews": ["1,200", "many"],
            "platform": ["amazon", "AMAZON"],
            "delivery": ["Free Delivery", "2 Days"],
        }
    )

    cleaned = clean_dataset(raw)
    featured = add_features(cleaned)

    assert "brand" in featured.columns
    assert "visibility_score" in featured.columns
    assert featured["price"].isna().sum() == 0
    assert featured["rating"].isna().sum() == 0
