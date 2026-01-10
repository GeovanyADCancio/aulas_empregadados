# 🌊 Tutorial Completo: Data Lakehouse Local (MinIO + Iceberg + Dremio)

Este guia contém todos os passos e códigos necessários para subir um Data Lakehouse funcional em sua máquina.

## 🚀 2. Execução (Terminal)

Abra o terminal na pasta `lakehouse-demo` e execute:

1. Subir os containers:
   $ docker-compose up -d --build

2. Verificar se o Python gerou os dados corretamente:
   $ docker logs -f iceberg-python

   *Aguarde até ver a mensagem: "🚀 SUCESSO TOTAL! Pronto para o Dremio."*

---

## ⚙️ 3. Configuração do Dremio (Web)

1. Abra o navegador: http://localhost:9047
2. Crie o primeiro usuário (Admin).
3. Clique em **(+) Add Source** (canto inferior esquerdo) -> Selecione **Amazon S3**.

**Configurações Obrigatórias:**

[Aba General]
- Name: MinioLake
- AWS Access Key: minioadmin
- AWS Secret Key: minioadmin
- Encrypt connection: [DESMARCADO] (Muito importante!)

[Aba Advanced Options]
- Enable compatibility mode: [MARCADO]
- Connection Properties (Adicione estas 3):
  1. Nome: fs.s3a.endpoint           Valor: minio:9000
  2. Nome: fs.s3a.path.style.access  Valor: true
  3. Nome: dremio.s3.compat          Valor: true

4. Salve.
5. Navegue na fonte criada: MinioLake -> lakehouse -> default.
6. Passe o mouse na pasta `orders` -> Clique no ícone "Format Table" (lado direito).
7. Escolha "Iceberg" e clique em Save.

---

## 🐘 4. Configuração do DBeaver (SQL Client)

1. Nova Conexão -> Dremio.
2. Host: localhost
3. Port: 31010 (Atenção: Porta JDBC, não a 9047).
4. Username/Password: Os mesmos criados no Dremio.
5. Test Connection -> Finish.

---

## 🧪 5. Comandos SQL

Rode no DBeaver:

-- 1. Consultar dados iniciais
SELECT * FROM MinioLake.lakehouse."default".orders;

-- 2. Inserir novo registro (Lakehouse em ação)
INSERT INTO MinioLake.lakehouse."default".orders 
VALUES (99, 'Daniela SQL', 500.50);

-- 3. Confirmar inserção
SELECT * FROM MinioLake.lakehouse."default".orders;

---

## 📚 Material Complementar
- Apache Iceberg Docs: https://iceberg.apache.org/
- Dremio University: https://www.dremio.com/university/
- MinIO Docker Guide: https://min.io/docs/minio/container/index.html

## 🔥 Desafios
1. Adicione uma coluna 'data_venda' no script Python e veja o Schema Evolution acontecer.
2. Use o comando 'AT SNAPSHOT' no SQL para ver como os dados eram antes do INSERT.
3. Tente conectar o PowerBI ao Dremio usando o conector ODBC/Direct Query.