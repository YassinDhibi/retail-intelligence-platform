-- Create PostgreSQL business marts for dashboards, APIs, and ML.
-- Run from the repository root with:
-- psql -h localhost -p 5432 -U postgres -d retail_warehouse -f sql/04_create_marts.sql

\set ON_ERROR_STOP on

CREATE SCHEMA IF NOT EXISTS marts;

\echo 'Creating marts.sales_overview'
\i sql/marts/sales_overview.sql

\echo 'Creating marts.product_performance'
\i sql/marts/product_performance.sql

\echo 'Creating marts.customer_performance'
\i sql/marts/customer_performance.sql

\echo 'Creating marts.store_performance'
\i sql/marts/store_performance.sql

\echo 'Creating marts.forecasting_base'
\i sql/marts/forecasting_base.sql

\echo 'Mart row counts'
SELECT 'marts.sales_overview' AS table_name, COUNT(*) AS row_count
FROM marts.sales_overview
UNION ALL
SELECT 'marts.product_performance', COUNT(*)
FROM marts.product_performance
UNION ALL
SELECT 'marts.customer_performance', COUNT(*)
FROM marts.customer_performance
UNION ALL
SELECT 'marts.store_performance', COUNT(*)
FROM marts.store_performance
UNION ALL
SELECT 'marts.forecasting_base', COUNT(*)
FROM marts.forecasting_base
ORDER BY table_name;
