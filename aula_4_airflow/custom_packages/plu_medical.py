import os
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
import numpy as np

BASE_DIR = os.path.dirname(__file__)
FILES = {
    "bronze_patients": os.path.join(BASE_DIR, "../../data/patients.csv"),
    "bronze_encounters": os.path.join(BASE_DIR, "../../data/encounters.csv"),
    "bronze_conditions": os.path.join(BASE_DIR, "../../data/conditions.csv"),
}

def get_engine(credentials):
    """
    Cria e retorna o engine de conexão com o banco de dados PostgreSQL.
    """
    try:

        # pg_user = credentials["PG_USER"]
        # pg_pass = credentials["PG_PASS"]
        # pg_host = credentials["PG_HOST"]
        # pg_port = credentials["PG_PORT"]
        # pg_db   = credentials["PG_DB"]

        pg_user = "geovany"
        pg_pass = "123456789"
        pg_host = "localhost"
        pg_port = "5432"
        pg_db = "dados_airflow"

        url = f"postgresql+psycopg2://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
        engine = create_engine(url, pool_pre_ping=True, echo=False)
        
        return engine
        
    except Exception as e:

        print(f"Erro ao criar o engine de conexão. Verifique as variáveis de ambiente: {e}")
        return None


def bronze_layer_construction(credentials):

    eng = get_engine(credentials)
    if eng is None:
        print("Processo abortado. Não foi possível conectar ao banco de dados.")
        return
    
    eng = get_engine(credentials)
    print("Tipo do engine:", type(eng))

    print(credentials["PG_USER"])
    print(credentials["PG_PASS"])
    print(credentials["PG_HOST"])
    
    # Processa cada arquivo e o carrega para o banco de dados
    for table_name, fname in FILES.items():
        try:

            print(f"Iniciando carregamento de '{fname}' para a tabela '{table_name}'...")

            df = pd.read_csv(fname, low_memory=False)

            if df.empty:
                print(f"Aviso: O DataFrame para {fname} está vazio. Pulando o carregamento.")
                continue

            # Adiciona a coluna de metadados para rastrear a data de carregamento
            snapshot_date = datetime.today().strftime('%Y-%m-%d')
            df['execution_date'] = snapshot_date

            # Grava os dados no banco. 'if_exists="replace"' substitui a tabela a cada execução.
            # df.to_sql(table_name, eng, if_exists="replace", index=False)
            with eng.connect() as conn:
                df.to_sql(table_name, conn, if_exists="replace", index=False)
                
            print(f"Dados do arquivo '{fname}' carregados com sucesso na tabela '{table_name}'.")

        except Exception as e:
            print(f"Erro no processamento ou carregamento do arquivo {fname}: {e}")
            # Continua para o próximo arquivo, mesmo se um falhar
            continue

    print("\nCarga bronze concluída.")


def silver_layer_construction(credentials):

    def transform_patients(df):
        
        print("Transformando dados de pacientes...")
        cols = [
            "id", "birthdate", "gender", "race", "ethnicity",
            "first", "middle", "last", "deathdate",
            "healthcare_expenses", "healthcare_coverage", "income"
        ]
        patients = df[cols].copy()

        # Nome completo
        patients["full_name"] = (
            patients["first"].fillna("") + " " +
            patients["middle"].fillna("") + " " +
            patients["last"].fillna("")
        ).str.strip().replace(r"\s+", " ", regex=True)

        # Status de vida
        patients["death"] = np.where(patients["deathdate"].notna(), "dead", "alive")

        # Diferença entre cobertura e despesas
        patients["coverage_minus_expenses"] = (
            patients["healthcare_coverage"].fillna(0) - patients["healthcare_expenses"].fillna(0)
        )

        # Indicador se passou dos gastos cobertos
        patients["over_expenses"] = np.where(patients["coverage_minus_expenses"] < 0, 1, 0)

        # Corrige renda
        patients["income"] = patients["income"].fillna(0)

        # Removendo colunas originais de nomes
        patients = patients.drop(columns=["first", "middle", "last"])

        return patients
    
    def transform_encounters(df):

        print("Transformando dados de encontros...")
        cols = [
            "id", "start", "stop", "patient", "encounterclass", "description",
            "base_encounter_cost", "total_claim_cost", "payer_coverage",
            "reasondescription"
        ]
        encounters = df[cols].copy()

        # Remover nulos importantes (id e patient)
        encounters = encounters.dropna(subset=["id", "patient"])

        # Converter datas
        encounters["start"] = pd.to_datetime(encounters["start"], errors="coerce")
        encounters["stop"] = pd.to_datetime(encounters["stop"], errors="coerce")

        # Tempo de permanência em horas
        encounters["duration_hours"] = (
            (encounters["stop"] - encounters["start"]).dt.total_seconds() / 3600
        )
        return encounters

    def transform_conditions(df):

        print("Transformando dados de condições...")
        cols = ["start", "stop", "patient", "description"]
        conditions = df[cols].copy()

        # Separar descrição e tipo
        conditions["condition"] = conditions["description"].str.replace(r"\s*\(.*\)", "", regex=True).str.strip()
        conditions["condition_type"] = conditions["description"].str.extract(r"\((.*?)\)")

        return conditions
    
    # MAIN FLOW OF THE TASK
    eng = get_engine(credentials)
    if eng is None:
        return

    try:
        # Extração (Camada Bronze)
        print("Lendo dados da camada bronze...")
        patients = pd.read_sql("SELECT * FROM bronze_patients", eng)
        encounters = pd.read_sql("SELECT * FROM bronze_encounters", eng)
        conditions = pd.read_sql("SELECT * FROM bronze_conditions", eng)
        print("Extração concluída com sucesso.")

        # Normaliza as colunas: remove espaços e converte para minúsculas
        print("\nTransformações para a camada silver iniciadas...")
        patients.columns = patients.columns.str.strip().str.lower()
        encounters.columns = encounters.columns.str.strip().str.lower()
        conditions.columns = conditions.columns.str.strip().str.lower()
        print("\nTransformações para a camada silver concluídas.")

        # Transform data
        patients_clean = transform_patients(patients)
        encounters_clean = transform_encounters(encounters)
        conditions_clean = transform_conditions(conditions)

        # Carregamento (Camada Silver)
        print("\nIniciando carregamento dos dados na camada silver...")
        patients_clean.to_sql("silver_patients", eng, if_exists="replace", index=False)
        encounters_clean.to_sql("silver_encounters", eng, if_exists="replace", index=False)
        conditions_clean.to_sql("silver_conditions", eng, if_exists="replace", index=False)
        print("\nDados inseridos com sucesso no banco na camada silver.")

    except Exception as e:
        print(f"Erro na tarefa silver: {e}")
        return


def gold_layer_construction(credentials):

    def create_one_big_table(patients_df, encounters_df):

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
    
    # Main flow of the Task
    eng = get_engine(credentials)
    if eng is None:
        return
    
    try:
        # Extração: Lendo os dados da camada Silver
        print("\nLendo dados da camada silver...")
        patients = pd.read_sql("SELECT * FROM silver_patients", eng)
        encounters = pd.read_sql("SELECT * FROM silver_encounters", eng)
        conditions = pd.read_sql("SELECT * FROM silver_conditions", eng)
        print("\nExtração da camada silver concluída.")

        print("\nIniciando modelagem...")
        obt_df = create_one_big_table(patients, encounters)
        patient_summary_df = create_patient_summary(patients, encounters)
        print("\nModelagem finalizada com sucesso.")

        print("\nIniciando carregamento dos dados na camada gold...")
        obt_df.to_sql("gold_obt_encounters", eng, if_exists="replace", index=False)
        patient_summary_df.to_sql("gold_patient_summary", eng, if_exists="replace", index=False)
        print("\nDados inseridos com sucesso no banco na camada gold.")
        
    except Exception as e:
        print(f"Erro na tarefa gold: {e}")
        return


def print_erro(context):
    """
    Função de callback chamada quando uma task falha.
    O parâmetro context é um dicionário com informações da execução.
    """
    task_id = context.get("task_instance").task_id
    dag_id = context.get("dag").dag_id
    execution_date = context.get("execution_date")
    exception = context.get("exception")

    print("⚠️ ERRO DETECTADO ⚠️")
    print(f"DAG: {dag_id}")
    print(f"Task: {task_id}")
    print(f"Data de execução: {execution_date}")
    print(f"Exceção: {exception}")
