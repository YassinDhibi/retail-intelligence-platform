select *
from {{ source('marts', 'product_performance') }}
