import json
import time
import random
from kafka import KafkaProducer
from datetime import datetime

KAFKA_BROKER = 'kafka:29092'
TOPIC = 'logs.aplicacoes'

APIS = ['api_login', 'api_pedidos', 'api_pagamentos', 'api_usuarios']
STATUS = ['OK', 'ERRO', 'LENTO']

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("🚀 Enviando logs simulados de microsserviços...")

try:
    while True:
        api = random.choice(APIS)
        status = random.choice(STATUS)
        log = {
            "api": api,
            "status": status,
            "tempo_resposta_ms": random.randint(50, 3000), # 2000, 250
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        producer.send(TOPIC, value=log)
        print(f"📡 Log enviado: {log}")
        time.sleep(3)
except KeyboardInterrupt:
    print("\nEncerrando produtor...")
finally:
    producer.close()
