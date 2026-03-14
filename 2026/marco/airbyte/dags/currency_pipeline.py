from airflow import DAG
from datetime import datetime, timedelta

# Importando apenas o Operador do Airbyte
from airflow.providers.airbyte.operators.airbyte import AirbyteTriggerSyncOperator

# ==========================================
# CONFIGURAÇÕES E CONSTANTES
# ==========================================
# INSIRA AQUI O ID DA SUA NOVA CONEXÃO DA API (Pegue na URL do Airbyte)
AIRBYTE_API_COTACAO_CONNECTION_ID = "COLE-O-ID-DA-CONEXAO-AQUI" 

default_args = {
    "owner": "engenharia_dados",
    "depends_on_past": False,
    "retries": 2, # Aumentei os retries pois APIs externas podem falhar por instabilidade de rede
    "retry_delay": timedelta(minutes=2),
}

# ==========================================
# DEFINIÇÃO DA DAG EXCLUSIVA DA API
# ==========================================
with DAG(
    dag_id="ingestao_api_cotacao_dolar",
    start_date=datetime(2026, 3, 9),
    schedule_interval='@daily', # Roda todo dia à meia-noite
    catchup=False,
    tags=["airbyte", "bronze", "api", "financas"],
    default_args=default_args,
    description="Extração diária da cotação do Dólar via AwesomeAPI",
) as dag:

    # ------------------------------------------
    # 1. TASK ÚNICA: EXTRAÇÃO COM AIRBYTE
    # ------------------------------------------
    ingest_api_cotacao = AirbyteTriggerSyncOperator(
        task_id="airbyte_sync_api_cotacao_bronze",
        airbyte_conn_id="airbyte_local",
        connection_id=AIRBYTE_API_COTACAO_CONNECTION_ID,
        asynchronous=False,
        timeout=3600,
        wait_seconds=10,
    )

    # Como é só uma task, não precisamos de setar dependências (>>)
    ingest_api_cotacao