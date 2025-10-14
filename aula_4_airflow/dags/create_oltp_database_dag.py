from airflow.decorators import dag, task
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from datetime import datetime, timedelta
import os

# Argumentos padrão aplicados a todas as tasks da DAG
DEFAULT_ARGS = {
    'start_date': datetime(2025, 10, 4), 
    'email': ["geovanyadc@gmail.com"],
    'email_on_failure': True,
    'retries': 2,
}

@dag(
    dag_id=os.path.basename(__file__).replace('.py', ''),
    description="DAG para estruturar e popular um ambiente OLTP no PostgreSQL, seguida por arquitetura medallion.",
    schedule="0 7 * * 1", # (minuto, hora, dia do mês, mês, dia da semana) -> Segunda-feira (O Airflow, como o Cron, usa 0 para Domingo e 1 para Segunda)
    default_args=DEFAULT_ARGS,
    dagrun_timeout=timedelta(hours=1),
    max_active_runs=1,
    catchup=False,
    template_searchpath='/home/geovany-cancio/airflow/plugins/custom_packages',
)
def oltp_medallion_pipeline():

    start_pipeline = EmptyOperator(task_id='start_pipeline')

    # 1. Cria a Estrutura OLTP (CREATE TABLES)
    # Executa o arquivo 'create_table.sql'
    create_oltp_structure = SQLExecuteQueryOperator(
        task_id='create_oltp_structure',
        conn_id='postgres_oltp_conn',
        sql= 'create_table.sql',
        autocommit=False, # Persiste no banco após todo o arquivo ser executado no banco
    )

    # 2. Insere os Dados (INSERT INTO)
    # Executa o arquivo 'insert_into.sql'
    insert_oltp_data = SQLExecuteQueryOperator(
        task_id='insert_oltp_data',
        conn_id='postgres_oltp_conn',
        sql= 'insert_into.sql',
        autocommit=False, # Persiste no banco após todo o arquivo ser executado no banco
    )

    end_pipeline = EmptyOperator(task_id='end_pipeline')

    # --- Orquestração ---
    # Sequência: START -> CREATE -> INSERT -> BRONZE -> SILVER -> GOLD -> END
    (
        start_pipeline >> create_oltp_structure >> insert_oltp_data >> end_pipeline
    )

# Instancia a DAG no escopo global
dag_instance = oltp_medallion_pipeline()
