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
# LOAD SOURCE DATA
# ============================================

print("Loading order items...")

order_items = pd.read_csv(
    RAW_DATA_DIR / "olist_order_items_dataset.csv"
)

print(f"Order items: {len(order_items):,}")


print("Loading orders...")

orders = pd.read_csv(
    RAW_DATA_DIR / "olist_orders_dataset.csv"
)

print(f"Orders: {len(orders):,}")


# ============================================
# PREPARE ORDERS
# ============================================

orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"]
)

orders = orders[
    [
        "order_id",
        "customer_id",
        "order_purchase_timestamp"
    ]
]


# ============================================
# JOIN ORDER ITEMS WITH ORDERS
# ============================================

print("Joining order items with orders...")

sales = order_items.merge(
    orders,
    on="order_id",
    how="inner"
)

print(f"Joined sales records: {len(sales):,}")


# ============================================
# LOAD DIMENSION LOOKUPS
# ============================================

print("Loading dimension keys...")

dim_customer = pd.read_sql(
    """
    SELECT customer_key, customer_id
    FROM dim_customer
    """,
    engine
)

dim_product = pd.read_sql(
    """
    SELECT product_key, product_id
    FROM dim_product
    """,
    engine
)

dim_seller = pd.read_sql(
    """
    SELECT seller_key, seller_id
    FROM dim_seller
    """,
    engine
)

dim_date = pd.read_sql(
    """
    SELECT date_key, full_date
    FROM dim_date
    """,
    engine
)


# ============================================
# MAP CUSTOMER KEY
# ============================================

print("Mapping customer keys...")

sales = sales.merge(
    dim_customer,
    on="customer_id",
    how="left"
)


# ============================================
# MAP PRODUCT KEY
# ============================================

print("Mapping product keys...")

sales = sales.merge(
    dim_product,
    on="product_id",
    how="left"
)


# ============================================
# MAP SELLER KEY
# ============================================

print("Mapping seller keys...")

sales = sales.merge(
    dim_seller,
    on="seller_id",
    how="left"
)


# ============================================
# MAP DATE KEY
# ============================================

print("Mapping date keys...")

sales["full_date"] = sales["order_purchase_timestamp"].dt.date

dim_date["full_date"] = pd.to_datetime(
    dim_date["full_date"]
).dt.date

sales = sales.merge(
    dim_date,
    on="full_date",
    how="left"
)


# ============================================
# CHECK FOREIGN KEY MAPPINGS
# ============================================

print("\nChecking dimension mappings...")

print(
    f"Missing customer keys: "
    f"{sales['customer_key'].isna().sum():,}"
)

print(
    f"Missing product keys: "
    f"{sales['product_key'].isna().sum():,}"
)

print(
    f"Missing seller keys: "
    f"{sales['seller_key'].isna().sum():,}"
)

print(
    f"Missing date keys: "
    f"{sales['date_key'].isna().sum():,}"
)


# ============================================
# CALCULATE ITEM TOTAL
# ============================================

sales["item_total"] = (
    sales["price"].fillna(0)
    + sales["freight_value"].fillna(0)
)


# ============================================
# SELECT FACT TABLE COLUMNS
# ============================================

fact_sales = sales[
    [
        "order_id",
        "order_item_id",
        "customer_key",
        "product_key",
        "seller_key",
        "date_key",
        "price",
        "freight_value",
        "item_total"
    ]
].copy()


# ============================================
# VALIDATION
# ============================================

if fact_sales[
    [
        "customer_key",
        "product_key",
        "seller_key",
        "date_key"
    ]
].isna().any().any():

    raise ValueError(
        "Some foreign keys could not be mapped. "
        "Check the dimension tables before loading fact_sales."
    )


# ============================================
# LOAD FACT TABLE
# ============================================

print("\nLoading fact_sales...")

fact_sales.to_sql(
    "fact_sales",
    engine,
    if_exists="append",
    index=False,
    chunksize=1000,
    method="multi"
)

print(
    f"Loaded {len(fact_sales):,} rows into fact_sales."
)

print("\nFact table loading completed successfully.")