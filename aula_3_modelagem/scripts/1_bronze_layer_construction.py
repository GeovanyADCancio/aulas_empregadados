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

        url = f"postgresql+psycopg2://{os.getenv('PG_USER')}:{os.getenv('PG_PASS')}@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DB')}"
        engine = create_engine(url, pool_pre_ping=True, echo=echo)

        return engine
        
    except Exception as e:
        print(f"Erro ao criar o engine de conexão. Verifique as variáveis de ambiente: {e}")
        return None


# -------------------------------
# Função Principal de Carregamento
# -------------------------------
def load_bronze():
    engine = get_engine()
    if engine is None:
        print("Não foi possível criar conexão. Abortando.")
        return

    queries_path = "../oltp_queries"

    try:
        with engine.connect() as conn:
            # Executa create_table.sql
            with open(os.path.join(queries_path, "create_table.sql"), "r", encoding="utf-8") as f:
                create_sql = f.read()
                conn.execute(text(create_sql))
                conn.commit()
                print("Tabelas criadas com sucesso.")

            # Executa insert_into.sql
            with open(os.path.join(queries_path, "insert_into.sql"), "r", encoding="utf-8") as f:
                insert_sql = f.read()
                conn.execute(text(insert_sql))
                conn.commit()
                print("Dados inseridos com sucesso.")

        print("\nCarga bronze concluída.")

    except SQLAlchemyError as e:
        print(f"Erro ao executar as queries: {e}")

if __name__ == "__main__":
    load_bronze()
