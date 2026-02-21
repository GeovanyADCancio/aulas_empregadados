with source as (
    -- A função ref() cria a dependência. O dbt sabe que deve ler a seed primeiro.
    select * from {{ ref('raw_drivers') }} -- evita SELECT * FROM banco_de_dados.schema.raw_drivers
),

renamed as (
    select
        driver_id,
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