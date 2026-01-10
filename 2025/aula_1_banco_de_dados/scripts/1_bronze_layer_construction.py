import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import text
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# -------------------------------
# Variáveis de Configuração
# -------------------------------
# Carrega as variáveis de ambiente a partir do arquivo .env
path_to_env = "./.env"
load_dotenv(dotenv_path=path_to_env, override=True)

# Mapeia nomes das tabelas de destino para os nomes dos arquivos CSV de origem.
FILES = {
    "bronze_patients": "patients.csv",
    "bronze_encounters": "encounters.csv",
    "bronze_conditions": "conditions.csv",
}

# -------------------------------
# Funções de Conexão e Utilitários
# -------------------------------
from sqlalchemy import create_engine
import os

def get_engine(echo=False):
    """
    Cria e retorna o engine de conexão com o banco de dados PostgreSQL.
    
    Args:
        echo (bool): Se True, o SQLAlchemy logará todas as instruções SQL.

    Returns:
        sqlalchemy.engine.Engine: O engine de conexão, ou None em caso de erro.
    """
    try:
        # 1. Construindo a URL: Define o dialeto ('postgresql'), o driver ('psycopg2') e 
        # as credenciais. Essa URL guia o SQLAlchemy até o banco de dados.
        url = f"postgresql+psycopg2://{os.getenv('PG_USER')}:{os.getenv('PG_PASS')}@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DB')}"
        
        # 2. Criando o Engine: O SQLAlchemy usa o driver 'psycopg2' para abrir uma conexão TCP/IP 
        # com o servidor. O servidor autentica as credenciais e cria um processo dedicado para esta conexão.
        # 'pool_pre_ping=True' garante que a conexão está ativa antes de ser usada.
        engine = create_engine(url, pool_pre_ping=True, echo=echo)
        
        # 3. Retornando o Engine: O objeto 'engine' está pronto para gerenciar o canal de comunicação 
        # com o banco de dados, enviando e recebendo comandos.
        return engine
        
    except Exception as e:
        # 4. Tratando Erros: Se a conexão falhar (credenciais erradas, banco inacessível, etc.), 
        # o erro é capturado aqui. O programa informa o problema e retorna None.
        print(f"Erro ao criar o engine de conexão. Verifique as variáveis de ambiente: {e}")
        return None


def read_csv_lowercase(path):
    """
    Lê um arquivo CSV, convertendo todos os nomes de colunas para minúsculas
    e removendo espaços extras.

    Args:
        path (str): Caminho completo para o arquivo CSV.

    Returns:
        pd.DataFrame: O DataFrame lido e com colunas normalizadas.
    """
    try:
        # 'low_memory=False' para evitar avisos ao lidar com datasets grandes.
        df = pd.read_csv(path, low_memory=False)
        # Normaliza as colunas: remove espaços e converte para minúsculas.
        df.columns = df.columns.str.strip().str.lower()
        return df
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado no caminho {path}")
        return pd.DataFrame() # Retorna um DataFrame vazio em caso de erro

# -------------------------------
# Função Principal de Carregamento
# -------------------------------
def load_bronze():
    """
    Orquestra o processo de extração e carregamento para a camada bronze.
    Lê arquivos CSV, adiciona uma coluna de data de execução e carrega-os
    no banco de dados.
    """
    eng = get_engine()
    if eng is None:
        print("Processo abortado. Não foi possível conectar ao banco de dados.")
        return

    DATA_DIR = os.getenv("DATA_DIR")
    if not DATA_DIR:
        print("Erro: Variável de ambiente DATA_DIR não está definida.")
        return

    # Processa cada arquivo e o carrega para o banco de dados
    for table_name, fname in FILES.items():
        try:
            path = os.path.join(DATA_DIR, fname)
            print(f"Iniciando carregamento de '{path}' para a tabela '{table_name}'...")

            df = read_csv_lowercase(path)
            if df.empty:
                print(f"Aviso: O DataFrame para {fname} está vazio. Pulando o carregamento.")
                continue

            # Adiciona a coluna de metadados para rastrear a data de carregamento
            snapshot_date = datetime.today().strftime('%Y-%m-%d')
            df['execution_date'] = snapshot_date

            # Grava os dados no banco. 'if_exists="replace"' substitui a tabela a cada execução.
            df.to_sql(table_name, eng, if_exists="replace", index=False)
            print(f"Dados do arquivo '{fname}' carregados com sucesso na tabela '{table_name}'.")

        except Exception as e:
            print(f"Erro no processamento ou carregamento do arquivo {fname}: {e}")
            # Continua para o próximo arquivo, mesmo se um falhar
            continue

    print("\nCarga bronze concluída.")

if __name__ == "__main__":
    load_bronze()
