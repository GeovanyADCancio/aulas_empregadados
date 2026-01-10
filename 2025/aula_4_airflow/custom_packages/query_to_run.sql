DROP TABLE IF EXISTS insight_one;

CREATE TABLE insight_one AS
SELECT 
    med.especialidade,
    EXTRACT(YEAR FROM cons.data_consulta) AS ano,
    SUM(fat.valor_pago) AS total_faturado
FROM oltp_consulta cons
JOIN oltp_medico med 
    ON cons.medico_id = med.id
JOIN oltp_faturamento fat 
    ON cons.id = fat.consulta_id
WHERE LOWER(cons.status) <> 'cancelada'
GROUP BY med.especialidade, EXTRACT(YEAR FROM cons.data_consulta)
ORDER BY med.especialidade, ano;
