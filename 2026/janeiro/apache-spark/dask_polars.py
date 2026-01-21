import time
import os
import dask.dataframe as dd
import polars as pl

# --- CONFIGURAÇÃO ---
# O arquivo deve estar na pasta mapeada (work)
filename = "work/dados_gigantes.csv" 

if not os.path.exists(filename):
    print(f"ERRO: Não encontrei {filename}")
    exit()

tamanho_mb = os.path.getsize(filename) / (1024*1024)
print(f"Arquivo alvo: {filename} ({tamanho_mb:.2f} MB)")
print("="*60)
print("TESTE: LEITURA DE DISCO + PROCESSAMENTO (COLD START)")
print("="*60)

# ==========================================
# 1. DASK (Leitura de Disco + GroupBy)
# ==========================================
print("\n1. Iniciando DASK...")
start = time.time()

# read_csv (Lazy) -> GroupBy -> Compute (Dispara leitura e cálculo)
df_dask = dd.read_csv(filename)
res_dask = df_dask.groupby("categoria")["valor"].sum().compute()

end_dask = time.time()
time_dask = end_dask - start
print(f"-> Tempo Dask (Disco): {time_dask:.4f} segundos")


# ==========================================
# 2. POLARS (Leitura de Disco + GroupBy)
# ==========================================
print("\n2. Iniciando POLARS...")
start = time.time()

# scan_csv (Lazy) -> GroupBy -> Collect (Dispara leitura e cálculo)
q = (
    pl.scan_csv(filename)
    .group_by("categoria")
    .agg(pl.col("valor").sum().alias("total"))
)
res_polars = q.collect()

end_polars = time.time()
time_polars = end_polars - start
print(f"-> Tempo Polars (Disco): {time_polars:.4f} segundos")


# ==========================================
# RESULTADO
# ==========================================
print("\n" + "="*30)
print("       PLACAR FINAL")
print("="*30)
print(f"Dask (Disco)  : {time_dask:.4f}s")
print(f"Polars (Disco): {time_polars:.4f}s")
print("-" * 30)
print("Compare estes tempos com a 'Execução 1' do seu Spark.")