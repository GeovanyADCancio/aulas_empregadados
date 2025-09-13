import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import numpy as np

# -------------------------------
# Variáveis e Funções de Conexão
# -------------------------------
# Carrega as variáveis de ambiente a partir do arquivo .env
path_to_env = "./.env"
load_dotenv(dotenv_path=path_to_env, override=True)

def get_engine(echo=False):
    """
    Cria e retorna o engine de conexão com o banco de dados PostgreSQL.
    """
    try:
        url = f"postgresql+psycopg2://{os.getenv('PG_USER')}:{os.getenv('PG_PASS')}@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DB')}"
        engine = create_engine(url, pool_pre_ping=True, echo=echo)
        return engine
    except Exception as e:
        print(f"Erro ao criar o engine de conexão. Verifique as variáveis de ambiente: {e}")
        return None

# -------------------------------
# Funções de Transformação para a Camada Gold
# -------------------------------
def create_one_big_table(patients_df, encounters_df):
    """
    Cria uma "One Big Table" (OBT) unindo dados de pacientes e encontros.
    A granularidade da tabela é por encontro clínico.
    """
    print("Criando a One Big Table (OBT)...")

    # Junta as tabelas de encontros e pacientes
    obt = encounters_df.merge(
        patients_df,
        left_on="patient",
        right_on="id",
        how="left",
        suffixes=("_encounter", "_patient")
    )
    
    # Renomeia as colunas com base nos nomes que o merge realmente produziu
    obt = obt.rename(columns={
        "id_encounter": "encounter_id",
        "patient": "patient_id",
        "start": "encounter_start_date",
        "stop": "encounter_end_date",
        "description": "encounter_description",
        "id_patient": "patient_original_id"
    })
    
    # Seleciona apenas as colunas que você quer manter
    cols = [
        "encounter_id", "patient_id", "encounter_start_date", "encounter_end_date",
        "encounterclass", "encounter_description", "duration_hours",
        "total_claim_cost", "payer_coverage",
        "gender", "race", "ethnicity", "full_name"
    ]
    obt = obt[cols]
    
    return obt


def create_patient_summary(patients_df, encounters_df):
    """
    Cria uma tabela de resumo agregada por paciente a partir de encounters e patients.
    """
    print("Criando tabela de resumo por paciente...")
    
    # Agregação na tabela de encounters para obter custos e contagem por paciente
    encounters_agg = encounters_df.groupby('patient').agg(
        total_encounters=('id', 'count'),
        total_claim_cost=('total_claim_cost', 'sum'),
        avg_encounter_duration_hours=('duration_hours', 'mean')
    ).reset_index().rename(columns={'patient': 'id'})
    
    # Junta os dados agregados com as informações dos pacientes
    patient_summary = patients_df.merge(
        encounters_agg,
        on='id',
        how='left'
    )
    
    # Renomeia a coluna id para patient_id e preenche nulos
    patient_summary = patient_summary.rename(columns={'id': 'patient_id'}).fillna(0)
    
    return patient_summary


def create_encounter_summary(encounters_df):
    """
    Cria uma tabela de resumo agregada por tipo de encontro (encounterclass).
    """
    print("Criando tabela de resumo por tipo de encontro...")
    
    # A agregação é feita diretamente na tabela de encontros
    encounter_summary = encounters_df.groupby("encounterclass").agg(
        total_encounters=('id', 'count'),
        avg_claim_cost=('total_claim_cost', 'mean'),
        sum_claim_cost=('total_claim_cost', 'sum'),
        avg_encounter_duration_hours=('duration_hours', 'mean')
    ).reset_index()
    
    return encounter_summary


# -------------------------------
# Função Principal de Carga da Camada Gold
# -------------------------------
def load_gold():
    """
    Orquestra o processo de ETL da camada Silver para a camada Gold.
    """
    eng = get_engine()
    if eng is None:
        return

    try:
        # Extração: Lendo os dados da camada Silver
        print("Lendo dados da camada silver...")
        patients = pd.read_sql("SELECT * FROM silver_patients", eng)
        encounters = pd.read_sql("SELECT * FROM silver_encounters", eng)
        conditions = pd.read_sql("SELECT * FROM silver_conditions", eng)
        print("Extração da camada silver concluída.")

        # Normaliza os nomes das colunas após a leitura
        patients.columns = patients.columns.str.lower()
        encounters.columns = encounters.columns.str.lower()
        conditions.columns = conditions.columns.str.lower()
        
    except SQLAlchemyError as e:
        print(f"Erro ao ler dados da camada silver: {e}")
        return

    # Transformação
    try:
        # Criação da One Big Table (OBT)
        obt_df = create_one_big_table(patients, encounters)
        
        # Criação das tabelas de resumo
        patient_summary_df = create_patient_summary(patients, encounters)
        encounter_summary_df = create_encounter_summary(encounters)
        
        print("\nTransformações para a camada gold concluídas.")

    except Exception as e:
        print(f"Erro durante as transformações para a camada gold: {e}")
        return

    # Carregamento na camada Gold
    try:
        print("Iniciando carregamento dos dados na camada gold...")
        obt_df.to_sql("gold_obt_encounters", eng, if_exists="replace", index=False)
        patient_summary_df.to_sql("gold_patient_summary", eng, if_exists="replace", index=False)
        encounter_summary_df.to_sql("gold_encounter_summary", eng, if_exists="replace", index=False)

        print("Dados inseridos com sucesso no banco na camada gold.")
        
    except SQLAlchemyError as e:
        print(f"Erro ao carregar dados na camada gold: {e}")

if __name__ == "__main__":
    load_gold()
