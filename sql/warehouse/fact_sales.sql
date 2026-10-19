-- Warehouse fact: measurable retail sales observations
-- Sources: staging.stg_online_retail_transactions and staging.stg_walmart_sales
-- Grain: one online invoice line or one Walmart train store-department-week observation

CREATE TABLE warehouse.fact_sales AS
WITH online_sales AS (
    SELECT
        transaction.transaction_line_id AS source_record_id,
        'online_retail'::text AS source_system,
        'invoice_line'::text AS sales_grain,
        NULL::text AS dataset_split,
        TO_CHAR(transaction.invoice_date, 'YYYYMMDD')::integer AS date_key,
        product.product_key,
        customer.customer_key,
        store.store_key,
        transaction.invoice_no,
        NULL::boolean AS is_holiday,
        transaction.quantity,
        transaction.unit_price,
        transaction.sales_amount::numeric(16, 4) AS sales_amount,
        transaction.sales_amount::numeric(16, 4) AS revenue,
        transaction.source_total_sales::numeric(16, 4) AS source_sales_amount,
        NULL::numeric(16, 2) AS weekly_sales_amount
    FROM staging.stg_online_retail_transactions transaction
    JOIN warehouse.dim_product product
      ON product.source_system = 'online_retail'
     AND product.product_code = transaction.stock_code
    JOIN warehouse.dim_customer customer
      ON customer.source_system = 'online_retail'
     AND customer.customer_id = transaction.customer_id
     AND customer.country = transaction.country
    JOIN warehouse.dim_store store
      ON store.source_system = 'online_retail'
     AND store.store_reference = 'ONLINE_CHANNEL'
),
walmart_sales AS (
    SELECT
        sales.walmart_sales_id AS source_record_id,
        'walmart'::text AS source_system,
        'weekly_store_department'::text AS sales_grain,
        sales.dataset_split,
        TO_CHAR(sales.sales_date, 'YYYYMMDD')::integer AS date_key,
        product.product_key,
        customer.customer_key,
        store.store_key,
        NULL::text AS invoice_no,
        sales.is_holiday,
        NULL::integer AS quantity,
        NULL::numeric(12, 4) AS unit_price,
        sales.weekly_sales_amount::numeric(16, 4) AS sales_amount,
        sales.weekly_sales_amount::numeric(16, 4) AS revenue,
        sales.weekly_sales_amount::numeric(16, 4) AS source_sales_amount,
        sales.weekly_sales_amount::numeric(16, 2) AS weekly_sales_amount
    FROM staging.stg_walmart_sales sales
    JOIN warehouse.dim_product product
      ON product.source_system = 'walmart'
     AND product.department_id = sales.department_id
    JOIN warehouse.dim_customer customer
      ON customer.source_system = 'walmart'
     AND customer.customer_reference = 'UNKNOWN'
    JOIN warehouse.dim_store store
      ON store.source_system = 'walmart'
     AND store.store_id = sales.store_id
    -- Test observations have no sales target and are not measurable sales facts.
    WHERE sales.dataset_split = 'train'
)
SELECT
    ROW_NUMBER() OVER (ORDER BY source_system, source_record_id) AS sales_key,
    source_record_id,
    source_system,
    sales_grain,
    dataset_split,
    date_key,
    product_key,
    customer_key,
    store_key,
    invoice_no,
    is_holiday,
    quantity,
    unit_price,
    sales_amount,
    revenue,
    source_sales_amount,
    weekly_sales_amount
FROM (
    SELECT * FROM online_sales
    UNION ALL
    SELECT * FROM walmart_sales
) combined_sales;

ALTER TABLE warehouse.fact_sales
    ADD PRIMARY KEY (sales_key),
    ADD CONSTRAINT fact_sales_source_record_unique UNIQUE (source_system, source_record_id),
    ADD CONSTRAINT fact_sales_date_fk
        FOREIGN KEY (date_key) REFERENCES warehouse.dim_date(date_key),
    ADD CONSTRAINT fact_sales_product_fk
        FOREIGN KEY (product_key) REFERENCES warehouse.dim_product(product_key),
    ADD CONSTRAINT fact_sales_customer_fk
        FOREIGN KEY (customer_key) REFERENCES warehouse.dim_customer(customer_key),
    ADD CONSTRAINT fact_sales_store_fk
        FOREIGN KEY (store_key) REFERENCES warehouse.dim_store(store_key);

CREATE INDEX fact_sales_date_key_idx ON warehouse.fact_sales (date_key);
CREATE INDEX fact_sales_product_key_idx ON warehouse.fact_sales (product_key);
CREATE INDEX fact_sales_customer_key_idx ON warehouse.fact_sales (customer_key);
CREATE INDEX fact_sales_store_key_idx ON warehouse.fact_sales (store_key);
