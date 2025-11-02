import os
import time

# Pega o Process ID (PID) deste script
meu_pid = os.getpid()

print(f"Olá! Eu sou um processo do sistema operacional.")
print(f"Meu Process ID (PID) é: {meu_pid}")
print("Vou ficar 'dormindo' por 60 segundos para você me encontrar.")
print("Abra outro terminal e procure pelo meu PID...")

try:
    # Mantém o script em execução por 60 segundos
    time.sleep(60)
except KeyboardInterrupt:
    # Permite que você pare o script com Ctrl+C
    print("\nScript interrompido.")

print(f"PID {meu_pid} está terminando. Adeus!")