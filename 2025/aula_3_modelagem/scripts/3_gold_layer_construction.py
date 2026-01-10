import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import os

# -------------------------------
# Conexão com o banco
# -------------------------------
load_dotenv(dotenv_path="./.env", override=True)

def get_engine(echo=False):
    try:
        url = f"postgresql+psycopg2://{os.getenv('PG_USER')}:{os.getenv('PG_PASS')}@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DB')}"
        return create_engine(url, pool_pre_ping=True, echo=echo)
    except Exception as e:
        print(f"Erro ao criar engine: {e}")
        return None

# -------------------------------
# Funções de construção das tabelas Gold
# -------------------------------
def create_dim_tempo(datas):
    datas = pd.to_datetime(datas.dropna().unique())
    idx = pd.date_range(datas.min(), datas.max())
    df = pd.DataFrame({'data': idx})
    df['ano'] = df['data'].dt.year
    df['mes'] = df['data'].dt.month
    df['dia'] = df['data'].dt.day
    df['dia_semana'] = df['data'].dt.day_name(locale='pt_BR')
    df['trimestre'] = df['data'].dt.quarter
    df.insert(0, 'tempo_sk', np.arange(1, len(df)+1))
    return df

def create_dim_forma_pagamento(faturamento_df):
    df = faturamento_df[['forma_pagamento']].dropna().drop_duplicates().copy()
    df['forma_pagamento'] = df['forma_pagamento'].str.lower().str.strip()
    df.insert(0, 'forma_pagamento_sk', np.arange(1, len(df)+1))
    return df

def create_fato_consulta(consulta_df, agenda_df, faturamento_df,
                         dim_paciente, dim_medico, dim_clinica,
                         dim_tempo, dim_forma_pagamento):

    # Renomeia para permitir merge por 'id'
    agenda_df = agenda_df.rename(columns={'consulta_id': 'id'})
    faturamento_df = faturamento_df.rename(columns={'consulta_id': 'id'})

    df = consulta_df.merge(agenda_df, on='id', how='left')
    df = df.merge(faturamento_df, on='id', how='left')

    # Mapeamento de SKs
    df['paciente_sk'] = df['paciente_id'].map(dict(zip(dim_paciente['id'], dim_paciente['paciente_sk'])))
    df['medico_sk'] = df['medico_id'].map(dict(zip(dim_medico['id'], dim_medico['medico_sk'])))
    df['clinica_sk'] = df['clinica_id'].map(dict(zip(dim_clinica['id'], dim_clinica['clinica_sk'])))

    df['tempo_agendamento_sk'] = pd.to_datetime(df['data_agendamento']).map(dict(zip(dim_tempo['data'], dim_tempo['tempo_sk'])))
    df['tempo_consulta_sk'] = pd.to_datetime(df['data_consulta']).map(dict(zip(dim_tempo['data'], dim_tempo['tempo_sk'])))
    
    df['forma_pagamento_sk'] = df['forma_pagamento'].str.lower().str.strip().map(
        dict(zip(dim_forma_pagamento['forma_pagamento'], dim_forma_pagamento['forma_pagamento_sk']))
    )

    # Métricas
    df['tempo_espera_min'] = (
        pd.to_datetime(df['data_consulta']) - pd.to_datetime(df['data_agendamento'])
    ).dt.total_seconds() // 60

    df['cancelamento_flag'] = df['status'].str.lower().isin(['cancelada'])

    df = df.rename(columns={'id': 'consulta_id_oltp'})
    df.insert(0, 'consulta_sk', np.arange(1, len(df)+1))

    return df[[
        'consulta_sk', 'consulta_id_oltp',
        'paciente_sk', 'medico_sk', 'clinica_sk',
        'tempo_agendamento_sk', 'tempo_consulta_sk', 'forma_pagamento_sk',
        'status', 'valor', 'valor_pago', 'tempo_espera_min',
        'cancelamento_flag'
    ]]

# -------------------------------
# Função principal
# -------------------------------
def load_gold():
    eng = get_engine()
    if eng is None:
        return

    try:
        print("Lendo dados da camada Silver...")
        paciente_df = pd.read_sql("SELECT * FROM silver_paciente", eng)
        medico_df = pd.read_sql("SELECT * FROM silver_medico", eng)
        clinica_df = pd.read_sql("SELECT * FROM silver_clinica", eng)
        consulta_df = pd.read_sql("SELECT * FROM silver_consulta", eng)
        agenda_df = pd.read_sql("SELECT * FROM silver_agenda", eng)
        faturamento_df = pd.read_sql("SELECT * FROM silver_faturamento", eng)
        print("Extração concluída.")
    except SQLAlchemyError as e:
        print(f"Erro na leitura da camada Silver: {e}")
        return

    try:
        print("Construindo dimensões...")
        dim_paciente = paciente_df.copy()
        # np.arange(1, len(dim_paciente)+1) -> se temos 10 pacientes retorna ids de 1, 2, 3, ... a 10.
        # dim_paciente.insert(0, 'paciente_sk', ...) -> insere a sequencia [1, 2, 3, ..., 10] numa coluna nova 'paciente_sk' na primeira coluna, posição 0
        dim_paciente.insert(0, 'paciente_sk', np.arange(1, len(dim_paciente)+1))

        dim_medico = medico_df.copy()
        dim_medico.insert(0, 'medico_sk', np.arange(1, len(dim_medico)+1))

        dim_clinica = clinica_df.copy()
        dim_clinica.insert(0, 'clinica_sk', np.arange(1, len(dim_clinica)+1))

        dim_forma_pagamento = create_dim_forma_pagamento(faturamento_df)

        datas = pd.concat([
            pd.to_datetime(consulta_df['data_consulta'], errors='coerce'),
            pd.to_datetime(agenda_df['data_agendamento'], errors='coerce')
        ])
        dim_tempo = create_dim_tempo(datas)

        print("Construindo tabela fato...")
        fato_consulta = create_fato_consulta(
            consulta_df, agenda_df, faturamento_df,
            dim_paciente, dim_medico, dim_clinica,
            dim_tempo, dim_forma_pagamento
        )

        print("Transformações concluídas.")
    except Exception as e:
        print(f"Erro durante a transformação para Gold: {e}")
        return

    try:
        print("Carregando dados na camada Gold...")
        dim_paciente.to_sql("gold_dim_paciente", eng, if_exists="replace", index=False)
        dim_medico.to_sql("gold_dim_medico", eng, if_exists="replace", index=False)
        dim_clinica.to_sql("gold_dim_clinica", eng, if_exists="replace", index=False)
        dim_forma_pagamento.to_sql("gold_dim_forma_pagamento", eng, if_exists="replace", index=False)
        dim_tempo.to_sql("gold_dim_tempo", eng, if_exists="replace", index=False)
        fato_consulta.to_sql("gold_fato_consulta", eng, if_exists="replace", index=False)
        print("Carga concluída com sucesso.")
    except SQLAlchemyError as e:
        print(f"Erro ao carregar dados na camada Gold: {e}")

if __name__ == "__main__":
    load_gold()
