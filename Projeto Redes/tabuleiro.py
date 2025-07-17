"""
Classe Tabuleiro - Representa o tabuleiro do jogo de damas
"""

from constantes import *
from peca import Peca
from quadrado import Quadrado


class Tabuleiro:
    """Gerencia o tabuleiro de damas e suas operações"""
    
    def __init__(self):
        """Inicializa o tabuleiro com a configuração inicial"""
        self.matriz = self._criar_tabuleiro()
    
    def _criar_tabuleiro(self):
        """Cria um novo tabuleiro com as peças na posição inicial"""
        matriz = [[None] * TAMANHO_TABULEIRO for _ in range(TAMANHO_TABULEIRO)]
        
        for x in range(TAMANHO_TABULEIRO):
            for y in range(TAMANHO_TABULEIRO):
                if (x % 2 != 0) and (y % 2 == 0):
                    matriz[y][x] = Quadrado(BRANCO)
                elif (x % 2 != 0) and (y % 2 != 0):
                    matriz[y][x] = Quadrado(PRETO)
                elif (x % 2 == 0) and (y % 2 != 0):
                    matriz[y][x] = Quadrado(BRANCO)
                elif (x % 2 == 0) and (y % 2 == 0):
                    matriz[y][x] = Quadrado(PRETO)
        
        self._colocar_pecas_iniciais(matriz)
        return matriz
    
    def _colocar_pecas_iniciais(self, matriz):
        """Coloca as peças na posição inicial do jogo"""
        # AMARELAS nas 3 primeiras linhas (topo - Y=0,1,2)
        for y in range(3):
            for x in range(TAMANHO_TABULEIRO):
                if matriz[y][x].cor == PRETO:
                    matriz[y][x].colocar_peca(Peca(AMARELO))
        
        # VERDES nas 3 últimas linhas (fundo - Y=5,6,7)
        for y in range(5, TAMANHO_TABULEIRO):
            for x in range(TAMANHO_TABULEIRO):
                if matriz[y][x].cor == PRETO:
                    matriz[y][x].colocar_peca(Peca(VERDE))
    
    def localizacao(self, coordenadas):
        """Retorna o quadrado na posição especificada"""
        x, y = coordenadas
        return self.matriz[y][x]
    
    def no_tabuleiro(self, coordenadas):
        """Verifica se as coordenadas estão dentro do tabuleiro"""
        x, y = coordenadas
        return 0 <= x < TAMANHO_TABULEIRO and 0 <= y < TAMANHO_TABULEIRO
    
    def obter_direcao(self, direcao, coordenadas):
        """Calcula nova posição baseada na direção diagonal especificada"""
        x, y = coordenadas
        
        # Mapear constantes de direção para mudanças de coordenadas
        if direcao == NOROESTE:
            return (x - 1, y - 1)  # Para cima e esquerda
        elif direcao == NORDESTE:
            return (x + 1, y - 1)  # Para cima e direita
        elif direcao == SUDOESTE:
            return (x - 1, y + 1)  # Para baixo e esquerda
        elif direcao == SUDESTE:
            return (x + 1, y + 1)  # Para baixo e direita
        else:
            return (0, 0)  # Direção inválida - retorna origem
    
    def adjacentes(self, coordenadas):
        """Retorna todas as posições diagonalmente adjacentes"""
        return [
            self.obter_direcao(direcao, coordenadas)
            for direcao in [NOROESTE, NORDESTE, SUDOESTE, SUDESTE]
        ]
    
    def _movimentos_rei(self, coordenadas):
        """Retorna movimentos possíveis para um rei (apenas uma casa por vez)"""
        movimentos = []
        direcoes = [NOROESTE, NORDESTE, SUDOESTE, SUDESTE]
        
        # Implementação de movimento restrito para reis:
        # Movem-se apenas uma casa por vez (não múltiplas casas)
        # mas podem se mover em todas as 4 direções diagonais
        for direcao in direcoes:
            proxima_posicao = self.obter_direcao(direcao, coordenadas)
            
            # Validar se a posição está dentro dos limites do tabuleiro
            if not self.no_tabuleiro(proxima_posicao):
                continue
                
            quadrado_proximo = self.localizacao(proxima_posicao)
            
            # Movimento válido apenas para casas vazias
            if quadrado_proximo.esta_vazio():
                movimentos.append(proxima_posicao)
        
        return movimentos
    
    def movimentos_possiveis(self, coordenadas):
        """Calcula movimentos básicos sem validar capturas obrigatórias"""
        quadrado = self.localizacao(coordenadas)
        
        if quadrado.esta_vazio():
            return []
        
        peca = quadrado.ocupante
        
        if peca.rei:
            # Reis: movimento em todas as direções diagonais (uma casa)
            return self._movimentos_rei(coordenadas)
        elif peca.cor == VERDE:
            # Peças verdes: apenas para frente (direção negativa Y)
            return [
                self.obter_direcao(NOROESTE, coordenadas),
                self.obter_direcao(NORDESTE, coordenadas)
            ]
        else:  # peca.cor == AMARELO
            # Peças amarelas: apenas para frente (direção positiva Y)
            # Peças amarelas movem para baixo (direção positiva Y)
            return [
                self.obter_direcao(SUDOESTE, coordenadas),
                self.obter_direcao(SUDESTE, coordenadas)
            ]
    
    def movimentos_legais(self, coordenadas, apenas_pulos=False):
        """Retorna lista de movimentos legais para uma peça"""
        movimentos_possiveis = self.movimentos_possiveis(coordenadas)
        movimentos_legais = []
        peca_atual = self.localizacao(coordenadas).ocupante
        
        if apenas_pulos:
            return self._encontrar_pulos(coordenadas, movimentos_possiveis, peca_atual)
        else:
            return self._encontrar_todos_movimentos(coordenadas, movimentos_possiveis, peca_atual)
    
    def _encontrar_todos_movimentos(self, coordenadas, movimentos_possiveis, peca_atual):
        """Encontra todos os movimentos possíveis (normais e pulos)"""
        movimentos = []
        
        if peca_atual.rei:
            # Para reis, os movimentos possíveis já são todos válidos (casas vazias)
            movimentos.extend(movimentos_possiveis)
            
            # Verificar pulos para reis
            movimentos.extend(self._encontrar_pulos_rei(coordenadas))
        else:
            # Para peças normais, verificar movimentos adjacentes
            for movimento in movimentos_possiveis:
                if not self.no_tabuleiro(movimento):
                    continue
                
                quadrado_destino = self.localizacao(movimento)
                
                if quadrado_destino.esta_vazio():
                    # Movimento normal
                    movimentos.append(movimento)
                elif quadrado_destino.ocupante.cor != peca_atual.cor:
                    # Possível pulo
                    pulo_destino = self._calcular_destino_pulo(coordenadas, movimento)
                    if (self.no_tabuleiro(pulo_destino) and 
                        self.localizacao(pulo_destino).esta_vazio()):
                        movimentos.append(pulo_destino)
        
        return movimentos
    
    def _encontrar_pulos(self, coordenadas, movimentos_possiveis, peca_atual):
        """Encontra apenas movimentos de pulo"""
        if peca_atual.rei:
            return self._encontrar_pulos_rei(coordenadas)
        
        pulos = []
        
        for movimento in movimentos_possiveis:
            if not self.no_tabuleiro(movimento):
                continue
            
            quadrado_destino = self.localizacao(movimento)
            if (quadrado_destino.esta_ocupado() and 
                quadrado_destino.ocupante.cor != peca_atual.cor):
                
                pulo_destino = self._calcular_destino_pulo(coordenadas, movimento)
                if (self.no_tabuleiro(pulo_destino) and 
                    self.localizacao(pulo_destino).esta_vazio()):
                    pulos.append(pulo_destino)
        
        return pulos
    
    def _encontrar_pulos_rei(self, coordenadas):
        """Encontra pulos para reis (damas) - capturas apenas adjacentes em todas as 4 diagonais"""
        pulos = []
        direcoes = [NOROESTE, NORDESTE, SUDOESTE, SUDESTE]
        
        for direcao in direcoes:
            # Posição da peça adjacente (uma casa na diagonal)
            posicao_adjacente = self.obter_direcao(direcao, coordenadas)
            
            # Verificar se está dentro do tabuleiro
            if not self.no_tabuleiro(posicao_adjacente):
                continue
            
            quadrado_adjacente = self.localizacao(posicao_adjacente)
            
            # Se há uma peça inimiga adjacente
            if (quadrado_adjacente.esta_ocupado() and 
                quadrado_adjacente.ocupante.cor != self.localizacao(coordenadas).ocupante.cor):
                
                # Posição de destino após o pulo (uma casa após a peça inimiga)
                posicao_destino = self.obter_direcao(direcao, posicao_adjacente)
                
                # Verificar se o destino está livre e dentro do tabuleiro
                if (self.no_tabuleiro(posicao_destino) and 
                    self.localizacao(posicao_destino).esta_vazio()):
                    pulos.append(posicao_destino)
        
        return pulos
    
    def pode_capturar_novamente(self, coordenadas):
        """Verifica se uma peça pode fazer capturas adicionais da posição atual"""
        quadrado = self.localizacao(coordenadas)
        
        if quadrado.esta_vazio():
            return False
        
        peca = quadrado.ocupante
        
        # Verificar se há pulos possíveis da posição atual
        pulos_possiveis = self._encontrar_pulos(coordenadas, self.movimentos_possiveis(coordenadas), peca)
        
        return len(pulos_possiveis) > 0
    
    def _calcular_destino_pulo(self, origem, peca_inimiga):
        """Calcula o destino de um pulo"""
        x_origem, y_origem = origem
        x_inimiga, y_inimiga = peca_inimiga
        
        return (x_inimiga + (x_inimiga - x_origem), y_inimiga + (y_inimiga - y_origem))
    
    def mover_peca(self, origem, destino):
        """Move uma peça de origem para destino"""
        peca = self.localizacao(origem).remover_peca()
        
        # Verificar se é um pulo e remover peças capturadas
        self._processar_capturas(origem, destino, peca)
        
        self.localizacao(destino).colocar_peca(peca)
        self._verificar_coroacao(destino)
    
    def _processar_capturas(self, origem, destino, peca):
        """Processa capturas durante um movimento"""
        x_origem, y_origem = origem
        x_destino, y_destino = destino
        
        # Calcular diferença de movimento
        dx = x_destino - x_origem
        dy = y_destino - y_origem
        
        # Se é movimento diagonal de exatamente 2 casas, é uma captura
        if abs(dx) == 2 and abs(dy) == 2:
            # Calcular posição da peça capturada (no meio do movimento)
            x_capturada = x_origem + (dx // 2)
            y_capturada = y_origem + (dy // 2)
            
            # Remover a peça capturada
            quadrado_capturado = self.localizacao((x_capturada, y_capturada))
            if quadrado_capturado.esta_ocupado():
                quadrado_capturado.remover_peca()
    
    def remover_peca(self, coordenadas):
        """Remove uma peça do tabuleiro"""
        return self.localizacao(coordenadas).remover_peca()
    
    def _verificar_coroacao(self, coordenadas):
        """Verifica se uma peça deve ser coroada"""
        x, y = coordenadas
        quadrado = self.localizacao(coordenadas)
        
        if quadrado.esta_vazio() or quadrado.ocupante.rei:
            return
            
        peca = quadrado.ocupante
        
        # Peças verdes chegam ao topo (y = 0)
        # Peças amarelas chegam à base (y = 7)
        if (peca.cor == VERDE and y == 0) or (peca.cor == AMARELO and y == TAMANHO_TABULEIRO - 1):
            peca.tornar_rei()
    
    def tem_movimentos_legais(self, cor):
        """Verifica se uma cor tem movimentos legais disponíveis"""
        for x in range(TAMANHO_TABULEIRO):
            for y in range(TAMANHO_TABULEIRO):
                quadrado = self.localizacao((x, y))
                if (quadrado.cor == PRETO and 
                    quadrado.esta_ocupado() and 
                    quadrado.ocupante.cor == cor):
                    
                    if self.movimentos_legais((x, y)):
                        return True
        return False
