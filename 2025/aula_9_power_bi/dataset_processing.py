import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import os

# --- Configuração ---
arquivo_grande_csv = './data/311_Service_Requests_from_2010_to_Present_20251115.csv'
arquivo_filtrado_parquet = './data/citi_dataset_2025_aula.parquet'
coluna_data = 'Created Date'
chunk_size = 1000
ano_alvo = 2025
formato_da_data = '%m/%d/%Y %I:%M:%S %p'
# --------------------

df_header = pd.read_csv(arquivo_grande_csv, nrows=0)
colunas = df_header.columns.tolist()
dtype_fix = {col: 'str' for col in colunas}

# Inicializa o 'writer' do Parquet. Ele ficará vazio até acharmos o primeiro chunk.
writer = None

# Cria um iterador que lê o CSV em pedaços (chunks)
print(f"Iniciando processamento em chunks de {chunk_size} linhas...")
leitor_chunks = pd.read_csv(
    arquivo_grande_csv,
    chunksize=chunk_size,
    dtype=dtype_fix,
    low_memory=False
)

total_linhas_filtradas = 0

for i, chunk in enumerate(leitor_chunks):

    print(f"Processando chunk {i+1}...")
    
    chunk[coluna_data] = pd.to_datetime(
        chunk[coluna_data],
        format=formato_da_data,
    )

    # A MÁGICA: Filtra o chunk para pegar apenas o ano desejado
    # .dt.year só funciona porque usamos 'parse_dates' acima
    chunk_filtrado = chunk[chunk[coluna_data].dt.year == ano_alvo]

    # Se encontramos dados de 2025 neste chunk, escrevemos no arquivo
    if not chunk_filtrado.empty:
        total_linhas_filtradas += len(chunk_filtrado)
        
        # Converte o chunk do pandas para uma Tabela do Arrow
        table = pa.Table.from_pandas(chunk_filtrado, preserve_index=False)

        # Se este é o primeiro chunk que estamos escrevendo,
        # precisamos criar o arquivo e definir o schema (a estrutura)
        if writer is None:
            writer = pq.ParquetWriter(arquivo_filtrado_parquet, table.schema)
        
        # Escreve a tabela (chunk) no arquivo Parquet
        writer.write_table(table)

# Fecha o arquivo Parquet
if writer:
    writer.close()
    print(f"\nConcluído! Total de {total_linhas_filtradas} linhas de 2025 salvas em '{arquivo_filtrado_parquet}'.")
else:
    print("\nConcluído. Nenhuma linha de 2025 foi encontrada.")
