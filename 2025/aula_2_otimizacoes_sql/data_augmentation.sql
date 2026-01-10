--------------------> PATIENTS <--------------------
-- Cria a nova tabela com a mesma estrutura da tabela original.
CREATE TABLE _patients_augmentation AS
SELECT * FROM silver_patients LIMIT 0;

-- Insere 10.000 cópias da tabela original, gerando novos IDs únicos para cada paciente.
-- O volume de dados será de 56.000 pacientes * 10.000 = 560.000.000.
-- Isso pode levar um tempo considerável para executar.
INSERT INTO _patients_augmentation (
    id,
    birthdate, gender, race, ethnicity, deathdate,
    healthcare_expenses, healthcare_coverage, income, full_name,
    death, coverage_minus_expenses, over_expenses
)
SELECT
    (s.i || '_' || p.id) AS id,
    p.birthdate, p.gender, p.race, p.ethnicity, p.deathdate,
    p.healthcare_expenses, p.healthcare_coverage, p.income, p.full_name,
    p.death, p.coverage_minus_expenses, p.over_expenses
FROM silver_patients AS p
JOIN generate_series(1, 10000) AS s(i) ON TRUE;

-- Verificação do volume de dados
SELECT count(*) FROM _patients_augmentation;


--------------------> ENCOUNTERS <--------------------
-- Cria a nova tabela com a mesma estrutura
CREATE TABLE _encounters_augmentation AS
SELECT * FROM silver_encounters LIMIT 0;

-- Insere 100 cópias da tabela original, gerando novos IDs para encontros e pacientes.
-- O volume de dados será de 1.4M * 100 = 140.000.000.
-- Isso também levará um tempo considerável.
INSERT INTO _encounters_augmentation (
    id, start, stop, patient, encounterclass, description,
    base_encounter_cost, total_claim_cost, payer_coverage,
    reasondescription, duration_hours
)
SELECT
    (s.i || '_' || e.id) AS id,
    e.start, e.stop,
    (s.i || '_' || p.id) AS patient,
    e.encounterclass, e.description,
    e.base_encounter_cost, e.total_claim_cost, e.payer_coverage,
    e.reasondescription, e.duration_hours
FROM silver_encounters AS e
JOIN silver_patients AS p ON e.patient = p.id
JOIN generate_series(1, 100) AS s(i) ON TRUE;

-- Verificação do volume de dados
SELECT count(*) FROM _encounters_augmentation;


--------------------> JOINs <--------------------
-- Cria a tabela resultante do JOIN entre as duas tabelas aumentadas
CREATE TABLE _all_encounters_patients_join AS
-- 1. INNER JOIN (registros com correspondência em ambas as tabelas)
SELECT
    p.id AS patient_id,
    p.full_name,
    e.id AS encounter_id,
    e.start AS encounter_start,
    e.total_claim_cost,
    'inner' AS join_type
FROM
    _patients_augmentation p
INNER JOIN
    _encounters_augmentation e ON p.id = e.patient

UNION ALL -- Não remove duplicados (se os dados não possuem duplicadas é melhor usar o union all)

-- 2. LEFT JOIN (registros sem correspondência na tabela da direita)
SELECT
    p.id AS patient_id,
    p.full_name,
    NULL AS encounter_id,
    NULL AS encounter_start,
    NULL AS total_claim_cost,
    'left_only' AS join_type
FROM
    _patients_augmentation p
LEFT JOIN
    _encounters_augmentation e ON p.id = e.patient
WHERE
    e.id IS NULL

UNION ALL

-- 3. RIGHT JOIN (registros sem correspondência na tabela da esquerda)
SELECT
    p.id AS patient_id,
    p.full_name,
    e.id AS encounter_id,
    e.start AS encounter_start,
    e.total_claim_cost,
    'right_only' AS join_type
FROM
    _patients_augmentation p
RIGHT JOIN
    _encounters_augmentation e ON p.id = e.patient
WHERE
    p.id IS NULL;
