select *
from {{ source('warehouse', 'dim_customer') }}
