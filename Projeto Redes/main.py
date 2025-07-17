"""
Arquivo principal para executar o jogo de damas
"""

import pygame
import sys
from jogo import Jogo
from constantes import *


def configurar_icone():
    """Configura o ícone da janela do jogo"""
    try:
        # Carrega e define o ícone personalizado da janela
        icone = pygame.image.load('resources/icon.png')
        pygame.display.set_icon(icone)
        return True
    except pygame.error:
        # Falha silenciosa se o ícone não existir - usa ícone padrão do sistema
        return False
    except Exception:
        # Falha silenciosa para outros erros de carregamento
        return False


class MenuInicial:
    """Menu inicial do jogo"""
    
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((TAMANHO_JANELA, TAMANHO_JANELA))
        pygame.display.set_caption(TITULO_JOGO)
        
        configurar_icone()
        
        self.relogio = pygame.time.Clock()
        self.fonte_titulo = pygame.font.Font(None, 54)
        self.fonte_botao = pygame.font.Font(None, 36)
        
        try:
            # Carrega e redimensiona a imagem de fundo da tela inicial
            self.imagem_fundo = pygame.image.load('resources/title_screen.png')
            self.imagem_fundo = pygame.transform.scale(self.imagem_fundo, (TAMANHO_JANELA, TAMANHO_JANELA))
        except pygame.error:
            # Se não encontrar a imagem, usa fundo preto simples
            self.imagem_fundo = None
        
        self.botao_largura = 200
        self.botao_altura = 60
        self.botao_x = (TAMANHO_JANELA - self.botao_largura) // 2
        self.botao_y = TAMANHO_JANELA // 2 + 50
        self.botao_rect = pygame.Rect(self.botao_x, self.botao_y, self.botao_largura, self.botao_altura)
    
    def desenhar(self):
        """Renderiza menu inicial com botão estilizado e efeitos visuais"""
        # Desenhar fundo (imagem personalizada ou cor sólida)
        if self.imagem_fundo:
            self.tela.blit(self.imagem_fundo, (0, 0))
        else:
            self.tela.fill(PRETO)
        
        # Determinar cor do botão baseada em interação do mouse
        cor_botao = VERDE if self.mouse_sobre_botao() else DOURADO
        mouse_hover = self.mouse_sobre_botao()
        
        # Criar efeito de sombra com múltiplas camadas
        sombra1_rect = pygame.Rect(self.botao_rect.x + 6, self.botao_rect.y + 6, 
                                  self.botao_rect.width, self.botao_rect.height)
        sombra2_rect = pygame.Rect(self.botao_rect.x + 3, self.botao_rect.y + 3, 
                                  self.botao_rect.width, self.botao_rect.height)
        
        pygame.draw.rect(self.tela, (20, 20, 20), sombra1_rect, border_radius=18)
        pygame.draw.rect(self.tela, (40, 40, 40), sombra2_rect, border_radius=16)
        
        # Aplicar efeito de pressionamento quando mouse está sobre botão
        if mouse_hover:
            botao_offset = pygame.Rect(self.botao_rect.x + 2, self.botao_rect.y + 2,
                                     self.botao_rect.width - 2, self.botao_rect.height - 2)
            cor_gradiente = tuple(max(0, c - 30) for c in cor_botao)  # Escurecer cor
        else:
            botao_offset = self.botao_rect
            cor_gradiente = cor_botao
        
        # Desenhar botão com efeito de gradiente em camadas
        for i in range(5):
            alpha = 1.0 - (i * 0.15)  # Transparência decrescente
            cor_camada = tuple(int(c * alpha) for c in cor_gradiente)
            camada_rect = pygame.Rect(botao_offset.x, botao_offset.y + i*2,
                                    botao_offset.width, botao_offset.height - i*4)
            pygame.draw.rect(self.tela, cor_camada, camada_rect, border_radius=15-i)
        
        # Adicionar bordas e efeitos decorativos
        pygame.draw.rect(self.tela, BRANCO, botao_offset, 3, border_radius=15)
        
        borda_interna = pygame.Rect(botao_offset.x + 6, botao_offset.y + 6,
                                  botao_offset.width - 12, botao_offset.height - 12)
        pygame.draw.rect(self.tela, (255, 255, 255, 150), borda_interna, 1, border_radius=10)
        
        highlight_rect = pygame.Rect(botao_offset.x + 8, botao_offset.y + 4,
                                   botao_offset.width - 16, 8)
        pygame.draw.rect(self.tela, (255, 255, 255, 120), highlight_rect, border_radius=6)
        
        # Efeito shimmer animado quando mouse está sobre o botão
        if mouse_hover:
            import time
            shimmer_alpha = int(50 + 30 * abs(pygame.math.Vector2(1, 0).rotate(time.time() * 180).x))
            shimmer_rect = pygame.Rect(botao_offset.x + 4, botao_offset.y + 4,
                                     botao_offset.width - 8, botao_offset.height - 8)
            shimmer_surface = pygame.Surface((shimmer_rect.width, shimmer_rect.height), pygame.SRCALPHA)
            shimmer_surface.fill((255, 255, 255, shimmer_alpha))
            self.tela.blit(shimmer_surface, shimmer_rect.topleft)
        # Renderizar texto do botão com múltiplas camadas de sombra
        fonte_bold = pygame.font.Font(None, 42)
        
        # Sombra mais distante (mais escura)
        texto_sombra3 = fonte_bold.render("START", True, (0, 0, 0))
        sombra3_rect = texto_sombra3.get_rect(center=(botao_offset.centerx + 4, botao_offset.centery + 4))
        self.tela.blit(texto_sombra3, sombra3_rect)
        
        # Sombra intermediária (cinza médio)
        texto_sombra2 = fonte_bold.render("START", True, (50, 50, 50))
        sombra2_rect = texto_sombra2.get_rect(center=(botao_offset.centerx + 2, botao_offset.centery + 2))
        self.tela.blit(texto_sombra2, sombra2_rect)
        
        texto_botao = fonte_bold.render("START", True, BRANCO)
        texto_rect = texto_botao.get_rect(center=botao_offset.center)
        
        # Adicionar contorno ao redor do texto principal
        for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1), (-1,0), (1,0), (0,-1), (0,1)]:
            outline_rect = texto_botao.get_rect(center=(botao_offset.centerx + dx, botao_offset.centery + dy))
            texto_outline = fonte_bold.render("START", True, PRETO)
            self.tela.blit(texto_outline, outline_rect)
        
        # Texto principal por cima de todos os efeitos
        self.tela.blit(texto_botao, texto_rect)
        
        # Instruções na parte inferior da tela
        fonte_instrucoes = pygame.font.Font(None, 18)
        instrucao1 = fonte_instrucoes.render("Clique no botão para começar", True, BRANCO)
        instrucao2 = fonte_instrucoes.render("ESC para sair", True, BRANCO)
        
        self.tela.blit(instrucao1, (TAMANHO_JANELA // 2 - instrucao1.get_width() // 2, TAMANHO_JANELA - 60))
        self.tela.blit(instrucao2, (TAMANHO_JANELA // 2 - instrucao2.get_width() // 2, TAMANHO_JANELA - 35))
        
        pygame.display.flip()
    
    def mouse_sobre_botao(self):
        """Detecta colisão entre cursor e área do botão"""
        pos_mouse = pygame.mouse.get_pos()
        return self.botao_rect.collidepoint(pos_mouse)
    
    def executar(self):
        """Loop principal do menu com tratamento de eventos"""
        executando = True
        
        while executando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return False
                
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        return False
                
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    if evento.button == 1 and self.mouse_sobre_botao():
                        return True
            
            self.desenhar()
            self.relogio.tick(FPS)
        
        return False


class TelaFimJogo:
    """Tela exibida ao final da partida"""
    
    def __init__(self, vencedor):
        pygame.init()
        self.vencedor = vencedor
        self.tela = pygame.display.set_mode((TAMANHO_JANELA, TAMANHO_JANELA))
        pygame.display.set_caption(TITULO_JOGO)
        
        configurar_icone()
        
        self.relogio = pygame.time.Clock()
        
        try:
            # Tenta carregar imagem específica da tela de fim de jogo
            self.imagem_fundo = pygame.image.load('resources/end_screen.png')
            self.imagem_fundo = pygame.transform.scale(self.imagem_fundo, (TAMANHO_JANELA, TAMANHO_JANELA))
        except pygame.error:
            # Sistema de fallback: tenta usar imagem da tela inicial
            try:
                self.imagem_fundo = pygame.image.load('resources/title_screen.png')
                self.imagem_fundo = pygame.transform.scale(self.imagem_fundo, (TAMANHO_JANELA, TAMANHO_JANELA))
            except pygame.error:
                # Se nenhuma imagem estiver disponível, usa fundo azul sólido
                self.imagem_fundo = None
        
        self.fonte_titulo = pygame.font.Font(None, 48)
        self.fonte_vencedor = pygame.font.Font(None, 36)
        self.fonte_botao = pygame.font.Font(None, 32)
        
        self.botao_largura = 250
        self.botao_altura = 60
        self.espaco_entre_botoes = 20
        
        self.botao_jogar_x = (TAMANHO_JANELA - self.botao_largura) // 2
        self.botao_jogar_y = TAMANHO_JANELA // 2 + 40
        self.botao_jogar_rect = pygame.Rect(self.botao_jogar_x, self.botao_jogar_y, 
                                           self.botao_largura, self.botao_altura)
        
        self.botao_sair_x = (TAMANHO_JANELA - self.botao_largura) // 2
        self.botao_sair_y = self.botao_jogar_y + self.botao_altura + self.espaco_entre_botoes
        self.botao_sair_rect = pygame.Rect(self.botao_sair_x, self.botao_sair_y, 
                                          self.botao_largura, self.botao_altura)
    
    def desenhar(self):
        """Desenha a tela de fim de jogo"""
        if self.imagem_fundo:
            self.tela.blit(self.imagem_fundo, (0, 0))
        else:
            fundo_azul = (30, 80, 150)
            self.tela.fill(fundo_azul)
        
        texto_titulo_sombra = self.fonte_titulo.render("FIM DE JOGO", True, PRETO)
        titulo_sombra_rect = texto_titulo_sombra.get_rect(center=(TAMANHO_JANELA // 2 + 2, TAMANHO_JANELA // 2 - 118))
        self.tela.blit(texto_titulo_sombra, titulo_sombra_rect)
        
        texto_titulo = self.fonte_titulo.render("FIM DE JOGO", True, BRANCO)
        titulo_rect = texto_titulo.get_rect(center=(TAMANHO_JANELA // 2, TAMANHO_JANELA // 2 - 120))
        self.tela.blit(texto_titulo, titulo_rect)
        
        cor_vencedor = VERDE if self.vencedor == "VERDE" else AMARELO
        
        texto_vencedor_sombra = self.fonte_vencedor.render(f"{self.vencedor} VENCEU!", True, PRETO)
        vencedor_sombra_rect = texto_vencedor_sombra.get_rect(center=(TAMANHO_JANELA // 2 + 2, TAMANHO_JANELA // 2 - 58))
        self.tela.blit(texto_vencedor_sombra, vencedor_sombra_rect)
        
        texto_vencedor = self.fonte_vencedor.render(f"{self.vencedor} VENCEU!", True, cor_vencedor)
        vencedor_rect = texto_vencedor.get_rect(center=(TAMANHO_JANELA // 2, TAMANHO_JANELA // 2 - 60))
        self.tela.blit(texto_vencedor, vencedor_rect)
        
        cor_botao_jogar = VERDE if self.mouse_sobre_botao_jogar() else DOURADO
        mouse_hover_jogar = self.mouse_sobre_botao_jogar()
        
        sombra_jogar = pygame.Rect(self.botao_jogar_rect.x + 3, self.botao_jogar_rect.y + 3,
                                  self.botao_jogar_rect.width, self.botao_jogar_rect.height)
        pygame.draw.rect(self.tela, (30, 30, 30), sombra_jogar, border_radius=12)
        
        if mouse_hover_jogar:
            botao_jogar_offset = pygame.Rect(self.botao_jogar_rect.x + 1, self.botao_jogar_rect.y + 1,
                                           self.botao_jogar_rect.width - 1, self.botao_jogar_rect.height - 1)
            cor_gradiente_jogar = tuple(max(0, c - 20) for c in cor_botao_jogar)
        else:
            botao_jogar_offset = self.botao_jogar_rect
            cor_gradiente_jogar = cor_botao_jogar
            
        pygame.draw.rect(self.tela, cor_gradiente_jogar, botao_jogar_offset, border_radius=12)
        pygame.draw.rect(self.tela, BRANCO, botao_jogar_offset, 3, border_radius=12)
        
        texto_jogar_sombra = self.fonte_botao.render("JOGAR NOVAMENTE", True, PRETO)
        jogar_sombra_rect = texto_jogar_sombra.get_rect(center=(botao_jogar_offset.centerx + 1, botao_jogar_offset.centery + 1))
        self.tela.blit(texto_jogar_sombra, jogar_sombra_rect)
        
        texto_jogar = self.fonte_botao.render("JOGAR NOVAMENTE", True, BRANCO)
        jogar_rect = texto_jogar.get_rect(center=botao_jogar_offset.center)
        self.tela.blit(texto_jogar, jogar_rect)
        
        cor_botao_sair = AMARELO if self.mouse_sobre_botao_sair() else DOURADO
        mouse_hover_sair = self.mouse_sobre_botao_sair()
        
        sombra_sair = pygame.Rect(self.botao_sair_rect.x + 3, self.botao_sair_rect.y + 3,
                                 self.botao_sair_rect.width, self.botao_sair_rect.height)
        pygame.draw.rect(self.tela, (30, 30, 30), sombra_sair, border_radius=12)
        
        if mouse_hover_sair:
            botao_sair_offset = pygame.Rect(self.botao_sair_rect.x + 1, self.botao_sair_rect.y + 1,
                                          self.botao_sair_rect.width - 1, self.botao_sair_rect.height - 1)
            cor_gradiente_sair = tuple(max(0, c - 20) for c in cor_botao_sair)
        else:
            botao_sair_offset = self.botao_sair_rect
            cor_gradiente_sair = cor_botao_sair
            
        pygame.draw.rect(self.tela, cor_gradiente_sair, botao_sair_offset, border_radius=12)
        pygame.draw.rect(self.tela, BRANCO, botao_sair_offset, 3, border_radius=12)
        
        texto_sair_sombra = self.fonte_botao.render("SAIR", True, PRETO)
        sair_sombra_rect = texto_sair_sombra.get_rect(center=(botao_sair_offset.centerx + 1, botao_sair_offset.centery + 1))
        self.tela.blit(texto_sair_sombra, sair_sombra_rect)
        
        texto_sair = self.fonte_botao.render("SAIR", True, BRANCO)
        sair_rect = texto_sair.get_rect(center=botao_sair_offset.center)
        self.tela.blit(texto_sair, sair_rect)
        
        fonte_instrucoes = pygame.font.Font(None, 20)
        instrucao = fonte_instrucoes.render("Ou pressione ESC para sair", True, BRANCO)
        self.tela.blit(instrucao, (TAMANHO_JANELA // 2 - instrucao.get_width() // 2, TAMANHO_JANELA - 50))
        
        pygame.display.flip()
    
    def mouse_sobre_botao_jogar(self):
        """Verifica se o mouse está sobre o botão jogar novamente"""
        pos_mouse = pygame.mouse.get_pos()
        return self.botao_jogar_rect.collidepoint(pos_mouse)
    
    def mouse_sobre_botao_sair(self):
        """Verifica se o mouse está sobre o botão sair"""
        pos_mouse = pygame.mouse.get_pos()
        return self.botao_sair_rect.collidepoint(pos_mouse)
    
    def executar(self):
        """Executa o loop da tela de fim de jogo. Retorna True para jogar novamente, False para sair."""
        executando = True
        
        while executando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return False
                
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        return False
                
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    if evento.button == 1:
                        if self.mouse_sobre_botao_jogar():
                            return True
                        elif self.mouse_sobre_botao_sair():
                            return False
            
            self.desenhar()
            self.relogio.tick(FPS)
        
        return False


def main():
    """Função principal que inicia o jogo de damas"""
    try:
        while True:
            menu = MenuInicial()
            iniciar_jogo = menu.executar()
            
            if not iniciar_jogo:
                break
            
            jogo = Jogo()
            vencedor = jogo.executar()
            
            if vencedor is None:
                break
            
            tela_fim = TelaFimJogo(vencedor)
            jogar_novamente = tela_fim.executar()
            
            if not jogar_novamente:
                break
        
    except KeyboardInterrupt:
        # Interrupção graceful via Ctrl+C
        pass
    except Exception:
        # Captura qualquer erro não previsto
        pass
    finally:
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()
