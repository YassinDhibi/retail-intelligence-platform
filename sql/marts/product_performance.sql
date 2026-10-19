-- Mart: product and department performance.
-- Grain: one row per source-aware product or Walmart department.

CREATE OR REPLACE VIEW marts.product_performance AS
WITH product_sales AS (
    SELECT
        p.product_key,
        p.product_code,
        p.product_name,
        p.department_id,
        p.product_level,
        p.source_system,
        COUNT(*)::integer AS sales_rows,
        COUNT(DISTINCT f.invoice_no) FILTER (WHERE f.invoice_no IS NOT NULL)::integer AS invoice_count,
        SUM(COALESCE(f.quantity, 0))::numeric(16, 2) AS quantity_sold,
        SUM(COALESCE(f.sales_amount, 0))::numeric(16, 2) AS total_revenue,
        AVG(f.unit_price) FILTER (WHERE f.unit_price IS NOT NULL)::numeric(14, 4) AS average_unit_price
    FROM warehouse.fact_sales f
    JOIN warehouse.dim_product p
      ON p.product_key = f.product_key
    GROUP BY
        p.product_key,
        p.product_code,
        p.product_name,
        p.department_id,
        p.product_level,
        p.source_system
)
SELECT
    product_key,
    product_code,
    product_name,
    department_id,
    product_level,
    source_system,
    sales_rows,
    invoice_count,
    quantity_sold,
    quantity_sold AS units_sold,
    total_revenue,
    total_revenue AS sales_amount,
    average_unit_price,
    ROW_NUMBER() OVER (
        PARTITION BY source_system
        ORDER BY total_revenue DESC, product_name
    ) AS revenue_rank,
    CASE
        WHEN NTILE(4) OVER (
            PARTITION BY source_system
            ORDER BY total_revenue DESC, product_name
        ) = 1 THEN 'top_quartile'
        WHEN NTILE(4) OVER (
            PARTITION BY source_system
            ORDER BY total_revenue DESC, product_name
        ) = 4 THEN 'bottom_quartile'
        ELSE 'middle'
    END AS performance_band
FROM product_sales;
