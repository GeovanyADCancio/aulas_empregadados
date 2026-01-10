
CREATE TABLE bronze_paciente (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    sexo CHAR(1) CHECK (sexo IN ('M','F')),
    nascimento DATE NOT NULL,
    cidade VARCHAR(100),
    estado CHAR(2)
);

CREATE TABLE bronze_medico (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    especialidade VARCHAR(50),
    crm VARCHAR(20) UNIQUE,
    estado_crm CHAR(2)
);

CREATE TABLE bronze_clinica (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cidade VARCHAR(100),
    estado CHAR(2)
);

CREATE TABLE bronze_consulta (
    id SERIAL PRIMARY KEY,
    paciente_id INT REFERENCES bronze_paciente(id),
    medico_id INT REFERENCES bronze_medico(id),
    clinica_id INT REFERENCES bronze_clinica(id),
    data_consulta DATE NOT NULL,
    valor NUMERIC(10,2),
    status VARCHAR(20) CHECK (status IN ('Agendada','Realizada','Cancelada'))
);

CREATE TABLE bronze_agenda (
    consulta_id INT PRIMARY KEY REFERENCES bronze_consulta(id),
    data_agendamento DATE NOT NULL
);

CREATE TABLE bronze_faturamento (
    consulta_id INT PRIMARY KEY REFERENCES bronze_consulta(id),
    valor_pago NUMERIC(10,2),
    forma_pagamento VARCHAR(20) CHECK (forma_pagamento IN ('Dinheiro','Cartão Crédito','Cartão Débito','PIX','Convênio')),
    data_pagamento DATE
);
