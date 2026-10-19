-- Mart: Walmart store performance and online-channel fallback.
-- Grain: one row per source-aware store or channel.

CREATE OR REPLACE VIEW marts.store_performance AS
WITH store_sales AS (
    SELECT
        s.store_key,
        s.store_id,
        s.store_reference,
        s.store_name,
        s.store_type,
        s.store_size,
        s.is_physical_store,
        s.is_unknown,
        s.source_system,
        MIN(d.date) AS first_sales_date,
        MAX(d.date) AS last_sales_date,
        COUNT(*)::integer AS sales_rows,
        SUM(COALESCE(f.sales_amount, 0))::numeric(16, 2) AS total_revenue,
        SUM(COALESCE(f.sales_amount, 0)) FILTER (WHERE f.is_holiday IS TRUE)::numeric(16, 2) AS holiday_revenue,
        SUM(COALESCE(f.sales_amount, 0)) FILTER (WHERE f.is_holiday IS FALSE)::numeric(16, 2) AS non_holiday_revenue
    FROM warehouse.fact_sales f
    JOIN warehouse.dim_store s
      ON s.store_key = f.store_key
    JOIN warehouse.dim_date d
      ON d.date_key = f.date_key
    GROUP BY
        s.store_key,
        s.store_id,
        s.store_reference,
        s.store_name,
        s.store_type,
        s.store_size,
        s.is_physical_store,
        s.is_unknown,
        s.source_system
)
SELECT
    store_key,
    store_id,
    store_reference,
    store_name,
    store_type,
    store_size,
    is_physical_store,
    is_unknown,
    source_system,
    first_sales_date,
    last_sales_date,
    sales_rows,
    total_revenue,
    total_revenue AS sales_amount,
    COALESCE(holiday_revenue, 0) AS holiday_revenue,
    COALESCE(non_holiday_revenue, 0) AS non_holiday_revenue,
    CASE
        WHEN store_size IS NULL OR store_size = 0 THEN NULL
        ELSE ROUND(total_revenue / store_size, 4)
    END AS sales_per_store_size,
    ROW_NUMBER() OVER (
        PARTITION BY source_system
        ORDER BY total_revenue DESC, store_reference
    ) AS store_revenue_rank
FROM store_sales;
