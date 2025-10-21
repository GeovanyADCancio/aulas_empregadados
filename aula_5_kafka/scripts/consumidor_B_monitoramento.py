from kafka import KafkaConsumer
import json

KAFKA_BROKER = 'localhost:9092'
TOPIC = 'logs.aplicacoes'
GROUP_ID = 'monitoramento-tempo-real'

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    group_id=GROUP_ID,
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='latest'
)

print("🧩 Consumidor B (Monitoramento) iniciado.\n")

for msg in consumer:
    log = msg.value
    if log['status'] == 'ERRO':
        print(f"[B] ⚠️ ERRO crítico detectado: {log}")
