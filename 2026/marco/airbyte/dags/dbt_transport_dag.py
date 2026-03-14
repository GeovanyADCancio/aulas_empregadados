from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount
from datetime import datetime, timedelta
import os

# ==========================================
# ATENÇÃO ALUNOS: MUDEM ESTE CAMINHO PARA A PASTA DO PROJETO NO SEU PC
# Ex Windows: 'C:/Users/SeuNome/Documents/projeto_dbt'
# Ex Mac/Linux: '/Users/SeuNome/Documents/projeto_dbt'
# ==========================================
# O caminho agora aponta para a subpasta do dbt
HOST_PROJECT_PATH = os.getenv(
    "DBT_PROJECT_PATH",
    "/mnt/c/Users/geova/OneDrive/Documentos/empregadados/codigo/aulas_empregadados/2026/marco/airbyte/dbt_transporte"
)

default_args = {
    'owner': 'engenharia_dados',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

# Configurações padrão que todos os containers efêmeros vão compartilhar
docker_default_kwargs = {
    'image': 'dbt_transporte_image:latest',     # A imagem que construímos
    'api_version': 'auto',
    'auto_remove': 'force',                     # MÁGICA: Destrói o container assim que acabar!
    'docker_url': 'unix://var/run/docker.sock', # Como o Airflow fala com o Docker
    'network_mode': 'dbt_net',                  # Para enxergar o DW
    'mount_tmp_dir': False,
    'mounts': [
        Mount(source=HOST_PROJECT_PATH, target='/usr/app', type='bind')
    ]
}

with DAG(
    'dbt_transport_pipeline_ephemeral',
    default_args=default_args,
    description='Pipeline dbt com containers efêmeros',
    schedule_interval=None, 
    start_date=datetime(2026, 2, 21),
    catchup=False,
    tags=['dbt', 'transporte', 'aula'],
) as dag:

    # 1. Carregar os CSVs
    # dbt_seed = DockerOperator(
    #     task_id='dbt_seed',
    #     command='dbt seed --profiles-dir /usr/app',
    #     **docker_default_kwargs
    # )

    # 2. Rodar a camada Staging
    dbt_run_staging = DockerOperator(
        task_id='dbt_run_staging',
        command='dbt run --select staging --profiles-dir /usr/app',
        **docker_default_kwargs
    )

    # 3. Rodar a camada Marts
    dbt_run_marts = DockerOperator(
        task_id='dbt_run_marts',
        command='dbt run --select marts --profiles-dir /usr/app',
        **docker_default_kwargs
    )

    # 4. Testes de Qualidade
    dbt_test = DockerOperator(
        task_id='dbt_test',
        command='dbt test --profiles-dir /usr/app',
        **docker_default_kwargs
    )

    # dbt_seed >> dbt_run_staging >> dbt_run_marts >> dbt_test
    # dbt_seed >> dbt_run_staging >> dbt_run_marts
    dbt_run_staging >> dbt_run_marts >> dbt_test