select *
from {{ source('warehouse', 'dim_store') }}
