import json
import io
from datetime import datetime
from kafka import KafkaConsumer
from minio import Minio
from colorama import Fore, Style, init

# Inicializa cores
init()

# --- CONFIGURAÇÕES ---
KAFKA_TOPIC = "orders_stream"
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
FRAUD_BUCKET = "fraud-cases"

# --- FUNÇÃO AUXILIAR DE PARTICIONAMENTO ---
def get_partition_path(order_date_str):
    """
    Transforma '2017-10-02 10:56:33' em 'year=2017/month=10/day=02'
    """
    try:
        # Tenta converter a string de data que vem no CSV
        dt = datetime.strptime(order_date_str, "%Y-%m-%d %H:%M:%S")
        return f"year={dt.year:04d}/month={dt.month:02d}/day={dt.day:02d}"
    except Exception:
        # Se a data vier vazia ou errada, usa a data de HOJE como fallback
        now = datetime.now()
        return f"year={now.year}/month={now.month:02d}/day={now.day:02d}"

def run_fraud_detector():
    print(Fore.CYAN + "🕵️  DETECTOR DE FRAUDE V3 (COM PARTICIONAMENTO)..." + Style.RESET_ALL)
    
    # 1. Configurar MinIO
    client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

    if not client.bucket_exists(FRAUD_BUCKET):
        client.make_bucket(FRAUD_BUCKET)
        print(Fore.YELLOW + f"⚠️ Bucket '{FRAUD_BUCKET}' criado." + Style.RESET_ALL)

    # 2. Configurar Consumer
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset='latest',
        group_id='fraud-squad-group-v3', # Novo grupo para garantir leitura limpa
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    print(Fore.CYAN + "📡  Monitorando fluxo..." + Style.RESET_ALL)

    try:
        for message in consumer:
            order = message.value
            order_id = order.get('order_id')
            order_date = order.get('order_purchase_timestamp') # Pegamos a data aqui
            
            # --- LÓGICA DE FRAUDE (SIMULADA) ---
            is_suspicious = str(order_id).endswith(('1', 'a', 'x'))
            
            if is_suspicious:
                # Gera o caminho da pasta baseado na data da compra
                partition_path = get_partition_path(order_date)
                
                print("\n" + "-" * 50)
                print(Fore.RED + f"🚨 FRAUDE DETECTADA! ID: {order_id}" + Style.RESET_ALL)
                
                # Enriquecimento
                order['fraud_reason'] = "Suspicious ID Pattern"
                order['detected_at'] = datetime.now().isoformat()
                
                # Preparação do Arquivo
                data_bytes = json.dumps(order, indent=2).encode('utf-8')
                data_stream = io.BytesIO(data_bytes)
                
                # Nome final com pastas: fraud-cases/year=2018/month=05/day=10/fraud_xyz.json
                file_name = f"{partition_path}/fraud_{order_id}.json"
                
                # Upload
                client.put_object(
                    FRAUD_BUCKET,
                    file_name,
                    data_stream,
                    length=len(data_bytes),
                    content_type='application/json'
                )
                
                print(Fore.YELLOW + f"📂 Salvo em: {FRAUD_BUCKET}/{file_name}" + Style.RESET_ALL)
                print("-" * 50)
                
            else:
                print(Fore.GREEN + ".", end="", flush=True)

    except KeyboardInterrupt:
        print(Style.RESET_ALL + "\n🛑 Monitoramento encerrado.")

if __name__ == "__main__":
    run_fraud_detector()