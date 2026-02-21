{{ config(materialized='table') }}

with trips as (
    select * from {{ ref('stg_trips') }}
),

drivers as (
    select * from {{ ref('stg_drivers') }}
),

passengers as (
    select * from {{ ref('stg_passengers') }}
),

joined as (
    select
        t.trip_id,
        t.start_time,
        t.status,
        
        -- Dimensão Motorista
        d.driver_name,
        d.category as car_category,
        
        -- Dimensão Passageiro
        p.passenger_name,
        p.rating as passenger_rating,
        
        -- Métricas Calculadas
        t.duration_minutes,
        t.distance_km,
        t.amount as revenue,
        
        -- Regra de Negócio: Ticket Médio por Km
        case 
            when t.distance_km > 0 then t.amount / t.distance_km 
            else 0 
        end as price_per_km

    from trips t
    left join drivers d on t.driver_id = d.driver_id
    left join passengers p on t.passenger_id = p.passenger_id
)

select * from joined