import pandas as pd
import os
from minio import Minio
from sqlalchemy import create_engine

# --- CONFIGURAÇÕES ---
MINIO_ENDPOINT = "minio:9000"
MINIO_ACCESS_KEY = "minioadmin" # Desafio: inserir as credenciais como variáveis no airflow
MINIO_SECRET_KEY = "minioadmin"
POSTGRES_CONN = 'postgresql+psycopg2://airflow:airflow@postgres:5432/airflow' # Desafio: inserir as credenciais como variáveis no airflow

MINIO_OPTS = {
    'client_kwargs': {'endpoint_url': f'http://{MINIO_ENDPOINT}'},
    'key': MINIO_ACCESS_KEY,
    'secret': MINIO_SECRET_KEY
}

# --- FUNÇÃO AUXILIAR ---
def ensure_bucket_exists(bucket_name):
    client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        print(f"✅ Bucket '{bucket_name}' criado automaticamente.")

def bronze_layer_construction():
    print("🔨 Construindo Camada Bronze...")
    ensure_bucket_exists("bronze")
    
    client = Minio(MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, secure=False)
    files = ['olist_customers_dataset.csv', 'olist_products_dataset.csv', 'olist_order_items_dataset.csv']
    path_local = "/opt/airflow/data"

    for f in files:
        full_path = os.path.join(path_local, f)
        object_name = f"raw/{f}"
        try:
            client.fput_object("bronze", object_name, full_path)
            print(f"✅ Uploaded: {f}")
        except Exception as e:
            print(f"❌ Erro em {f}: {e}")
            raise e

def silver_layer_construction():
    print("🥈 Construindo Camada Silver (Com Tratamento de Dados)...")
    ensure_bucket_exists("silver")

    # ==========================================
    # 1. TRATAMENTO DE PRODUTOS
    # ==========================================
    print("   -> Processando Produtos...")
    df_prods = pd.read_csv('s3://bronze/raw/olist_products_dataset.csv', storage_options=MINIO_OPTS)
    df_prods = df_prods[['product_id', 'product_category_name']]
    
    # Limpeza: Preencher nulos
    df_prods['product_category_name'] = df_prods['product_category_name'].fillna('outros')
    
    # Padronização: Remover underscores (cama_mesa_banho -> Cama Mesa Banho) e colocar em Título
    df_prods['product_category_name'] = (
        df_prods['product_category_name']
        .str.replace('_', ' ')
        .str.title()
    )
    
    # Deduplicação: Garantir IDs únicos
    df_prods = df_prods.drop_duplicates(subset=['product_id'])
    
    df_prods.to_parquet('s3://silver/dim_products.parquet', storage_options=MINIO_OPTS)
    
    # ==========================================
    # 2. TRATAMENTO DE CLIENTES
    # ==========================================
    print("   -> Processando Clientes...")
    df_cust = pd.read_csv('s3://bronze/raw/olist_customers_dataset.csv', storage_options=MINIO_OPTS)
    df_cust = df_cust[['customer_id', 'customer_unique_id', 'customer_city', 'customer_state']]
    
    # Padronização: Cidade como Título (Sao paulo -> Sao Paulo) e Estado em Upper (sp -> SP)
    df_cust['customer_city'] = df_cust['customer_city'].str.title().str.strip()
    df_cust['customer_state'] = df_cust['customer_state'].str.upper().str.strip()
    
    # Deduplicação de IDs
    df_cust = df_cust.drop_duplicates(subset=['customer_id'])
    
    df_cust.to_parquet('s3://silver/dim_customers.parquet', storage_options=MINIO_OPTS)

    # ==========================================
    # 3. TRATAMENTO DE ITENS (FATO)
    # ==========================================
    print("   -> Processando Itens de Pedidos...")
    df_items = pd.read_csv('s3://bronze/raw/olist_order_items_dataset.csv', storage_options=MINIO_OPTS)
    df_items = df_items[['order_id', 'product_id', 'price', 'freight_value']]
    
    # Tipagem Forte: Garantir que preço é float
    df_items['price'] = pd.to_numeric(df_items['price'], errors='coerce').fillna(0.0)
    df_items['freight_value'] = pd.to_numeric(df_items['freight_value'], errors='coerce').fillna(0.0)
    
    # Regra de Negócio: Remover itens com preço negativo ou zero (sujeira)
    initial_rows = len(df_items)
    df_items = df_items[df_items['price'] > 0]
    dropped_rows = initial_rows - len(df_items)
    if dropped_rows > 0:
        print(f"      ⚠️ Aviso: {dropped_rows} linhas removidas por preço inválido.")

    df_items.to_parquet('s3://silver/fact_order_items.parquet', storage_options=MINIO_OPTS)

    print("✅ Silver Concluída com Sucesso!")

def gold_layer_construction():
    print("🥇 Construindo Camada Gold...")
    ensure_bucket_exists("gold")
    
    # Leitura da Silver (já limpa)
    df_prods = pd.read_parquet('s3://silver/dim_products.parquet', storage_options=MINIO_OPTS)
    df_items = pd.read_parquet('s3://silver/fact_order_items.parquet', storage_options=MINIO_OPTS)
    
    # Join
    df_gold = df_items.merge(df_prods, on='product_id', how='left')
    
    # Data Quality no Gold: Preencher produtos que não tiveram match no join
    df_gold['product_category_name'] = df_gold['product_category_name'].fillna('Produto Desconhecido')

    # Salvar no Lake
    df_gold.to_parquet('s3://gold/fact_sales_enriched.parquet', storage_options=MINIO_OPTS)
    
    # Salvar no DW
    print("📦 Escrevendo no Postgres...")
    engine = create_engine(POSTGRES_CONN)
    
    # Dica: chunksize ajuda a não estourar a memória se a tabela for grande
    df_gold.to_sql('fact_orders', engine, if_exists='replace', index=False, chunksize=1000)
    
    # Dimensões
    df_cust = pd.read_parquet('s3://silver/dim_customers.parquet', storage_options=MINIO_OPTS)
    df_cust.to_sql('dim_customers', engine, if_exists='replace', index=False, chunksize=1000)
    df_prods.to_sql('dim_products', engine, if_exists='replace', index=False, chunksize=1000)
    
    print("✅ Gold e DW Concluídos!")