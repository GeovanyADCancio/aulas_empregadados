with source as (
    select * from {{ source('airbyte_raw', 'raw_passengers') }}
),

renamed as (
    select
        cast(passenger_id as integer) as passenger_id,
        name as passenger_name,
        email,
        -- Garante que a nota seja um número decimal e não texto
        cast(rating_avg as numeric) as rating
    from source
)

select * from renamed