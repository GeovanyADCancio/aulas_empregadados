from kafka import KafkaConsumer
import json

KAFKA_BROKER = 'kafka:29092',
TOPIC = 'logs.aplicacoes'
GROUP_ID = 'monitoramento-tempo-real'

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    group_id=GROUP_ID,
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='latest'
)

print("🧩 Consumidor A (Monitoramento) iniciado.\n")

for msg in consumer:
    log = msg.value
    if log['status'] == 'ERRO' or log['tempo_resposta_ms'] > 2000:
        print(f"[A] 🚨 ALERTA: {log['api']} apresentou problema -> {log}")
    else:
        print(f"[A] OK: {log['api']} respondeu normalmente.")
