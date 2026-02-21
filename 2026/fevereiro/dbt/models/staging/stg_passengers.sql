with source as (
    select * from {{ ref('raw_passengers') }}
),

renamed as (
    select
        passenger_id,
        name as passenger_name,
        email,
        -- Garante que a nota seja um número decimal e não texto
        cast(rating_avg as numeric) as rating
    from source
)

select * from renamed