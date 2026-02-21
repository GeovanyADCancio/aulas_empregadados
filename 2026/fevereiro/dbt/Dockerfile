# Usa uma imagem Python leve oficial
FROM python:3.10-slim

# Define variáveis de ambiente para o Python não gerar arquivos .pyc e logs imediatos
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala git (necessário para o dbt baixar pacotes/dependências)
RUN apt-get update && apt-get install -y git

# Define o diretório de trabalho dentro do container
WORKDIR /usr/app

# Copia o requirements e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Configuração importante: Onde o dbt vai procurar o profiles.yml
# Vamos apontar para a própria pasta do projeto para facilitar
ENV DBT_PROFILES_DIR=/usr/app

# Comando padrão para manter o container vivo (Zumbi mode)
CMD ["tail", "-f", "/dev/null"]