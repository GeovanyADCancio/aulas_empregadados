from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta
import os
import sys
from airflow.models import Variable

sys.path.append(os.path.expanduser("~/airflow/custom_packages"))
import custom_packages.plu_medical as plu_medical

# Argumentos padrão aplicados a todas as tasks da DAG
DEFAULT_ARGS = {
    'start_date': datetime(2025, 9, 26),   # Data inicial da DAG
    'email': ["geovanyadc@gmail.com"],     # Email para notificações
    'email_on_failure': True,              # Envia email em caso de falha
    'retries': 2,                          # Número de tentativas em caso de erro
    'on_failure_callback': plu_medical.print_erro,  # Função customizada para tratar falhas
}

@dag(
    dag_id=os.path.basename(__file__).replace('.py', ''),  # Nome da DAG = nome do arquivo
    description="DAG para estruturar tabelas médicas em arquitetura medallion no PostgreSQL",
    schedule="0 10 * * *",                        # Sem agendamento automático (execução manual)
    default_args=DEFAULT_ARGS,            # Argumentos padrão definidos acima
    dagrun_timeout=timedelta(hours=1),    # Tempo máximo de execução de uma DAG Run
    max_active_runs=1,                    # Apenas uma execução ativa por vez
    catchup=False,                        # Não executa runs passadas
)
def new_pipeline():

    start_pipeline = EmptyOperator(task_id='start_pipeline')

    @task()
    def bronze_layer_construction():
        credentials = Variable.get("medical_db_credentials", deserialize_json=True)
        plu_medical.bronze_layer_construction(credentials)

    @task()
    def silver_layer_construction():
        credentials = Variable.get("medical_db_credentials", deserialize_json=True)
        plu_medical.silver_layer_construction(credentials)

    @task()
    def gold_layer_construction():
        credentials = Variable.get("medical_db_credentials", deserialize_json=True)
        plu_medical.gold_layer_construction(credentials)

    end_pipeline = EmptyOperator(task_id='end_pipeline')

    bronze = bronze_layer_construction()
    silver = silver_layer_construction()
    gold = gold_layer_construction()

    start_pipeline >> bronze >> silver >> gold >> end_pipeline

# Instancia a DAG no escopo global
dag_instance = new_pipeline()