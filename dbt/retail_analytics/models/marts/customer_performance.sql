select *
from {{ source('marts', 'customer_performance') }}
