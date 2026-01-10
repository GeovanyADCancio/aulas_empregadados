FROM apache/airflow:2.7.1

# Copia o arquivo de requisitos para dentro da imagem
COPY requirements.txt .

# Instala as dependências extras (MinIO, Pandas, Kafka, etc)
RUN pip install --no-cache-dir -r requirements.txt