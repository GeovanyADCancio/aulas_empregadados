with source as (
    select * from {{ source('airbyte_raw', 'raw_trips') }}
),

-- PASSO NOVO: Extrair os dados de dentro da coluna JSON 'data'
extracted as (
    select
        cast(data->>'trip_id' as varchar) as trip_id,
        cast(data->>'driver_id' as varchar) as driver_id,
        cast(data->>'passenger_id' as varchar) as passenger_id,
        data->>'start_time' as start_time_raw,
        data->>'end_time' as end_time_raw,
        cast(data->>'distance_km' as numeric) as distance_km,
        cast(data->>'amount' as numeric) as amount,
        data->>'status' as status,
        data->>'payment_method' as payment_method
    from source
),

renamed as (
    select
        trip_id,
        cast(driver_id as integer) as driver_id,
        cast(passenger_id as integer) as passenger_id,
        cast(start_time_raw as timestamp) as start_time,
        cast(nullif(end_time_raw, '') as timestamp) as end_time,
        distance_km,
        amount,
        status,
        payment_method
    from extracted
),

final as (
    select
        *,
        -- Cálculo de duração seguro
        case 
            when end_time is null then 0 
            else extract(epoch from (end_time - start_time)) / 60 
        end as duration_minutes
    from renamed
)

select * from final