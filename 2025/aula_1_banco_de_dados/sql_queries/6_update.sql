-- Aumentar o salário mensal em 15% para todos os funcionários do departamento de 'Vendas'
UPDATE funcionarios
SET MonthlyIncome = MonthlyIncome * 1.15
WHERE Department = 'Sales';
