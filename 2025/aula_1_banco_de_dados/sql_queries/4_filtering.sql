-- Encontrar funcionários com idade entre 30 e 40 anos
SELECT Age, Department, JobRole
FROM funcionarios
WHERE Age BETWEEN 30 AND 40;

-- Encontrar funcionários que saíram da empresa ('Yes' na coluna Attrition) e viajam frequentemente
SELECT EmployeeNumber, Age, Department, JobRole
FROM funcionarios
WHERE Attrition = 'Yes' AND BusinessTravel = 'Travel_Frequently';

-- Encontrar todos os cargos que ganham mais de 7000
SELECT JobRole, MonthlyIncome
FROM funcionarios
WHERE MonthlyIncome > 7000;
