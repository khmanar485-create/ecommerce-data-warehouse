-- ============================================
-- E-COMMERCE DATA WAREHOUSE
-- Star Schema
-- ============================================

DROP TABLE IF EXISTS fact_sales CASCADE;
DROP TABLE IF EXISTS dim_customer CASCADE;
DROP TABLE IF EXISTS dim_product CASCADE;
DROP TABLE IF EXISTS dim_seller CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;


-- ============================================
-- DIMENSION: CUSTOMER
-- ============================================

CREATE TABLE dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id VARCHAR(32) NOT NULL UNIQUE,
    customer_unique_id VARCHAR(32),
    customer_zip_code_prefix INTEGER,
    customer_city VARCHAR(100),
    customer_state VARCHAR(2)
);


-- ============================================
-- DIMENSION: PRODUCT
-- ============================================

CREATE TABLE dim_product (
    product_key SERIAL PRIMARY KEY,
    product_id VARCHAR(32) NOT NULL UNIQUE,
    product_category_name VARCHAR(100),
    product_name_length INTEGER,
    product_description_length INTEGER,
    product_photos_qty INTEGER,
    product_weight_g NUMERIC,
    product_length_cm NUMERIC,
    product_height_cm NUMERIC,
    product_width_cm NUMERIC
);


-- ============================================
-- DIMENSION: SELLER
-- ============================================

CREATE TABLE dim_seller (
    seller_key SERIAL PRIMARY KEY,
    seller_id VARCHAR(32) NOT NULL UNIQUE,
    seller_zip_code_prefix INTEGER,
    seller_city VARCHAR(100),
    seller_state VARCHAR(2)
);


-- ============================================
-- DIMENSION: DATE
-- ============================================

CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    day INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(20) NOT NULL
);


-- ============================================
-- FACT: SALES
-- Grain:
-- One row = one product item within an order
-- ============================================

CREATE TABLE fact_sales (
    sales_key SERIAL PRIMARY KEY,

    order_id VARCHAR(32) NOT NULL,
    order_item_id INTEGER NOT NULL,

    customer_key INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    seller_key INTEGER NOT NULL,
    date_key INTEGER NOT NULL,

    price NUMERIC(12,2),
    freight_value NUMERIC(12,2),
    item_total NUMERIC(12,2),

    CONSTRAINT fk_customer
        FOREIGN KEY (customer_key)
        REFERENCES dim_customer(customer_key),

    CONSTRAINT fk_product
        FOREIGN KEY (product_key)
        REFERENCES dim_product(product_key),

    CONSTRAINT fk_seller
        FOREIGN KEY (seller_key)
        REFERENCES dim_seller(seller_key),

    CONSTRAINT fk_date
        FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key)
);


-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX idx_fact_sales_customer
    ON fact_sales(customer_key);

CREATE INDEX idx_fact_sales_product
    ON fact_sales(product_key);

CREATE INDEX idx_fact_sales_seller
    ON fact_sales(seller_key);

CREATE INDEX idx_fact_sales_date
    ON fact_sales(date_key);

CREATE INDEX idx_fact_sales_order
    ON fact_sales(order_id);