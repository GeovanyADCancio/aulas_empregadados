#### Recriar o ambiente

abctl local uninstall
rm -rf ~/.airbyte
abctl local install

docker stop airbyte-abctl-control-plane
docker start airbyte-abctl-control-plane

#### Módulo 1: Otimizando a Ingestão com Airbyte (Carga Incremental)


Acesse o Airbyte no navegador: http://localhost:8000.

No menu lateral, clique em Connections e abra a conexão Postgres → Postgres (DW).

Clique na aba Schema.

Na linha da tabela raw_drivers, clique na coluna Sync mode e altere para Incremental | Append.

se O Airbyte pedir um Cursor field, selecione a coluna driver_id.

Clique no botão Save changes (no canto inferior ou superior da tela).

Bash
python scripts/demo_incremental.py

Volte para a interface do Airbyte e clique novamente em Sync now (ou dispare a DAG correspondente no Airflow).

Após o término, clique na aba Timeline (ou em Job History) no Airbyte e abra os logs da execução recente.

## Laboratório Prático: Lidando com Atualizações (Updates) e Duplicidade

O que acontece quando um motorista antigo muda de categoria? Se usarmos o modo `Incremental | Append`, o Airbyte vai puxar a alteração, mas vai empilhar (duplicar) o registro no Data Warehouse. Vamos forçar esse erro e depois corrigi-lo usando o recurso de Deduplicação (`Deduped`).

### Passo 2: Preparar a Origem para Rastrear Atualizações

Para o Airbyte perceber que um dado antigo mudou, a tabela precisa de uma coluna de data de modificação. 
Conecte-se ao seu banco de dados de origem (**Postgres Source - Porta 5433**) e execute o seguinte SQL:

```sql
-- 1. Adiciona a coluna para rastrear quando a linha foi modificada
ALTER TABLE raw_drivers 
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- 2. Atualiza os 5 primeiros motoristas (Simulando uma promoção para a categoria VIP)
UPDATE raw_drivers
SET 
    category = 'VIP', 
    updated_at = CURRENT_TIMESTAMP
WHERE driver_id <= 5;

### Passo 3: Configurar o Airbyte para capturar a alteração (Modo Append)

Agora que a origem tem dados novos e atualizados, precisamos dizer ao Airbyte para olhar para a nova coluna.

2. Vá em **Connections** e abra a conexão **Postgres → Postgres**.
3. Na aba **Schema**, o passo mais importante: clique no botão **Refresh source schema** (🔄) no canto superior direito da lista de tabelas. Sem isso, o Airbyte não enxerga a coluna `updated_at` que acabamos de criar.
4. Na linha da tabela `raw_drivers`, clique na coluna **Sync mode** e altere para **`Incremental | Append`**.
5. **Para definir o Cursor:** * Procure a coluna chamada **Cursor field** (geralmente fica logo à direita do Sync mode). Clique nela e selecione `updated_at`.
   * **Se a coluna não estiver visível:** Clique na setinha (`>`) ou no próprio nome da tabela (`raw_drivers`) para expandir os detalhes dela. Lá dentro, você verá a lista de todas as colunas. Encontre a `updated_at` e marque-a como o Cursor.
6. Clique em **Save changes** e depois no botão **Sync now** para rodar a extração.

### Passo 4: Verificar a duplicidade no Data Warehouse

Como usamos apenas o modo *Append*, o Airbyte simplesmente empilhou a nova versão do dado em cima da antiga. Vamos comprovar isso.

Conecte-se ao **Data Warehouse (Porta 5432)** e execute:

```sql
SELECT 
    driver_id, 
    name, 
    category, 
    updated_at
FROM raw_drivers
WHERE driver_id <= 5
ORDER BY driver_id, updated_at;


UPDATE raw_drivers
SET 
    category = 'TESTE', 
    updated_at = CURRENT_TIMESTAMP
WHERE driver_id <= 5;

DELETE FROM raw_drivers
WHERE driver_id > 10;


#### 

-- 1. Altera o nível do log para lógico (necessário para CDC)
ALTER SYSTEM SET wal_level = logical;

-- 2. Cria a "Publication" (quais tabelas o Airbyte vai ler)
CREATE PUBLICATION airbyte_pub FOR TABLE raw_drivers, raw_passengers;

SELECT pg_create_logical_replication_slot('airbyte_slot', 'pgoutput');

SELECT pg_create_logical_replication_slot('airbyte_slot', 'pgoutput');

docker restart source_transporte

Criar a nova conexão com o CDC neste banco:

- Host: `host.docker.internal` *(Para o Docker enxergar a máquina local)*
- Port: `5433`
- Database: `app_db`
- User: `admin`
- Password: `senha_secreta`
- Replication Slot: `airbyte_slot`
- Publication: `airbyte_pub`

Executando a leitura dos dados deduplicada com CDC

-- ==============================================================================
-- CONFIGURAÇÃO DE CDC (LOGICAL REPLICATION) PARA O AIRBYTE
-- ==============================================================================

-- 1. Altera o nível do log para lógico. Permite que o Postgres registre as mudanças (INSERT/UPDATE/DELETE) em formato legível, não apenas em binário para recuperação de falhas. (Exige reinício do banco).
ALTER SYSTEM SET wal_level = logical;

-- 2. Cria a "Publication" (O Transmissor). Define exatamente quais tabelas vão transmitir as suas alterações para o exterior.
CREATE PUBLICATION airbyte_pub FOR TABLE raw_drivers, raw_passengers;

-- 3. Cria o "Replication Slot" (A Fila/Marcador). Garante que o Postgres guarde os logs até o Airbyte confirmar que os leu. Usa o plugin padrão 'pgoutput'.
SELECT pg_create_logical_replication_slot('airbyte_slot', 'pgoutput');

-- 4. Define Chave Primária. Obrigatório para CDC: permite que o Airbyte saiba exatamente qual linha específica no destino deve ser atualizada ou deletada.
ALTER TABLE raw_drivers ADD PRIMARY KEY (driver_id);

-- 5. Altera a Identidade de Réplica. Força o Postgres a enviar a linha completa (todos os valores antigos) no log durante um UPDATE ou DELETE, garantindo precisão na desduplicação.
ALTER TABLE raw_drivers REPLICA IDENTITY FULL;

-- 6. Verificação: Confirma se o slot de replicação foi criado e está ativo no banco correto.
SELECT slot_name, database FROM pg_replication_slots WHERE slot_name = 'airbyte_slot';

-- 7. Permissão de Usuário. Concede ao usuário 'admin' o privilégio especial necessário para ler o fluxo contínuo de replicação do banco.
ALTER ROLE admin REPLICATION;

-- 8. Verificação: Confirma se a publicação (o transmissor) foi registrada corretamente no sistema.
SELECT pubname FROM pg_publication