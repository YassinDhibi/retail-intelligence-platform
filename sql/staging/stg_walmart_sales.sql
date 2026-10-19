-- Staging model: Walmart weekly sales observations
-- Sources: raw.walmart_train_clean and raw.walmart_test_clean
-- Grain: one store, department, date, and dataset split observation

DROP TABLE IF EXISTS staging.stg_walmart_sales;

CREATE TABLE staging.stg_walmart_sales AS
WITH train_source AS (
    SELECT
        'train'::text AS dataset_split,
        NULLIF(TRIM(store), '') AS store_id_text,
        NULLIF(TRIM(dept), '') AS department_id_text,
        NULLIF(TRIM(date), '') AS sales_date_text,
        NULLIF(TRIM(weekly_sales), '') AS weekly_sales_text,
        NULLIF(TRIM(isholiday), '') AS is_holiday_text
    FROM raw.walmart_train_clean
),
test_source AS (
    SELECT
        'test'::text AS dataset_split,
        NULLIF(TRIM(store), '') AS store_id_text,
        NULLIF(TRIM(dept), '') AS department_id_text,
        NULLIF(TRIM(date), '') AS sales_date_text,
        NULL::text AS weekly_sales_text,
        NULLIF(TRIM(isholiday), '') AS is_holiday_text
    FROM raw.walmart_test_clean
),
combined AS (
    SELECT * FROM train_source
    UNION ALL
    SELECT * FROM test_source
),
typed AS (
    SELECT
        dataset_split,
        store_id_text::integer AS store_id,
        department_id_text::integer AS department_id,
        sales_date_text::date AS sales_date,
        CASE
            WHEN weekly_sales_text IS NULL THEN NULL
            ELSE weekly_sales_text::numeric(14, 2)
        END AS weekly_sales_amount,
        CASE LOWER(is_holiday_text)
            WHEN 'true' THEN TRUE
            WHEN 'false' THEN FALSE
            ELSE NULL
        END AS is_holiday
    FROM combined
    WHERE store_id_text ~ '^[0-9]+$'
      AND department_id_text ~ '^[0-9]+$'
      AND sales_date_text ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'
      AND (weekly_sales_text IS NULL OR weekly_sales_text ~ '^-?[0-9]+(\.[0-9]+)?$')
      AND LOWER(is_holiday_text) IN ('true', 'false')
)
SELECT
    MD5(CONCAT_WS('|', dataset_split, store_id::text, department_id::text, sales_date::text)) AS walmart_sales_id,
    dataset_split,
    store_id,
    department_id,
    sales_date,
    weekly_sales_amount,
    is_holiday,
    'walmart'::text AS source_system
FROM typed
WHERE store_id > 0
  AND department_id > 0
  AND (dataset_split = 'test' OR weekly_sales_amount >= 0);
