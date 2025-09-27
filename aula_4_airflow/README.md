# 🚀 Instalação do Apache Airflow no WSL em modo Standalone

## 📦 Requisitos
Instale o suporte a ambientes virtuais do Python:
- `sudo apt install -y python3-venv python3-pip`

## 📂 Criar pasta do projeto
- `mkdir ~/airflow-standalone`
- `cd ~/airflow-standalone`

## 🐍 Criar e ativar ambiente virtual
- `python3 -m venv venv`
- `source venv/bin/activate`

## ⬆️ Atualizar o pip
- `python3 -m pip install --upgrade pip`

## ⚙️ Instalar o Airflow
Defina a versão desejada (exemplo: `3.1.0`) e use o arquivo de *constraints* para garantir compatibilidade das dependências:
- `AIRFLOW_VERSION=3.1.0`
- `PYTHON_VERSION="$(python3 --version | cut -d " " -f2 | cut -d. -f1-2)"`
- `CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"`
- `pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"`

🔎 **Por que usar constraints?**  
O Airflow depende de muitos pacotes Python (Flask, SQLAlchemy, Pandas, etc.).  
Se você rodar apenas `pip install apache-airflow`, o `pip` pode instalar versões mais novas desses pacotes que não foram testadas e podem quebrar a compatibilidade.  
O arquivo de *constraints* garante que todas as dependências sejam instaladas em versões validadas para aquela versão do Airflow.  

Exemplo de um trecho de arquivo de constraints:  
- `Flask==2.2.5`  
- `SQLAlchemy==1.4.49`  
- `pendulum==2.1.2`  


Baixar as dependências no venv:

- `pip install pandas sqlalchemy numpy psycopg2-binary`

## ▶️ Iniciar o Airflow
- `airflow standalone`

Esse comando irá:  
- Criar a pasta `~/airflow`  
- Inicializar o banco de dados SQLite  
- Criar um usuário admin  
- Subir o webserver e o scheduler  

## 🌐 Acessar a interface web
Abra no navegador:  
- `http://localhost:8080`
🔑 **Observação:**  
O **usuário e senha** aparecem no terminal logo após rodar `airflow standalone` ou no arquivo com o seguinte comando:

- `cat /home/geovany-cancio/airflow/simple_auth_manager_passwords.json.generated`

## 📂 Criar pastas de DAGs e Tasks

- `cd ~/airflow`
- `mkdir -p ~/airflow/dags`
- `mkdir -p ~/airflow/plugins/custom_packages`

Configurar o airflow.cfg para não aparecer dags de teste:
- `load_examples = False`

Após a criação dos scripts copiar na pasta de dags e tasks:

- `cp /mnt/c/Users/geova/OneDrive/Documentos/empregadados/codigo/aulas_empregadados/aula_4_airflow/dags/new_pipeline_dag.py ~/airflow/dags/`
- `cp /mnt/c/Users/geova/OneDrive/Documentos/empregadados/codigo/aulas_empregadados/aula_4_airflow/custom_packages/plu_medical.py ~/airflow/plugins/custom_packages/`