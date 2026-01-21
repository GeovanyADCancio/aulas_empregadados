import csv
import random
import os
import shutil

# Configurações
pasta_saida = "data"
arq_usuarios = os.path.join(pasta_saida, "usuarios.csv")
arq_vendas = os.path.join(pasta_saida, "vendas.csv")

qtd_usuarios = 50_000        # 50 mil clientes
qtd_vendas = 5_000_000       # 5 milhões de vendas

# Limpeza e preparação
if os.path.exists(pasta_saida):
    shutil.rmtree(pasta_saida)

# Cria a pasta 'data'
os.makedirs(pasta_saida, exist_ok=True)

print("--- Gerando Dados para Aula 2 ---")

# 1. Gerar Usuários (Dimensão)
print(f"1. Gerando {qtd_usuarios} usuários...")
estados = ['SP', 'RJ', 'MG', 'RS', 'PE', 'BA', 'AM', 'GO']

# Modo 'w' write cria o arquivo caso não exista. Se existe apaga o conteúdo e recria
with open(arq_usuarios, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["id_user", "nome", "estado", "idade"])
    for i in range(1, qtd_usuarios + 1):
        writer.writerow([
            i, 
            f"Cliente_{i}", 
            random.choice(estados), 
            random.randint(18, 90)
        ])

# 2. Gerar Vendas (Fatos)
print(f"2. Gerando {qtd_vendas} registros de vendas...")
produtos = ['Smartphone', 'TV 4K', 'Geladeira', 'Notebook', 'Fritadeira', 'Sofá']
with open(arq_vendas, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["id_venda", "id_user", "produto", "valor", "timestamp"])
    
    for i in range(1, qtd_vendas + 1):
        writer.writerow([
            i,
            random.randint(1, qtd_usuarios), # Link com usuário
            random.choice(produtos),
            round(random.uniform(20.0, 5000.0), 2),
            random.randint(1672531200, 1704067200) # Timestamp aleatório
        ])

tamanho_vendas = os.path.getsize(arq_vendas) / (1024*1024)
print(f"\nConcluído!")
print(f"Arquivo Vendas: {tamanho_vendas:.2f} MB")
print(f"Arquivos salvos em: {os.path.abspath(pasta_saida)}")