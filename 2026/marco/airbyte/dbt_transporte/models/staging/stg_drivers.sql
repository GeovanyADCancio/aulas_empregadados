with source as (
    -- A função ref() cria a dependência. O dbt sabe que deve ler a seed primeiro.
    select * from {{ source('airbyte_raw', 'raw_drivers') }}
),

renamed as (
    select
        cast(driver_id as integer) as driver_id,
        -- Corrige: "joao silva" vira "Joao Silva"
        initcap(name) as driver_name,
        city,
        vehicle_model,
        category,
        -- Tipagem segura
        cast(joined_at as date) as joined_date
    from source
)

select * from renamed