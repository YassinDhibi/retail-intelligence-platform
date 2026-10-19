select *
from {{ source('marts', 'store_performance') }}
