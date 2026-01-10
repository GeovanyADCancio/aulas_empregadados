-- Contar o número de funcionários por departamento
SELECT Department, COUNT(*) AS total_funcionarios
FROM funcionarios
GROUP BY Department;

-- Contar quantos funcionários saíram da empresa ('Yes') e quantos ficaram ('No')
SELECT Attrition, COUNT(*) as status
FROM funcionarios
GROUP BY Attrition;
