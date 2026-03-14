import pandas as pd
from sqlalchemy import create_engine, text
from faker import Faker
import random
from datetime import datetime

# Conecta no Postgres Transacional (Origem - Porta 5433)
engine = create_engine('postgresql://admin:senha_secreta@localhost:5433/app_db')
fake = Faker('pt_BR')

print("--- DEMO DE CARGA INCREMENTAL ---")

# 1. Descobre qual é o maior ID atual na tabela
with engine.connect() as conn:
    result = conn.execute(text("SELECT MAX(driver_id) FROM raw_drivers"))
    max_id = result.scalar() or 0

print(f"Último driver_id encontrado no banco de origem: {max_id}")
print("Simulando o cadastro de 5 novos motoristas no app...")

# 2. Gera 5 novos motoristas
novos_motoristas = []
for i in range(1, 6):
    novo_id = int(max_id) + i
    motorista = {
        'driver_id': novo_id,
        'name': fake.name() + " (NOVO)", # Coloquei (NOVO) para ficar fácil de ver no banco depois
        'city': fake.city(),
        'vehicle_model': fake.license_plate() + " - " + random.choice(['Onix', 'HB20', 'Corolla']),
        'category': random.choice(['X', 'Black', 'Comfort']),
        'joined_at': datetime.now().strftime('%Y-%m-%d')
    }
    novos_motoristas.append(motorista)

df_novos = pd.DataFrame(novos_motoristas)

# 3. O SEGREDO: if_exists='append' (Apenas adiciona as 5 linhas, mantendo as antigas intactas)
df_novos.to_sql('raw_drivers', engine, if_exists='append', index=False)

print(f"Sucesso! Motoristas do ID {max_id + 1} ao {max_id + 5} inseridos no Postgres de origem.")