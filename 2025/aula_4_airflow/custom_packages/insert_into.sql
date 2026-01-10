-- =========================
-- Pacientes
-- =========================
INSERT INTO oltp_paciente (nome, sexo, nascimento, cidade, estado) VALUES
('Ana Souza', 'F', '1990-05-14', 'Curitiba', 'PR'),
('Carlos Pereira', 'M', '1985-09-20', 'São Paulo', 'SP'),
('Fernanda Lima', 'F', '1992-12-02', 'Belo Horizonte', 'MG'),
('João Santos', 'M', '1978-03-30', 'Rio de Janeiro', 'RJ'),
('Mariana Costa', 'F', '2000-07-18', 'Porto Alegre', 'RS'),
('Rafael Oliveira', 'M', '1995-01-10', 'Campinas', 'SP'),
('Luciana Gomes', 'F', '1988-04-05', 'Curitiba', 'PR'),
('Eduardo Alves', 'M', '1993-11-22', 'São Paulo', 'SP'),
('Patrícia Mendes', 'F', '1999-08-14', 'Fortaleza', 'CE'),
('Rodrigo Nunes', 'M', '1981-06-30', 'Recife', 'PE'),
('Beatriz Ferreira', 'F', '1986-09-09', 'Curitiba', 'PR'),
('Felipe Araújo', 'M', '1990-10-11', 'São Paulo', 'SP'),
('Sofia Almeida', 'F', '2001-01-20', 'Rio de Janeiro', 'RJ'),
('Gabriel Moreira', 'M', '1994-07-25', 'Porto Alegre', 'RS'),
('Carolina Silva', 'F', '1983-03-03', 'Salvador', 'BA'),
('André Souza', 'M', '1987-02-17', 'Belo Horizonte', 'MG'),
('Vanessa Rocha', 'F', '1996-12-30', 'Curitiba', 'PR'),
('Marcelo Pinto', 'M', '1975-05-05', 'São Paulo', 'SP'),
('Juliana Ribeiro', 'F', '1991-04-12', 'Campinas', 'SP'),
('Thiago Fernandes', 'M', '1998-09-18', 'Fortaleza', 'CE');

-- =========================
-- Médicos
-- =========================
INSERT INTO oltp_medico (nome, especialidade, crm, estado_crm) VALUES
('Dr. Ricardo Alves', 'Cardiologia', '12345', 'SP'),
('Dra. Paula Martins', 'Dermatologia', '67890', 'PR'),
('Dr. Felipe Moreira', 'Ortopedia', '11223', 'RJ'),
('Dra. Juliana Rocha', 'Pediatria', '44556', 'MG'),
('Dr. Gustavo Tavares', 'Clínico Geral', '77889', 'SP'),
('Dra. Renata Castro', 'Ginecologia', '33445', 'RS'),
('Dr. Bruno Carvalho', 'Endocrinologia', '55667', 'BA'),
('Dra. Camila Duarte', 'Psiquiatria', '99112', 'PE');

-- =========================
-- Clínicas
-- =========================
INSERT INTO oltp_clinica (nome, cidade, estado) VALUES
('Clínica Vida', 'São Paulo', 'SP'),
('Clínica Saúde Total', 'Curitiba', 'PR'),
('Hospital Central', 'Rio de Janeiro', 'RJ'),
('Instituto Bem-Estar', 'Belo Horizonte', 'MG'),
('Santa Casa Saúde', 'Porto Alegre', 'RS'),
('Clínica Popular Nordeste', 'Fortaleza', 'CE');

-- =========================
-- Consultas
-- =========================
INSERT INTO oltp_consulta (paciente_id, medico_id, clinica_id, data_consulta, valor, status) VALUES
(1, 1, 1, '2025-01-10', 250.00, 'Realizada'),
(2, 2, 2, '2025-01-12', 180.00, 'Realizada'),
(3, 3, 3, '2025-01-15', 300.00, 'Cancelada'),
(4, 4, 3, '2025-01-18', 200.00, 'Realizada'),
(5, 5, 1, '2025-01-20', 220.00, 'Agendada'),
(6, 6, 5, '2025-01-22', 400.00, 'Realizada'),
(7, 7, 4, '2025-01-25', 320.00, 'Realizada'),
(8, 8, 6, '2025-01-28', 180.00, 'Cancelada'),
(9, 1, 1, '2025-02-01', 260.00, 'Realizada'),
(10, 2, 2, '2025-02-05', 180.00, 'Agendada'),
(11, 3, 3, '2025-02-07', 300.00, 'Realizada'),
(12, 4, 4, '2025-02-10', 220.00, 'Realizada'),
(13, 5, 5, '2025-02-12', 250.00, 'Cancelada'),
(14, 6, 6, '2025-02-15', 400.00, 'Realizada'),
(15, 7, 1, '2025-02-18', 320.00, 'Realizada'),
(16, 8, 2, '2025-02-20', 180.00, 'Realizada'),
(17, 1, 3, '2025-02-25', 260.00, 'Realizada'),
(18, 2, 4, '2025-02-28', 220.00, 'Agendada'),
(19, 3, 5, '2025-03-02', 310.00, 'Realizada'),
(20, 4, 6, '2025-03-05', 200.00, 'Realizada'),
(1, 2, 1, '2025-03-07', 270.00, 'Realizada'),
(2, 3, 2, '2025-03-10', 300.00, 'Cancelada'),
(3, 4, 3, '2025-03-12', 220.00, 'Agendada'),
(4, 5, 4, '2025-03-15', 240.00, 'Realizada'),
(5, 6, 5, '2025-03-17', 400.00, 'Realizada'),
(6, 7, 6, '2025-03-20', 320.00, 'Realizada'),
(7, 8, 1, '2025-03-22', 200.00, 'Cancelada'),
(8, 1, 2, '2025-03-25', 250.00, 'Realizada'),
(9, 2, 3, '2025-03-28', 180.00, 'Realizada'),
(10, 3, 4, '2025-03-30', 300.00, 'Realizada');

-- =========================
-- Agenda
-- =========================
INSERT INTO oltp_agenda (consulta_id, data_agendamento) VALUES
(1, '2024-12-20'), (2, '2024-12-21'), (3, '2024-12-22'), (4, '2024-12-23'),
(5, '2025-01-05'), (6, '2025-01-08'), (7, '2025-01-10'), (8, '2025-01-12'),
(9, '2025-01-15'), (10, '2025-01-18'), (11, '2025-01-20'), (12, '2025-01-22'),
(13, '2025-01-25'), (14, '2025-01-28'), (15, '2025-02-01'), (16, '2025-02-03'),
(17, '2025-02-05'), (18, '2025-02-07'), (19, '2025-02-10'), (20, '2025-02-12'),
(21, '2025-02-15'), (22, '2025-02-17'), (23, '2025-02-20'), (24, '2025-02-22'),
(25, '2025-02-25'), (26, '2025-02-27'), (27, '2025-03-01'), (28, '2025-03-03'),
(29, '2025-03-05'), (30, '2025-03-07');

-- =========================
-- Faturamento
-- =========================
INSERT INTO oltp_faturamento (consulta_id, valor_pago, forma_pagamento, data_pagamento) VALUES
(1, 250.00, 'Cartão Crédito', '2025-01-10'),
(2, 180.00, 'PIX', '2025-01-12'),
(4, 200.00, 'Convênio', '2025-01-18'),
(6, 400.00, 'Dinheiro', '2025-01-22'),
(7, 320.00, 'Cartão Débito', '2025-01-25'),
(9, 260.00, 'Cartão Crédito', '2025-02-01'),
(11, 300.00, 'PIX', '2025-02-07'),
(12, 220.00, 'Convênio', '2025-02-10'),
(14, 400.00, 'Cartão Débito', '2025-02-15'),
(15, 320.00, 'PIX', '2025-02-18'),
(16, 180.00, 'Dinheiro', '2025-02-20'),
(17, 260.00, 'Cartão Crédito', '2025-02-25'),
(19, 310.00, 'Convênio', '2025-03-02'),
(20, 200.00, 'PIX', '2025-03-05'),
(21, 270.00, 'Cartão Crédito', '2025-03-07'),
(24, 240.00, 'Dinheiro', '2025-03-15'),
(25, 400.00, 'Convênio', '2025-03-17'),
(26, 320.00, 'Cartão Débito', '2025-03-20'),
(28, 250.00, 'PIX', '2025-03-25'),
(29, 180.00, 'Cartão Crédito', '2025-03-28'),
(30, 300.00, 'Convênio', '2025-03-30');
