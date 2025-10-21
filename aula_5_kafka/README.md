# 🚀 Subindo uma instância local do Apache Kafka com Rancher Desktop

Este guia mostra como configurar e executar o **Apache Kafka localmente** no seu ambiente **WSL + Rancher Desktop**, sem precisar do Docker Desktop.

---

## 🧩 1. Pré-requisitos

Antes de começar, verifique se possui o seguinte instalado:

- ✅ **WSL 2** (Windows Subsystem for Linux)
- ✅ **Rancher Desktop** (substitui o Docker Desktop, baixar em: https://rancherdesktop.io/) 

---

## ⚙️ 2. Configurando o ambiente no Rancher Desktop com WSL

1. Abra o **Rancher Desktop**  
2. Vá em **Preferences → WSL** e habilite a integração com o **Ubuntu**, então clique em **Apply**.
---

## 🐘 3. Subindo o Kafka e o Zookeeper com Docker Compose

Crie um arquivo chamado `docker-compose.yml` na sua pasta de projeto.

## ▶️ 4. Subindo o ambiente

No terminal do **Ubuntu (WSL)**, vá até a pasta onde está o `docker-compose.yml` e execute:

```bash
docker compose up -d
```

Para verificar se os containers estão ativos:

```bash
docker ps
```

Para encerrar os containers:

```bash
docker compose down
```

---

✨ Pronto!
Agora você tem um ambiente Kafka completo rodando localmente com Rancher Desktop — ideal para demonstrações, estudos e desenvolvimento.

---

## 5. Configurando o conector Debezium

```bash
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "debezium-eventosvoo-connector",
    "config": {
      "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
      "plugin.name": "pgoutput",
      "database.hostname": "postgres",
      "database.port": "5432",
      "database.user": "postgres",
      "database.password": "postgres",
      "database.dbname": "mydb",
      "topic.prefix": "aeroporto",
      "slot.name": "slot_eventosvoo",
      "publication.name": "pub_eventosvoo",
      "table.include.list": "public.eventos_voo",
      "tombstones.on.delete": "false",
      "database.history.kafka.bootstrap.servers": "kafka:29092",
      "database.history.kafka.topic": "schema-changes.eventosvoo"
    }
  }'
```
Verifique se o conector foi criado:

```bash
curl http://localhost:8083/connectors/debezium-eventosvoo-connector/status
```

Listar tópicos do kafka:

```bash
docker exec -it kafka kafka-topics --bootstrap-server localhost:9092 --list
```

Monitorar novas mensagens na linha de comando:

```bash
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic aeroporto.public.eventos_voo
```

## 6. Script python para leitura dos dados do tópico

Baixar a biblioteca:

pip install confluent-kafka kafka-python

## 7. Exemplo de consumidores e produtores de logs

Verificar o estado do tópico criado:

```bash
docker exec -it kafka kafka-topics --bootstrap-server localhost:9092 --describe --topic logs.aplicacoes
```

Deletar tópico:

```bash
docker exec -it kafka kafka-topics --bootstrap-server localhost:9092 --delete --topic logs.aplicacoes
```

Criar tópicos com várias partições:

```bash
docker exec -it kafka kafka-topics --bootstrap-server localhost:9092 --create \
 --topic logs.aplicacoes \
 --partitions 2 \
 --replication-factor 1
 ```
