from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.app_components.ui import page_header
from src.config import CLEAN_DATA_PATH, QUALITY_REPORT_PATH
from src.database.database import ensure_database_ready

st.set_page_config(page_title="Data Quality", page_icon="✅", layout="wide")
ensure_database_ready()

page_header("Data Quality Report", "Cleaning summary, missing values, generated columns, and final dataset validation.")

if QUALITY_REPORT_PATH.exists():
    report = json.loads(QUALITY_REPORT_PATH.read_text(encoding="utf-8"))
    c1, c2, c3 = st.columns(3)
    c1.metric("Raw Rows", report["raw_shape"]["rows"])
    c2.metric("Cleaned Rows", report["cleaned_shape"]["rows"])
    c3.metric("Cleaned Columns", report["cleaned_shape"]["columns"])

    st.subheader("Missing Values Before Cleaning")
    st.dataframe(pd.DataFrame(report["missing_values_before"].items(), columns=["Column", "Missing Count"]), use_container_width=True, hide_index=True)

    st.subheader("Missing Values After Cleaning")
    st.dataframe(pd.DataFrame(report["missing_values_after"].items(), columns=["Column", "Missing Count"]), use_container_width=True, hide_index=True)

    st.subheader("Platforms")
    st.write(", ".join(report["platforms"]))

    st.subheader("Keywords")
    st.write(", ".join(report["keywords"]))

    st.subheader("Full JSON Report")
    st.json(report)
else:
    st.warning("Quality report not found. Run the ETL pipeline from the sidebar.")

if CLEAN_DATA_PATH.exists():
    st.subheader("Cleaned Dataset Preview")
    st.dataframe(pd.read_csv(CLEAN_DATA_PATH).head(50), use_container_width=True, hide_index=True)
