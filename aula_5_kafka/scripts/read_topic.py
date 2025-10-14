import json
from kafka import KafkaConsumer
from datetime import datetime

# --- Configurações ---
KAFKA_BROKER = 'localhost:9092'  # Endereço do seu broker Kafka
KAFKA_TOPIC = 'aeroporto.public.eventos_voo'
CONSUMER_GROUP = 'monitor-python-grupo' # ID do grupo de consumidores

def formatar_timestamp(ts_micro):
    """Converte timestamp de microssegundos para uma string legível."""
    if ts_micro is None:
        return "N/A"
    # O timestamp do Debezium está em microssegundos, dividimos por 1000000
    return datetime.fromtimestamp(ts_micro / 1000000).strftime('%Y-%m-%d %H:%M:%S')

def analisar_evento(payload):
    """Extrai e formata as informações de um evento do Debezium."""
    
    op = payload.get('op')
    source = payload.get('source', {})
    before = payload.get('before')
    after = payload.get('after')
    
    # Mapeia a operação para uma descrição amigável
    mapa_operacao = {
        'c': 'CREATE (Inserção)',
        'u': 'UPDATE (Atualização)',
        'd': 'DELETE (Remoção)',
        'r': 'READ (Leitura/Snapshot)'
    }
    
    print("\n" + "="*50)
    print(f"✔️ NOVO EVENTO DETECTADO ÀS {datetime.now().strftime('%H:%M:%S')}")
    print("="*50)

    print("\n--- Análise da Mensagem ---")
    
    # 1. Operação
    print(f"\n[OPERAÇÃO]: {mapa_operacao.get(op, 'Desconhecida')}")
    if op == 'c':
        print("  > Um novo registro foi inserido na tabela.")
    elif op == 'u':
        print("  > Um registro existente foi atualizado.")
    elif op == 'd':
        print("  > Um registro foi removido da tabela.")

    # 2. Estado ANTES da alteração
    print("\n[ESTADO 'BEFORE']:")
    if before:
        print(json.dumps(before, indent=2, ensure_ascii=False))
    else:
        print("  > Nulo (típico para operações de INSERT).")
        
    # 3. Estado DEPOIS da alteração
    print("\n[ESTADO 'AFTER']:")
    if after:
        # Extraindo dados específicos do 'after' para melhor visualização
        voo_id = after.get('voo_id')
        evento = after.get('evento')
        observacoes = after.get('observacoes')
        timestamp_voo = formatar_timestamp(after.get('timestamp'))

        print(f"  - Voo ID: {voo_id}")
        print(f"  - Evento: '{evento}'")
        print(f"  - Timestamp do Evento: {timestamp_voo}")
        print(f"  - Observações: '{observacoes}'")
    else:
        print("  > Nulo (típico para operações de DELETE).")
        
    # 4. Metadados da Origem
    print("\n[ORIGEM (SOURCE)]:")
    print(f"  - Conector: {source.get('connector')}")
    print(f"  - Banco de Dados: {source.get('db')}")
    print(f"  - Tabela: {source.get('schema')}.{source.get('table')}")
    print("="*50 + "\n")


if __name__ == "__main__":
    print("Iniciando consumidor Python para o tópico de voos...")
    print(f"Conectando ao broker: {KAFKA_BROKER}")
    print(f"Monitorando o tópico: {KAFKA_TOPIC}")
    print("Aguardando novas mensagens... (Pressione Ctrl+C para sair)")

    consumer = None
    try:
        # value_deserializer converte o JSON (bytes) para um dicionário Python automaticamente
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BROKER,
            auto_offset_reset='latest',  # Começa a ler a partir da última mensagem
            group_id=CONSUMER_GROUP,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )

        # O loop 'for' irá aguardar aqui até que uma nova mensagem chegue
        for message in consumer:
            payload = message.value.get('payload')
            if payload:
                analisar_evento(payload)

    except KeyboardInterrupt:
        print("\nDesligamento solicitado. Encerrando o consumidor...")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    finally:
        if consumer:
            consumer.close()
            print("Consumidor Kafka fechado.")
