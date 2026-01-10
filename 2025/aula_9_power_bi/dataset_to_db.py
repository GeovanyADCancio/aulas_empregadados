import pandas as pd
from sqlalchemy import create_engine
import time

# --- Configurações de Entrada/Saída ---
ARQUIVO_PARQUET = './data/citi_dataset_2025_aula.parquet' # Arquivo Parquet filtrado
TABELA_DESTINO = 'cities_information_aula' # MUDEI o nome da tabela para não sobrescrever a original
MAX_REGISTROS_TESTE = 1000 # <-- NOVO: Define o limite de registros para o teste
# ---------------------------------------------------------------------------------

# --- Configurações de Conexão (Baseado no seu docker-compose) ---
DB_USER = "geovany"
DB_PASSWORD = "teste-geovany"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "my_db"
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# ----------------------------------------------------------------

def carregar_parquet_para_postgres():
    print(f"1. Lendo arquivo Parquet: {ARQUIVO_PARQUET}...")
    
    # 1. Leitura do Arquivo Parquet
    try:
        # Pandas usa o PyArrow para ler o arquivo Parquet de forma eficiente
        df = pd.read_parquet(ARQUIVO_PARQUET)
        print(f"    -> Leitura completa do Parquet. Total de {len(df):,} registros disponíveis.")
    except Exception as e:
        print(f"Erro ao ler o arquivo Parquet: {e}")
        return

    # 🛑 MUDANÇA CRUCIAL AQUI: Limita o DataFrame para o teste
    if len(df) > MAX_REGISTROS_TESTE:
        df = df.head(MAX_REGISTROS_TESTE)
        print(f"    -> LIMITANDO: Apenas os primeiros {MAX_REGISTROS_TESTE} registros serão carregados.")


    # 2. Criação da Engine de Conexão
    print("\n2. Conectando ao banco de dados...")
    try:
        # Tenta criar a engine de conexão SQLAlchemy
        engine = create_engine(DB_URL)
        # Teste de conexão: espera um pouco caso o Docker não tenha iniciado totalmente
        max_tentativas = 5
        for tentativa in range(max_tentativas):
            try:
                engine.connect()
                print("    -> Conexão estabelecida com sucesso.")
                break
            except Exception:
                if tentativa < max_tentativas - 1:
                    print(f"    Aguardando o DB iniciar (Tentativa {tentativa+1}/{max_tentativas})...")
                    time.sleep(5)
                else:
                    raise  # Se falhar na última, levanta o erro original
    except Exception as e:
        print(f"Erro ao conectar ao PostgreSQL. Verifique se o Docker está rodando: {e}")
        return

    # 3. Escrita no Banco de Dados
    print(f"\n3. Iniciando a escrita de {len(df)} registros na tabela '{TABELA_DESTINO}'...")
    try:
        # .to_sql é o método do Pandas para salvar um DataFrame em um DB SQL.
        df.to_sql(
            TABELA_DESTINO,
            engine,
            if_exists='replace', # Opções: 'fail', 'replace', 'append'
            index=False,         # Não salvar o índice do DataFrame como coluna
            chunksize=500        # Reduza o chunksize para o teste rápido, se necessário
        )
        print("\n✅ Carga de dados de teste concluída com sucesso!")
        print(f"    A tabela '{TABELA_DESTINO}' foi criada/atualizada no banco '{DB_NAME}' com {len(df)} registros.")
        
    except Exception as e:
        print(f"Erro durante a escrita dos dados: {e}")

if __name__ == '__main__':
    carregar_parquet_para_postgres()