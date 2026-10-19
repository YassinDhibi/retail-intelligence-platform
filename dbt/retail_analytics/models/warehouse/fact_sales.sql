select *
from {{ source('warehouse', 'fact_sales') }}
