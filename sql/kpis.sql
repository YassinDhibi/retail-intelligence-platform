-- KPI queries for validation, analysis, and Power BI checks.

-- Overall sales summary
SELECT
    source_system,
    COUNT(*) AS sales_rows,
    SUM(COALESCE(quantity, 0)) AS units_sold,
    SUM(COALESCE(sales_amount, 0))::numeric(14, 2) AS sales_amount
FROM warehouse.fact_sales
GROUP BY source_system
ORDER BY sales_amount DESC;

-- Monthly sales trend
SELECT
    year,
    month,
    source_system,
    SUM(sales_amount)::numeric(14, 2) AS sales_amount
FROM marts.sales_overview
GROUP BY year, month, source_system
ORDER BY year, month, source_system;

-- Top products or departments
SELECT
    product_name,
    source_system,
    sales_rows,
    units_sold,
    sales_amount
FROM marts.product_performance
ORDER BY sales_amount DESC
LIMIT 20;

-- Customer geography for Online Retail
SELECT
    country,
    invoice_count,
    sales_rows,
    sales_amount
FROM marts.customer_performance
WHERE source_system = 'online_retail'
ORDER BY sales_amount DESC
LIMIT 20;

-- Walmart store performance
SELECT
    store_id,
    store_type,
    store_size,
    sales_rows,
    sales_amount,
    sales_per_store_size
FROM marts.store_performance
WHERE source_system = 'walmart'
ORDER BY sales_amount DESC
LIMIT 20;

-- Holiday impact for Walmart training records
SELECT
    is_holiday,
    COUNT(*) AS sales_rows,
    AVG(weekly_sales_amount)::numeric(14, 2) AS average_weekly_sales,
    SUM(weekly_sales_amount)::numeric(14, 2) AS total_weekly_sales
FROM warehouse.fact_sales
WHERE source_system = 'walmart'
GROUP BY is_holiday
ORDER BY is_holiday;
