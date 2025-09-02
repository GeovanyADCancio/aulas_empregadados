## **Comandos da Aula**

### **Configuração do Git**

Crie um novo repositório ou clone um já existente e faça o seu primeiro commit para versionar o projeto.

1.  **Clonar o repositório:**
    ```bash
    git clone git@github.com:GeovanyADCancio/aulas_empregadados.git
    ```
    *Ou, se preferir criar um novo:*
    ```bash
    git init
    ```

2.  **Acessar a pasta do projeto:**
    ```bash
    cd aulas_empregadados
    ```

3.  **Adicionar e salvar arquivos (`commit`):**
    ```bash
    git add .
    git commit -m "Adicionando o arquivo README."
    ```

4.  **Enviar as alterações para o repositório remoto:**
    ```bash
    git push origin main
    ```

5.  **Verificar o histórico de commits:**
    ```bash
    git log
    ```

6.  **Gerenciar branches para novas funcionalidades:**
    ```bash
    git branch dev
    git checkout dev
    git merge main
    ```

---

### **Ambiente Virtual Python (`venv`)**

Configure um ambiente virtual para isolar as dependências do seu projeto.

1.  **Criar o ambiente virtual:**
    ```bash
    python -m venv venv
    ```

2.  **Gerar o arquivo de dependências (`requirements.txt`):**
    ```bash
    pip freeze > requirements.txt
    ```

3.  **Instalar dependências (se o arquivo `requirements.txt` já existir):**
    ```bash
    pip install -r requirements.txt
    ```

---

### **PostgreSQL no WSL**

Siga estes passos para instalar e configurar o PostgreSQL no Subsistema do Windows para Linux (WSL).

#### **Instalação e Início**

1.  **Atualizar os pacotes do sistema:**
    ```bash
    sudo apt update && sudo apt upgrade -y
    ```

2.  **Instalar o PostgreSQL:**
    ```bash
    sudo apt install postgresql postgresql-contrib -y
    ```

3.  **Iniciar o serviço do banco de dados:**
    ```bash
    sudo service postgresql start
    ```

#### **Configuração de Usuário e Banco de Dados**

1.  **Acessar o terminal interativo do PostgreSQL (`psql`):**
    ```bash
    sudo -u postgres psql
    ```

2.  **Criar o usuário `geovany`:**
    ```sql
    CREATE USER geovany WITH SUPERUSER CREATEDB CREATEROLE LOGIN ENCRYPTED PASSWORD '123456789';
    ```

3.  **Criar o banco de dados `analise_funcionarios` e definir o proprietário:**
    ```sql
    CREATE DATABASE analise_funcionarios OWNER geovany;
    ```

4.  **Conceder permissões ao novo banco de dados:**
    ```sql
    GRANT ALL PRIVILEGES ON DATABASE analise_funcionarios TO geovany;
    ```

#### **Configuração para Acesso Externo (Windows)**

Permita que o DBeaver, Python e outras ferramentas no Windows se conectem ao banco de dados rodando no WSL.

1.  **Encontrar o arquivo de configuração:**
    ```bash
    sudo -u postgres psql -c "SHOW config_file;"
    ```

2.  **Editar o arquivo `postgresql.conf`:**
    * Abra o arquivo no editor de texto:
        ```bash
        sudo nano /etc/postgresql/16/main/postgresql.conf
        ```
    * Troque `#listen_addresses = 'localhost'` por:
        ```bash
        listen_addresses = '*'
        ```

3.  **Editar o arquivo `pg_hba.conf`:**
    * Abra o arquivo:
        ```bash
        sudo nano /etc/postgresql/16/main/pg_hba.conf
        ```
    * Adicione a seguinte linha no final para permitir conexões de qualquer IP:
        ```
        host    all             all             0.0.0.0/0                 md5
        ```

4.  **Reiniciar o serviço do PostgreSQL para aplicar as alterações:**
    ```bash
    sudo service postgresql restart
    ```

#### **Liberação da Porta no Firewall do Windows**

Libere a porta 5432 do PostgreSQL no Firewall do Windows para permitir as conexões.

1.  Acesse o **Firewall do Windows com Segurança Avançada**.
2.  No painel esquerdo, clique em **Regras de Entrada** e, em seguida, em **Nova Regra...** no painel da direita.
3.  **Siga o assistente:**
    * **Tipo de Regra:** Selecione **Porta**.
    * **Protocolo e Portas:** Escolha **TCP** e insira **5432** no campo "Portas locais específicas".
    * **Ação:** Selecione **Permitir a conexão**.
    * **Perfil:** Marque todos os perfis (**Domínio**, **Particular**, **Público**).
    * **Nome:** Dê um nome para a regra, por exemplo, `PostgreSQL_WSL`, e finalize.