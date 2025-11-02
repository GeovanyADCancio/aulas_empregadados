# 1. FROM: Define a Imagem Base (Root Filesystem)
FROM python:3.11-slim-bookworm

# 2. WORKDIR: Define o diretório de trabalho padrão dentro do container.
WORKDIR /app

# 3. COPY: Copia os arquivos de dependência do Host para a Imagem.
COPY requirements.txt .

# 4. RUN: Executa um comando no BUILD TIME (na criação da Imagem).
RUN pip install --no-cache-dir -r requirements.txt

# 5. COPY: Copia os arquivos de código-fonte.
COPY kafka_producer.py .
COPY kafka_consumer.py .
