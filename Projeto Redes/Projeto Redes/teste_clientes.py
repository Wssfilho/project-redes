"""
Script simples para testar o problema de turno
"""
import socket
import json
import threading
import time
from constantes import VERDE, AMARELO
from protocolo import TipoMensagem

def cliente_teste(nome, porta_cliente):
    """Cliente de teste simples"""
    try:
        # Conecta ao servidor
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 12345))
        
        print(f"[{nome}] Conectado ao servidor")
        
        # Thread para receber mensagens
        def receber_mensagens():
            buffer = ""
            while True:
                try:
                    dados = sock.recv(1024).decode('utf-8')
                    if not dados:
                        break
                    
                    buffer += dados
                    while '\n' in buffer:
                        linha, buffer = buffer.split('\n', 1)
                        if linha.strip():
                            try:
                                mensagem = json.loads(linha)
                                print(f"[{nome}] RECEBEU: {mensagem['tipo']}")
                                
                                if mensagem['tipo'] == 'MOVIMENTO_EXECUTADO':
                                    print(f"[{nome}] Turno atual: {mensagem['turno']}")
                                    
                            except json.JSONDecodeError:
                                print(f"[{nome}] Erro ao decodificar: {linha}")
                except Exception as e:
                    print(f"[{nome}] Erro na recepção: {e}")
                    break
        
        # Inicia thread de recepção
        thread_recv = threading.Thread(target=receber_mensagens)
        thread_recv.daemon = True
        thread_recv.start()
        
        # Aguarda um pouco para estabelecer conexão
        time.sleep(2)
        
        # Se for cliente 1, faz um movimento
        if nome == "Cliente1":
            print(f"[{nome}] Enviando movimento...")
            movimento = {
                'tipo': TipoMensagem.MOVIMENTO_SOLICITADO.value,
                'origem': [3, 5],
                'destino': [2, 4]
            }
            sock.send((json.dumps(movimento) + '\n').encode('utf-8'))
        
        # Mantém conexão por 10 segundos
        time.sleep(10)
        
    except Exception as e:
        print(f"[{nome}] Erro: {e}")
    finally:
        sock.close()
        print(f"[{nome}] Desconectado")

def main():
    # Inicia dois clientes
    t1 = threading.Thread(target=cliente_teste, args=("Cliente1", 12346))
    t2 = threading.Thread(target=cliente_teste, args=("Cliente2", 12347))
    
    t1.start()
    time.sleep(1)  # Aguarda um pouco antes de conectar o segundo
    t2.start()
    
    t1.join()
    t2.join()

if __name__ == "__main__":
    main()
