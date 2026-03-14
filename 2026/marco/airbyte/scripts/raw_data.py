import pandas as pd
from sqlalchemy import create_engine
import boto3

# 1. Enviar Drivers e Passengers para o PostgreSQL Source
print("Enviando drivers e passengers para o Postgres Source...")
engine = create_engine('postgresql://admin:senha_secreta@localhost:5433/app_db')

df_drivers = pd.read_csv('../datasets/raw_drivers.csv')
df_drivers.to_sql('raw_drivers', engine, if_exists='replace', index=False)

df_passengers = pd.read_csv('../datasets/raw_passengers.csv')
df_passengers.to_sql('raw_passengers', engine, if_exists='replace', index=False)

# 2. Enviar Trips para o MinIO (Simulando um Data Lake/S3)
print("Enviando trips para o MinIO...")
s3_client = boto3.client(
    's3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id='admin',
    aws_secret_access_key='password123'
)

# Faz o upload do arquivo de viagens
s3_client.upload_file('../datasets/raw_trips.csv', 'datalake', 'raw_trips.csv')

print("Carga inicial concluída!")