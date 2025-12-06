import socket
import time

HOST = 'localhost' # Mude para o nome do serviço se usar Docker Compose
PORT_TCP = 50000
PORT_UDP = 50001
PAYLOAD = "DADOS_CRITICOS_DE_VENDAS".encode('utf-8')

def teste_tcp():
    print(f"\n--- INICIANDO TESTE TCP (O Burocrático) ---")
    start = time.perf_counter()
    
    # 1. Criação
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # 2. Connect (O GRANDE CUSTO): Realiza o Three-Way Handshake.
        # Envia SYN -> Recebe SYN-ACK -> Envia ACK.
        # Se o servidor não estiver ouvindo, falha aqui (ConnectionRefused).
        sock.connect((HOST, PORT_TCP))
        
        # 3. Send: Envia stream de dados garantido.
        sock.send(PAYLOAD)
        
        # 4. Recv: Espera a confirmação/resposta do servidor.
        resp = sock.recv(1024)
        
        # 5. Close: Encerra educadamente.
        sock.close()
        
        tempo = (time.perf_counter() - start) * 1000
        print(f"[TCP] ✅ Sucesso. Tempo total (Handshake + Dados): {tempo:.4f} ms")
        
    except Exception as e:
        print(f"[TCP] ❌ Falha: {e}")

def teste_udp():
    print(f"\n--- INICIANDO TESTE UDP (O Rápido) ---")
    start = time.perf_counter()
    
    # 1. Criação
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # 2. Timeout: Vital para UDP. Se o pacote se perder, o script não trava para sempre.
    sock.settimeout(2.0)
    
    try:
        # 3. SendTo (SEM HANDSHAKE): Apenas joga o pacote na rede.
        # Não verifica se o servidor está ativo antes de enviar.
        sock.sendto(PAYLOAD, (HOST, PORT_UDP))
        
        # 4. RecvFrom: Tenta ouvir resposta (se houver).
        data, server = sock.recvfrom(1024)
        
        sock.close()
        
        tempo = (time.perf_counter() - start) * 1000
        print(f"[UDP] ✅ Sucesso. Tempo total (Apenas Dados): {tempo:.4f} ms")
        
    except socket.timeout:
        print(f"[UDP] ⚠️ Timeout: Enviei, mas não recebi resposta (Pacote perdido?)")

if __name__ == "__main__":
    teste_tcp()
    teste_udp()
