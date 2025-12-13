from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

# IMPORTAÇÃO DOS PLUGINS
# Como mapeamos a pasta ./plugins para /opt/airflow/plugins no Docker, 
# o Python consegue achar o arquivo 'etl_tasks.py'
from etl_tasks import bronze_layer_construction, silver_layer_construction, gold_layer_construction

DEFAULT_ARGS = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
}

with DAG(
    dag_id='pipeline_medallion_semanal',
    default_args=DEFAULT_ARGS,
    description='Pipeline Ponta a Ponta: CSV -> MinIO -> Postgres',
    # Schedule: Roda toda segunda-feira à meia-noite (Notação Cron)
    # Ou use '@weekly' que roda domingo meia-noite
    schedule_interval='0 0 * * 1', 
    catchup=False,
    tags=['projeto_final', 'medallion']
) as dag:

    # --- TASK 1: BRONZE ---
    task_bronze = PythonOperator(
        task_id='1_bronze_layer',
        python_callable=bronze_layer_construction
    )

    # --- TASK 2: SILVER ---
    task_silver = PythonOperator(
        task_id='2_silver_layer',
        python_callable=silver_layer_construction
    )

    # --- TASK 3: GOLD ---
    task_gold = PythonOperator(
        task_id='3_gold_layer',
        python_callable=gold_layer_construction
    )

    # --- ORQUESTRAÇÃO ---
    task_bronze >> task_silver >> task_gold