-- Mart: monthly sales overview KPIs for BI, API, and executive reporting.
-- Grain: one row per source system and calendar month.

CREATE OR REPLACE VIEW marts.sales_overview AS
WITH monthly_sales AS (
    SELECT
        DATE_TRUNC('month', d.date)::date AS month_start_date,
        d.year,
        d.month,
        d.month_name,
        f.source_system,
        COUNT(*)::integer AS sales_rows,
        COUNT(DISTINCT f.invoice_no) FILTER (WHERE f.invoice_no IS NOT NULL)::integer AS invoice_count,
        SUM(COALESCE(f.quantity, 0))::numeric(16, 2) AS total_quantity,
        SUM(COALESCE(f.revenue, f.sales_amount, 0))::numeric(16, 2) AS total_revenue,
        SUM(COALESCE(f.sales_amount, 0))::numeric(16, 2) AS sales_amount
    FROM warehouse.fact_sales f
    JOIN warehouse.dim_date d
      ON d.date_key = f.date_key
    GROUP BY
        DATE_TRUNC('month', d.date)::date,
        d.year,
        d.month,
        d.month_name,
        f.source_system
),
with_order_metrics AS (
    SELECT
        month_start_date,
        year,
        month,
        month_name,
        source_system,
        sales_rows,
        invoice_count,
        CASE
            WHEN invoice_count > 0 THEN invoice_count
            ELSE sales_rows
        END AS total_orders,
        total_quantity,
        total_revenue,
        sales_amount
    FROM monthly_sales
)
SELECT
    month_start_date,
    year,
    month,
    month_name,
    source_system,
    sales_rows,
    invoice_count,
    total_orders,
    total_quantity,
    total_quantity AS units_sold,
    total_revenue,
    sales_amount,
    total_revenue AS monthly_revenue,
    ROUND(total_revenue / NULLIF(total_orders, 0), 2) AS average_order_value,
    LAG(total_revenue) OVER (
        PARTITION BY source_system
        ORDER BY month_start_date
    ) AS previous_month_revenue,
    ROUND(
        (
            total_revenue
            - LAG(total_revenue) OVER (
                PARTITION BY source_system
                ORDER BY month_start_date
            )
        )
        / NULLIF(
            LAG(total_revenue) OVER (
                PARTITION BY source_system
                ORDER BY month_start_date
            ),
            0
        )
        * 100,
        2
    ) AS revenue_growth_pct
FROM with_order_metrics;
