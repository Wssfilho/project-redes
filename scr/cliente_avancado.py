"""
Cliente melhorado do jogo de damas com interface avançada
"""

import socket
import threading
import json
import pygame
import sys
import time
from typing import Dict, List, Optional, Tuple

from constantes import *
from protocolo import TipoMensagem, ProtocoloDamas


class ClienteDamasAvancado:
    """Cliente avançado com interface rica"""
    
    def __init__(self, host='localhost', porta=12345):
        """Inicializa o cliente"""
        self.host = host
        self.porta = porta
        self.socket_cliente = None
        
        # Estado de conexão
        self.conectado = False
        self.tentando_conectar = False
        
        # Informações do jogador
        self.jogador_id = None
        self.cor_jogador = None
        self.nome_jogador = None
        
        # Estado do jogo
        self.jogo_iniciado = False
        self.turno_atual = None
        self.meu_turno = False
        self.estado_tabuleiro = None
        self.estatisticas_jogo = {}
        
        # Interface gráfica
        self.tela = None
        self.relogio = None
        self.fonte_titulo = None
        self.fonte_normal = None
        self.fonte_pequena = None
        
        # Controle de interface
        self.quadrado_selecionado = None
        self.movimentos_possiveis = []
        self.ultimo_movimento = None
        self.animacao_movimento = None
        
        # Chat e mensagens
        self.mensagens_chat = []
        self.mensagens_sistema = []
        self.entrada_chat = ""
        self.modo_chat = False
        self.mostrar_chat = True
        
        # Controle
        self.rodando = True
        self.thread_recepcao = None
        
        # Status e notificações
        self.status_conexao = "Desconectado"
        self.mensagem_status = "Pressione C para conectar"
        self.notificacoes = []
        
        # Configurações visuais
        self.mostrar_coordenadas = False
        self.destacar_ultimo_movimento = True
        self.som_habilitado = True
        
        # Histórico
        self.historico_movimentos = []
    
    def conectar_servidor(self) -> bool:
        """Conecta ao servidor"""
        if self.conectado or self.tentando_conectar:
            return False
        
        self.tentando_conectar = True
        self.status_conexao = "Conectando..."
        self.mensagem_status = f"Conectando a {self.host}:{self.porta}..."
        
        try:
            self.socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_cliente.settimeout(10)
            self.socket_cliente.connect((self.host, self.porta))
            
            self.conectado = True
            self.tentando_conectar = False
            self.status_conexao = "Conectado"
            self.mensagem_status = "Conectado! Aguardando outro jogador..."
            
            self.adicionar_mensagem_sistema(f"Conectado ao servidor {self.host}:{self.porta}")
            
            # Inicia thread de recepção
            self.thread_recepcao = threading.Thread(target=self.receber_mensagens)
            self.thread_recepcao.daemon = True
            self.thread_recepcao.start()
            
            return True
            
        except socket.timeout:
            self.mensagem_status = "Timeout na conexão"
            self.adicionar_mensagem_sistema("Erro: Timeout na conexão")
        except ConnectionRefusedError:
            self.mensagem_status = "Servidor indisponível"
            self.adicionar_mensagem_sistema("Erro: Servidor indisponível")
        except Exception as e:
            self.mensagem_status = f"Erro: {e}"
            self.adicionar_mensagem_sistema(f"Erro de conexão: {e}")
        
        self.tentando_conectar = False
        return False
    
    def receber_mensagens(self):
        """Thread para receber mensagens do servidor"""
        buffer = ""
        
        while self.rodando and self.conectado:
            try:
                dados = self.socket_cliente.recv(4096).decode('utf-8')
                if not dados:
                    break
                
                buffer += dados
                
                while '\n' in buffer:
                    linha, buffer = buffer.split('\n', 1)
                    if linha.strip():
                        try:
                            mensagem = json.loads(linha)
                            self.processar_mensagem_servidor(mensagem)
                        except json.JSONDecodeError:
                            self.adicionar_mensagem_sistema("Erro: Mensagem malformada")
                
            except socket.timeout:
                continue
            except socket.error:
                break
            except Exception as e:
                self.adicionar_mensagem_sistema(f"Erro na recepção: {e}")
                break
        
        self.desconectar()
    
    def processar_mensagem_servidor(self, mensagem: Dict):
        """Processa mensagens do servidor"""
        tipo = mensagem.get('tipo')
        print(f"📨 RECEBIDO: {tipo}")
        print(f"   Mensagem completa: {mensagem}")
        
        if tipo == TipoMensagem.CONEXAO_ACEITA.value:
            self.jogador_id = mensagem['jogador_id']
            # Garante que a cor seja tratada como tupla
            if isinstance(mensagem['cor'], (list, tuple)):
                self.cor_jogador = tuple(mensagem['cor'])
            else:
                self.cor_jogador = mensagem['cor']
            self.nome_jogador = mensagem['nome']
            self.status_conexao = f"{self.nome_jogador}"
            self.mensagem_status = mensagem['mensagem']
            self.adicionar_mensagem_sistema(mensagem['mensagem'])
            
            print(f"DEBUG: Cor do jogador recebida: {self.cor_jogador} (tipo: {type(self.cor_jogador)})")
            
        elif tipo == TipoMensagem.CONEXAO_REJEITADA.value:
            self.mensagem_status = mensagem['mensagem']
            self.adicionar_mensagem_sistema(f"Conexão rejeitada: {mensagem['motivo']}")
            
        elif tipo == TipoMensagem.JOGO_INICIADO.value:
            self.jogo_iniciado = True
            # Garante que o turno seja tratado como tupla
            if isinstance(mensagem['turno'], (list, tuple)):
                self.turno_atual = tuple(mensagem['turno'])
            else:
                self.turno_atual = mensagem['turno']
            self.estado_tabuleiro = mensagem['tabuleiro']
            self.estatisticas_jogo = mensagem.get('estatisticas', {})
            
            # Comparação adequada
            if isinstance(self.cor_jogador, (list, tuple)) and isinstance(self.turno_atual, (list, tuple)):
                self.meu_turno = (tuple(self.turno_atual) == tuple(self.cor_jogador))
            else:
                self.meu_turno = (self.turno_atual == self.cor_jogador)
            
            self.mensagem_status = mensagem['mensagem']
            self.adicionar_mensagem_sistema("🎯 Jogo iniciado!")
            self.adicionar_notificacao("Jogo iniciado!", "success")
            
            print(f"DEBUG: Jogo iniciado - Turno: {self.turno_atual}, Meu turno: {self.meu_turno}")
            
        elif tipo == TipoMensagem.MOVIMENTO_EXECUTADO.value:
            self.processar_movimento_executado(mensagem)
            
        elif tipo == TipoMensagem.MOVIMENTO_INVALIDO.value:
            self.mensagem_status = mensagem['mensagem']
            self.quadrado_selecionado = None
            self.movimentos_possiveis = []
            self.adicionar_notificacao(mensagem['mensagem'], "error")
            
        elif tipo == TipoMensagem.JOGO_FINALIZADO.value:
            self.processar_fim_jogo(mensagem)
            
        elif tipo == TipoMensagem.CHAT.value:
            remetente = mensagem['remetente']
            texto = mensagem['texto']
            self.adicionar_mensagem_chat(f"{remetente['nome']}", texto)
            
        elif tipo == TipoMensagem.NOTIFICACAO.value:
            self.adicionar_mensagem_sistema(mensagem['texto'])
            self.adicionar_notificacao(mensagem['texto'], mensagem.get('nivel', 'info'))
            
        elif tipo == TipoMensagem.JOGO_INTERROMPIDO.value:
            self.jogo_iniciado = False
            self.meu_turno = False
            self.mensagem_status = mensagem['mensagem']
            self.adicionar_mensagem_sistema(mensagem['mensagem'])
            self.adicionar_notificacao("Jogo interrompido", "warning")
            
        elif tipo == TipoMensagem.ERRO.value:
            self.adicionar_mensagem_sistema(f"Erro: {mensagem['descricao']}")
            self.adicionar_notificacao(mensagem['descricao'], "error")
            
        elif tipo == TipoMensagem.ESTADO_JOGO.value:
            self.turno_atual = tuple(mensagem['turno']) if isinstance(mensagem['turno'], (list, tuple)) else mensagem['turno']
            self.estado_tabuleiro = mensagem['tabuleiro']
            self.estatisticas_jogo = mensagem.get('estatisticas', {})
            self.meu_turno = (self.turno_atual == self.cor_jogador)
    
    def processar_movimento_executado(self, mensagem: Dict):
        """Processa movimento executado"""
        movimento = mensagem['movimento']
        self.estado_tabuleiro = mensagem['tabuleiro']
        self.turno_atual = tuple(mensagem['turno']) if isinstance(mensagem['turno'], (list, tuple)) else mensagem['turno']
        self.estatisticas_jogo = mensagem.get('estatisticas', {})
        
        # Debug: imprimir informações do turno
        print(f"DEBUG: Turno atual recebido: {self.turno_atual} (tipo: {type(self.turno_atual)})")
        print(f"DEBUG: Cor do jogador: {self.cor_jogador} (tipo: {type(self.cor_jogador)})")
        
        # Comparação correta das cores
        if isinstance(self.turno_atual, (list, tuple)):
            self.meu_turno = (tuple(self.turno_atual) == tuple(self.cor_jogador))
        else:
            self.meu_turno = (self.turno_atual == self.cor_jogador)
        
        print(f"DEBUG: Meu turno: {self.meu_turno}")
        
        # Salva último movimento para destacar
        self.ultimo_movimento = {
            'origem': tuple(movimento['origem']),
            'destino': tuple(movimento['destino']),
            'cor': movimento['cor_jogador']
        }
        
        # Adiciona ao histórico
        self.historico_movimentos.append({
            'movimento': movimento,
            'timestamp': time.time()
        })
        
        # Limita histórico
        if len(self.historico_movimentos) > 50:
            self.historico_movimentos.pop(0)
        
        # Mensagem de status
        if self.meu_turno:
            self.mensagem_status = "🎯 Seu turno!"
        else:
            self.mensagem_status = "⏳ Turno do adversário"
        
        # Adiciona ao chat
        self.adicionar_mensagem_sistema(mensagem['mensagem'])
        
        # Reset seleção
        self.quadrado_selecionado = None
        self.movimentos_possiveis = []
    
    def processar_fim_jogo(self, mensagem: Dict):
        """Processa fim do jogo"""
        vencedor = mensagem['vencedor']
        motivo = mensagem['motivo']
        self.estado_tabuleiro = mensagem['tabuleiro_final']
        self.jogo_iniciado = False
        self.meu_turno = False
        
        # Converte cores para comparação correta
        if tuple(vencedor) == tuple(self.cor_jogador):
            self.mensagem_status = "🎉 Você venceu!"
            self.adicionar_notificacao("Vitória!", "success")
        else:
            self.mensagem_status = "😞 Você perdeu!"
            self.adicionar_notificacao("Derrota!", "error")
        
        self.adicionar_mensagem_sistema(f"Jogo finalizado! {vencedor} venceu ({motivo})")
    
    def inicializar_interface(self):
        """Inicializa interface gráfica"""
        pygame.init()
        
        # Dimensões da janela
        largura_janela = TAMANHO_JANELA + 350  # Espaço para painel lateral
        altura_janela = TAMANHO_JANELA
        
        self.tela = pygame.display.set_mode((largura_janela, altura_janela))
        pygame.display.set_caption("Damas Online - Cliente")
        
        self.relogio = pygame.time.Clock()
        
        # Configurar fontes
        self.fonte_titulo = pygame.font.Font(None, 28)
        self.fonte_normal = pygame.font.Font(None, 20)
        self.fonte_pequena = pygame.font.Font(None, 16)
        
        # Carregar imagens de recursos
        try:
            self.imagem_tabuleiro = pygame.image.load('resources/tabuleiro.png')
            self.imagem_tabuleiro = pygame.transform.scale(self.imagem_tabuleiro, (TAMANHO_JANELA, TAMANHO_JANELA))
            print("✅ Tabuleiro carregado com sucesso")
        except Exception as e:
            self.imagem_tabuleiro = None
            print(f"❌ Erro ao carregar tabuleiro: {e}")
            
        try:
            self.imagem_peca_verde = pygame.image.load('resources/peca_verde.png')
            self.imagem_peca_amarela = pygame.image.load('resources/peca_amarela.png')
            self.imagem_dama_verde = pygame.image.load('resources/peca_verde_dama.png')
            self.imagem_dama_amarela = pygame.image.load('resources/peca_amarela_dama.png')
            
            print("✅ Imagens das peças carregadas:")
            print(f"   - Peça verde: {self.imagem_peca_verde.get_size()}")
            print(f"   - Peça amarela: {self.imagem_peca_amarela.get_size()}")
            print(f"   - Dama verde: {self.imagem_dama_verde.get_size()}")
            print(f"   - Dama amarela: {self.imagem_dama_amarela.get_size()}")
            
            # Redimensionar peças
            tamanho_peca = (TAMANHO_JANELA // TAMANHO_TABULEIRO) - 10
            print(f"   - Redimensionando para: {tamanho_peca}x{tamanho_peca}")
            
            self.imagem_peca_verde = pygame.transform.scale(self.imagem_peca_verde, (tamanho_peca, tamanho_peca))
            self.imagem_peca_amarela = pygame.transform.scale(self.imagem_peca_amarela, (tamanho_peca, tamanho_peca))
            self.imagem_dama_verde = pygame.transform.scale(self.imagem_dama_verde, (tamanho_peca, tamanho_peca))
            self.imagem_dama_amarela = pygame.transform.scale(self.imagem_dama_amarela, (tamanho_peca, tamanho_peca))
            
            print("✅ Redimensionamento concluído")
        except Exception as e:
            self.imagem_peca_verde = None
            self.imagem_peca_amarela = None
            self.imagem_dama_verde = None
            self.imagem_dama_amarela = None
            print(f"❌ Erro ao carregar peças: {e}")
        
        # Carregar ícone se disponível
        try:
            icone = pygame.image.load('resources/icon.png')
            pygame.display.set_icon(icone)
        except:
            pass
    
    def desenhar_interface(self):
        """Desenha interface completa"""
        self.tela.fill(PRETO)
        
        # Desenha tabuleiro
        self.desenhar_tabuleiro()
        
        # Desenha painel lateral
        self.desenhar_painel_lateral()
        
        # Desenha notificações
        self.desenhar_notificacoes()
        
        pygame.display.flip()
    
    def desenhar_tabuleiro(self):
        """Desenha o tabuleiro de jogo"""
        # Se temos a imagem do tabuleiro, usa ela como fundo
        if self.imagem_tabuleiro:
            self.tela.blit(self.imagem_tabuleiro, (0, 0))
        
        tamanho_quadrado = TAMANHO_JANELA // TAMANHO_TABULEIRO
        
        for x in range(TAMANHO_TABULEIRO):
            for y in range(TAMANHO_TABULEIRO):
                pos_x = x * tamanho_quadrado
                pos_y = y * tamanho_quadrado
                rect = pygame.Rect(pos_x, pos_y, tamanho_quadrado, tamanho_quadrado)
                
                # Se não temos imagem de fundo, desenha quadrados coloridos
                if not self.imagem_tabuleiro:
                    # Cor base do quadrado
                    if self.estado_tabuleiro:
                        cor_quadrado = self.estado_tabuleiro[x][y]['cor_quadrado']
                    else:
                        cor_quadrado = BRANCO if (x + y) % 2 == 0 else PRETO
                    
                    pygame.draw.rect(self.tela, cor_quadrado, rect)
                
                # Destaques especiais (mesmo com imagem de fundo)
                cor_destaque = None
                
                if self.quadrado_selecionado == (x, y):
                    cor_destaque = DESTAQUE
                elif (x, y) in self.movimentos_possiveis:
                    cor_destaque = (100, 255, 100)  # Verde claro para movimentos possíveis
                elif (self.ultimo_movimento and self.destacar_ultimo_movimento and
                      ((x, y) == self.ultimo_movimento['origem'] or 
                       (x, y) == self.ultimo_movimento['destino'])):
                    cor_destaque = (255, 200, 100)  # Laranja para último movimento
                
                # Aplica destaque se necessário
                if cor_destaque:
                    # Desenha uma sobreposição semi-transparente para destaque
                    overlay = pygame.Surface((tamanho_quadrado, tamanho_quadrado))
                    overlay.set_alpha(128)  # Semi-transparente
                    overlay.fill(cor_destaque)
                    self.tela.blit(overlay, (pos_x, pos_y))
                
                # Desenha bordas apenas se não temos imagem de fundo
                if not self.imagem_tabuleiro:
                    pygame.draw.rect(self.tela, (50, 50, 50), rect, 1)
                
                # Desenha coordenadas se habilitado
                if self.mostrar_coordenadas:
                    coord_texto = self.fonte_pequena.render(f"{x},{y}", True, (128, 128, 128))
                    self.tela.blit(coord_texto, (pos_x + 2, pos_y + 2))
                
                # Desenha peça
                if self.estado_tabuleiro and self.estado_tabuleiro[x][y]['peca']:
                    self.desenhar_peca(pos_x, pos_y, tamanho_quadrado, 
                                     self.estado_tabuleiro[x][y]['peca'])
    
    def desenhar_peca(self, pos_x: int, pos_y: int, tamanho: int, peca_dados: Dict):
        """Desenha uma peça"""
        cor_peca = peca_dados['cor']
        e_dama = peca_dados['e_dama']
        
        # Tenta usar imagens das peças primeiro
        imagem_peca = None
        
        # Converte cor da lista JSON para tupla para comparação
        cor_tupla = tuple(cor_peca) if isinstance(cor_peca, list) else cor_peca
        
        if cor_tupla == VERDE:
            if e_dama and self.imagem_dama_verde:
                imagem_peca = self.imagem_dama_verde
            elif not e_dama and self.imagem_peca_verde:
                imagem_peca = self.imagem_peca_verde
        elif cor_tupla == AMARELO:
            if e_dama and self.imagem_dama_amarela:
                imagem_peca = self.imagem_dama_amarela
            elif not e_dama and self.imagem_peca_amarela:
                imagem_peca = self.imagem_peca_amarela
        
        if imagem_peca:
            # Centraliza a imagem no quadrado
            img_rect = imagem_peca.get_rect()
            img_rect.center = (pos_x + tamanho // 2, pos_y + tamanho // 2)
            self.tela.blit(imagem_peca, img_rect)
        else:
            # Fallback para desenho procedural
            centro = (pos_x + tamanho // 2, pos_y + tamanho // 2)
            raio = tamanho // 3
            
            # Sombra
            pygame.draw.circle(self.tela, (50, 50, 50), 
                              (centro[0] + 2, centro[1] + 2), raio)
            
            # Peça principal
            pygame.draw.circle(self.tela, cor_peca, centro, raio)
            pygame.draw.circle(self.tela, PRETO, centro, raio, 3)
            
            # Brilho
            pygame.draw.circle(self.tela, (255, 255, 255, 100), 
                              (centro[0] - raio//3, centro[1] - raio//3), raio//4)
            
            # Marca de dama
            if e_dama:
                pygame.draw.circle(self.tela, BRANCO, centro, raio // 2)
                pygame.draw.circle(self.tela, PRETO, centro, raio // 2, 2)
                
                # Coroa simples
                for i in range(5):
                    angle = i * 72
                    crown_x = centro[0] + int((raio // 3) * pygame.math.Vector2(1, 0).rotate(angle).x)
                    crown_y = centro[1] + int((raio // 3) * pygame.math.Vector2(1, 0).rotate(angle).y)
                    pygame.draw.circle(self.tela, DOURADO, (crown_x, crown_y), 3)
    
    def desenhar_painel_lateral(self):
        """Desenha painel lateral com informações"""
        painel_x = TAMANHO_JANELA + 10
        y = 10
        largura_painel = 330
        
        # Título
        titulo = self.fonte_titulo.render("🎮 DAMAS ONLINE", True, BRANCO)
        self.tela.blit(titulo, (painel_x, y))
        y += 35
        
        # Linha separadora
        pygame.draw.line(self.tela, BRANCO, (painel_x, y), (painel_x + largura_painel, y), 2)
        y += 15
        
        # Status da conexão
        cor_status = VERDE if self.conectado else AMARELO if self.tentando_conectar else (255, 100, 100)
        status = self.fonte_normal.render(f"Status: {self.status_conexao}", True, cor_status)
        self.tela.blit(status, (painel_x, y))
        y += 25
        
        # Informações do jogador
        if self.nome_jogador and self.cor_jogador:
            jogador_info = self.fonte_normal.render(f"Você: {self.nome_jogador}", True, self.cor_jogador)
            self.tela.blit(jogador_info, (painel_x, y))
            y += 20
            
            # Indicador de turno
            if self.jogo_iniciado:
                turno_texto = "🎯 SEU TURNO" if self.meu_turno else "⏳ AGUARDE"
                cor_turno = VERDE if self.meu_turno else (150, 150, 150)
                turno = self.fonte_normal.render(turno_texto, True, cor_turno)
                self.tela.blit(turno, (painel_x, y))
                y += 25
        
        # Estatísticas do jogo
        if self.estatisticas_jogo:
            stats_titulo = self.fonte_normal.render("📊 Estatísticas:", True, BRANCO)
            self.tela.blit(stats_titulo, (painel_x, y))
            y += 20
            
            # Mapear cores para nomes de estatísticas
            stats_info = [
                (VERDE, "Verdes", "verdes"),
                (AMARELO, "Amarelas", "amarelas")
            ]
            
            for cor, label, nome_stat in stats_info:
                pecas = self.estatisticas_jogo.get(f'pecas_{nome_stat}', 0)
                damas = self.estatisticas_jogo.get(f'damas_{nome_stat}', 0)
                
                stat_texto = f"{label}: {pecas} ({damas} damas)"
                stat = self.fonte_pequena.render(stat_texto, True, cor)
                self.tela.blit(stat, (painel_x + 10, y))
                y += 18
            y += 10
        
        # Mensagem de status
        if self.mensagem_status:
            linhas = self.quebrar_texto(self.mensagem_status, largura_painel)
            for linha in linhas:
                status_msg = self.fonte_pequena.render(linha, True, BRANCO)
                self.tela.blit(status_msg, (painel_x, y))
                y += 18
        y += 15
        
        # Chat
        if self.mostrar_chat:
            self.desenhar_secao_chat(painel_x, y, largura_painel)
        
        # Controles na parte inferior
        self.desenhar_controles(painel_x, largura_painel)
    
    def desenhar_secao_chat(self, x: int, y: int, largura: int):
        """Desenha seção de chat"""
        chat_titulo = self.fonte_normal.render("💬 Chat:", True, BRANCO)
        self.tela.blit(chat_titulo, (x, y))
        y += 25
        
        # Área do chat
        altura_chat = 150
        chat_rect = pygame.Rect(x, y, largura, altura_chat)
        pygame.draw.rect(self.tela, (20, 20, 20), chat_rect)
        pygame.draw.rect(self.tela, BRANCO, chat_rect, 1)
        
        # Mensagens
        mensagens_visiveis = (self.mensagens_chat + self.mensagens_sistema)[-8:]
        for i, mensagem in enumerate(mensagens_visiveis):
            linhas = self.quebrar_texto(mensagem, largura - 10)
            for linha in linhas:
                if y + 5 + i * 18 < chat_rect.bottom - 5:
                    cor_texto = (200, 200, 200) if mensagem.startswith("Sistema:") else BRANCO
                    chat_msg = self.fonte_pequena.render(linha, True, cor_texto)
                    self.tela.blit(chat_msg, (x + 5, y + 5 + i * 18))
        
        # Campo de entrada
        y = chat_rect.bottom + 10
        entrada_titulo = self.fonte_pequena.render("Digite T para abrir chat:", True, BRANCO)
        self.tela.blit(entrada_titulo, (x, y))
        y += 18
        
        cor_entrada = DESTAQUE if self.modo_chat else (60, 60, 60)
        entrada_rect = pygame.Rect(x, y, largura, 22)
        pygame.draw.rect(self.tela, cor_entrada, entrada_rect)
        pygame.draw.rect(self.tela, BRANCO, entrada_rect, 1)
        
        if self.entrada_chat or self.modo_chat:
            texto_entrada = self.fonte_pequena.render(self.entrada_chat, True, PRETO)
            self.tela.blit(texto_entrada, (x + 5, y + 3))
    
    def desenhar_controles(self, x: int, largura: int):
        """Desenha controles na parte inferior"""
        y = TAMANHO_JANELA - 80
        
        controles = [
            "C - Conectar/Reconectar",
            "T - Chat",
            "H - Mostrar/Ocultar coordenadas",
            "ESC - Sair"
        ]
        
        for i, controle in enumerate(controles):
            ctrl_texto = self.fonte_pequena.render(controle, True, (150, 150, 150))
            self.tela.blit(ctrl_texto, (x, y + i * 15))
    
    def desenhar_notificacoes(self):
        """Desenha notificações temporárias"""
        agora = time.time()
        notificacoes_ativas = []
        
        for notif in self.notificacoes:
            if agora - notif['timestamp'] < 3:  # 3 segundos
                notificacoes_ativas.append(notif)
        
        self.notificacoes = notificacoes_ativas
        
        for i, notif in enumerate(notificacoes_ativas):
            y = 10 + i * 40
            
            # Cor da notificação
            if notif['tipo'] == 'success':
                cor_fundo = (0, 150, 0, 200)
            elif notif['tipo'] == 'error':
                cor_fundo = (150, 0, 0, 200)
            elif notif['tipo'] == 'warning':
                cor_fundo = (150, 150, 0, 200)
            else:
                cor_fundo = (0, 0, 150, 200)
            
            # Desenha notificação
            texto = self.fonte_normal.render(notif['texto'], True, BRANCO)
            rect = pygame.Rect(10, y, texto.get_width() + 20, 30)
            
            superficie_notif = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            superficie_notif.fill(cor_fundo)
            self.tela.blit(superficie_notif, rect)
            
            self.tela.blit(texto, (rect.x + 10, rect.y + 5))
    
    def quebrar_texto(self, texto: str, largura_max: int) -> List[str]:
        """Quebra texto em múltiplas linhas"""
        palavras = texto.split(' ')
        linhas = []
        linha_atual = ""
        
        for palavra in palavras:
            teste_linha = linha_atual + (" " if linha_atual else "") + palavra
            largura_teste = self.fonte_pequena.size(teste_linha)[0]
            
            if largura_teste <= largura_max:
                linha_atual = teste_linha
            else:
                if linha_atual:
                    linhas.append(linha_atual)
                linha_atual = palavra
        
        if linha_atual:
            linhas.append(linha_atual)
        
        return linhas
    
    def processar_clique(self, pos: Tuple[int, int]):
        """Processa clique do mouse"""
        if not self.jogo_iniciado or not self.meu_turno:
            return
        
        x, y = pos
        if x >= TAMANHO_JANELA:  # Clique no painel
            return
        
        # Converte para coordenadas do tabuleiro
        tamanho_quadrado = TAMANHO_JANELA // TAMANHO_TABULEIRO
        tab_x = x // tamanho_quadrado
        tab_y = y // tamanho_quadrado
        
        if not (0 <= tab_x < TAMANHO_TABULEIRO and 0 <= tab_y < TAMANHO_TABULEIRO):
            return
        
        coord = (tab_x, tab_y)
        
        if self.quadrado_selecionado is None:
            # Seleciona peça
            if (self.estado_tabuleiro and 
                self.estado_tabuleiro[tab_x][tab_y]['peca'] and
                tuple(self.estado_tabuleiro[tab_x][tab_y]['peca']['cor']) == tuple(self.cor_jogador)):
                
                self.quadrado_selecionado = coord
                self.movimentos_possiveis = self.calcular_movimentos_possiveis(coord)
                self.mensagem_status = "Peça selecionada. Clique no destino."
        else:
            if coord == self.quadrado_selecionado:
                # Deseleciona
                self.quadrado_selecionado = None
                self.movimentos_possiveis = []
                self.mensagem_status = "Peça desselecionada."
            elif coord in self.movimentos_possiveis:
                # Move peça
                self.enviar_movimento(self.quadrado_selecionado, coord)
                self.quadrado_selecionado = None
                self.movimentos_possiveis = []
                self.mensagem_status = "Movimento enviado..."
            else:
                # Seleciona nova peça se for nossa
                if (self.estado_tabuleiro and 
                    self.estado_tabuleiro[tab_x][tab_y]['peca'] and
                    tuple(self.estado_tabuleiro[tab_x][tab_y]['peca']['cor']) == tuple(self.cor_jogador)):
                    
                    self.quadrado_selecionado = coord
                    self.movimentos_possiveis = self.calcular_movimentos_possiveis(coord)
                    self.mensagem_status = "Nova peça selecionada."
                else:
                    self.mensagem_status = "Movimento inválido."
    
    def calcular_movimentos_possiveis(self, origem: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Calcula movimentos possíveis para uma peça (simplificado)"""
        if not self.estado_tabuleiro:
            return []
        
        x, y = origem
        peca = self.estado_tabuleiro[x][y]['peca']
        if not peca:
            return []
        
        movimentos = []
        
        # Direções baseadas no tipo de peça
        if peca['e_dama']:
            direcoes = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        else:
            # VERDE começa na parte inferior e move para cima (y diminui)
            # AMARELO começa na parte superior e move para baixo (y aumenta)
            if tuple(peca['cor']) == VERDE:  # Converte lista para tupla
                direcoes = [(-1, -1), (1, -1)]  # Move para cima (diagonal superior esquerda e direita)
            else:
                direcoes = [(-1, 1), (1, 1)]   # Move para baixo (diagonal inferior esquerda e direita)
        
        for dx, dy in direcoes:
            # Movimento simples
            novo_x, novo_y = x + dx, y + dy
            if (0 <= novo_x < TAMANHO_TABULEIRO and 0 <= novo_y < TAMANHO_TABULEIRO and
                not self.estado_tabuleiro[novo_x][novo_y]['peca']):
                movimentos.append((novo_x, novo_y))
            
            # Captura
            captura_x, captura_y = x + 2*dx, y + 2*dy
            if (0 <= captura_x < TAMANHO_TABULEIRO and 0 <= captura_y < TAMANHO_TABULEIRO and
                self.estado_tabuleiro[novo_x][novo_y]['peca'] and
                tuple(self.estado_tabuleiro[novo_x][novo_y]['peca']['cor']) != tuple(peca['cor']) and
                not self.estado_tabuleiro[captura_x][captura_y]['peca']):
                movimentos.append((captura_x, captura_y))
        
        return movimentos
    
    def enviar_movimento(self, origem: Tuple[int, int], destino: Tuple[int, int]):
        """Envia movimento para o servidor"""
        if self.conectado:
            mensagem = {
                'tipo': TipoMensagem.MOVIMENTO_SOLICITADO.value,
                'origem': origem,
                'destino': destino
            }
            self.enviar_mensagem(mensagem)
    
    def enviar_mensagem(self, mensagem: Dict):
        """Envia mensagem para o servidor"""
        if not self.conectado:
            return False
        
        try:
            dados = json.dumps(mensagem, ensure_ascii=False) + '\n'
            self.socket_cliente.send(dados.encode('utf-8'))
            return True
        except Exception as e:
            self.adicionar_mensagem_sistema(f"Erro ao enviar: {e}")
            return False
    
    def adicionar_mensagem_chat(self, remetente: str, texto: str):
        """Adiciona mensagem ao chat (limpa mensagens anteriores automaticamente)"""
        # Limpa todas as mensagens anteriores e mantém apenas a nova
        self.mensagens_chat.clear()
        self.mensagens_chat.append(f"{remetente}: {texto}")
    
    def adicionar_mensagem_sistema(self, texto: str):
        """Adiciona mensagem do sistema"""
        self.mensagens_sistema.append(f"Sistema: {texto}")
        if len(self.mensagens_sistema) > 50:
            self.mensagens_sistema.pop(0)
    
    def adicionar_notificacao(self, texto: str, tipo: str = "info"):
        """Adiciona notificação temporária"""
        self.notificacoes.append({
            'texto': texto,
            'tipo': tipo,
            'timestamp': time.time()
        })
    
    def processar_entrada_chat(self, tecla: int, texto: str):
        """Processa entrada de chat"""
        if tecla == pygame.K_RETURN:
            if self.entrada_chat.strip():
                # Adiciona a mensagem localmente (limpa chat anterior)
                self.adicionar_mensagem_chat("Você", self.entrada_chat.strip())
                
                # Envia para o servidor
                mensagem = {
                    'tipo': TipoMensagem.CHAT.value,
                    'texto': self.entrada_chat.strip()
                }
                self.enviar_mensagem(mensagem)
                self.entrada_chat = ""
            self.modo_chat = False
        elif tecla == pygame.K_BACKSPACE:
            self.entrada_chat = self.entrada_chat[:-1]
        elif tecla == pygame.K_ESCAPE:
            self.entrada_chat = ""
            self.modo_chat = False
        else:
            if len(self.entrada_chat) < 100:
                self.entrada_chat += texto
    
    def executar(self):
        """Loop principal do cliente"""
        self.inicializar_interface()
        
        while self.rodando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.rodando = False
                
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        if self.modo_chat:
                            self.modo_chat = False
                            self.entrada_chat = ""
                        else:
                            self.rodando = False
                    
                    elif evento.key == pygame.K_c and not self.modo_chat:
                        if not self.conectado and not self.tentando_conectar:
                            threading.Thread(target=self.conectar_servidor, daemon=True).start()
                    
                    elif evento.key == pygame.K_t and not self.modo_chat and self.conectado:
                        self.modo_chat = True
                    
                    elif evento.key == pygame.K_h and not self.modo_chat:
                        self.mostrar_coordenadas = not self.mostrar_coordenadas
                    
                    elif self.modo_chat:
                        if evento.unicode.isprintable():
                            self.processar_entrada_chat(evento.key, evento.unicode)
                        else:
                            self.processar_entrada_chat(evento.key, "")
                
                elif evento.type == pygame.MOUSEBUTTONDOWN:
                    if evento.button == 1:  # Botão esquerdo
                        self.processar_clique(evento.pos)
            
            self.desenhar_interface()
            self.relogio.tick(FPS)
        
        self.desconectar()
        pygame.quit()
    
    def desconectar(self):
        """Desconecta do servidor"""
        if self.conectado:
            self.conectado = False
            self.status_conexao = "Desconectado"
            
            try:
                if self.socket_cliente:
                    self.socket_cliente.close()
            except:
                pass


def obter_configuracoes():
    """Obtém configurações do usuário"""
    print("🎮 Cliente Damas Online")
    print("=" * 30)
    
    host = input("Host do servidor (Enter = localhost): ").strip() or 'localhost'
    porta_input = input("Porta (Enter = 12345): ").strip()
    porta = int(porta_input) if porta_input else 12345
    
    return host, porta


def main():
    """Função principal do cliente"""
    try:
        host, porta = obter_configuracoes()
        
        cliente = ClienteDamasAvancado(host, porta)
        print(f"\n🔌 Configurado para {host}:{porta}")
        print("💡 Pressione C na interface para conectar")
        print("🎮 Iniciando interface...")
        
        cliente.executar()
        
    except KeyboardInterrupt:
        print("\n🛑 Interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")
        input("Pressione Enter para sair...")


if __name__ == "__main__":
    main()
