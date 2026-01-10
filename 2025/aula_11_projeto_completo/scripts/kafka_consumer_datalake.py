import json
import io
from datetime import datetime
from kafka import KafkaConsumer
from minio import Minio

# --- CONFIGURAÇÕES ---
KAFKA_TOPIC = "orders_stream"
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
BUCKET_NAME = "bronze"

def get_partition_path(order_date_str):
    """
    Cria estrutura de pastas estilo Hive (Big Data):
    Exemplo entrada: '2017-10-02 10:56:33'
    Exemplo saída: 'raw/orders/year=2017/month=10/day=02/'
    """
    try:
        dt = datetime.strptime(order_date_str, "%Y-%m-%d %H:%M:%S")
        return f"raw/orders/year={dt.year:04d}/month={dt.month:02d}/day={dt.day:02d}"
    except Exception:
        # Fallback se a data for inválida ou nula
        now = datetime.now()
        return f"raw/orders/year={now.year}/month={now.month:02d}/day={now.day:02d}"

def run_consumer():
    print("🎧 --- CONSUMER INICIADO (Datalake Ingestion) ---")
    print(f"📡 Ouvindo tópico: {KAFKA_TOPIC}")

    # 1. Conexão MinIO
    minio_client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

    if not minio_client.bucket_exists(BUCKET_NAME):
        print(f"⚠️ Bucket '{BUCKET_NAME}' não existe. Criando...")
        minio_client.make_bucket(BUCKET_NAME)

    # 2. Conexão Kafka
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='datalake-group-v2',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    # 3. Loop de Ingestão
    try:
        for message in consumer:
            order_data = message.value
            order_id = order_data.get('order_id')
            order_date = order_data.get('order_purchase_timestamp')

            # Lógica de Particionamento (Inteligência de Arquitetura)
            partition_path = get_partition_path(order_date)
            file_name = f"{partition_path}/order_{order_id}.json"

            # Preparando o arquivo
            data_bytes = json.dumps(order_data, indent=2).encode('utf-8')
            data_stream = io.BytesIO(data_bytes)

            # Salvando no Object Storage
            minio_client.put_object(
                BUCKET_NAME,
                file_name,
                data_stream,
                length=len(data_bytes),
                content_type='application/json'
            )
            
            # Print bonito mostrando onde foi salvo
            print(f"💾 [MinIO] Salvo em: {file_name}")

    except KeyboardInterrupt:
        print("\n🛑 Consumer parado.")
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
    finally:
        consumer.close()

if __name__ == "__main__":
    run_consumer()