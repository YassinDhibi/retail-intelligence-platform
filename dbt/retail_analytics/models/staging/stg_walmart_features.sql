select *
from {{ source('staging', 'stg_walmart_features') }}
