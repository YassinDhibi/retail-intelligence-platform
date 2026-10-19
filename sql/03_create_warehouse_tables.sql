-- Create PostgreSQL warehouse star-schema tables from verified staging models.
-- Run from the repository root with:
-- psql -h localhost -p 5432 -U postgres -d retail_warehouse -f sql/03_create_warehouse_tables.sql

\set ON_ERROR_STOP on

CREATE SCHEMA IF NOT EXISTS warehouse;

-- Drop the fact before dimensions because it owns the foreign keys.
-- CASCADE allows this full refresh to replace tables after downstream views exist.
-- Rebuild marts separately after the warehouse refresh when that phase is enabled.
DROP TABLE IF EXISTS warehouse.fact_sales CASCADE;
DROP TABLE IF EXISTS warehouse.dim_date CASCADE;
DROP TABLE IF EXISTS warehouse.dim_product CASCADE;
DROP TABLE IF EXISTS warehouse.dim_customer CASCADE;
DROP TABLE IF EXISTS warehouse.dim_store CASCADE;

\echo 'Creating warehouse.dim_date'
\i sql/warehouse/dim_date.sql

\echo 'Creating warehouse.dim_product'
\i sql/warehouse/dim_product.sql

\echo 'Creating warehouse.dim_customer'
\i sql/warehouse/dim_customer.sql

\echo 'Creating warehouse.dim_store'
\i sql/warehouse/dim_store.sql

\echo 'Creating warehouse.fact_sales'
\i sql/warehouse/fact_sales.sql

\echo 'Warehouse row counts'
SELECT 'warehouse.dim_date' AS table_name, COUNT(*) AS row_count
FROM warehouse.dim_date
UNION ALL
SELECT 'warehouse.dim_product', COUNT(*)
FROM warehouse.dim_product
UNION ALL
SELECT 'warehouse.dim_customer', COUNT(*)
FROM warehouse.dim_customer
UNION ALL
SELECT 'warehouse.dim_store', COUNT(*)
FROM warehouse.dim_store
UNION ALL
SELECT 'warehouse.fact_sales', COUNT(*)
FROM warehouse.fact_sales
ORDER BY table_name;
