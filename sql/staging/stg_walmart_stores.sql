-- Staging model: Walmart store attributes
-- Source: raw.walmart_stores_clean
-- Grain: one row per store

DROP TABLE IF EXISTS staging.stg_walmart_stores;

CREATE TABLE staging.stg_walmart_stores AS
WITH source AS (
    SELECT
        NULLIF(TRIM(store), '') AS store_id_text,
        NULLIF(UPPER(TRIM(type)), '') AS store_type,
        NULLIF(TRIM(size), '') AS store_size_text
    FROM raw.walmart_stores_clean
),
typed AS (
    SELECT
        store_id_text::integer AS store_id,
        store_type,
        store_size_text::integer AS store_size
    FROM source
    WHERE store_id_text ~ '^[0-9]+$'
      AND store_type IN ('A', 'B', 'C')
      AND store_size_text ~ '^[0-9]+$'
)
SELECT
    store_id,
    store_type,
    store_size,
    'walmart'::text AS source_system
FROM typed
WHERE store_id > 0
  AND store_size > 0;
