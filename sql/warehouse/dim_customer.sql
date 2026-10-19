-- Warehouse dimension: source-specific customer profiles
-- Source: staging.stg_online_retail_transactions
-- Grain: one source-system customer and country profile

CREATE TABLE warehouse.dim_customer AS
WITH source_customers AS (
    SELECT DISTINCT
        customer_id,
        customer_id::text AS customer_reference,
        country,
        FALSE AS is_unknown,
        'online_retail'::text AS source_system
    FROM staging.stg_online_retail_transactions

    UNION ALL

    -- Walmart weekly sales do not contain a customer identifier.
    SELECT
        NULL::integer AS customer_id,
        'UNKNOWN'::text AS customer_reference,
        NULL::text AS country,
        TRUE AS is_unknown,
        'walmart'::text AS source_system
)
SELECT
    ROW_NUMBER() OVER (
        ORDER BY source_system, customer_reference, country NULLS FIRST
    ) AS customer_key,
    customer_id,
    customer_reference,
    country,
    is_unknown,
    source_system
FROM source_customers;

ALTER TABLE warehouse.dim_customer
    ADD PRIMARY KEY (customer_key),
    ADD CONSTRAINT dim_customer_source_profile_unique
        UNIQUE NULLS NOT DISTINCT (source_system, customer_reference, country);
