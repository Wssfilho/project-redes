"""
Teste para verificar se o problema do turno está sendo resolvido
"""
import json
from constantes import VERDE, AMARELO

# Simula o que acontece no servidor
def simular_servidor():
    turno_atual = VERDE
    print(f"Turno atual no servidor: {turno_atual} (tipo: {type(turno_atual)})")
    
    # Simula serialização JSON
    mensagem = {
        'tipo': 'MOVIMENTO_EXECUTADO',
        'turno': turno_atual
    }
    
    dados_json = json.dumps(mensagem)
    print(f"JSON serializado: {dados_json}")
    
    # Simula deserialização no cliente
    mensagem_recebida = json.loads(dados_json)
    turno_recebido = mensagem_recebida['turno']
    print(f"Turno recebido no cliente: {turno_recebido} (tipo: {type(turno_recebido)})")
    
    # Simula comparação no cliente
    cor_jogador = VERDE  # Cliente é verde
    print(f"Cor do jogador: {cor_jogador} (tipo: {type(cor_jogador)})")
    
    # Teste de comparação direta
    meu_turno_direto = (turno_recebido == cor_jogador)
    print(f"Comparação direta: {meu_turno_direto}")
    
    # Teste com conversão para tupla
    meu_turno_tupla = (tuple(turno_recebido) == tuple(cor_jogador))
    print(f"Comparação com tupla: {meu_turno_tupla}")
    
    # Teste alternando turno
    print("\n--- Alternando turno ---")
    turno_atual = AMARELO if turno_atual == VERDE else VERDE
    print(f"Novo turno atual: {turno_atual}")
    
    mensagem['turno'] = turno_atual
    dados_json = json.dumps(mensagem)
    mensagem_recebida = json.loads(dados_json)
    turno_recebido = mensagem_recebida['turno']
    
    print(f"Turno recebido após alternância: {turno_recebido}")
    
    # Teste para cliente verde
    meu_turno_verde = (tuple(turno_recebido) == tuple(VERDE))
    print(f"É turno do verde: {meu_turno_verde}")
    
    # Teste para cliente amarelo
    meu_turno_amarelo = (tuple(turno_recebido) == tuple(AMARELO))
    print(f"É turno do amarelo: {meu_turno_amarelo}")

if __name__ == "__main__":
    simular_servidor()
