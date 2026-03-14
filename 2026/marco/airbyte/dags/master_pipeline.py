from airflow import DAG
from datetime import datetime, timedelta
import os

# Importando os Operadores necessários
from airflow.providers.airbyte.operators.airbyte import AirbyteTriggerSyncOperator
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount

# ==========================================
# CONFIGURAÇÕES E CONSTANTES
# ==========================================
AIRBYTE_MINIO_CONNECTION_ID = "6439898b-8ea4-4bce-81de-83d0669ddbe2"
AIRBYTE_CONNECTION_ID = "ec3cdc0f-47a5-4d0c-8d7e-7655f21700d9"

HOST_PROJECT_PATH = os.getenv(
    "DBT_PROJECT_PATH",
    "/mnt/c/Users/geova/OneDrive/Documentos/empregadados/codigo/aulas_empregadados/2026/marco/airbyte/dbt_transporte"
)

default_args = {
    "owner": "engenharia_dados",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

docker_default_kwargs = {
    'image': 'dbt_transporte_image:latest',     
    'api_version': 'auto',
    'auto_remove': 'force',                     
    'docker_url': 'unix://var/run/docker.sock', 
    'network_mode': 'dbt_net',                  
    'mount_tmp_dir': False,
    'mounts': [
        Mount(source=HOST_PROJECT_PATH, target='/usr/app', type='bind')
    ]
}

# ==========================================
# DEFINIÇÃO DA DAG MESTRA
# ==========================================
with DAG(
    dag_id="master_transport_pipeline",
    start_date=datetime(2026, 2, 21),
    schedule_interval=None, # Mude para '@daily' se quiser que rode todo dia
    catchup=False,
    tags=["master", "airbyte", "dbt", "bronze", "silver", "gold"],
    default_args=default_args,
    description="Orquestração completa: Ingestão paralela (Airbyte) -> Transformação (dbt)",
) as dag:

    # ------------------------------------------
    # 1. CAMADA BRONZE (EXTRAÇÃO COM AIRBYTE)
    # ------------------------------------------
    ingest_minio = AirbyteTriggerSyncOperator(
        task_id="airbyte_sync_minio_bronze",
        airbyte_conn_id="airbyte_local", 
        connection_id=AIRBYTE_MINIO_CONNECTION_ID,
        asynchronous=False,
        timeout=3600,
        wait_seconds=10,
    )

    ingest_postgres_bronze = AirbyteTriggerSyncOperator(
        task_id="airbyte_sync_postgres_bronze",
        airbyte_conn_id="airbyte_local",
        connection_id=AIRBYTE_CONNECTION_ID,
        asynchronous=False,
        timeout=3600,
        wait_seconds=10,
    )

    # ------------------------------------------
    # 2. CAMADAS SILVER E GOLD (TRANSFORMAÇÃO COM DBT)
    # ------------------------------------------
    dbt_run_staging = DockerOperator(
        task_id='dbt_run_staging',
        command='dbt run --select staging --profiles-dir /usr/app',
        **docker_default_kwargs
    )

    dbt_run_marts = DockerOperator(
        task_id='dbt_run_marts',
        command='dbt run --select marts --profiles-dir /usr/app',
        **docker_default_kwargs
    )

    dbt_test = DockerOperator(
        task_id='dbt_test',
        command='dbt test --profiles-dir /usr/app',
        **docker_default_kwargs
    )

    # ------------------------------------------
    # 3. ORDEM DE EXECUÇÃO (DEPENDÊNCIAS)
    # ------------------------------------------
    # As ingestões do MinIO e do Postgres rodam ao mesmo tempo.
    # A task Staging do dbt só começa quando AMBAS finalizarem com sucesso.
    [ingest_minio, ingest_postgres_bronze] >> dbt_run_staging >> dbt_run_marts >> dbt_test