-- ============================================================
-- E-COMMERCE DATA WAREHOUSE
-- ANALYTICS QUERIES
-- ============================================================


-- ============================================================
-- 1. OVERALL SALES KPIs
-- ============================================================

SELECT
    COUNT(*) AS total_items,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(price) AS total_product_revenue,
    SUM(freight_value) AS total_freight,
    SUM(item_total) AS total_sales,
    AVG(item_total) AS average_item_value
FROM fact_sales;


-- ============================================================
-- 2. MONTHLY SALES PERFORMANCE
-- ============================================================

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


-- ============================================================
-- 3. SALES BY PRODUCT CATEGORY
-- ============================================================

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


-- ============================================================
-- 4. SALES BY CUSTOMER STATE
-- ============================================================

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


-- ============================================================
-- 5. ONE-TIME VS REPEAT CUSTOMERS
-- ============================================================


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
ORDER BY customer_count DESC;


-- ============================================================
-- 6. YEARLY SALES PERFORMANCE
-- ============================================================

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


-- ============================================================
-- 7. TOP 20 PRODUCTS BY REVENUE
-- ============================================================

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


-- ============================================================
-- 8. TOP 20 SELLERS BY REVENUE
-- ============================================================

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


-- ============================================================
-- 9. SALES BY PRODUCT CATEGORY AND YEAR
-- ============================================================

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


-- ============================================================
-- 10. SALES BY CUSTOMER CITY
-- ============================================================

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


-- ============================================================
-- 11. FREIGHT ANALYSIS
-- ============================================================

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


-- ============================================================
-- 12. CATEGORY SALES RANKING
-- ============================================================

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


-- ============================================================
-- END OF ANALYTICS QUERIES
-- ============================================================