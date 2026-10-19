-- Warehouse dimension: shared reporting calendar
-- Sources: staging.stg_online_retail_transactions,
--          staging.stg_walmart_sales, and staging.stg_walmart_features
-- Grain: one calendar day

CREATE TABLE warehouse.dim_date AS
WITH source_dates AS (
    SELECT invoice_date AS date_value
    FROM staging.stg_online_retail_transactions

    UNION

    SELECT sales_date AS date_value
    FROM staging.stg_walmart_sales

    UNION

    SELECT feature_date AS date_value
    FROM staging.stg_walmart_features
),
date_bounds AS (
    SELECT
        MIN(date_value) AS minimum_date,
        MAX(date_value) AS maximum_date
    FROM source_dates
    WHERE date_value IS NOT NULL
),
date_spine AS (
    SELECT GENERATE_SERIES(minimum_date, maximum_date, INTERVAL '1 day')::date AS date_value
    FROM date_bounds
)
SELECT
    TO_CHAR(date_value, 'YYYYMMDD')::integer AS date_key,
    date_value AS date,
    EXTRACT(DAY FROM date_value)::integer AS day_of_month,
    EXTRACT(ISODOW FROM date_value)::integer AS day_of_week,
    TO_CHAR(date_value, 'FMDay') AS day_name,
    EXTRACT(WEEK FROM date_value)::integer AS week_of_year,
    EXTRACT(MONTH FROM date_value)::integer AS month,
    TO_CHAR(date_value, 'FMMonth') AS month_name,
    EXTRACT(QUARTER FROM date_value)::integer AS quarter,
    EXTRACT(YEAR FROM date_value)::integer AS year,
    EXTRACT(ISODOW FROM date_value) IN (6, 7) AS is_weekend
FROM date_spine;

ALTER TABLE warehouse.dim_date
    ADD PRIMARY KEY (date_key),
    ADD CONSTRAINT dim_date_date_unique UNIQUE (date);
