import pandas as pd
import numpy as np
import random
from faker import Faker
from datetime import datetime, timedelta

# Configurações Iniciais
FAKE = Faker('pt_BR')  # Gera dados em Português (nomes, endereços)
np.random.seed(42)      # Garante que os "erros" sejam sempre os mesmos na aula
random.seed(42)

def gerar_dataset_vendas(n_linhas=1000):
    """
        Gera um dataset de vendas com qualidade degradada intencionalmente
        para exercícios de Data Quality.
    """
    print(f"Gerando {n_linhas} registros de vendas...")
    
    # --- 1. Geração da Base "Limpa" (Ideal) ---
    data = []
    category_list = ['Eletrônicos', 'Livros', 'Casa', 'Moda', 'Brinquedos']
    payment_list = ['Cartão de Crédito', 'Pix', 'Boleto', 'Voucher']
    
    for _ in range(n_linhas):
        price = round(random.uniform(10.0, 5000.0), 2)
        qty = random.randint(1, 5)
        
        record = {
            'transaction_id': FAKE.uuid4(),
            'customer_id': random.randint(1000, 9999),
            'customer_name': FAKE.name(),
            'customer_email': FAKE.email(),
            'transaction_date': FAKE.date_between(start_date='-1y', end_date='today'),
            'category': random.choice(category_list),
            'unit_price': price,
            'quantity': qty,
            'total_amount': round(price * qty, 2), # Cálculo correto inicial
            'payment_method': random.choice(payment_list),
            'status': 'Aprovado'
        }
        data.append(record)
        
    df = pd.DataFrame(data)
    
    # --- 2. Injeção de Erros (A Camada de "Sujeira") ---
    
    # CASO A: Duplicidade (Uniqueness)
    # Pegamos as primeiras 50 linhas e duplicamos no final
    print("-> Injetando duplicatas...")
    duplicates = df.head(50).copy()
    df = pd.concat([df, duplicates], ignore_index=True)
    
    # CASO B: Completude (Completeness / Nulls)
    # Removemos IDs de clientes e E-mails aleatoriamente
    print("-> Injetando valores nulos...")
    mask_null_customer = np.random.rand(len(df)) < 0.05  # 5% sem customer_id
    df.loc[mask_null_customer, 'customer_id'] = np.nan
    
    mask_null_email = np.random.rand(len(df)) < 0.08     # 8% sem email
    df.loc[mask_null_email, 'customer_email'] = None

    # CASO C: Consistência / Regra de Negócio (Consistency)
    # Erro Crítico: Total Amount menor que Unit Price (Matemática errada)
    print("-> Injetando erros de cálculo...")
    indices_erro_calc = df.sample(frac=0.03).index # 3% das linhas
    df.loc[indices_erro_calc, 'total_amount'] = df.loc[indices_erro_calc, 'unit_price'] / 2 
    
    # Erro Crítico: Preço ou Quantidade Negativa
    indices_negativos = df.sample(n=10).index
    df.loc[indices_negativos, 'unit_price'] = df.loc[indices_negativos, 'unit_price'] * -1

    # CASO D: Validade / Tempestividade (Validity)
    # Datas no futuro (Viagem no tempo) e datas muito antigas
    print("-> Injetando datas inválidas...")
    df.loc[0:5, 'transaction_date'] = datetime(2099, 12, 31).date() # Futuro
    df.loc[6:10, 'transaction_date'] = datetime(1900, 1, 1).date()  # Passado remoto
    
    # Datas como String em formato errado (ex: DD/MM/YYYY misturado com YYYY-MM-DD)
    # O Pandas provavelmente converteu tudo para object/datetime, vamos forçar string ruim
    df['transaction_date'] = df['transaction_date'].astype(str)
    df.iloc[15:20, df.columns.get_loc('transaction_date')] = "31/02/2023" # Data inexistente

    # CASO E: Conformidade (Conformity)
    # Sujeira em campos categóricos (Espaços, caixa alta/baixa, typos)
    print("-> Injetando sujeira em strings...")
    
    # "Eletrônicos" vira "eletronicos", "ELETRONICOS ", "Eletro"
    mapa_erros_cat = {
        'Eletrônicos': ['eletronicos', 'ELETRONICOS ', 'Eletro '],
        'Casa': ['casa', 'CASA', 'Home']
    }
    
    def sujar_categoria(valor):
        if valor in mapa_erros_cat and random.random() < 0.2: # 20% de chance de erro
            return random.choice(mapa_erros_cat[valor])
        return valor

    df['category'] = df['category'].apply(sujar_categoria)
    
    # CASO F: Injeção de Tipo Incorreto (Schema Violation)
    # Colocar uma string na coluna de quantidade (que deveria ser int)
    df.iloc[100, df.columns.get_loc('quantity')] = "dois"
    df.iloc[101, df.columns.get_loc('quantity')] = "10 un."

    print(f"Dataset Final Gerado com {len(df)} linhas.")
    return df

# --- Execução ---
df_vendas = gerar_dataset_vendas(n_linhas=2000)

# Visualização Rápida para validação
print("\n--- Amostra dos Dados Sujos ---")
# display(df_vendas.sample(10))

print("\n--- Informações dos Tipos de Dados (Note as colunas 'object') ---")
print(df_vendas.info())

df_vendas.to_csv('./data/sales.csv', index=None)