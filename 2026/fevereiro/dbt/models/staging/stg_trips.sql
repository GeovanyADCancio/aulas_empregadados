with source as (
    select * from {{ ref('raw_trips') }}
),

renamed as (
    select
        trip_id,
        driver_id,
        passenger_id,
        
        -- start_time geralmente vem limpo, mas vamos garantir
        cast(start_time as timestamp) as start_time,
        
        -- A SOLUÇÃO BLINDADA:
        -- 1. cast(end_time as varchar): Força o dado a virar texto (mesmo que já seja data).
        -- 2. nullif(..., ''): Se esse texto for vazio, vira NULL.
        -- 3. cast(... as timestamp): Agora que é seguro (data ou null), vira Timestamp.
        cast(nullif(cast(end_time as varchar), '') as timestamp) as end_time,

        distance_km,
        amount,
        status,
        payment_method
    from source
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