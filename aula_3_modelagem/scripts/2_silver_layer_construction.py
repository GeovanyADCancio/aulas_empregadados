import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# -------------------------------
# Variáveis e Funções de Conexão
# -------------------------------
path_to_env = "./.env"
load_dotenv(dotenv_path=path_to_env, override=True)

def get_engine(echo=False):
    try:
        url = f"postgresql+psycopg2://{os.getenv('PG_USER')}:{os.getenv('PG_PASS')}@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DB')}"
        engine = create_engine(url, pool_pre_ping=True, echo=echo)
        return engine
    except Exception as e:
        print(f"Erro ao criar o engine de conexão: {e}")
        return None

# -------------------------------
# Funções de Transformação
# -------------------------------
def derivar_faixa_etaria(nascimento, referencia=None):
    referencia = pd.Timestamp.today().normalize() if referencia is None else pd.to_datetime(referencia)
    nascimento = pd.to_datetime(nascimento, errors='coerce')

    idade = (referencia - nascimento).dt.days // 365

    return pd.cut(
        idade,
        bins=[0, 12, 17, 25, 35, 45, 60, 75, float('inf')],
        labels=['0-12', '13-17', '18-25', '26-35', '36-45', '46-60', '61-75', '75+'],
        right=True
    )

def derivar_regiao(uf):
    REGIAO_POR_UF = {
        'AC':'Norte','AP':'Norte','AM':'Norte','PA':'Norte','RO':'Norte','RR':'Norte','TO':'Norte',
        'AL':'Nordeste','BA':'Nordeste','CE':'Nordeste','MA':'Nordeste','PB':'Nordeste','PE':'Nordeste',
        'PI':'Nordeste','RN':'Nordeste','SE':'Nordeste',
        'DF':'Centro-Oeste','GO':'Centro-Oeste','MT':'Centro-Oeste','MS':'Centro-Oeste',
        'ES':'Sudeste','MG':'Sudeste','RJ':'Sudeste','SP':'Sudeste',
        'PR':'Sul','RS':'Sul','SC':'Sul'
    }
    return uf.map(REGIAO_POR_UF).fillna('Desconhecida')

# -------------------------------
# Transformações específicas
# -------------------------------
def transform_paciente(df):
    df = df.copy()
    df['nome'] = df['nome'].str.strip().str.title()
    df['sexo'] = df['sexo'].str.upper().str.strip()
    df['nascimento'] = pd.to_datetime(df['nascimento'], errors='coerce')
    df['faixa_etaria'] = derivar_faixa_etaria(df['nascimento']).astype(str)
    df['estado'] = df['estado'].str.upper().str.strip()
    df['regiao'] = derivar_regiao(df['estado'])
    return df

def transform_medico(df):
    df = df.copy()
    df['nome'] = df['nome'].str.strip().str.title()
    df['especialidade'] = df['especialidade'].str.strip().str.title()
    df['crm'] = df['crm'].str.strip().str.upper()
    df['estado_crm'] = df['estado_crm'].str.upper().str.strip()
    return df

def transform_clinica(df):
    df = df.copy()
    df['nome'] = df['nome'].str.strip().str.title()
    df['cidade'] = df['cidade'].str.strip().str.title()
    df['estado'] = df['estado'].str.upper().str.strip()
    df['regiao'] = derivar_regiao(df['estado'])
    return df

def transform_agenda(df):
    df = df.copy()
    df['data_agendamento'] = pd.to_datetime(df['data_agendamento'], errors='coerce')
    return df

def transform_consulta(df):
    df = df.copy()
    df['data_consulta'] = pd.to_datetime(df['data_consulta'], errors='coerce')
    df['status'] = df['status'].str.lower().str.strip()
    return df

def transform_faturamento(df):
    df = df.copy()
    df['data_pagamento'] = pd.to_datetime(df['data_pagamento'], errors='coerce')
    df['forma_pagamento'] = df['forma_pagamento'].str.lower().str.strip()
    return df

# -------------------------------
# Função Principal
# -------------------------------
def load_silver():
    eng = get_engine()
    if eng is None:
        return

    try:
        print("Lendo dados da camada bronze...")
        agenda_df = pd.read_sql("SELECT * FROM bronze_agenda", eng)
        clinica_df = pd.read_sql("SELECT * FROM bronze_clinica", eng)
        consulta_df = pd.read_sql("SELECT * FROM bronze_consulta", eng)
        faturamento_df = pd.read_sql("SELECT * FROM bronze_faturamento", eng)
        medico_df = pd.read_sql("SELECT * FROM bronze_medico", eng)
        paciente_df = pd.read_sql("SELECT * FROM bronze_paciente", eng)
        print("Extração concluída.")
    except Exception as e:
        print(f"Erro na extração: {e}")
        return

    try:
        print("Aplicando transformações (Silver)...")
        agenda_silver = transform_agenda(agenda_df)
        clinica_silver = transform_clinica(clinica_df)
        consulta_silver = transform_consulta(consulta_df)
        faturamento_silver = transform_faturamento(faturamento_df)
        medico_silver = transform_medico(medico_df)
        paciente_silver = transform_paciente(paciente_df)
        print("Transformações concluídas.")

        print("Carregando dados na camada silver...")
        agenda_silver.to_sql("silver_agenda", eng, if_exists="replace", index=False)
        clinica_silver.to_sql("silver_clinica", eng, if_exists="replace", index=False)
        consulta_silver.to_sql("silver_consulta", eng, if_exists="replace", index=False)
        faturamento_silver.to_sql("silver_faturamento", eng, if_exists="replace", index=False)
        medico_silver.to_sql("silver_medico", eng, if_exists="replace", index=False)
        paciente_silver.to_sql("silver_paciente", eng, if_exists="replace", index=False)
        print("Carga concluída com sucesso.")
    except Exception as e:
        print(f"Erro na transformação ou carga: {e}")

if __name__ == "__main__":
    load_silver()
