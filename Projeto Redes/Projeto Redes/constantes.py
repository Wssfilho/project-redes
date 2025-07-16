"""
Arquivo de configuração com todas as constantes do jogo
"""

# === PALETA DE CORES ===
BRANCO = (255, 255, 255)    # Quadrados claros do tabuleiro
VERDE = (0, 255, 0)         # Peças do jogador verde 
AMARELO = (255, 255, 0)     # Peças do jogador amarelo
PRETO = (0, 0, 0)           # Quadrados escuros do tabuleiro
DOURADO = (255, 215, 0)     # Cor de destaque para botões
DESTAQUE = (160, 190, 255)  # Indicador visual de seleção

# === SISTEMA DE DIREÇÕES ===
NOROESTE = "noroeste"   # Diagonal superior esquerda
NORDESTE = "nordeste"   # Diagonal superior direita
SUDOESTE = "sudoeste"   # Diagonal inferior esquerda
SUDESTE = "sudeste"     # Diagonal inferior direita

# === PARÂMETROS DO JOGO ===
TAMANHO_TABULEIRO = 8   # Tabuleiro 8x8 padrão
TAMANHO_JANELA = 600    # Resolução da janela em pixels
FPS = 60                # Taxa de quadros por segundo
TITULO_JOGO = "Damas"   # Título exibido na barra da janela
