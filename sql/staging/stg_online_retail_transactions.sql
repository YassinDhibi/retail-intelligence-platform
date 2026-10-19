-- Staging model: online retail invoice-line transactions
-- Source: raw.online_retail_clean
-- Grain: one cleaned invoice line per product/customer transaction

DROP TABLE IF EXISTS staging.stg_online_retail_transactions;

CREATE TABLE staging.stg_online_retail_transactions AS
WITH source AS (
    SELECT
        NULLIF(TRIM(invoice_no), '') AS invoice_no,
        NULLIF(TRIM(stock_code), '') AS stock_code,
        NULLIF(TRIM(description), '') AS product_description,
        NULLIF(TRIM(quantity), '') AS quantity_text,
        NULLIF(TRIM(invoice_date), '') AS invoice_date_text,
        NULLIF(TRIM(unit_price), '') AS unit_price_text,
        NULLIF(TRIM(customer_id), '') AS customer_id_text,
        NULLIF(TRIM(country), '') AS country,
        NULLIF(TRIM(total_sales), '') AS total_sales_text
    FROM raw.online_retail_clean
),
typed AS (
    SELECT
        invoice_no,
        stock_code,
        product_description,
        quantity_text::integer AS quantity,
        invoice_date_text::timestamp AS invoice_timestamp,
        unit_price_text::numeric(12, 4) AS unit_price,
        customer_id_text::integer AS customer_id,
        country,
        total_sales_text::numeric(14, 4) AS source_total_sales
    FROM source
    WHERE invoice_no IS NOT NULL
      AND stock_code IS NOT NULL
      AND product_description IS NOT NULL
      AND invoice_date_text ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$'
      AND quantity_text ~ '^[0-9]+$'
      AND unit_price_text ~ '^[0-9]+(\.[0-9]+)?$'
      AND customer_id_text ~ '^[0-9]+$'
      AND total_sales_text ~ '^[0-9]+(\.[0-9]+)?$'
      AND country IS NOT NULL
)
SELECT
    -- Include all source line attributes so repeated product purchases remain distinct.
    MD5(CONCAT_WS(
        '|',
        invoice_no,
        stock_code,
        product_description,
        quantity::text,
        invoice_timestamp::text,
        unit_price::text,
        customer_id::text,
        country,
        source_total_sales::text
    )) AS transaction_line_id,
    invoice_no,
    stock_code,
    product_description,
    quantity,
    invoice_timestamp,
    invoice_timestamp::date AS invoice_date,
    unit_price,
    customer_id,
    country,
    ROUND(quantity * unit_price, 4) AS sales_amount,
    source_total_sales,
    'online_retail'::text AS source_system
FROM typed
WHERE quantity > 0
  AND unit_price > 0
  AND source_total_sales >= 0;
