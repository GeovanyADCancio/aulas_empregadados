import pandas as pd
import pyarrow as pa
import s3fs
import os
import json
from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.types import NestedField, LongType, StringType, DoubleType

# =========================
# CONFIGURAÇÃO
# =========================
MINIO_ENDPOINT = "http://minio:9000"
ACCESS_KEY = "minioadmin"
SECRET_KEY = "minioadmin"
BUCKET_NAME = "lakehouse"
CATALOG_DB = "iceberg_catalog.db"

# Remove banco local antigo para garantir execução limpa
if os.path.exists(CATALOG_DB):
    os.remove(CATALOG_DB)

print("🛠️ Inicializando S3FileSystem...")
fs = s3fs.S3FileSystem(
    endpoint_url=MINIO_ENDPOINT,
    key=ACCESS_KEY,
    secret=SECRET_KEY
)

# Garante que o bucket existe
try:
    if not fs.exists(BUCKET_NAME):
        fs.mkdir(BUCKET_NAME)
except Exception as e:
    print(f"⚠️  Info Bucket: {e}")

# Limpa dados anteriores no MinIO (Opcional, para teste limpo)
try:
    if fs.exists(f"{BUCKET_NAME}/default/orders"):
        fs.rm(f"{BUCKET_NAME}/default/orders", recursive=True)
        print("🧹 Dados antigos limpos no MinIO.")
except:
    pass

# =========================
# 1. CONFIGURAÇÃO DO CATÁLOGO
# =========================.
catalog = load_catalog(
    "local",
    **{
        "type": "sql", 
        "uri": f"sqlite:///{CATALOG_DB}",
        "s3.endpoint": MINIO_ENDPOINT,
        "s3.access-key-id": ACCESS_KEY,
        "s3.secret-access-key": SECRET_KEY,
        "s3.region": "us-east-1",
        "warehouse": f"s3://{BUCKET_NAME}",
    }
)

# =========================
# 2. DADOS E TABELA
# =========================
schema_orders = Schema(
    NestedField(1, "order_id", LongType(), required=False),
    NestedField(2, "customer", StringType(), required=False),
    NestedField(3, "value", DoubleType(), required=False),
)

df_pandas = pd.DataFrame({
    "order_id": [1, 2, 3],
    "customer": ["Ana", "Bruno", "Carlos"],
    "value": [100.50, 200.00, 150.75],
})
df_arrow = pa.Table.from_pandas(df_pandas)

# Cria namespace 'default'
try:
    catalog.create_namespace("default")
except:
    pass

print("✨ Criando tabela e escrevendo dados...")
table_name = "default.orders"
table = catalog.create_table(table_name, schema=schema_orders)
table.append(df_arrow) # Quebra em parquet, envia ao minio e gera o json de metadados

# Pegamos onde o PyIceberg salvou o arquivo de metadados (ex: 00000-uuid.metadata.json)
current_metadata_location = table.metadata_location
print(f"📍 Metadados gerados em: {current_metadata_location}")

# =========================
# 3. AJUSTE PARA O DREMIO
# =========================
print("🔄 Padronizando metadados para leitura no Dremio...")

# Caminho da pasta de metadados (remove o nome do arquivo)
metadata_dir = os.path.dirname(current_metadata_location).replace("s3://", "")
old_file_path = current_metadata_location.replace("s3://", "")

# 1. Definir novos nomes padrão Iceberg
new_metadata_path = f"{metadata_dir}/v1.metadata.json"
version_hint_path = f"{metadata_dir}/version-hint.text"

# 2. Ler o JSON original e ajustar o caminho interno (metadata-log) para não apontar pro arquivo velho
with fs.open(old_file_path, 'r') as f:
    meta_content = json.load(f)

# Limpa o log de metadados para evitar referências circulares ao arquivo antigo
meta_content['metadata-log'] = []

# 3. Salvar como v1.metadata.json
with fs.open(new_metadata_path, 'w') as f:
    json.dump(meta_content, f)

# 4. Criar o arquivo ponteiro version-hint.text
with fs.open(version_hint_path, 'w') as f:
    f.write("1")

# 5. Remover o arquivo antigo (opcional, mas mantém limpo)
fs.rm(old_file_path)

print("✅ SUCESSO! Dados ajustados.")
print(f"📂 Pasta pronta para o Dremio: lakehouse/default/orders")