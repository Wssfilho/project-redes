"""
Funções auxiliares para validação e conversão de dados
"""

from constantes import *


def coordenadas_validas(x, y):
    """Valida se coordenadas estão dentro dos limites do tabuleiro"""
    return 0 <= x < TAMANHO_TABULEIRO and 0 <= y < TAMANHO_TABULEIRO


def cor_para_string(cor):
    """Converte código de cor RGB para identificador de texto"""
    if cor == VERDE:
        return "VERDE"
    elif cor == AMARELO:
        return "AMARELO"
    elif cor == PRETO:
        return "PRETO"
    elif cor == BRANCO:
        return "BRANCO"
    else:
        return "DESCONHECIDA"


def eh_movimento_diagonal(origem, destino):
    """Confirma se movimento respeita padrão diagonal das damas"""
    dx = abs(destino[0] - origem[0])
    dy = abs(destino[1] - origem[1])
    return dx == dy
