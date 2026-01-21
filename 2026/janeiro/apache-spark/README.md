# 1️⃣ Como saber quantos núcleos de CPU seu computador tem

## 🔹 Windows (mais simples)

1. `Ctrl + Shift + Esc` → Gerenciador de Tarefas
2. Aba **Desempenho**
3. Clique em **CPU**

Você verá algo como:
- **Núcleos:** 8
- **Processadores lógicos:** 16

📌 Para Spark, o número mais importante é **NÚCLEOS**.

---

# 2️⃣ Configuração do Ambiente

### 🐍 Criar o ambiente virtual no WSL:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 🐳 Iniciar o ecossistema:
```bash
docker-compose up -d
```

---

## ⚠️ REGRA DE OURO: Evitando a "Porta Presa"

O Docker foi configurado para expor a Spark UI na porta **4040**. No entanto, o Spark é "educado": se a porta 4040 estiver ocupada, ele muda automaticamente para a **4041**, **4042**, etc.

### O Problema:
Nosso Docker só libera a porta **4040**. Se o Spark mudar de porta internamente, você perderá o acesso visual ao painel (`localhost:4040`).

### A Solução:
Sempre que terminar um Notebook e for abrir outro:

1. Vá no menu lateral esquerdo do Jupyter Lab.
2. Clique no ícone **"Running Terminals and Kernels"** (círculo com quadrado).
3. Em **KERNELS**, clique em **SHUT DOWN** (X) no notebook antigo.
4. Só então inicie o novo notebook.

---

# 🚀 Desafios Pós-Aula

Para fixar o conteúdo, tente resolver os desafios abaixo. Eles simulam tarefas reais de um Engenheiro de Dados.

## 🏆 Desafio 1: O Poliglota (Python vs SQL)

Aprendemos que o **Catalyst Optimizer** torna o SQL e o Python equivalentes em performance. Prove isso!

1. Abra o `lazy_check.ipynb`.
2. Registre o DataFrame de Vendas como uma tabela temporária:
```python
df_vendas.createOrReplaceTempView("tb_vendas")
```

3. Reescreva a lógica de filtro e cálculo usando SQL (`spark.sql("SELECT ...")`).
4. Use o `time.time()` para medir o tempo de execução do `.count()` na versão Python e na versão SQL.

**Pergunta:** A diferença de tempo foi significativa? (Dica: deve ser quase idêntico).

---

## 🏆 Desafio 2: Tunando o Shuffle

No `shuffle.ipynb`, vimos o **SortMergeJoin**. O Spark, por padrão, cria **200 partições** sempre que faz um Shuffle (comando `spark.sql.shuffle.partitions`).

Para nossos dados pequenos (alguns MBs), 200 partições é exagero (cria muitos arquivos minúsculos e overhead).

1. Tente alterar essa configuração antes de rodar o Join:
```python
spark.conf.set("spark.sql.shuffle.partitions", "5")
```

2. Rode o Join com Shuffle novamente. Ficou mais rápido ou mais lento?
3. Tente mudar para `"1"` partição. O que acontece?
4. Olhe na Spark UI (Stages) como o número de Tasks muda de acordo com esse número.

---

# 📚 Material Complementar

Aqui estão os links oficiais e leituras recomendadas para aprofundar:

## 📖 Documentação Oficial

- **PySpark DataFrame API** - O "dicionário" de comandos.
- **Spark SQL Guide** - Guia completo de SQL no Spark.

## 🧠 Entendendo a Arquitetura

- **Cluster Mode Overview:** [Link](https://spark.apache.org/docs/latest/cluster-overview.html) - Entenda Driver, Executor e Cluster Manager.
- **Tuning Spark:** [Link](https://spark.apache.org/docs/latest/tuning.html) - Dicas avançadas de performance.

## 🛠 Ferramentas

- **Spark UI:** Explicação visual das abas - Entenda o que cada gráfico significa.