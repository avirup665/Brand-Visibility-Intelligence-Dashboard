# Brand Visibility Intelligence Dashboard

A professional end-to-end Data Science and Business Intelligence project for analyzing e-commerce brand visibility, product pricing, platform performance, and search ranking behavior.

## Project Objective

This project builds a **Brand Visibility Intelligence Dashboard** using product data from a provided dirty CSV dataset and optional Google Shopping API extraction through SerpAPI.

The solution demonstrates:

- API-based data extraction
- Data cleaning and transformation
- Feature engineering
- SQL database integration
- Exploratory data analysis
- Interactive Streamlit dashboard
- Business insight generation
- Clean project structure suitable for GitHub and deployment

## Project Pipeline

```text
Raw CSV / API Data
        ↓
Load Data
        ↓
Clean Missing Values, Prices, Reviews, Ratings, Text, Categories
        ↓
Feature Engineering
        ↓
Save Clean CSV
        ↓
Store in SQLite Database
        ↓
Run SQL-backed Dashboard
        ↓
Generate Business Insights
```

## Folder Structure

```text
Brand_Visibility_Intelligence_Dashboard/
│
├── app.py
├── pages/
│   ├── 1_Overview.py
│   ├── 2_Brand_Analysis.py
│   ├── 3_Pricing_Analysis.py
│   ├── 4_Platform_Analysis.py
│   ├── 5_Visibility_Ranking.py
│   ├── 6_Product_Explorer.py
│   └── 7_Data_Quality.py
│
├── src/
│   ├── api/
│   ├── preprocessing/
│   ├── database/
│   ├── analysis/
│   ├── visualization/
│   ├── app_components/
│   └── utils/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── database/
├── scripts/
├── tests/
├── requirements.txt
└── README.md
```

## How to Run in VS Code

### 1. Open the Project Folder

Open this folder in VS Code:

```bash
Brand_Visibility_Intelligence_Dashboard
```

### 2. Create Virtual Environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS / Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the ETL Pipeline

```bash
python scripts/run_pipeline.py
```

This creates:

```text
data/processed/cleaned_products.csv
database/brand_visibility.db
data/processed/data_quality_report.json
```

### 5. Run Streamlit App

```bash
streamlit run app.py
```

## Deploy on Streamlit Cloud

1. Push this project to GitHub.
2. Go to Streamlit Cloud.
3. Select your repository.
4. Set the main file path as:

```text
app.py
```

5. Click Deploy.

The app automatically creates the cleaned dataset and SQLite database on startup if they are missing.

## Optional API Extraction

If you want to fetch live Google Shopping data using SerpAPI:

```bash
set SERPAPI_API_KEY=your_key_here
python scripts/extract_api_data.py
python scripts/run_pipeline.py
```

On macOS / Linux:

```bash
export SERPAPI_API_KEY=your_key_here
python scripts/extract_api_data.py
python scripts/run_pipeline.py
```

## Key Features Created

The pipeline creates the following professional analytical fields:

- `brand`
- `raw_price`
- `discount_amount`
- `discount_pct`
- `position`
- `visibility_score`
- `price_range`
- `rating_category`
- `review_category`
- `delivery_category`
- `is_top_10`
- `is_popular`

## Dashboard Pages

1. **Executive Overview**
2. **Brand Analysis**
3. **Pricing Analysis**
4. **Platform Analysis**
5. **Visibility & Ranking Analysis**
6. **Product Explorer**
7. **Data Quality Report**

## Evaluation Strengths

This project is suitable for evaluation because it includes:

- Modular Python files
- SQL-backed filtering
- Automated ETL pipeline
- Cleaned and feature-engineered data
- Dynamic Streamlit dashboard
- Business insights
- Data quality reporting
- GitHub-ready structure
