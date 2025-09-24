--  CONSULTA NO MODELO GOLD (STAR SCHEMA)
-- Valor total faturado por especialidade médica e ano da consulta
EXPLAIN ANALYSE
SELECT 
    m.especialidade,
    t.ano,
    SUM(f.valor_pago) AS total_faturado
FROM gold_fato_consulta f
JOIN gold_dim_medico m 
    ON f.medico_sk = m.medico_sk
JOIN gold_dim_tempo t 
    ON f.tempo_consulta_sk = t.tempo_sk
WHERE f.cancelamento_flag = FALSE
GROUP BY m.especialidade, t.ano
ORDER BY m.especialidade, t.ano;

--  CONSULTA NO MODELO SILVER (NORMALIZADO)
-- Valor total faturado por especialidade médica e ano da consulta
EXPLAIN ANALYSE
SELECT 
    med.especialidade,
    EXTRACT(YEAR FROM cons.data_consulta) AS ano,
    SUM(fat.valor_pago) AS total_faturado
FROM silver_consulta cons
JOIN silver_medico med 
    ON cons.medico_id = med.id
JOIN silver_faturamento fat 
    ON cons.id = fat.consulta_id
WHERE LOWER(cons.status) <> 'cancelada'
GROUP BY med.especialidade, EXTRACT(YEAR FROM cons.data_consulta)
ORDER BY med.especialidade, ano;

--  CONSULTA NO MODELO GOLD (STAR SCHEMA)
-- Valor total faturado por especialidade médica, faixa etária do paciente, região da clínica e mês/ano da consulta, apenas para consultas realizadas
EXPLAIN ANALYSE
SELECT 
    m.especialidade,
    p.faixa_etaria,
    c.regiao AS regiao_clinica,
    t.ano,
    t.mes,
    SUM(f.valor_pago) AS total_faturado
FROM gold_fato_consulta f
JOIN gold_dim_medico m 
    ON f.medico_sk = m.medico_sk
JOIN gold_dim_paciente p 
    ON f.paciente_sk = p.paciente_sk
JOIN gold_dim_clinica c 
    ON f.clinica_sk = c.clinica_sk
JOIN gold_dim_tempo t 
    ON f.tempo_consulta_sk = t.tempo_sk
WHERE f.cancelamento_flag = FALSE
GROUP BY m.especialidade, p.faixa_etaria, c.regiao, t.ano, t.mes
ORDER BY m.especialidade, p.faixa_etaria, c.regiao, t.ano, t.mes;


--  CONSULTA NO MODELO SILVER (NORMALIZADO)
-- Valor total faturado por especialidade médica, faixa etária do paciente, região da clínica e mês/ano da consulta, apenas para consultas realizadas
EXPLAIN ANALYSE
SELECT 
    med.especialidade,
    CASE 
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, pac.nascimento)) <= 12 THEN '0-12'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, pac.nascimento)) <= 17 THEN '13-17'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, pac.nascimento)) <= 25 THEN '18-25'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, pac.nascimento)) <= 35 THEN '26-35'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, pac.nascimento)) <= 45 THEN '36-45'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, pac.nascimento)) <= 60 THEN '46-60'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, pac.nascimento)) <= 75 THEN '61-75'
        ELSE '75+'
    END AS faixa_etaria,
    CASE 
        WHEN cli.estado IN ('AC','AP','AM','PA','RO','RR','TO') THEN 'Norte'
        WHEN cli.estado IN ('AL','BA','CE','MA','PB','PE','PI','RN','SE') THEN 'Nordeste'
        WHEN cli.estado IN ('DF','GO','MT','MS') THEN 'Centro-Oeste'
        WHEN cli.estado IN ('ES','MG','RJ','SP') THEN 'Sudeste'
        WHEN cli.estado IN ('PR','RS','SC') THEN 'Sul'
        ELSE 'Desconhecida'
    END AS regiao_clinica,
    EXTRACT(YEAR FROM cons.data_consulta) AS ano,
    EXTRACT(MONTH FROM cons.data_consulta) AS mes,
    SUM(fat.valor_pago) AS total_faturado
FROM silver_consulta cons
JOIN silver_medico med 
    ON cons.medico_id = med.id
JOIN silver_paciente pac 
    ON cons.paciente_id = pac.id
JOIN silver_clinica cli 
    ON cons.clinica_id = cli.id
JOIN silver_faturamento fat 
    ON cons.id = fat.consulta_id
WHERE LOWER(cons.status) = 'realizada'
GROUP BY med.especialidade, faixa_etaria, regiao_clinica, ano, mes
ORDER BY med.especialidade, faixa_etaria, regiao_clinica, ano, mes;
