import time

start_time = time.time()

# Lógica Python Tradicional (Lê linha a linha)
somas = {}
contagem = 0
filename = "work/dados_gigantes.csv"

with open(filename, 'r') as f:
    header = next(f) # Pula cabeçalho
    for line in f:
        partes = line.strip().split(',')
        categoria = partes[1]
        valor = float(partes[2])
        
        if categoria in somas:
            somas[categoria] += valor
        else:
            somas[categoria] = valor
        contagem += 1

end_time = time.time()

print(f"Resultado Python: {somas}")
print(f"Tempo Python Puro: {end_time - start_time:.4f} segundos")