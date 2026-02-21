# 🚀 Pipeline de Dados: dbt, Airflow e Containers Efêmeros

Bem-vindo ao repositório do projeto de Engenharia de Dados! Este guia documenta a evolução da nossa pipeline de transformação de dados para o aplicativo de transportes, desde a execução local até a orquestração profissional.

---

## 📁 Estrutura de Pastas do dbt (Onde cada coisa vive?)

Para entender o dbt como um verdadeiro framework de engenharia de software, é importante conhecer a função de cada pasta gerada no projeto:

* **`macros/` (As "Funções" do SQL):**
  Assim como criamos funções no Python para não repetir código, no dbt criamos *Macros*. Se você tem uma regra de negócio que se repete (ex: converter centavos para reais), você escreve o SQL dinâmico aqui uma vez e reutiliza em qualquer modelo. Isso mantém o código limpo (padrão DRY - Don't Repeat Yourself).

* **`analyses/` (O "Bloco de Notas" do Analista):**
  Lugar para guardar consultas SQL complexas usadas para exploração ou para responder perguntas de negócio específicas. O dbt compila e testa esses códigos, mas **não** cria tabelas ou views deles no banco de dados. Fica tudo salvo e versionado com segurança.

* **`snapshots/` (A "Máquina do Tempo"):**
  Usada para rastrear o histórico dos dados (conhecido como Slowly Changing Dimensions - SCD). Se um usuário muda de cidade, sobrescrever o dado antigo apaga o histórico. Os *snapshots* tiram "fotos" da tabela de tempos em tempos, guardando a informação de que o usuário morou na cidade A até ontem, e na cidade B a partir de hoje.

* **`target/` (O "Forno" de Compilação):**
  O banco de dados não entende as marcações dinâmicas do dbt (como o `{{ ref() }}`). Quando você roda o projeto, o dbt traduz tudo para SQL puro e salva o resultado final dentro desta pasta antes de enviar ao banco. *Nota: Esta pasta é gerada automaticamente e nunca deve ser "commitada" no GitHub.*

* **`logs/` (O "Gravador de Caixa Preta"):**
  Guarda o registro em texto de tudo o que o dbt fez e processou. É exatamente o conteúdo desta pasta que o Apache Airflow "escuta" e captura para exibir as barras de progresso e mensagens de sucesso/erro na sua interface web.

## 🧠 Conceitos Chave da Aula de Hoje

Antes de rodar os comandos, é fundamental entender a arquitetura que estamos construindo:

* **Abordagem Declarativa vs Imperativa:** Em vez de programar "como" testar os dados (ex: usando Python/DuckDB com `if/else`), usamos o dbt para "declarar" em arquivos `.yml` como o dado deve ser. O dbt compila isso em SQL sob os panos.
* **Containers Efêmeros (Docker-out-of-Docker):** O Apache Airflow age apenas como o "Maestro". Ele não instala o dbt. Em vez disso, ele pede ao motor do Docker para criar um container do dbt do zero, executar a transformação/teste e, em seguida, destruir o container. Isso garante um ambiente limpo, sem conflitos e altamente escalável.
* **Circuit Breaker (Disjuntor de Pipeline):** Se um teste de qualidade de dados (`dbt test`) falhar, o Airflow recebe um sinal de erro (Exit Code 1) e interrompe a pipeline imediatamente, impedindo que dados sujos contaminem os dashboards finais.

---

## 🛠️ Fase 1: Setup Básico e Execução Local (dbt puro)

Os comandos abaixo foram utilizados na nossa primeira etapa, rodando o dbt diretamente dentro de um container de desenvolvimento.

# Passo A: Subir a Infraestrutura inicial
docker-compose up -d --build

# Passo B: "Entrar" no container
docker exec -it dbt_dev_env bash

# Passo C: Inicializar o Projeto dbt
dbt init transport_project

# Ajuste de pastas: Se existir uma pasta criada pelo init, mova o conteúdo dela para a raiz
cp -r transport_project/* . 2>/dev/null || :

# Apague a pasta vazia (se ela existir)
rm -rf transport_project

# Fluxo de Trabalho do dbt (Ações Locais):
# 1. Coloque os CSVs na pasta seeds/.
# 2. Crie os arquivos .sql na pasta models/.
# 3. Rode os comandos abaixo no terminal do container:

# Criação das tabelas no banco a partir dos CSVs
dbt seed

# Executar os models (transformações)
dbt run

# Executar testes de qualidade (Data Quality)
dbt test

# Gerar e servir a documentação / linhagem de dados
dbt docs generate
dbt docs serve

# Limpar o schema de teste do banco de dados
dbt run-operation drop_schema --args "{schema: dbt_aluno}"

---

## 🏗️ Fase 2: Orquestração Profissional com Airflow

Nesta fase, passamos a responsabilidade de execução para o Apache Airflow utilizando a técnica de containers efêmeros.

# Passo 1: Fazer o build da imagem do dbt que será usada pelo Airflow
# (Execute este comando na pasta onde está o Dockerfile do dbt)
docker build -t dbt_transporte_image .

# Passo 2: Subir a infraestrutura completa (Airflow + Postgres DW)
# Certifique-se de que o docker-compose.yml possui a rede "dbt_net" bem definida.
docker-compose up -d

# Passo 3: Acessar a Interface do Airflow
# URL: http://localhost:8080
# Usuário/Senha: admin / admin

# Em caso de erro ou necessidade de limpar a infra do Airflow:
docker-compose down -v

---

## 🏆 Desafios para Casa (Nível Sênior)

Para consolidar o aprendizado e aproximar este projeto de um cenário real de engenharia de dados, tente implementar as seguintes melhorias:

### Desafio 1: Alertas de Falha (Email ou Slack)
Atualmente, se a DAG falhar, o Airflow apenas fica vermelho. 
**Missão:** Configure o parâmetro `on_failure_callback` nos `default_args` da DAG do Airflow para enviar um e-mail ou uma mensagem num canal do Slack avisando a equipe de engenharia que a pipeline quebrou.

### Desafio 2: Quarentena de Dados Falhos (Store Failures)
Quando um teste falha de madrugada, precisamos saber quais foram as linhas problemáticas.
**Missão:** Altere o arquivo `schema.yml` do dbt adicionando a configuração `store_failures: true` nos testes (como o `unique` do `trip_id`). Verifique no banco de dados se o dbt criou uma tabela de auditoria guardando apenas os registros que causaram o erro.

### Desafio 3: Padrão Write-Audit-Publish (WAP)
Na nossa DAG atual, rodamos toda a camada Staging, depois toda a camada Marts, e só no final fazemos os testes.
**Missão:** Separe as execuções na DAG do Airflow para que ela teste cada camada antes de avançar. A ordem deve ser:
1. `dbt run --select staging`
2. `dbt test --select staging` (Se falhar aqui, o Airflow cancela o resto!)
3. `dbt run --select marts`
4. `dbt test --select marts`

### Desafio 4: Soft Warnings
Nem todo erro deve parar a empresa. Se o método de pagamento vier como "Pix" (não catalogado), queremos avisar, mas não parar a pipeline.
**Missão:** Configure a `severity: warn` no teste de `accepted_values` do `payment_method`. Rode a DAG no Airflow com um dado errado e perceba que a task ficará verde (sucesso), mas os logs registrarão o aviso.