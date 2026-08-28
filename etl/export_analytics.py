
from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine


# ============================================================
# PATHS & ENVIRONMENT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ANALYTICS_DIR = PROJECT_ROOT / "data" / "analytics"
ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(PROJECT_ROOT / ".env")


# ============================================================
# DATABASE CONNECTION
# ============================================================

connection_url = (
    f"postgresql+psycopg2://"
    f"{os.getenv('POSTGRES_USER')}:"
    f"{os.getenv('POSTGRES_PASSWORD')}@"
    f"{os.getenv('POSTGRES_HOST')}:"
    f"{os.getenv('POSTGRES_PORT')}/"
    f"{os.getenv('POSTGRES_DB')}"
)

engine = create_engine(connection_url)


# ============================================================
# ANALYTICS QUERIES
# ============================================================

queries = {

    "overall_kpis": """
        SELECT
            COUNT(*) AS total_items,
            COUNT(DISTINCT order_id) AS total_orders,
            SUM(price) AS total_product_revenue,
            SUM(freight_value) AS total_freight,
            SUM(item_total) AS total_sales,
            AVG(item_total) AS average_item_value
        FROM fact_sales;
    """,

    "monthly_sales": """
        SELECT
            d.year,
            d.month,
            d.month_name,
            COUNT(*) AS items_sold,
            SUM(f.item_total) AS total_sales
        FROM fact_sales f
        JOIN dim_date d
            ON f.date_key = d.date_key
        GROUP BY
            d.year,
            d.month,
            d.month_name
        ORDER BY
            d.year,
            d.month;
    """,

    "category_sales": """
        SELECT
            COALESCE(p.product_category_name, 'Unknown') AS category,
            COUNT(*) AS items_sold,
            COUNT(DISTINCT f.order_id) AS orders,
            SUM(f.item_total) AS total_sales
        FROM fact_sales f
        JOIN dim_product p
            ON f.product_key = p.product_key
        GROUP BY
            COALESCE(p.product_category_name, 'Unknown')
        ORDER BY
            total_sales DESC;
    """,

    "state_sales": """
        SELECT
            c.customer_state,
            COUNT(DISTINCT c.customer_key) AS customers,
            COUNT(*) AS items_sold,
            SUM(f.item_total) AS total_sales
        FROM fact_sales f
        JOIN dim_customer c
            ON f.customer_key = c.customer_key
        GROUP BY
            c.customer_state
        ORDER BY
            total_sales DESC;
    """,

    "customer_type": """
    WITH customer_orders AS (
        SELECT
            c.customer_unique_id,
            COUNT(DISTINCT f.order_id) AS order_count
        FROM fact_sales f
        JOIN dim_customer c
            ON f.customer_key = c.customer_key
        GROUP BY c.customer_unique_id
    )

    SELECT
        CASE
            WHEN order_count = 1 THEN 'One-time customer'
            ELSE 'Repeat customer'
        END AS customer_type,
        COUNT(*) AS customer_count
    FROM customer_orders
    GROUP BY
        CASE
            WHEN order_count = 1 THEN 'One-time customer'
            ELSE 'Repeat customer'
        END
    ORDER BY customer_count DESC
""",

    "yearly_sales": """
        SELECT
            d.year,
            COUNT(DISTINCT f.order_id) AS orders,
            SUM(f.item_total) AS total_sales,
            AVG(f.item_total) AS average_item_value
        FROM fact_sales f
        JOIN dim_date d
            ON f.date_key = d.date_key
        GROUP BY
            d.year
        ORDER BY
            d.year;
    """,

    "top_products": """
        SELECT
            p.product_id,
            COALESCE(p.product_category_name, 'Unknown') AS category,
            COUNT(*) AS items_sold,
            COUNT(DISTINCT f.order_id) AS orders,
            SUM(f.item_total) AS total_sales
        FROM fact_sales f
        JOIN dim_product p
            ON f.product_key = p.product_key
        GROUP BY
            p.product_id,
            COALESCE(p.product_category_name, 'Unknown')
        ORDER BY
            total_sales DESC
        LIMIT 20;
    """,

    "top_sellers": """
        SELECT
            s.seller_id,
            s.seller_city,
            s.seller_state,
            COUNT(*) AS items_sold,
            COUNT(DISTINCT f.order_id) AS orders,
            SUM(f.item_total) AS total_sales
        FROM fact_sales f
        JOIN dim_seller s
            ON f.seller_key = s.seller_key
        GROUP BY
            s.seller_id,
            s.seller_city,
            s.seller_state
        ORDER BY
            total_sales DESC
        LIMIT 20;
    """,

    "category_year": """
        SELECT
            d.year,
            COALESCE(p.product_category_name, 'Unknown') AS category,
            SUM(f.item_total) AS total_sales
        FROM fact_sales f
        JOIN dim_product p
            ON f.product_key = p.product_key
        JOIN dim_date d
            ON f.date_key = d.date_key
        GROUP BY
            d.year,
            COALESCE(p.product_category_name, 'Unknown')
        ORDER BY
            d.year,
            total_sales DESC;
    """,

    "city_sales": """
        SELECT
            c.customer_city,
            c.customer_state,
            COUNT(*) AS items_sold,
            COUNT(DISTINCT f.order_id) AS orders,
            SUM(f.item_total) AS total_sales
        FROM fact_sales f
        JOIN dim_customer c
            ON f.customer_key = c.customer_key
        GROUP BY
            c.customer_city,
            c.customer_state
        ORDER BY
            total_sales DESC
        LIMIT 20;
    """,

    "freight_analysis": """
        SELECT
            d.year,
            SUM(f.freight_value) AS total_freight,
            AVG(f.freight_value) AS average_freight,
            AVG(f.price) AS average_product_price
        FROM fact_sales f
        JOIN dim_date d
            ON f.date_key = d.date_key
        GROUP BY
            d.year
        ORDER BY
            d.year;
    """,

    "category_ranking": """
        SELECT
            COALESCE(p.product_category_name, 'Unknown') AS category,
            SUM(f.item_total) AS total_sales,
            RANK() OVER (
                ORDER BY SUM(f.item_total) DESC
            ) AS sales_rank
        FROM fact_sales f
        JOIN dim_product p
            ON f.product_key = p.product_key
        GROUP BY
            COALESCE(p.product_category_name, 'Unknown')
        ORDER BY
            sales_rank;
    """
}


# ============================================================
# EXPORT ANALYTICS
# ============================================================

print("\n============================================")
print("EXPORTING ANALYTICS DATA")
print("============================================\n")

for name, query in queries.items():

    print(f"Exporting {name}...")

    df = pd.read_sql(query, engine)

    output_file = ANALYTICS_DIR / f"{name}.csv"

    df.to_csv(output_file, index=False)

    print(f"  ✓ {len(df):,} rows → {output_file.name}")


print("\n============================================")
print("ANALYTICS EXPORT COMPLETED SUCCESSFULLY")
print("============================================")

