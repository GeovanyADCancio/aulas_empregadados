from airflow.decorators import dag
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.sensors.filesystem import FileSensor
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os

# Argumentos padrão
DEFAULT_ARGS = {
    'start_date': datetime(2025, 10, 3), 
    'retries': 1,
}

# --- CONFIGURAÇÃO ESPECÍFICA DE CAMINHOS ---
# O Airflow JÁ ESTÁ configurado para procurar templates aqui:
# template_searchpath = /home/geovany-cancio/airflow/plugins/custom_packages
MONITORED_DIR = '/home/geovany-cancio/airflow/plugins/custom_packages'
SQL_FILE_TO_MONITOR = 'query_to_run.sql' # Nome do arquivo que a DAG vai esperar

@dag(
    dag_id='sql_file_monitor_pipeline',
    description="DAG que espera por um arquivo SQL específico e o executa.",
    schedule= "0 9 * * 3", # (minuto, hora, dia do mês, mês, dia da semana) -> (O Airflow, como o Cron, usa 0 para Domingo e 1 para Segunda)
    default_args=DEFAULT_ARGS,
    catchup=False,
    dagrun_timeout=timedelta(hours=1),
    tags=['sensor', 'postgres'],
    template_searchpath=[MONITORED_DIR],
)
def sql_file_monitor_pipeline():

    start = EmptyOperator(task_id='start_pipeline')

    # 1. TAREFA SENSOR: Espera que o arquivo 'query_to_run.sql' exista
    # O FileSensor precisa do caminho absoluto para verificar o Sistema de Arquivos (FS)
    wait_for_file = FileSensor(
        task_id='wait_for_new_query_file',
        # Monta o caminho absoluto do arquivo a ser monitorado
        filepath=os.path.join(MONITORED_DIR, SQL_FILE_TO_MONITOR), 
        fs_conn_id='fs_default', # Usa a conexão padrão do FileSystem
        poke_interval=30,        # Verifica a cada 30 segundos (polling)
        timeout=60 * 60,         # Tempo máximo de espera: 1 hora
        mode='poke',
    )

    execute_detected_query = SQLExecuteQueryOperator(
        task_id='execute_detected_query',
        conn_id='postgres_oltp_conn',
        sql=SQL_FILE_TO_MONITOR,  # isso carrega o conteúdo do arquivo
        autocommit=False,
    )

    end = EmptyOperator(task_id='end_pipeline')

    start >> wait_for_file >> execute_detected_query >> end

dag_instance = sql_file_monitor_pipeline()
