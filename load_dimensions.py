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
# LOAD CUSTOMER DIMENSION
# ============================================

print("Loading dim_customer...")

customers = pd.read_csv(
    RAW_DATA_DIR / "olist_customers_dataset.csv"
)

customers = customers.rename(columns={
    "customer_id": "customer_id",
    "customer_unique_id": "customer_unique_id",
    "customer_zip_code_prefix": "customer_zip_code_prefix",
    "customer_city": "customer_city",
    "customer_state": "customer_state"
})

try:
    customers.to_sql(
        "dim_customer",
        engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000
    )

except Exception as e:
    print("\n===== ACTUAL ERROR =====")
    print(type(e))
    print(e)

    if hasattr(e, "orig"):
        print("\n===== ORIGINAL DATABASE ERROR =====")
        print(type(e.orig))
        print(e.orig)

    raise

print(f"Loaded {len(customers):,} customers.")


# ============================================
# LOAD PRODUCT DIMENSION
# ============================================

print("Loading dim_product...")

products = pd.read_csv(
    RAW_DATA_DIR / "olist_products_dataset.csv"
)

products = products.rename(columns={
    "product_name_lenght": "product_name_length",
    "product_description_lenght": "product_description_length"
})



products.to_sql(
    "dim_product",
    engine,
    if_exists="append",
    index=False,
    chunksize=1000,
    method="multi"
)

print(f"Loaded {len(products):,} products.")


# ============================================
# LOAD SELLER DIMENSION
# ============================================

print("Loading dim_seller...")

sellers = pd.read_csv(
    RAW_DATA_DIR / "olist_sellers_dataset.csv"
)



sellers.to_sql(
    "dim_seller",
    engine,
    if_exists="append",
    index=False,
    method="multi",
    chunksize=1000
)

print(f"Loaded {len(sellers):,} sellers.")


print("\nDimension loading completed successfully.")