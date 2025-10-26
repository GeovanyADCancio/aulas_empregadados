import threading
import time
import random

contador_global = 0
lock = threading.Lock()

def processar_dados(thread_id, usar_lock=False):
    global contador_global
    for _ in range(100000):
        if usar_lock:
            with lock:
                contador_global += 1
        else:
            # Simula tempo de processamento variável
            valor_temp = contador_global
            time.sleep(random.random() * 0.00001)  # força alternância de threads
            contador_global = valor_temp + 1
    print(f"[Thread {thread_id}] Finalizou.")

if __name__ == "__main__":
    print("=== Exemplo: Threads e Concorrência ===")

    # PARTE 1: Sem lock
    contador_global = 0
    threads = [threading.Thread(target=processar_dados, args=(i, False)) for i in range(5)]

    print("\n--> Rodando sem LOCK (race condition)...")
    for t in threads: t.start()
    for t in threads: t.join()

    print(f"Contador global esperado = 500000, obtido = {contador_global}")
    print("Observe que o valor ficou incorreto devido à competição entre as threads.\n")

    # PARTE 2: Com lock
    contador_global = 0
    threads = [threading.Thread(target=processar_dados, args=(i, True)) for i in range(5)]

    print("--> Rodando com LOCK (sincronizado)...")
    for t in threads: t.start()
    for t in threads: t.join()

    print(f"Contador global esperado = 500000, obtido = {contador_global}")
