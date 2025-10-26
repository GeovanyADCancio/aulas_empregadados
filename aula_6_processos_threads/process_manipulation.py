# =============================================
# Demonstração: Processos e Memória Independente
# Engenharia de Dados - Aula de Sistemas Operacionais
# =============================================

import multiprocessing
import os
import time

# Função executada por cada processo
def processar_parte_dataset(numeros, resultado_local):
    print(f"[Processo {os.getpid()}] Iniciando processamento com dados: {numeros}")
    
    soma_local = sum(numeros)
    print(f"[Processo {os.getpid()}] Soma local = {soma_local}")
    
    # Alterando a variável resultado_local (que é uma cópia)
    resultado_local += soma_local
    print(f"[Processo {os.getpid()}] Resultado local alterado para {resultado_local}")
    
    time.sleep(1)  # só para mostrar os processos rodando em paralelo
    print(f"[Processo {os.getpid()}] Finalizado.\n")

if __name__ == "__main__":
    print("=== Exemplo: Processos Multiprocessing ===")
    
    dataset = [1, 2, 3, 4, 5, 6, 7, 8]
    metade = len(dataset) // 2
    
    parte1 = dataset[:metade]
    parte2 = dataset[metade:]

    resultado_global = 0  # cada processo terá sua própria cópia dessa variável

    # Criando dois processos
    p1 = multiprocessing.Process(target=processar_parte_dataset, args=(parte1, resultado_global))
    p2 = multiprocessing.Process(target=processar_parte_dataset, args=(parte2, resultado_global))

    p1.start()
    p2.start()

    p1.join() # Aguarda a execução de p1
    p2.join()

    print(f"[Processo Principal {os.getpid()}] Resultado global final = {resultado_global}")
