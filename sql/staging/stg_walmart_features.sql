-- Staging model: Walmart weekly store features
-- Source: raw.walmart_features_clean
-- Grain: one row per store and feature date

DROP TABLE IF EXISTS staging.stg_walmart_features;

CREATE TABLE staging.stg_walmart_features AS
WITH source AS (
    SELECT
        NULLIF(TRIM(store), '') AS store_id_text,
        NULLIF(TRIM(date), '') AS feature_date_text,
        NULLIF(TRIM(temperature), '') AS temperature_text,
        NULLIF(TRIM(fuel_price), '') AS fuel_price_text,
        NULLIF(TRIM(markdown1), '') AS markdown1_text,
        NULLIF(TRIM(markdown2), '') AS markdown2_text,
        NULLIF(TRIM(markdown3), '') AS markdown3_text,
        NULLIF(TRIM(markdown4), '') AS markdown4_text,
        NULLIF(TRIM(markdown5), '') AS markdown5_text,
        NULLIF(TRIM(cpi), '') AS cpi_text,
        NULLIF(TRIM(unemployment), '') AS unemployment_text,
        NULLIF(TRIM(isholiday), '') AS is_holiday_text
    FROM raw.walmart_features_clean
),
typed AS (
    SELECT
        store_id_text::integer AS store_id,
        feature_date_text::date AS feature_date,
        temperature_text::numeric(8, 2) AS temperature,
        fuel_price_text::numeric(8, 3) AS fuel_price,
        COALESCE(markdown1_text::numeric(14, 2), 0) AS markdown_1,
        COALESCE(markdown2_text::numeric(14, 2), 0) AS markdown_2,
        COALESCE(markdown3_text::numeric(14, 2), 0) AS markdown_3,
        COALESCE(markdown4_text::numeric(14, 2), 0) AS markdown_4,
        COALESCE(markdown5_text::numeric(14, 2), 0) AS markdown_5,
        cpi_text::numeric(12, 6) AS cpi,
        unemployment_text::numeric(8, 3) AS unemployment_rate,
        CASE LOWER(is_holiday_text)
            WHEN 'true' THEN TRUE
            WHEN 'false' THEN FALSE
            ELSE NULL
        END AS is_holiday
    FROM source
    WHERE store_id_text ~ '^[0-9]+$'
      AND feature_date_text ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'
      AND temperature_text ~ '^-?[0-9]+(\.[0-9]+)?$'
      AND fuel_price_text ~ '^[0-9]+(\.[0-9]+)?$'
      AND COALESCE(markdown1_text, '0') ~ '^-?[0-9]+(\.[0-9]+)?$'
      AND COALESCE(markdown2_text, '0') ~ '^-?[0-9]+(\.[0-9]+)?$'
      AND COALESCE(markdown3_text, '0') ~ '^-?[0-9]+(\.[0-9]+)?$'
      AND COALESCE(markdown4_text, '0') ~ '^-?[0-9]+(\.[0-9]+)?$'
      AND COALESCE(markdown5_text, '0') ~ '^-?[0-9]+(\.[0-9]+)?$'
      AND cpi_text ~ '^[0-9]+(\.[0-9]+)?$'
      AND unemployment_text ~ '^[0-9]+(\.[0-9]+)?$'
      AND LOWER(is_holiday_text) IN ('true', 'false')
)
SELECT
    MD5(CONCAT_WS('|', store_id::text, feature_date::text)) AS walmart_feature_id,
    store_id,
    feature_date,
    temperature,
    fuel_price,
    GREATEST(markdown_1, 0) AS markdown_1,
    GREATEST(markdown_2, 0) AS markdown_2,
    GREATEST(markdown_3, 0) AS markdown_3,
    GREATEST(markdown_4, 0) AS markdown_4,
    GREATEST(markdown_5, 0) AS markdown_5,
    cpi,
    unemployment_rate,
    is_holiday,
    'walmart'::text AS source_system
FROM typed
WHERE store_id > 0
  AND fuel_price > 0
  AND cpi > 0
  AND unemployment_rate >= 0;
