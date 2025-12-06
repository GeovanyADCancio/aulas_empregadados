import socket
import threading

# Configurações de Endereço
HOST = '0.0.0.0'  # 0.0.0.0 permite conexões externas (importante para Docker)
PORT_TCP = 50000
PORT_UDP = 50001

def start_tcp_server():
    """Funciona como uma CHAMADA TELEFÔNICA (Conexão persistente)"""
    print(f"[TCP] Iniciando protocolo SOCK_STREAM (Garantia de entrega)...")
    
    # 1. Cria o Socket TCP (IPv4, Stream/Fluxo): AF_INET -> IPV4; SOCK_STREAM -> Garantia de entrega
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 2. Configuração para liberar a porta rápido se o script travar (Evita erro 'Address in use')
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # 3. Bind: "Reserva" a porta 50000 para este processo
    server.bind((HOST, PORT_TCP))
    
    # 4. Listen: Entra em modo passivo, cria a fila de espera. Exclusivo do TCP.
    server.listen(1)
    print(f"[TCP] 👂 Ouvindo em {HOST}:{PORT_TCP}. Aguardando 'connect()' do cliente...")
    
    while True:
        # 5. Accept (BLOQUEANTE): O código para aqui até ocorrer o Handshake (SYN/ACK).
        # Retorna 'conn' (o túnel exclusivo) e 'addr' (quem conectou).
        conn, addr = server.accept()
        print(f"[TCP] 🤝 Conexão estabelecida com {addr}")
        
        try:
            # 6. Recv: Lê do túnel. Se o cliente parar de falar, fica esperando.
            data = conn.recv(1024)
            if data:
                # 7. Send: Responde pelo mesmo túnel já aberto.
                conn.send(data)
        except Exception as e:
            print(f"[TCP] Erro: {e}")
        finally:
            # 8. Close: Encerra a chamada (envia pacote FIN). Importante para liberar recursos do DB.
            conn.close()

def start_udp_server():
    """Funciona como CORREIO (Cartas soltas, sem conexão)"""
    print(f"[UDP] Iniciando protocolo SOCK_DGRAM (Fire and Forget)...")
    
    # 1. Cria o Socket UDP (IPv4, Datagrama/Pacote soltos)
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # 2. Bind: Apenas abre a "caixa de correio" na porta 50001.
    # NOTA: Não existe listen() nem accept() no UDP.
    server.bind((HOST, PORT_UDP))
    print(f"[UDP] 👂 Ouvindo em {HOST}:{PORT_UDP}. Pronto para receber pacotes soltos.")
    
    while True:
        # 3. RecvFrom: Recebe a mensagem E o endereço de quem mandou.
        # Como não há conexão fixa, cada pacote traz seu remetente.
        data, addr = server.recvfrom(1024)
        
        if data:
            print(f"[UDP] 📩 Pacote recebido de {addr}")
            # 4. SendTo: Para responder, precisamos especificar o endereço explicitamente.
            server.sendto(data, addr)

if __name__ == "__main__":
    # Rodando ambos em paralelo (Threads) para a demonstração
    t1 = threading.Thread(target=start_tcp_server)
    t2 = threading.Thread(target=start_udp_server)
    t1.start()
    t2.start()