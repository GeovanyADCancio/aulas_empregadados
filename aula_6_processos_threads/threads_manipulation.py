import threading
import time

# Contador global compartilhado entre as threads
contador_global = 0

# Lock (mutex) para evitar race condition
lock = threading.Lock()

def processar_dados(thread_id, usar_lock=False):
    global contador_global
    for _ in range(100000):  # simula trabalho (soma parcial)
        if usar_lock:
            # Usando lock para evitar que duas threads alterem o contador ao mesmo tempo
            with lock:
                contador_global += 1
        else:
            # Sem lock: ocorre race condition
            contador_global += 1
    print(f"[Thread {thread_id}] Finalizou.")

if __name__ == "__main__":
    print("=== Exemplo: Threads e Concorrência ===")

    # PARTE 1: Sem lock (race condition)
    contador_global = 0
    threads = [threading.Thread(target=processar_dados, args=(i, False)) for i in range(5)]

    print("\n--> Rodando sem LOCK (race condition)...")
    for t in threads: t.start()
    for t in threads: t.join()

    print(f"Contador global esperado = 500000, obtido = {contador_global}")
    print("Observe que o valor ficou incorreto devido à competição entre as threads.\n")

    # PARTE 2: Com lock (sincronização)
    contador_global = 0
    threads = [threading.Thread(target=processar_dados, args=(i, True)) for i in range(5)]

    print("--> Rodando com LOCK (sincronizado)...")
    for t in threads: t.start()
    for t in threads: t.join() # Aguarda as threads terminarem

    print(f"Contador global esperado = 500000, obtido = {contador_global}")
    print("Agora o resultado está correto, pois o lock garantiu exclusão mútua!")
