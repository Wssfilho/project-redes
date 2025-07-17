"""
Classe Graficos - Responsável pela interface gráfica do jogo
"""

import pygame
from constantes import *


class Graficos:
    """Gerencia a interface gráfica do jogo de damas"""
    
    def __init__(self):
        """Inicializa o sistema gráfico"""
        self.titulo = TITULO_JOGO
        self.fps = FPS
        self.relogio = pygame.time.Clock()
        
        self.tamanho_janela = TAMANHO_JANELA
        self.tela = pygame.display.set_mode((self.tamanho_janela, self.tamanho_janela))
        
        # Carregar imagem de fundo do tabuleiro com fallback para padrão
        try:
            self.fundo = pygame.image.load('resources/tabuleiro.png')
        except pygame.error:
            # Se não encontrar imagem, usa desenho procedural do tabuleiro
            self.fundo = None
        
        # Calcular tamanhos
        self.tamanho_quadrado = self.tamanho_janela // TAMANHO_TABULEIRO
        self.tamanho_peca = self.tamanho_quadrado // 2
        
        # Carregar e redimensionar imagens das peças com sistema de fallback
        try:
            imagem_peca_amarela = pygame.image.load('resources/peca_amarela.png')
            tamanho_imagem = self.tamanho_peca * 2  # Diâmetro da peça
            self.imagem_peca_amarela = pygame.transform.scale(imagem_peca_amarela, (tamanho_imagem, tamanho_imagem))
        except pygame.error:
            # Usa desenho procedural se não encontrar imagem personalizada
            self.imagem_peca_amarela = None
        
        try:
            imagem_peca_verde = pygame.image.load('resources/peca_verde.png')
            tamanho_imagem = self.tamanho_peca * 2  # Diâmetro da peça
            self.imagem_peca_verde = pygame.transform.scale(imagem_peca_verde, (tamanho_imagem, tamanho_imagem))
        except pygame.error:
            # Usa desenho procedural se não encontrar imagem personalizada
            self.imagem_peca_verde = None
        
        try:
            imagem_dama_amarela = pygame.image.load('resources/peca_amarela_dama.png')
            tamanho_imagem = self.tamanho_peca * 2  # Diâmetro da peça
            self.imagem_dama_amarela = pygame.transform.scale(imagem_dama_amarela, (tamanho_imagem, tamanho_imagem))
        except pygame.error:
            # Usa desenho procedural se não encontrar imagem personalizada
            self.imagem_dama_amarela = None
        
        try:
            imagem_dama_verde = pygame.image.load('resources/peca_verde_dama.png')
            tamanho_imagem = self.tamanho_peca * 2  # Diâmetro da peça
            self.imagem_dama_verde = pygame.transform.scale(imagem_dama_verde, (tamanho_imagem, tamanho_imagem))
        except pygame.error:
            # Usa desenho procedural se não encontrar imagem personalizada
            self.imagem_dama_verde = None
        
        # Estado da mensagem
        self.mensagem_ativa = False
        self.superficie_texto = None
        self.retangulo_texto = None
        
        # Configurar ícone da janela
        self._configurar_icone()
    
    def _configurar_icone(self):
        """Configura o ícone da janela do jogo"""
        try:
            # Carrega ícone personalizado se disponível
            icone = pygame.image.load('resources/icon.png')
            pygame.display.set_icon(icone)
        except pygame.error:
            # Usa ícone padrão do sistema se não encontrar arquivo
            pass
    
    def configurar_janela(self):
        """Configura a janela do jogo"""
        pygame.init()
        pygame.display.set_caption(self.titulo)
    
    def atualizar_tela(self, tabuleiro, movimentos_legais, peca_selecionada):
        """Atualiza a tela do jogo"""
        # Desenhar fundo
        if self.fundo:
            self.tela.blit(self.fundo, (0, 0))
        else:
            self._desenhar_tabuleiro_padrao(tabuleiro)
        
        # Destacar movimentos e peça selecionada
        self._destacar_quadrados(movimentos_legais, peca_selecionada)
        
        # Desenhar peças
        self._desenhar_pecas_tabuleiro(tabuleiro)
        
        # Desenhar mensagem se houver
        if self.mensagem_ativa and self.superficie_texto:
            self.tela.blit(self.superficie_texto, self.retangulo_texto)
        
        # Atualizar display
        pygame.display.update()
        self.relogio.tick(self.fps)
    
    def _desenhar_tabuleiro_padrao(self, tabuleiro):
        """Desenha o tabuleiro quando não há imagem de fundo"""
        for x in range(TAMANHO_TABULEIRO):
            for y in range(TAMANHO_TABULEIRO):
                rect = (x * self.tamanho_quadrado, y * self.tamanho_quadrado,
                       self.tamanho_quadrado, self.tamanho_quadrado)
                cor_quadrado = tabuleiro.localizacao((x, y)).cor
                pygame.draw.rect(self.tela, cor_quadrado, rect)
    
    def _desenhar_pecas_tabuleiro(self, tabuleiro):
        """Desenha todas as peças no tabuleiro"""
        for x in range(TAMANHO_TABULEIRO):
            for y in range(TAMANHO_TABULEIRO):
                quadrado = tabuleiro.matriz[x][y]
                
                if quadrado.esta_ocupado():
                    centro = self._coordenadas_pixel((x, y))
                    peca = quadrado.ocupante
                    
                    # Desenhar peças com imagens ou círculos de fallback
                    if peca.cor == AMARELO:
                        if peca.rei and self.imagem_dama_amarela:
                            # Usar imagem da dama amarela
                            pos_imagem = (centro[0] - self.tamanho_peca, centro[1] - self.tamanho_peca)
                            self.tela.blit(self.imagem_dama_amarela, pos_imagem)
                        elif self.imagem_peca_amarela:
                            # Usar imagem da peça amarela normal
                            pos_imagem = (centro[0] - self.tamanho_peca, centro[1] - self.tamanho_peca)
                            self.tela.blit(self.imagem_peca_amarela, pos_imagem)
                        else:
                            # Usar círculo se imagem não carregou
                            pygame.draw.circle(self.tela, peca.cor, centro, self.tamanho_peca)
                    elif peca.cor == VERDE:
                        if peca.rei and self.imagem_dama_verde:
                            # Usar imagem da dama verde
                            pos_imagem = (centro[0] - self.tamanho_peca, centro[1] - self.tamanho_peca)
                            self.tela.blit(self.imagem_dama_verde, pos_imagem)
                        elif self.imagem_peca_verde:
                            # Usar imagem da peça verde normal
                            pos_imagem = (centro[0] - self.tamanho_peca, centro[1] - self.tamanho_peca)
                            self.tela.blit(self.imagem_peca_verde, pos_imagem)
                        else:
                            # Usar círculo se imagem não carregou
                            pygame.draw.circle(self.tela, peca.cor, centro, self.tamanho_peca)
                    else:
                        # Usar círculo se imagem não carregou
                        pygame.draw.circle(self.tela, peca.cor, centro, self.tamanho_peca)
                    
                    # Desenhar coroa se for rei e não tiver imagem específica de dama
                    if peca.rei and not ((peca.cor == AMARELO and self.imagem_dama_amarela) or 
                                        (peca.cor == VERDE and self.imagem_dama_verde)):
                        raio_interno = int(self.tamanho_peca / 1.7)
                        espessura = self.tamanho_peca // 4
                        pygame.draw.circle(self.tela, DOURADO, centro, raio_interno, espessura)
    
    def _coordenadas_pixel(self, coordenadas_tabuleiro):
        """Converte coordenadas do tabuleiro para coordenadas de pixel"""
        x, y = coordenadas_tabuleiro
        return (x * self.tamanho_quadrado + self.tamanho_peca,
                y * self.tamanho_quadrado + self.tamanho_peca)
    
    def coordenadas_tabuleiro(self, pixel):
        """Converte coordenadas de pixel para coordenadas do tabuleiro"""
        return (pixel[0] // self.tamanho_quadrado, pixel[1] // self.tamanho_quadrado)
    
    def _destacar_quadrados(self, quadrados, origem):
        """Destaca os quadrados com movimentos possíveis usando efeitos visuais elegantes"""
        # Destacar movimentos legais com quadrados cinza quase invisíveis
        import time
        
        # Calcular a intensidade da piscada (ciclo lento de 3 segundos)
        tempo_atual = time.time()
        ciclo_piscada = (tempo_atual % 3.0) / 3.0  # Varia de 0 a 1 em 3 segundos
        # Criar efeito suave de vai e vem
        intensidade = abs(ciclo_piscada * 2 - 1)  # Varia de 0 a 1 e volta
        
        # Calcular cor cinza muito sutil (quase invisível)
        cor_base = 200  # Cinza claro como base
        variacao = int(intensidade * 25)  # Variação muito pequena de 0 a 25
        cinza_atual = cor_base + variacao  # Varia entre 200 e 225
        
        for quadrado in quadrados:
            x, y = quadrado
            
            # Calcular posições do quadrado (preenche todo o quadrado)
            left = x * self.tamanho_quadrado
            top = y * self.tamanho_quadrado
            tamanho = self.tamanho_quadrado
            
            # Criar uma superfície com transparência para simular opacidade
            superficie_transparente = pygame.Surface((tamanho, tamanho))
            superficie_transparente.set_alpha(30 + int(intensidade * 20))  # Opacidade muito baixa (30-50)
            
            # Cor cinza muito sutil
            cor_quadrado = (cinza_atual, cinza_atual, cinza_atual)
            superficie_transparente.fill(cor_quadrado)
            
            # Desenhar o quadrado quase invisível que preenche toda a área
            self.tela.blit(superficie_transparente, (left, top))
            
            # Adicionar uma borda muito sutil para definir melhor a área
            borda_cor = (cinza_atual + 15, cinza_atual + 15, cinza_atual + 15)
            pygame.draw.rect(self.tela, borda_cor, (left, top, tamanho, tamanho), 1)
        
        # Destacar peça selecionada com moldura elegante (mantém o mesmo)
        if origem is not None:
            x, y = origem
            
            # Calcular posições da moldura
            left = x * self.tamanho_quadrado
            top = y * self.tamanho_quadrado
            right = left + self.tamanho_quadrado
            bottom = top + self.tamanho_quadrado
            
            # Moldura principal com gradiente simulado
            cores_moldura = [
                (255, 50, 50),    # Vermelho intenso
                (255, 100, 100),  # Vermelho médio
                (255, 150, 150),  # Vermelho claro
                (255, 200, 200)   # Vermelho muito claro
            ]
            
            # Desenhar moldura com múltiplas camadas
            for i, cor in enumerate(cores_moldura):
                espessura = 6 - i
                if espessura > 0:
                    rect = pygame.Rect(left - i, top - i, 
                                     self.tamanho_quadrado + (i * 2), 
                                     self.tamanho_quadrado + (i * 2))
                    pygame.draw.rect(self.tela, cor, rect, espessura)
            
            # Adicionar efeito de brilho nos cantos
            tamanho_canto = 12
            margin = 3
            
            # Cantos superiores
            pygame.draw.circle(self.tela, (255, 255, 100), (left + margin, top + margin), tamanho_canto // 2)
            pygame.draw.circle(self.tela, (255, 255, 100), (right - margin, top + margin), tamanho_canto // 2)
            
            # Cantos inferiores
            pygame.draw.circle(self.tela, (255, 255, 100), (left + margin, bottom - margin), tamanho_canto // 2)
            pygame.draw.circle(self.tela, (255, 255, 100), (right - margin, bottom - margin), tamanho_canto // 2)
            
            # Linhas decorativas nas bordas
            meio_x = left + self.tamanho_quadrado // 2
            meio_y = top + self.tamanho_quadrado // 2
            
            # Linhas horizontais
            pygame.draw.line(self.tela, (255, 255, 200), (left + 10, meio_y), (left + 25, meio_y), 3)
            pygame.draw.line(self.tela, (255, 255, 200), (right - 25, meio_y), (right - 10, meio_y), 3)
            
            # Linhas verticais
            pygame.draw.line(self.tela, (255, 255, 200), (meio_x, top + 10), (meio_x, top + 25), 3)
            pygame.draw.line(self.tela, (255, 255, 200), (meio_x, bottom - 25), (meio_x, bottom - 10), 3)
    
    def desenhar_mensagem(self, mensagem):
        """Desenha uma mensagem na tela"""
        self.mensagem_ativa = True
        
        try:
            fonte = pygame.font.Font('freesansbold.ttf', 44)
        except pygame.error:
            fonte = pygame.font.Font(None, 44)
        
        self.superficie_texto = fonte.render(mensagem, True, DESTAQUE, PRETO)
        self.retangulo_texto = self.superficie_texto.get_rect()
        self.retangulo_texto.center = (self.tamanho_janela // 2, self.tamanho_janela // 2)
    
    def limpar_mensagem(self):
        """Remove a mensagem da tela"""
        self.mensagem_ativa = False
        self.superficie_texto = None
        self.retangulo_texto = None
    
    def tela_fim_jogo(self, vencedor):
        """Exibe tela de fim de jogo e retorna True se o jogador quiser jogar novamente, False para sair."""
        import pygame
        self.tela.fill(PRETO)
        fonte_titulo = pygame.font.Font(None, 72)
        fonte_opcao = pygame.font.Font(None, 48)
        texto_vencedor = fonte_titulo.render(f"{vencedor} VENCEU!", True, DOURADO)
        rect_vencedor = texto_vencedor.get_rect(center=(self.tamanho_janela // 2, self.tamanho_janela // 2 - 60))
        self.tela.blit(texto_vencedor, rect_vencedor)
        # Botão jogar novamente
        botao_largura, botao_altura = 320, 60
        botao_x = (self.tamanho_janela - botao_largura) // 2
        botao_y = self.tamanho_janela // 2 + 20
        botao_rect = pygame.Rect(botao_x, botao_y, botao_largura, botao_altura)
        cor_botao = VERDE
        pygame.draw.rect(self.tela, cor_botao, botao_rect)
        pygame.draw.rect(self.tela, BRANCO, botao_rect, 3)
        texto_botao = fonte_opcao.render("JOGAR NOVAMENTE", True, PRETO)
        rect_botao = texto_botao.get_rect(center=botao_rect.center)
        self.tela.blit(texto_botao, rect_botao)
        # Instrução sair
        fonte_instrucao = pygame.font.Font(None, 32)
        texto_sair = fonte_instrucao.render("Pressione ESC para sair", True, BRANCO)
        rect_sair = texto_sair.get_rect(center=(self.tamanho_janela // 2, self.tamanho_janela // 2 + 110))
        self.tela.blit(texto_sair, rect_sair)
        pygame.display.flip()
        # Loop de escolha
        while True:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return False
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        return False
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    if evento.button == 1 and botao_rect.collidepoint(evento.pos):
                        return True
            self.relogio.tick(FPS)
