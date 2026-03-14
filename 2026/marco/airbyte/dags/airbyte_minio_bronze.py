from airflow import DAG
from datetime import datetime, timedelta

from airflow.providers.airbyte.operators.airbyte import (
    AirbyteTriggerSyncOperator
)

default_args = {
    "owner": "engenharia_dados",
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

# ID da conexão exclusiva do MinIO (S3) para o Postgres
AIRBYTE_MINIO_CONNECTION_ID = "6439898b-8ea4-4bce-81de-83d0669ddbe2"

with DAG(
    dag_id="airbyte_minio_bronze_ingestion",
    start_date=datetime(2026, 2, 21),
    schedule_interval=None,
    catchup=False,
    tags=["airbyte", "bronze", "minio", "s3"],
    default_args=default_args,
) as dag:

    # Tarefa: Ingerir Trips do MinIO (Data Lake) para o Data Warehouse
    ingest_minio = AirbyteTriggerSyncOperator(
        task_id="airbyte_sync_minio_bronze",
        airbyte_conn_id="airbyte_local", # Usa a mesma conexão com o Airbyte que você já configurou
        connection_id=AIRBYTE_MINIO_CONNECTION_ID,
        asynchronous=False,
        timeout=3600,
        wait_seconds=10,
    )

    ingest_minio