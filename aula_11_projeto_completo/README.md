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

* **WSL** e **Rancher Desktop** (Essencial para subir a infraestrutura).
* **Python 3.8+** (Para rodar os scripts locais de simulação).
* **Git** (Para versionamento).

---

## 🚀 5. Configuração do Ambiente (Passo a Passo)

Siga os passos abaixo na ordem para configurar todo o ecossistema.

### Passo 1: Clonar o Repositório

Abra o seu terminal (dentro do WSL ou Git Bash).

### Passo 2: Criar o ambiente virtual

```bash
python3 -m venv .venv
```

### Passo 3: Ativar o ambiente virtual

```bash
# No Linux/Mac/WSL:
source .venv/bin/activate

# No Windows (Powershell):
.venv\Scripts\Activate
```

### Passo 4: Instalar dependências

```bash
pip install -r requirements.txt
```

### Passo 5: Subir o ambiente

```bash
docker-compose up -d
```

⚙️ 6. Configuração dos Sistemas

Acesso às Interfaces

Airflow: http://localhost:8080 (User: airflow, Pass: airflow)

MinIO (Data Lake): http://localhost:9001 (User: minioadmin, Pass: minioadmin)

Postgres (DW): localhost:5432 (User: user, Pass: password, DB: warehouse)

Configurando o Data Lake (MinIO)

Acesse o MinIO no navegador.

Faça login.

No menu lateral, vá em Buckets -> Create Bucket.

Crie 3 buckets chamados:

bronze  
silver  
gold  
fraud-cases

Configurando Conexões no Airflow

Acesse o Airflow.

Vá em Admin -> Connections.

Crie/Edite a conexão aws_default (usada para o MinIO):

Conn Type: Amazon Web Services

Extra:
```json
{"aws_access_key_id":"minioadmin","aws_secret_access_key":"minioadmin","endpoint_url":"http://minio:9000"}
```

Crie a conexão postgres_dw:

Conn Type: Postgres  
Host: postgres  
Login: user  
Password: password  
Schema: warehouse  

▶️ 7. Execução do Projeto

### A. Ingestão Streaming (Kafka)

Mantenha o terminal aberto.

Execute o script Consumidor (ele ficará ouvindo o Kafka e gravando no MinIO):

```bash
python scripts/kafka_consumer_datalake.py
```

Abra um novo terminal, ative o venv novamente e execute o Produtor (Simulador de vendas):

```bash
python scripts/kafka_producer_simulation.py
```

Você verá logs indicando que pedidos estão sendo enviados.

### B. Ingestão Batch e Processamento (Airflow)

Acesse o Airflow.

Ative a DAG 1_process_medallion:

- Lê da bronze  
- Trata dados e salva na silver (Parquet)  
- Faz a modelagem Star Schema e salva na gold  
- Carrega as tabelas Fato e Dimensão no Postgres  


## 📚 8. Material de Apoio e Referências Bibliográficas

Para aprofundar seus conhecimentos nos conceitos aplicados neste projeto, recomendamos as seguintes leituras e vídeos:

### 📖 Livros Essenciais
* **Fundamentos de Engenharia de Dados** (Joe Reis & Matt Housley) - *A "bíblia" moderna da área. Foca em conceitos agnósticos de ferramentas.*
* **Designing Data-Intensive Applications** (Martin Kleppmann) - *Leitura obrigatória para entender como sistemas distribuídos (como Kafka) funcionam por baixo do capô.*

### 📄 Artigos e Documentação Oficial
* [What is a Data Lakehouse?](https://www.databricks.com/glossary/data-lakehouse) - *Explicação oficial da Databricks sobre a união de Data Lakes e Data Warehouses.*
* [Medallion Architecture (Bronze, Silver, Gold)](https://www.databricks.com/glossary/medallion-architecture) - *Entenda a lógica de refinamento de dados em camadas.*
* [Apache Kafka: Introduction](https://kafka.apache.org/intro) - *Documentação oficial, excelente para entender Tópicos, Partições e Brokers.*
* [Hive Partitioning Layout](https://docs.aws.amazon.com/athena/latest/ug/partitions.html) - *Por que organizamos pastas como `year=2023/month=10`? (Conceito da AWS/Athena).*
* [Airflow Concepts](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/index.html) - *Entenda o que são DAGs, Operators e Tasks.*

## 📝 9. Tarefas de Casa / Desafios

Quer levar este projeto para o próximo nível? Tente implementar as seguintes melhorias para enriquecer seu portfólio:

### 🥈 Nível 1: Expandindo o Data Warehouse (Batch / Airflow)
**O Desafio:** O time de vendas quer analisar a performance dos Vendedores (Sellers), mas essa tabela ainda não está no nosso DW.
* **Tarefa:**
    1.  Adicione o arquivo `olist_sellers_dataset.csv` na pasta `data/`.
    2.  Crie uma nova DAG (ou edite a existente) para ingerir esse arquivo na camada **Bronze**.
    3.  Na camada **Silver**, padronize os nomes das cidades (ex: tudo maiúsculo).
    4.  Na camada **Gold**, crie a tabela `dim_sellers` e carregue-a no PostgreSQL.

### 🥇 Nível 2: Business Intelligence (Analytics / Power BI)
**O Desafio:** A diretoria quer ver gráficos, não apenas tabelas no banco de dados.
* **Tarefa:**
    1.  Abra o Power BI Desktop (ou outra ferramenta de BI).
    2.  Conecte-se ao banco PostgreSQL local (`localhost:5432`, banco `warehouse`).
    3.  Importe as tabelas `fact_orders` e `dim_products`.
    4.  **Responda visualmente:** "Qual categoria de produtos tem o maior custo médio de frete?"
    5.  **Responda visualmente:** "Qual estado (UF) tem o maior número de pedidos?"