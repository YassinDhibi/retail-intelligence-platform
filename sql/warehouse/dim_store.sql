-- Warehouse dimension: physical stores and controlled channel fallback members
-- Source: staging.stg_walmart_stores
-- Grain: one source-system store or channel reference

CREATE TABLE warehouse.dim_store AS
WITH source_stores AS (
    SELECT
        store_id,
        store_id::text AS store_reference,
        CONCAT('Walmart Store ', store_id::text) AS store_name,
        store_type,
        store_size,
        TRUE AS is_physical_store,
        FALSE AS is_unknown,
        'walmart'::text AS source_system
    FROM staging.stg_walmart_stores

    UNION ALL

    -- Online Retail does not provide a physical store identifier.
    SELECT
        NULL::integer AS store_id,
        'ONLINE_CHANNEL'::text AS store_reference,
        'Online channel (physical store not supplied)'::text AS store_name,
        'ONLINE'::text AS store_type,
        NULL::integer AS store_size,
        FALSE AS is_physical_store,
        TRUE AS is_unknown,
        'online_retail'::text AS source_system
)
SELECT
    ROW_NUMBER() OVER (ORDER BY source_system, store_reference) AS store_key,
    store_id,
    store_reference,
    store_name,
    store_type,
    store_size,
    is_physical_store,
    is_unknown,
    source_system
FROM source_stores;

ALTER TABLE warehouse.dim_store
    ADD PRIMARY KEY (store_key),
    ADD CONSTRAINT dim_store_source_reference_unique UNIQUE (source_system, store_reference);
