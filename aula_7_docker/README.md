# 🚀 Ambiente de Logs Kafka com Docker

### 🛠️ Pré-requisitos
* ### Docker Engine (ou Rancher Desktop) instalado e rodando.
* ### Os arquivos `docker-compose.yml`, `Dockerfile`, `requirements.txt`, `logs_producer.py` e `consumidor_A_monitoramento.py` na mesma pasta.

---

### 🐳 Comandos Essenciais do Docker e Docker Compose

### 1. Construção e Execução (Docker Compose)
Este é o modo preferencial, pois inicia a arquitetura completa (Zookeeper, Kafka, Postgres, Produtor, Consumidor).

* ### **Construir Imagens e Subir Serviços (Modo Padrão):**
    ```bash
    docker-compose up --build -d
    ```
    (O `--build` garante que o Dockerfile do seu Produtor/Consumidor seja recompilado caso haja mudanças no código ou no `requirements.txt`).

* ### **Subir em Segundo Plano (Modo Detached):**
    ```bash
    docker-compose up -d
    ```

* ### **Visualizar Logs de Todos os Serviços:**
    ```bash
    docker-compose logs -f
    ```

* ### **Parar e Remover Containers, Redes e Volumes (Limpeza Total):**
    ```bash
    docker-compose down -v
    ```
    (O `-v` é crucial para remover o volume persistente do Postgres (`pgdata_new`), se você desejar uma limpeza completa do ambiente, incluindo os dados).

---

### 2. Explorando Containers (Status e Debug)

* ### **Listar Containers em Execução (Todos os Serviços Ativos):**
    ```bash
    docker ps
    ```
    (Use `docker ps -a` para ver todos, incluindo os parados).

* ### **Inspecionar Detalhes de um Container Específico:**
    ```bash
    docker inspect kafka
    ```
    (Substitua `kafka` pelo nome do container, ex: `zookeeper` ou `logs_producer_container`).

* ### **Acessar o Terminal de um Container em Execução (para Debug):**
    ```bash
    docker exec -it kafka /bin/bash
    ```
    (Você entrará no shell do container Kafka para explorar arquivos ou executar comandos).

---

### 3. ### Gerenciamento de Imagens e Redes

* ### **Listar Todas as Imagens Locais:**
    ```bash
    docker images
    ```

* ### **Remover uma Imagem Local (pelo ID ou Nome):**
    ```bash
    docker rmi <ID_DA_IMAGEM>
    ```

* ### **Listar Todas as Redes Criadas pelo Docker:**
    ```bash
    docker network ls
    ```
    (Você verá a rede que o Docker Compose criou, geralmente nomeada `[nome_da_pasta]_default`).

---

### 4. Construção Direta do Dockerfile (Sem Compose)

Use este comando para demonstrar como o **`Dockerfile`** se transforma em uma **Imagem**, antes que o Compose entre em ação.

* ### **Construir a Imagem e Nomeá-la:**
    ```bash
    docker build -t app-kafka-py:latest .
    ```
    (O `-t` nomeia a imagem como `app-kafka-py:latest`. O `.` indica que o `Dockerfile` está no diretório atual).

* ### **Rodar o Produtor a partir da Imagem Criada (Alternativa ao Compose):**
    ```bash
    docker run -it --network=[nome_da_rede_do_compose] app-kafka-py:latest python logs_producer.py
    ```
    (É necessário conectar manualmente à rede do Compose para que ele encontre o Kafka. Isso ilustra o poder do Compose de gerenciar a rede automaticamente).
