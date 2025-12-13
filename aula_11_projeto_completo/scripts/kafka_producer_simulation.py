import time
import json
import random
import pandas as pd
from datetime import datetime
from kafka import KafkaProducer

# --- CONFIGURAÇÕES ---
KAFKA_TOPIC = "orders_stream"
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092'] # Rodando fora do Docker (Windows)
CSV_FILE_PATH = '../data/olist_orders_dataset.csv'

# --- CALLBACK DE ENTREGA ---
def delivery_report(err, msg):
    """ Chamado uma vez para cada mensagem produzida para indicar entrega (ou falha) """
    if err is not None:
        print(f'❌ Falha na entrega: {err}')
    else:
        # msg.topic() e msg.partition() mostram onde o dado caiu
        print(f'✅ Enviado: Tópico={msg.topic()} | Partição={msg.partition()} | Offset={msg.offset()}')

def run_producer():
    print("🔄 --- INICIANDO SIMULADOR DE E-COMMERCE ---")
    
    # Configuração Robusta do Producer
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda x: json.dumps(x).encode('utf-8'),
        # acks='all': Garante que o Líder e as Réplicas salvaram (Segurança máxima)
        acks='all' 
    )

    print(f"📂 Lendo base de dados: {CSV_FILE_PATH}")
    try:
        # Carregando uma amostra aleatória para variar a demo
        df = pd.read_csv(CSV_FILE_PATH)
        df_sample = df.sample(n=1000).replace({float('nan'): None}) # Remove NaNs para não quebrar JSON
        
        orders = df_sample.to_dict(orient='records')
        print(f"🚀 Iniciando stream de {len(orders)} pedidos...")
        print("-" * 50)

        for order in orders:
            order_id = order['order_id']
            
            # ENRIQUECIMENTO: Adicionando timestamp de ingestão (audit trail)
            order['event_emitted_at'] = datetime.now().isoformat()
            
            # Envio Assíncrono com Callback
            producer.send(
                KAFKA_TOPIC, 
                value=order
            ).add_callback(delivery_report)
            
            # Simula variabilidade de tráfego (picos e calmaria)
            # As vezes rápido (0.1s), as vezes lento (1.5s)
            wait_time = random.choice([0.1, 0.1, 0.5, 1.5]) 
            time.sleep(wait_time)
            
            # flush a cada envio para ver o print acontecer em tempo real na aula
            producer.flush() 

    except FileNotFoundError:
        print("❌ Erro: Arquivo não encontrado. Execute o script a partir da raiz do projeto.")
    except KeyboardInterrupt:
        print("\n🛑 Simulação interrompida pelo usuário.")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
    finally:
        producer.close()
        print("🏁 Producer finalizado.")

if __name__ == "__main__":
    run_producer()