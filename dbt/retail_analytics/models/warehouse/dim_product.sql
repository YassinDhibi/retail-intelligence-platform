select *
from {{ source('warehouse', 'dim_product') }}
