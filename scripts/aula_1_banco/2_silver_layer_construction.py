import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

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
        print(f"Erro ao criar o engine de conexão: {e}")
        return None

# -------------------------------
# Funções de Transformação (Camada Silver)
# -------------------------------
def transform_patients(df):
    """
    Transforma o DataFrame de pacientes para a camada silver.
    - Cria a coluna 'full_name'.
    - Cria a coluna 'death' para indicar se o paciente está morto ou vivo.
    - Calcula a diferença entre a cobertura e as despesas de saúde.
    - Adiciona um indicador para gastos acima da cobertura.
    """
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
    """
    Transforma o DataFrame de encontros clínicos para a camada silver.
    - Converte colunas de data para o tipo datetime.
    - Calcula a duração do encontro em horas.
    """
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
    """
    Transforma o DataFrame de condições de saúde para a camada silver.
    - Separa a descrição da condição do tipo de condição.
    """
    print("Transformando dados de condições...")
    cols = ["start", "stop", "patient", "description"]
    conditions = df[cols].copy()

    # Separar descrição e tipo
    conditions["condition"] = conditions["description"].str.replace(r"\s*\(.*\)", "", regex=True).str.strip()
    conditions["condition_type"] = conditions["description"].str.extract(r"\((.*?)\)")

    return conditions

# -------------------------------
# Funções de Qualidade de Dados
# -------------------------------
def check_data_quality(df, table_name):
    """
    Realiza verificações básicas de qualidade de dados.
    - Verifica se o DataFrame não está vazio.
    - Verifica a presença de nulos em colunas críticas.
    - Verifica se valores de custo não são negativos.
    """
    print(f"\nVerificando qualidade dos dados para a tabela: {table_name}")
    
    if df.empty:
        print(f"Alerta: O DataFrame para {table_name} está vazio!")
        return False
    
    if table_name == "patients":
        if df["id"].isnull().any():
            print("Alerta: Coluna 'id' contém valores nulos.")
            return False

    if table_name == "encounters":
        if df["id"].isnull().any():
            print("Alerta: Coluna 'id' contém valores nulos.")
            return False
        if (df["base_encounter_cost"] < 0).any():
            print("Alerta: 'base_encounter_cost' contém valores negativos.")
            return False
        if (df["total_claim_cost"] < 0).any():
            print("Alerta: 'total_claim_cost' contém valores negativos.")
            return False

    print(f"Verificação de qualidade de dados para {table_name} concluída. Dados OK.")
    return True

# -------------------------------
# Função Principal (Orquestração)
# -------------------------------
def load_silver():
    """
    Orquestra o processo de ETL (Extract, Transform, Load) para a camada silver.
    """
    eng = get_engine()
    if eng is None:
        return

    try:
        # Extração (Camada Bronze)
        print("Lendo dados da camada bronze...")
        patients = pd.read_sql("SELECT * FROM bronze_patients", eng)
        encounters = pd.read_sql("SELECT * FROM bronze_encounters", eng)
        conditions = pd.read_sql("SELECT * FROM bronze_conditions", eng)
        print("Extração concluída com sucesso.")
        
    except Exception as e:
        print(f"Erro na extração dos dados do banco: {e}")
        return

    # Qualidade de Dados (Pré-Transformação)
    if not all([
        check_data_quality(patients, "patients"),
        check_data_quality(encounters, "encounters"),
        check_data_quality(conditions, "conditions")
    ]):
        print("Processo abortado devido a falhas na qualidade dos dados da camada bronze.")
        return

    try:
        # Transformação (Camada Silver)
        patients_clean = transform_patients(patients)
        encounters_clean = transform_encounters(encounters)
        conditions_clean = transform_conditions(conditions)
        print("\nTransformações para a camada silver concluídas.")

        # Qualidade de Dados (Pós-Transformação)
        if not all([
            check_data_quality(patients_clean, "patients_silver"),
            check_data_quality(encounters_clean, "encounters_silver"),
            check_data_quality(conditions_clean, "conditions_silver")
        ]):
            print("Processo abortado devido a falhas na qualidade dos dados da camada silver.")
            return

        # Carregamento (Camada Silver)
        print("\nIniciando carregamento dos dados na camada silver...")
        patients_clean.to_sql("silver_patients", eng, if_exists="replace", index=False)
        encounters_clean.to_sql("silver_encounters", eng, if_exists="replace", index=False)
        conditions_clean.to_sql("silver_conditions", eng, if_exists="replace", index=False)
        print("Dados inseridos com sucesso no banco na camada silver.")
        
    except Exception as e:
        print(f"Erro durante a transformação ou carregamento dos dados: {e}")

if __name__ == "__main__":
    load_silver()