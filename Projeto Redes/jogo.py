"""
Classe Jogo - Controla a lógica principal do jogo de damas
"""

import pygame
import sys
from pygame.locals import *

from constantes import *
from graficos import Graficos
from tabuleiro import Tabuleiro


class Jogo:
    """Classe principal que controla o fluxo do jogo de damas"""
    
    def __init__(self):
        """Inicializa componentes e estado inicial do jogo"""
        self.graficos = Graficos()
        self.tabuleiro = Tabuleiro()
        
        # Controle de turnos e seleção
        self.turno = VERDE  # Verde sempre inicia a partida
        self.peca_selecionada = None
        self.em_pulo = False  # Flag para capturas contínuas obrigatórias
        self.movimentos_legais_selecionados = []
        
        # Estado de execução do loop principal
        self.jogo_ativo = True
    
    def configurar(self):
        """Configura o jogo para iniciar"""
        self.graficos.configurar_janela()
    
    def executar(self):
        """Loop principal do jogo. Retorna vencedor ou None se fechado prematuramente"""
        self.configurar()
        
        # Executa até que o jogo seja encerrado (vitória ou saída)
        while self.jogo_ativo:
            self._processar_eventos()
            self._atualizar_tela()
        
        # Retorna o resultado da partida
        if hasattr(self, '_vencedor'):
            return self._vencedor  # Jogo terminou com vitória
        else:
            return None  # Jogo foi fechado antes de terminar
    
    def _processar_eventos(self):
        """Processa entrada do usuário e eventos de sistema"""
        # Calcular movimentos válidos para a peça atualmente selecionada
        if self.peca_selecionada is not None:
            self.movimentos_legais_selecionados = self.tabuleiro.movimentos_legais(
                self.peca_selecionada, self.em_pulo
            )
        
        # Processar fila de eventos do pygame
        for evento in pygame.event.get():
            if evento.type == QUIT:
                self._terminar_jogo()
            elif evento.type == MOUSEBUTTONDOWN:
                self._processar_clique_mouse()
    
    def _processar_clique_mouse(self):
        """Converte clique do mouse em ação do jogo"""
        pos_mouse = self.graficos.coordenadas_tabuleiro(pygame.mouse.get_pos())
        
        # Distinguir entre movimento normal e capturas contínuas
        if not self.em_pulo:
            self._processar_movimento_normal(pos_mouse)
        else:
            self._processar_pulo_continuo(pos_mouse)
    
    def _processar_movimento_normal(self, pos_mouse):
        """Lida com seleção de peças e movimentos regulares"""
        quadrado_clicado = self.tabuleiro.localizacao(pos_mouse)
        
        # Seleção de peça: clique em peça própria
        if (quadrado_clicado.esta_ocupado() and 
            quadrado_clicado.ocupante.cor == self.turno):
            self.peca_selecionada = pos_mouse
            return
        
        # Execução de movimento: clique em destino válido
        if (self.peca_selecionada is not None and 
            pos_mouse in self.tabuleiro.movimentos_legais(self.peca_selecionada)):
            self._executar_movimento(pos_mouse)
    
    def _processar_pulo_continuo(self, pos_mouse):
        """Lida com capturas múltiplas obrigatórias"""
        if (self.peca_selecionada is not None and 
            pos_mouse in self.tabuleiro.movimentos_legais(self.peca_selecionada, apenas_pulos=True)):
            
            # Executar captura atual
            self._executar_pulo(pos_mouse)
            
            # Verificar se existem capturas adicionais obrigatórias
            if not self.tabuleiro.movimentos_legais(pos_mouse, apenas_pulos=True):
                self._finalizar_turno()  # Não há mais capturas - finalizar turno
            else:
                self.peca_selecionada = pos_mouse  # Continuar com a mesma peça
    
    def _executar_movimento(self, destino):
        """Determina tipo de movimento e executa ação apropriada"""
        origem = self.peca_selecionada
        
        # Distinguir entre captura (pulo) e movimento simples
        if destino not in self.tabuleiro.adjacentes(origem):
            # É uma captura - executar pulo
            self._executar_pulo(destino)
            
            # Verificar capturas adicionais obrigatórias
            if self.tabuleiro.pode_capturar_novamente(destino):
                self.em_pulo = True  # Ativar modo de captura contínua
                self.peca_selecionada = destino
            else:
                self._finalizar_turno()
        else:
            # Movimento simples adjacente
            self.tabuleiro.mover_peca(origem, destino)
            self._finalizar_turno()
    
    def _executar_pulo(self, destino):
        """Executa captura removendo peça adversária do tabuleiro"""
        origem = self.peca_selecionada
        
        # Mover peça atacante para posição final
        self.tabuleiro.mover_peca(origem, destino)
        
        # Calcular posição da peça capturada (ponto médio do pulo)
        pos_capturada = (
            (origem[0] + destino[0]) // 2,
            (origem[1] + destino[1]) // 2
        )
        self.tabuleiro.remover_peca(pos_capturada)
    
    def _finalizar_turno(self):
        """Limpa estado atual e transfere controle para próximo jogador"""
        # Alternar entre jogadores
        self.turno = AMARELO if self.turno == VERDE else VERDE
        
        # Limpar estado da jogada anterior
        self.peca_selecionada = None
        self.movimentos_legais_selecionados = []
        self.em_pulo = False  # Sair do modo de captura contínua
        
        # Verificar condições de término da partida
        self._verificar_fim_jogo()
    
    def _verificar_fim_jogo(self):
        """Detecta condições de vitória e encerra partida se necessário"""
        if not self.tabuleiro.tem_movimentos_legais(self.turno):
            # Jogador atual sem movimentos válidos = derrota
            vencedor = "AMARELO" if self.turno == VERDE else "VERDE"
            self._vencedor = vencedor
            self.jogo_ativo = False
    
    def _atualizar_tela(self):
        """Renderiza frame atual do jogo"""
        self.graficos.atualizar_tela(
            self.tabuleiro,
            self.movimentos_legais_selecionados,
            self.peca_selecionada
        )
    
    def _terminar_jogo(self):
        """Encerra execução imediata do jogo (fechamento de janela)"""
        self.jogo_ativo = False
