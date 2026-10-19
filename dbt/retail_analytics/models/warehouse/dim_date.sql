select *
from {{ source('warehouse', 'dim_date') }}
