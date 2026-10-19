-- Warehouse dimension: products and Walmart departments
-- Sources: staging.stg_online_retail_transactions and staging.stg_walmart_sales
-- Grain: one source-system product code

CREATE TABLE warehouse.dim_product AS
WITH online_description_counts AS (
    SELECT
        stock_code,
        product_description,
        COUNT(*) AS description_frequency
    FROM staging.stg_online_retail_transactions
    GROUP BY stock_code, product_description
),
ranked_online_products AS (
    SELECT
        stock_code,
        product_description,
        ROW_NUMBER() OVER (
            PARTITION BY stock_code
            ORDER BY description_frequency DESC, product_description
        ) AS description_rank
    FROM online_description_counts
),
source_products AS (
    -- A stock code can have several descriptions. Keep the most frequently observed label.
    SELECT
        stock_code AS product_code,
        product_description AS product_name,
        NULL::integer AS department_id,
        'product'::text AS product_level,
        'online_retail'::text AS source_system
    FROM ranked_online_products
    WHERE description_rank = 1

    UNION ALL

    -- Walmart sales are supplied at department level, not SKU level.
    SELECT DISTINCT
        department_id::text AS product_code,
        CONCAT('Department ', department_id::text) AS product_name,
        department_id,
        'department'::text AS product_level,
        'walmart'::text AS source_system
    FROM staging.stg_walmart_sales
)
SELECT
    ROW_NUMBER() OVER (ORDER BY source_system, product_code) AS product_key,
    product_code,
    product_name,
    department_id,
    product_level,
    source_system
FROM source_products;

ALTER TABLE warehouse.dim_product
    ADD PRIMARY KEY (product_key),
    ADD CONSTRAINT dim_product_source_code_unique UNIQUE (source_system, product_code);
