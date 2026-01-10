from kafka import KafkaConsumer
import json

KAFKA_BROKER = 'localhost:9092'
TOPIC = 'logs.aplicacoes'
GROUP_ID = 'persistencia-historica'

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    group_id=GROUP_ID,
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest'
)

print("🧩 Consumidor D (Persistência) iniciado.\n")

for msg in consumer:
    log = msg.value
    print(f"[D] Gravando log bruto: {log}")
