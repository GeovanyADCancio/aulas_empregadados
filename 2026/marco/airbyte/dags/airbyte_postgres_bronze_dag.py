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

AIRBYTE_CONNECTION_ID = "ec3cdc0f-47a5-4d0c-8d7e-7655f21700d9"

with DAG(
    dag_id="airbyte_bronze_ingestion",
    start_date=datetime(2026, 2, 21),
    schedule_interval=None,
    catchup=False,
    tags=["airbyte", "bronze"],
    default_args=default_args,
) as dag:

    ingest_bronze = AirbyteTriggerSyncOperator(
        task_id="airbyte_sync_bronze",
        airbyte_conn_id="airbyte_local",
        connection_id=AIRBYTE_CONNECTION_ID,
        asynchronous=False,
        timeout=3600,
        wait_seconds=10,
    )

    ingest_bronze