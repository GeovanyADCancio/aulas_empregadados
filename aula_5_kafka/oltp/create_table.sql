-- Tabela de aeronaves
CREATE TABLE aeronaves (
    id SERIAL PRIMARY KEY,
    modelo TEXT NOT NULL,
    fabricante TEXT NOT NULL,
    ano_fabricacao INT NOT NULL,
    capacidade_passageiros INT NOT NULL
);

-- Tabela de voos
CREATE TABLE voos (
    id SERIAL PRIMARY KEY,
    numero_voo VARCHAR(10) UNIQUE NOT NULL,
    origem TEXT NOT NULL,
    destino TEXT NOT NULL,
    data_partida TIMESTAMP NOT NULL,
    data_chegada_prevista TIMESTAMP NOT NULL,
    aeronave_id INT REFERENCES aeronaves(id),
    status TEXT NOT NULL  -- agendado, em voo, pousado, cancelado, atrasado
);

-- Tabela de tripulantes
CREATE TABLE tripulantes (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    funcao TEXT NOT NULL, -- piloto, copiloto, comissário
    matricula VARCHAR(10) UNIQUE NOT NULL
);

-- Tabela de escalas de tripulação
CREATE TABLE escalas_tripulacao (
    id SERIAL PRIMARY KEY,
    voo_id INT REFERENCES voos(id),
    tripulante_id INT REFERENCES tripulantes(id)
);

-- Tabela de eventos do voo (ideal para CDC)
CREATE TABLE eventos_voo (
    id SERIAL PRIMARY KEY,
    voo_id INT REFERENCES voos(id),
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    evento TEXT NOT NULL,  -- decolou, pousou, em solo, taxiando, etc.
    observacoes TEXT
);
