# Projeto EngregaDados: Pipeline com Airbyte, Airflow e dbt

---

## 1. Subindo a Infraestrutura Principal (Airflow, Postgres, MinIO)

```bash
# Construir as imagens Docker sem usar o cache
docker compose build --no-cache

# Criar as pastas necessárias mapeadas nos volumes
mkdir -p ./dags ./logs ./dbt_transporte

# Dar permissão total para evitar erros de escrita do Airflow (Errno 13)
sudo chmod -R 777 ./dags ./logs ./dbt_transporte

# Subir os containers em segundo plano
docker compose up -d
```

---

## 2. Gerando os Dados de Origem

Simula o sistema transacional gerando dados no Postgres (Origem na porta 5433) e no MinIO.

```bash
python scripts/raw_data.py
```

---

## 3. Instalando e Subindo o Airbyte

A forma oficial e moderna de rodar o Airbyte localmente é via `abctl`.

```bash
# 1. Baixar e instalar o abctl automaticamente
curl -LsfS https://get.airbyte.com | bash -

# 2. Subir o cluster local do Airbyte
abctl local install

# 3. Pegar as credenciais geradas automaticamente (Email e Senha)
abctl local credentials
```

**Acesso:**  
Abra o navegador em:

```
http://localhost:8000
```

e faça login com as credenciais acima.

---

## 4. Configurando o Airbyte (Interface Gráfica)

### 4.1 Criar Origem (Source) — Postgres Transacional

**Type:** Postgres

- Host: `host.docker.internal` *(Para o Docker enxergar a máquina local)*
- Port: `5433`
- Database: `app_db`
- User: `admin`
- Password: `senha_secreta`


**Nota:**  
Em **Update Method**, escolha:

- `Detect Changes with Xmin System Column` **ou**
- `Scan Changes with User Defined Cursor`

para remover a exigência de CDC/Replicação.

---

### 4.2 Criar Destino (Destination) — Data Warehouse

**Type:** Postgres

- Host: `host.docker.internal`
- Port: `5432`
- Database: `transport_dw`
- Default Schema: `raw`
- User: `admin`
- Password: `senha_secreta`

---

### 4.3 Criar Conexão (Connection)

Conecte a **Origem** ao **Destino**.

- Schedule: `Manual` *(O Airflow é quem vai ditar o ritmo)*
- Sync Mode: `Full Refresh | Overwrite`
- Streams:
  - `raw_drivers`
  - `raw_passengers`

---

### 4.4 Capturar o UUID da Conexão para o Airflow

Após salvar a conexão, olhe a URL no navegador. Será algo como:

```
http://localhost:8000/workspaces/<workspace-id>/connections/<CONNECTION-ID>/status
```

Copie o `<CONNECTION-ID>` e atualize a variável na sua DAG:

```
dags/airbyte_bronze_ingestion.py
```

```python
AIRBYTE_CONNECTION_ID = "coloque-o-id-aqui"
```

---

## 5. Configurando o Airflow e Iniciando a Ingestão

### 5.1 Criar a Conexão com o Airbyte

O Airflow precisa saber como acessar o Airbyte via API.

Acesse:

```
http://localhost:8080
```

Login:
- Usuário: `admin`
- Senha: `admin`

No menu superior:

```
Admin > Connections > +
```

Preencha exatamente:

- **Connection Id:** `airbyte_local` *(Obrigatório este nome)*
- **Connection Type:** `Airbyte`
- **Host:** `host.docker.internal`
- **Port:** `8000`
- **Login:** *(email gerado no passo 3)*
- **Password:** *(senha gerada no passo 3)*

Clique em **Save**.

---

### 5.2 Disparar a Pipeline 🚀

1. Na tela inicial do Airflow (lista de DAGs), ative:
   ```
   airbyte_bronze_ingestion
   ```
   clicando em **Unpause**.

2. Clique no ícone ▶ (**Trigger DAG**).

Se você abrir a aba de conexões do Airbyte, verá a sincronização iniciando automaticamente.

## 6. Ingestão de Dados do MinIO (Data Lake) para o Data Warehouse

Nesta etapa, configuramos a extração do arquivo `raw_trips.csv` armazenado no MinIO (que atua como nosso Data Lake simulando o Amazon S3) para a nossa camada Bronze no PostgreSQL.

### 6.1. Configurando a Origem (Source) no Airbyte
Como o MinIO é compatível com a API do S3, utilizamos o conector oficial do **S3** no Airbyte.

1. Acesse o Airbyte em `http://localhost:8000` e vá em **Sources** > **New source**.
2. Pesquise e selecione o conector **S3**.
3. Preencha os campos de configuração:
   * **Bucket:** `datalake`
   * **Authentication:** Selecione a opção para usar *Access Keys* (HMAC).
   * **AWS Access Key ID:** `admin`
   * **AWS Secret Access Key:** `password123`
4. Na seção **The list of streams to sync**, é obrigatório declarar o arquivo que será lido. Clique em **Add** e preencha:
   * **Name:** `raw_trips`
   * **Format:** `CSV` (garanta que a leitura de cabeçalho/header esteja ativada).
   * **Globs:** `raw_trips.csv`
5. Na seção **Optional fields**, adicione os parâmetros essenciais para o MinIO local:
   * **Endpoint:** `http://host.docker.internal:9000` *(Obrigatório ter o `http://`)*
   * **Region:** `us-east-1`
6. Clique em **Set up source** e aguarde o teste passar (ficar verde).

### 6.2. Configurando o Destino e a Conexão no Airbyte
1. Logo após configurar a origem, escolha o destino **Postgres** já existente (o nosso `transport_dw`).
2. Configure a conexão com os seguintes parâmetros:
   * **Schedule:** Manual
   * **Sync Mode:** Full Refresh | Overwrite
   * **Streams:** Selecione a stream `raw_trips` recém-criada.
3. Clique em **Set up connection**.
4. **Importante:** Após salvar, copie o `<CONNECTION-ID>` que aparece na URL do navegador. Ele tem o formato de um UUID (ex: `c650bff0-e1ce-453d-84d6-6ef25ad5d47b`).


## 7. Configuração e Inicialização do dbt com Docker

Nesta etapa, configuramos a orquestração do dbt pelo Airflow usando o `DockerOperator` e inicializamos a estrutura padrão do projeto dbt seguindo as melhores práticas, sem precisar instalar a ferramenta localmente no host.

---

### 7.1 Ajuste do Caminho Absoluto na DAG do Airflow

O Airflow utiliza o Docker do host (via `docker.sock`) para subir containers efêmeros do dbt.  
Para que o Docker consiga montar os arquivos do projeto corretamente, ele precisa do **caminho absoluto do sistema hospedeiro (host)**, e não do caminho interno do container do Airflow.

1. No arquivo da DAG:

```
dags/dbt_transport_dag.py
```

configure a variável `HOST_PROJECT_PATH` utilizando `os.getenv` para permitir flexibilidade entre ambientes (Local vs Produção):

```python
import os

# O caminho aponta para a pasta do dbt no host (ex: WSL ou diretório local do Windows/Mac)
HOST_PROJECT_PATH = os.getenv(
    "DBT_PROJECT_PATH",
    "/mnt/c/Users/SeuUsuario/.../dbt_transporte"  # Substitua pelo seu caminho absoluto local
)
```

---

### 7.2 Inicializando o Projeto dbt via Container

Como o dbt está instalado apenas na nossa imagem Docker customizada (`dbt_transporte_image:latest`), utilizamos um container interativo temporário para rodar o comando oficial de inicialização (`dbt init`).

Abra o terminal na pasta raiz do dbt:

```
dbt_transporte
```

onde o arquivo `profiles.yml` já está localizado.

Suba um container interativo montando o diretório atual:

```bash
docker run --rm -it \
  -v $(pwd):/usr/app \
  -w /usr/app \
  dbt_transporte_image:latest \
  /bin/bash
```

Dentro do container, execute o comando de inicialização do dbt:

```bash
dbt init transporte_dw
```

*(Selecione a opção correspondente ao banco de dados Postgres quando solicitado.)*

---

O dbt criará uma subpasta com o nome do projeto.  
Para que o Airflow leia os arquivos na raiz da montagem, mova os arquivos gerados um nível para cima e apague a pasta vazia:

```bash
mv transporte_dw/* .
mv transporte_dw/.* . 2>/dev/null  # Move arquivos ocultos, se houver
rmdir transporte_dw
exit
```

---

### 7.3 Próximos Passos: Criação de Models e Tests

Com a estrutura base do dbt criada corretamente — incluindo:

- `models/`
- `tests/`
- `seeds/`
- `macros/`
- `dbt_project.yml`

e a comunicação com o Airflow validada (tasks executando com sucesso), o ambiente está pronto para o desenvolvimento das transformações de dados.