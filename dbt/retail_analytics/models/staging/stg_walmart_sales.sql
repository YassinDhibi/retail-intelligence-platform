select *
from {{ source('staging', 'stg_walmart_sales') }}
