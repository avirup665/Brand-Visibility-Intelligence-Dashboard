"""Optional Google Shopping extraction using SerpAPI.

The project can run fully with the provided CSV dataset. If a SERPAPI_API_KEY is
available, this module can fetch additional live Google Shopping rows and save
them into data/raw/api_products.csv.
"""

from __future__ import annotations

import os
import time
from typing import Iterable

import pandas as pd
import requests

from src.config import API_DATA_PATH, ensure_directories
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SerpAPIExtractor:
    """Small production-friendly wrapper around SerpAPI Google Shopping."""

    ENDPOINT = "https://serpapi.com/search.json"

    def __init__(self, api_key: str | None = None, country: str = "in", language: str = "en"):
        self.api_key = api_key or os.getenv("SERPAPI_API_KEY")
        self.country = country
        self.language = language

    def is_configured(self) -> bool:
        """Return True if an API key is available."""
        return bool(self.api_key)

    def fetch_keyword(self, keyword: str, max_results: int = 40) -> pd.DataFrame:
        """Fetch product rows for one keyword.

        Parameters
        ----------
        keyword:
            Shopping search term, for example "wireless earbuds".
        max_results:
            Maximum number of rows to keep from SerpAPI shopping results.
        """
        if not self.api_key:
            logger.warning("SERPAPI_API_KEY is not configured. Returning an empty DataFrame.")
            return pd.DataFrame()

        params = {
            "engine": "google_shopping",
            "q": keyword,
            "api_key": self.api_key,
            "gl": self.country,
            "hl": self.language,
        }

        response = requests.get(self.ENDPOINT, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()

        rows: list[dict] = []
        shopping_results = payload.get("shopping_results", [])[:max_results]

        for idx, item in enumerate(shopping_results, start=1):
            rows.append(
                {
                    "keyword": keyword,
                    "title": item.get("title"),
                    "price": item.get("extracted_price") or item.get("price"),
                    "raw_price": item.get("extracted_old_price") or item.get("old_price"),
                    "rating": item.get("rating"),
                    "reviews": item.get("reviews"),
                    "platform": item.get("source"),
                    "position": item.get("position") or idx,
                    "delivery": item.get("delivery") or item.get("extensions", ["Unknown"])[0],
                    "link": item.get("link") or item.get("product_link"),
                    "thumbnail": item.get("thumbnail"),
                    "source_type": "api",
                }
            )

        return pd.DataFrame(rows)

    def fetch_keywords(self, keywords: Iterable[str], max_results_per_keyword: int = 40, pause_seconds: float = 1.0) -> pd.DataFrame:
        """Fetch and combine data for multiple keywords."""
        frames: list[pd.DataFrame] = []

        for keyword in keywords:
            logger.info("Fetching shopping data for keyword: %s", keyword)
            try:
                frame = self.fetch_keyword(keyword, max_results=max_results_per_keyword)
                if not frame.empty:
                    frames.append(frame)
            except Exception as exc:  # API failures should not break local project use.
                logger.error("Failed to fetch keyword '%s': %s", keyword, exc)
            time.sleep(pause_seconds)

        if not frames:
            return pd.DataFrame()

        return pd.concat(frames, ignore_index=True)

    def save_keywords(self, keywords: Iterable[str], max_results_per_keyword: int = 40) -> pd.DataFrame:
        """Fetch keywords and save them to data/raw/api_products.csv."""
        ensure_directories()
        frame = self.fetch_keywords(keywords, max_results_per_keyword=max_results_per_keyword)
        if frame.empty:
            logger.warning("No API rows were saved because extraction returned no data.")
            return frame

        frame.to_csv(API_DATA_PATH, index=False)
        logger.info("Saved API data to %s", API_DATA_PATH)
        return frame


def main() -> None:
    """Manual CLI entry point."""
    keywords = ["smartphone", "laptop", "running shoes", "air fryer", "office chair"]
    extractor = SerpAPIExtractor()
    extractor.save_keywords(keywords)


if __name__ == "__main__":
    main()
