-- Mart: modeling-ready weekly sales base for forecasting.
-- Grain: one Walmart store, department, and weekly sales date.

CREATE OR REPLACE VIEW marts.forecasting_base AS
SELECT
    w.sales_date AS date,
    w.sales_date,
    w.store_id,
    w.department_id AS product_id,
    w.department_id,
    CONCAT('Department ', w.department_id::text) AS category,
    w.weekly_sales_amount::numeric(16, 2) AS revenue,
    w.weekly_sales_amount::numeric(16, 2) AS weekly_sales_amount,
    NULL::numeric(16, 2) AS quantity,
    w.is_holiday AS holiday_flag,
    w.is_holiday,
    st.store_type,
    st.store_size,
    ft.temperature,
    ft.fuel_price,
    ft.markdown_1,
    ft.markdown_2,
    ft.markdown_3,
    ft.markdown_4,
    ft.markdown_5,
    ft.cpi,
    ft.unemployment_rate,
    w.source_system
FROM staging.stg_walmart_sales w
LEFT JOIN staging.stg_walmart_stores st
  ON st.store_id = w.store_id
LEFT JOIN staging.stg_walmart_features ft
  ON ft.store_id = w.store_id
 AND ft.feature_date = w.sales_date
WHERE w.dataset_split = 'train'
  AND w.weekly_sales_amount IS NOT NULL;

-- Backward-compatible alias for earlier documentation and API exploration.
CREATE OR REPLACE VIEW marts.forecasting_features AS
SELECT *
FROM marts.forecasting_base;
