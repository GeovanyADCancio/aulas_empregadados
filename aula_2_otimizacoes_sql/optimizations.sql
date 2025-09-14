--------------------> CENÁRIO SEM OTIMIZAÇÃO <--------------------

-- Consulta de Junção Lenta
EXPLAIN ANALYZE
SELECT COUNT(*)
FROM _patients_augmentation p
JOIN _encounters_augmentation e ON p.id = e.patient;

-- Consulta de Filtro Lenta
EXPLAIN ANALYZE
SELECT *
FROM _encounters_augmentation
WHERE description = 'Patient-initiated visit' AND encounterclass = 'outpatient';

-- Consulta de Texto Lenta (com LIKE)
EXPLAIN ANALYZE
SELECT id
FROM _encounters_augmentation
WHERE description LIKE '%Hospitalization%';

--------------------> CONFIGURAÇÕES DE OTIMIZAÇÃO <--------------------

-- Índice na chave primária de pacientes
CREATE INDEX idx_patients_id ON _patients_augmentation (id);
-- Índice na chave estrangeira de encontros
CREATE INDEX idx_encounters_id ON _encounters_augmentation (patient);

-- Índice nas colunas usadas na cláusula WHERE
CREATE INDEX idx_encounters_description ON _encounters_augmentation (description);
CREATE INDEX idx_encounters_class ON _encounters_augmentation (encounterclass);

-- Índice para a Busca de Texto
-- O extension é um pacote do postgresql, como um import em python
-- Compara strings de texto de forma eficiente
-- Cria índices baseados em trigamas ' Hosp', 'Hosp', 'ospi', etc.
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_encounters_description_gin ON _encounters_augmentation USING GIN (description gin_trgm_ops);

--------------------> CONSULTAS INICIAIS COM OTIMIZAÇÃO <--------------------
-- MESMAS CONSULTAS INICIAIS COM OTIMIZAÇÃO

-- Consulta de Junção Rápida
EXPLAIN ANALYZE
SELECT COUNT(*)
FROM _patients_augmentation p
JOIN _encounters_augmentation e ON p.id = e.patient;

-- Consulta de Filtro Rápida
EXPLAIN ANALYZE
SELECT *
FROM _encounters_augmentation
WHERE description = 'Patient-initiated visit' AND encounterclass = 'outpatient';

-- Consulta de Texto Rápida
EXPLAIN ANALYZE
SELECT id
FROM _encounters_augmentation
WHERE description LIKE '%Hospitalization%';

--------------------> OUTRAS OTIMIZAÇÕES <--------------------
-- Otimização de UNION vs. UNION ALL
EXPLAIN ANALYZE
(
    SELECT id, 'patients' AS source
    FROM _patients_augmentation
    WHERE gender = 'M'
)
UNION -- Tira os duplicados
(
    SELECT patient AS id, 'encounters' AS source
    FROM _encounters_augmentation
    WHERE encounterclass = 'emergency'
);

EXPLAIN ANALYZE
(
    SELECT id, 'patients' AS source
    FROM _patients_augmentation
    WHERE gender = 'M'
)
UNION ALL -- Não tem a etapa de remoção de duplicados
(
    SELECT patient AS id, 'encounters' AS source
    FROM _encounters_augmentation
    WHERE encounterclass = 'emergency'
);
