-- Mart: customer and geography performance.
-- Grain: one row per source-aware customer profile.

CREATE OR REPLACE VIEW marts.customer_performance AS
WITH customer_sales AS (
    SELECT
        c.customer_key,
        c.customer_id,
        c.customer_reference,
        c.country,
        c.is_unknown,
        c.source_system,
        MIN(d.date) AS first_purchase_date,
        MAX(d.date) AS last_purchase_date,
        COUNT(*)::integer AS sales_rows,
        COUNT(DISTINCT f.invoice_no) FILTER (WHERE f.invoice_no IS NOT NULL)::integer AS invoice_count,
        SUM(COALESCE(f.sales_amount, 0))::numeric(16, 2) AS total_revenue
    FROM warehouse.fact_sales f
    JOIN warehouse.dim_customer c
      ON c.customer_key = f.customer_key
    JOIN warehouse.dim_date d
      ON d.date_key = f.date_key
    GROUP BY
        c.customer_key,
        c.customer_id,
        c.customer_reference,
        c.country,
        c.is_unknown,
        c.source_system
),
with_segments AS (
    SELECT
        *,
        CASE
            WHEN invoice_count > 0 THEN ROUND(total_revenue / NULLIF(invoice_count, 0), 2)
            ELSE ROUND(total_revenue / NULLIF(sales_rows, 0), 2)
        END AS average_order_value,
        CASE
            WHEN invoice_count > 1 THEN TRUE
            ELSE FALSE
        END AS is_repeat_customer,
        NTILE(4) OVER (
            PARTITION BY source_system
            ORDER BY total_revenue DESC, customer_reference
        ) AS revenue_quartile
    FROM customer_sales
)
SELECT
    customer_key,
    customer_id,
    customer_reference,
    country,
    is_unknown,
    source_system,
    first_purchase_date,
    last_purchase_date,
    sales_rows,
    invoice_count,
    total_revenue,
    total_revenue AS sales_amount,
    average_order_value,
    is_repeat_customer,
    CASE
        WHEN is_unknown THEN 'unknown'
        WHEN revenue_quartile = 1 THEN 'high_value'
        WHEN revenue_quartile = 4 THEN 'low_value'
        ELSE 'standard'
    END AS customer_segment
FROM with_segments;
