# 🚚 Projeto Final: Pipeline de Dados Ponta a Ponta - E-Logística Express

Este repositório contém o projeto final da jornada de Engenharia de Dados. O objetivo é simular um ambiente real de uma empresa de logística e e-commerce, integrando dados transacionais em tempo real e dados cadastrais em batch para criar um Data Lakehouse robusto.

---

## 🏢 1. O Problema de Negócio

A **E-Logística Express** é uma empresa em rápido crescimento, mas que sofre com dados descentralizados. Atualmente, a diretoria enfrenta dois grandes problemas:

1.  **Cegueira Operacional (Tempo Real):** O time de operações não sabe quantos pedidos estão entrando no site *agora*, o que dificulta a alocação de entregadores e gestão de estoque imediata.
2.  **Dificuldade Analítica (Histórico):** O time de marketing e vendas demora dias para consolidar relatórios de vendas, performance de vendedores e análise de clientes, pois os dados estão em arquivos soltos e sistemas legados.

**Nossa Missão como Engenheiros de Dados:**
Construir uma arquitetura moderna que suporte tanto a ingestão de dados em tempo real (para o operacional) quanto o processamento em lote (para o analítico), centralizando tudo em um Data Lake e disponibilizando tabelas modeladas em um Data Warehouse.

---

## 🏗️ 2. Arquitetura da Solução

Utilizaremos uma **Arquitetura Medallion** (Bronze, Silver, Gold) com as seguintes ferramentas:

* **Fonte de Dados:** Dataset público do Olist (CSV).
* **Ingestão Batch:** Apache Airflow.
* **Ingestão Streaming:** Apache Kafka.
* **Data Lake (Armazenamento):** MinIO.
* **Processamento/Transformação:** Python (Pandas/Airflow).
* **Data Warehouse (Serving):** PostgreSQL.
* **Visualização:** Power BI.

---

## 📂 3. Base de Dados (Origem)

Utilizaremos o **Brazilian E-Commerce Public Dataset by Olist**, disponível no Kaggle. Este conjunto de dados contém informações de 100k pedidos de 2016 a 2018.

🔗 **Link para Download:** [Kaggle - Olist Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

**Tabelas que utilizaremos:**
1.  `olist_orders_dataset.csv` (Simularemos como Streaming)
2.  `olist_products_dataset.csv` (Carga Batch)
3.  `olist_customers_dataset.csv` (Carga Batch)
4.  `olist_order_items_dataset.csv` (Carga Batch)

> **⚠️ Importante:** Após baixar, descompacte os arquivos e coloque-os dentro da pasta `data/` na raiz deste projeto.

---

## 🛠️ 4. Pré-requisitos

Para executar este projeto, você precisará ter instalado na sua máquina:

* **Docker** e **Docker Compose** (Essencial para subir a infraestrutura).
* **Python 3.8+** (Para rodar os scripts locais de simulação).
* **Git** (Para versionamento).
* **Power BI Desktop** (Opcional, para visualizar o resultado final).

---

## 🚀 5. Configuração do Ambiente (Passo a Passo)

Siga os passos abaixo na ordem para configurar todo o ecossistema.

### Passo 1: Clonar o Repositório
Abra o seu terminal (dentro do WSL):

### Passo 2: Criar o ambiente virtual
```bash
    python3 -m venv .venv
```

### Passo 3: Ativa o ambiente virtual
```bash
    source .venv/bin/activate
```

### Passo 4: Instalar dependências
```bash
    pip install -r requirements.txt
```

### Passo 5: Subir o ambiente
```bash
    docker-compose up -d
```

## ⚙️ 6. Configuração dos Sistemas

### Acesso às Interfaces
* **Airflow:** http://localhost:8080 (User: `airflow`, Pass: `airflow`)
* **MinIO (Data Lake):** http://localhost:9001 (User: `minioadmin`, Pass: `minioadmin`)
* **Postgres (DW):** `localhost:5432` (User: `user`, Pass: `password`, DB: `warehouse`)

### Configurando o Data Lake (MinIO)
1.  Acesse o MinIO no navegador.
2.  Faça login.
3.  No menu lateral, vá em **Buckets** -> **Create Bucket**.
4.  Crie 3 buckets chamados:
    * `bronze`
    * `silver`
    * `gold`

### Configurando Conexões no Airflow
1.  Acesse o Airflow.
2.  Vá em **Admin** -> **Connections**.
3.  Crie/Edite a conexão `aws_default` (usada para o MinIO):
    * **Conn Type:** Amazon Web Services
    * **Extra:** `{"aws_access_key_id": "minioadmin", "aws_secret_access_key": "minioadmin", "endpoint_url": "http://minio:9000"}`
4.  Crie a conexão `postgres_dw`:
    * **Conn Type:** Postgres
    * **Host:** postgres
    * **Login:** user
    * **Password:** password
    * **Schema:** warehouse

---

## ▶️ 7. Execução do Projeto

### A. Ingestão Streaming (Kafka)

1.  Mantenha o terminal aberto.
2.  Execute o script **Consumidor** (ele ficará ouvindo o Kafka e gravando no MinIO):
    ```bash
    python scripts/kafka_consumer_datalake.py
    ```
3.  Abra um **novo terminal**, ative o venv novamente e execute o **Produtor** (Simulador de vendas):
    ```bash
    python scripts/kafka_producer_simulation.py
    ```
    *Você verá logs indicando que pedidos estão sendo enviados.*

### B. Ingestão Batch e Processamento (Airflow)
1.  Acesse o Airflow.
2.  Ative a DAG **`1_ingestion_batch`**: Ela pegará os arquivos CSV da pasta `data/` e enviará para o bucket `bronze`.
3.  Ative a DAG **`2_process_medallion`**:
    * Lê da `bronze`.
    * Trata dados e salva na `silver` (Parquet).
    * Faz a modelagem Star Schema e salva na `gold`.
    * Carrega as tabelas Fato e Dimensão no Postgres.