
from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine


# ============================================
# PATHS & ENVIRONMENT
# ============================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

load_dotenv(PROJECT_ROOT / ".env")


# ============================================
# DATABASE CONNECTION
# ============================================

connection_url = (
    f"postgresql+psycopg2://"
    f"{os.getenv('POSTGRES_USER')}:"
    f"{os.getenv('POSTGRES_PASSWORD')}@"
    f"{os.getenv('POSTGRES_HOST')}:"
    f"{os.getenv('POSTGRES_PORT')}/"
    f"{os.getenv('POSTGRES_DB')}"
)

engine = create_engine(connection_url)


# ============================================
# LOAD ORDER DATES
# ============================================

print("Loading dim_date...")

orders = pd.read_csv(
    RAW_DATA_DIR / "olist_orders_dataset.csv"
)

# Convert order purchase timestamp to datetime
orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"]
)

# Get the required date range
min_date = orders["order_purchase_timestamp"].dt.date.min()
max_date = orders["order_purchase_timestamp"].dt.date.max()

print(f"Date range: {min_date} → {max_date}")


# ============================================
# GENERATE DATE DIMENSION
# ============================================

date_range = pd.date_range(
    start=min_date,
    end=max_date,
    freq="D"
)

dates = pd.DataFrame({
    "full_date": date_range
})

dates["year"] = dates["full_date"].dt.year
dates["quarter"] = dates["full_date"].dt.quarter
dates["month"] = dates["full_date"].dt.month
dates["month_name"] = dates["full_date"].dt.month_name()
dates["day"] = dates["full_date"].dt.day

# Monday = 1, Sunday = 7
dates["day_of_week"] = dates["full_date"].dt.dayofweek + 1
dates["day_name"] = dates["full_date"].dt.day_name()

# Generate YYYYMMDD integer key
dates["date_key"] = (
    dates["full_date"].dt.year * 10000
    + dates["full_date"].dt.month * 100
    + dates["full_date"].dt.day
)

# Match database column order
dates = dates[
    [
        "date_key",
        "full_date",
        "year",
        "quarter",
        "month",
        "month_name",
        "day",
        "day_of_week",
        "day_name"
    ]
]





# ============================================
# INSERT DATE DIMENSION
# ============================================

dates.to_sql(
    "dim_date",
    engine,
    if_exists="append",
    index=False,
    method="multi"
)

print(f"Loaded {len(dates):,} dates.")

print("\nDate dimension loading completed successfully.")

