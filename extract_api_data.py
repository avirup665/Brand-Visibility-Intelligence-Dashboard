"""Optional script to collect live Google Shopping data using SerpAPI.

Before running:
    set SERPAPI_API_KEY=your_key_here          # Windows PowerShell
    export SERPAPI_API_KEY=your_key_here       # macOS/Linux

Usage:
    python scripts/extract_api_data.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.api.serpapi_extractor import SerpAPIExtractor


def main() -> None:
    keywords = [
        "office chair ergonomic",
        "microwave oven convection",
        "power bank fast charging",
        "men running shoes",
        "air fryer india",
    ]

    extractor = SerpAPIExtractor()
    if not extractor.is_configured():
        print("SERPAPI_API_KEY not found. Skipping API extraction.")
        return

    frame = extractor.save_keywords(keywords, max_results_per_keyword=40)
    print(f"Saved {len(frame):,} API rows to data/raw/api_products.csv")


if __name__ == "__main__":
    main()
