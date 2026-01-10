INSERT INTO aeronaves (modelo, fabricante, ano_fabricacao, capacidade_passageiros) VALUES
('737 MAX', 'Boeing', 2018, 180),
('A320neo', 'Airbus', 2020, 190),
('Embraer E195-E2', 'Embraer', 2021, 132),
('A350-900', 'Airbus', 2019, 325),
('B787-9', 'Boeing', 2017, 296);

INSERT INTO aeronaves (modelo, fabricante, ano_fabricacao, capacidade_passageiros) VALUES
('737 MAX', 'Boeing', 2018, 180),
('A320neo', 'Airbus', 2020, 190),
('Embraer E195-E2', 'Embraer', 2021, 132),
('A350-900', 'Airbus', 2019, 325),
('B787-9', 'Boeing', 2017, 296);

INSERT INTO tripulantes (nome, funcao, matricula) VALUES
('Carlos Silva', 'piloto', 'TRP1001'),
('Mariana Souza', 'copiloto', 'TRP1002'),
('Rafael Lima', 'comissário', 'TRP1003'),
('Ana Clara Torres', 'comissário', 'TRP1004'),
('João Batista', 'piloto', 'TRP1005'),
('Fernanda Nogueira', 'copiloto', 'TRP1006'),
('Diego Ramos', 'comissário', 'TRP1007'),
('Luciana Faria', 'comissário', 'TRP1008');

INSERT INTO voos (numero_voo, origem, destino, data_partida, data_chegada_prevista, aeronave_id, status) VALUES
('JJ1001', 'São Paulo', 'Rio de Janeiro', '2025-10-11 08:00', '2025-10-11 09:10', 1, 'agendado'),
('LA2045', 'Brasília', 'Fortaleza', '2025-10-11 10:30', '2025-10-11 13:20', 2, 'agendado'),
('G32010', 'Salvador', 'Recife', '2025-10-11 09:15', '2025-10-11 10:40', 3, 'agendado'),
('AZ789', 'Curitiba', 'Porto Alegre', '2025-10-11 12:00', '2025-10-11 13:15', 3, 'cancelado'),
('TP501', 'Rio de Janeiro', 'Lisboa', '2025-10-11 18:00', '2025-10-12 06:30', 4, 'agendado'),
('JJ2002', 'São Paulo', 'Manaus', '2025-10-11 15:00', '2025-10-11 18:50', 5, 'em voo'),
('AZ555', 'Belém', 'São Luís', '2025-10-11 07:00', '2025-10-11 08:10', 2, 'pousado'),
('G32110', 'Natal', 'Fortaleza', '2025-10-11 06:30', '2025-10-11 07:20', 1, 'pousado'),
('JJ8888', 'Florianópolis', 'São Paulo', '2025-10-11 16:00', '2025-10-11 17:30', 2, 'atrasado'),
('LA1010', 'São Paulo', 'Belo Horizonte', '2025-10-11 11:00', '2025-10-11 12:10', 1, 'em voo');

INSERT INTO escalas_tripulacao (voo_id, tripulante_id) VALUES
(1, 1), (1, 2), (1, 3), (1, 4),
(2, 5), (2, 6), (2, 7), (2, 8),
(3, 1), (3, 2), (3, 3), (3, 4),
(4, 5), (4, 6), (4, 7), (4, 8),
(5, 1), (5, 2), (5, 3), (5, 4),
(6, 5), (6, 6), (6, 7), (6, 8);

INSERT INTO eventos_voo (voo_id, timestamp, evento, observacoes) VALUES
(6, '2025-10-11 15:10', 'decolou', 'Decolagem realizada com sucesso.'),
(6, '2025-10-11 16:45', 'em voo', 'Sobrevoando região norte do Brasil.'),
(6, '2025-10-11 18:55', 'pousou', 'Pouso realizado com leve atraso.'),
(10, '2025-10-11 11:10', 'decolou', 'Voo partiu com 10 minutos de atraso.'),
(10, '2025-10-11 12:00', 'em voo', 'Altitude de cruzeiro alcançada.'),
(10, '2025-10-11 12:30', 'pousou', 'Chegada em BH antes do previsto.'),
(4, '2025-10-11 11:00', 'cancelado', 'Condições climáticas adversas.'),
(9, '2025-10-11 16:30', 'atrasado', 'Aeronave em manutenção preventiva.');
