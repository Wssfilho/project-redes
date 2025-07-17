"""
Servidor melhorado do jogo de damas com integração completa
"""

import socket
import threading
import json
import time
import logging
from typing import Dict, List, Optional, Tuple

from jogo import Jogo
from constantes import *
from protocolo import (
    ProtocoloDamas, TipoMensagem, EstadoJogo, EstadoJogador, 
    Jogador, Movimento, EstadoTabuleiro, CodigosErro
)


class ServidorDamasAvancado:
    """Servidor avançado para jogo de damas online"""
    
    def __init__(self, host='0.0.0.0', porta=12345):
        """Inicializa o servidor"""
        self.host = host
        self.porta = porta
        self.socket_servidor = None
        
        # Configuração de logging
        self.configurar_logging()
        
        # Controle de jogadores
        self.jogadores: Dict[socket.socket, Jogador] = {}
        self.max_jogadores = 2
        self.proximo_id = 1
        
        # Estado do jogo
        self.estado_jogo = EstadoJogo.AGUARDANDO_JOGADORES
        self.jogo = None
        self.turno_atual = VERDE
        self.movimentos_obrigatorios = []
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Controle do servidor
        self.rodando = True
        self.estatisticas = {
            'jogos_concluidos': 0,
            'conexoes_totais': 0,
            'tempo_inicio': time.time()
        }
    
    def configurar_logging(self):
        """Configura sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('servidor_damas.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def obter_ip_local(self):
        """Obtém o IP local da máquina"""
        try:
            # Conecta a um endereço externo para descobrir IP local
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_local = s.getsockname()[0]
            s.close()
            return ip_local
        except:
            return "127.0.0.1"
    
    def obter_todos_ips(self):
        """Obtém todos os IPs disponíveis da máquina"""
        ips = []
        try:
            hostname = socket.gethostname()
            ip_list = socket.gethostbyname_ex(hostname)[2]
            ips.extend([ip for ip in ip_list if not ip.startswith("127.")])
        except:
            pass
        
        ip_principal = self.obter_ip_local()
        if ip_principal not in ips:
            ips.insert(0, ip_principal)
        
        return ips
    
    def iniciar_servidor(self):
        """Inicia o servidor"""
        try:
            self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket_servidor.bind((self.host, self.porta))
            self.socket_servidor.listen(5)
            
            self.logger.info(f"🎮 Servidor Damas Online iniciado em {self.host}:{self.porta}")
            
            # Mostra informações de rede completas
            if self.host == '0.0.0.0':
                ips_disponiveis = self.obter_todos_ips()
                self.logger.info(f"📍 IPs disponíveis para conexão:")
                for i, ip in enumerate(ips_disponiveis, 1):
                    self.logger.info(f"   {i}. {ip}:{self.porta}")
                
                if ips_disponiveis:
                    ip_recomendado = ips_disponiveis[0]
                    self.logger.info(f"✅ IP recomendado: {ip_recomendado}:{self.porta}")
                
                self.logger.info(f"💡 Configure firewall para permitir porta {self.porta}")
                self.logger.info(f"🔧 Use config_rede.py para diagnósticos de rede")
            
            self.logger.info("⏳ Aguardando conexões...")
            
            while self.rodando:
                try:
                    cliente_socket, endereco = self.socket_servidor.accept()
                    self.logger.info(f"🔗 Nova conexão de {endereco}")
                    
                    # Inicia thread para cliente
                    thread_cliente = threading.Thread(
                        target=self.gerenciar_cliente,
                        args=(cliente_socket, endereco),
                        daemon=True
                    )
                    thread_cliente.start()
                    
                except socket.error as e:
                    if self.rodando:
                        self.logger.error(f"Erro ao aceitar conexão: {e}")
                        
        except Exception as e:
            self.logger.error(f"Erro fatal do servidor: {e}")
        finally:
            self.parar_servidor()
    
    def gerenciar_cliente(self, cliente_socket: socket.socket, endereco: Tuple[str, int]):
        """Gerencia comunicação com cliente"""
        jogador = None
        
        try:
            with self.lock:
                # Verifica se servidor está lotado
                if len(self.jogadores) >= self.max_jogadores:
                    mensagem = ProtocoloDamas.criar_mensagem_conexao_rejeitada(
                        "Servidor lotado. Máximo 2 jogadores."
                    )
                    self.enviar_mensagem(cliente_socket, mensagem)
                    cliente_socket.close()
                    return
                
                # Cria novo jogador
                jogador = Jogador(
                    id=self.proximo_id,
                    nome=f"Jogador {self.proximo_id}",
                    cor=VERDE if self.proximo_id == 1 else AMARELO,
                    socket=cliente_socket,
                    endereco=endereco,
                    estado=EstadoJogador.CONECTADO,
                    conectado_em=time.time()
                )
                
                self.jogadores[cliente_socket] = jogador
                self.proximo_id += 1
                self.estatisticas['conexoes_totais'] += 1
                
                self.logger.info(f"👤 {jogador.nome} ({jogador.cor}) conectado")
                
                # Envia confirmação de conexão
                mensagem_aceita = ProtocoloDamas.criar_mensagem_conexao_aceita(jogador)
                self.enviar_mensagem(cliente_socket, mensagem_aceita)
                
                # Verifica se pode iniciar jogo
                if len(self.jogadores) == 2:
                    self.iniciar_novo_jogo()
            
            # Loop de comunicação
            self.loop_comunicacao_cliente(cliente_socket, jogador)
            
        except Exception as e:
            self.logger.error(f"Erro ao gerenciar cliente {endereco}: {e}")
        finally:
            if jogador:
                self.desconectar_jogador(cliente_socket, jogador)
    
    def loop_comunicacao_cliente(self, cliente_socket: socket.socket, jogador: Jogador):
        """Loop principal de comunicação com cliente"""
        buffer = ""
        
        while self.rodando and cliente_socket in self.jogadores:
            try:
                dados = cliente_socket.recv(4096).decode('utf-8')
                if not dados:
                    break
                
                buffer += dados
                
                # Processa mensagens completas
                while '\n' in buffer:
                    linha, buffer = buffer.split('\n', 1)
                    if linha.strip():
                        try:
                            mensagem = json.loads(linha)
                            self.processar_mensagem(cliente_socket, jogador, mensagem)
                        except json.JSONDecodeError:
                            self.logger.warning(f"Mensagem JSON inválida de {jogador.nome}")
                            self.enviar_erro(cliente_socket, 
                                           CodigosErro.MENSAGEM_MALFORMADA,
                                           "Formato de mensagem inválido")
                
            except socket.timeout:
                continue
            except socket.error:
                break
            except Exception as e:
                self.logger.error(f"Erro na comunicação com {jogador.nome}: {e}")
                break
    
    def processar_mensagem(self, cliente_socket: socket.socket, jogador: Jogador, mensagem: Dict):
        """Processa mensagem recebida do cliente"""
        # Valida mensagem
        valida, erro = ProtocoloDamas.validar_mensagem(mensagem)
        if not valida:
            self.enviar_erro(cliente_socket, CodigosErro.MENSAGEM_MALFORMADA, erro)
            return
        
        tipo = mensagem.get('tipo')
        
        if tipo == TipoMensagem.MOVIMENTO_SOLICITADO.value:
            self.processar_movimento(cliente_socket, jogador, mensagem)
        elif tipo == TipoMensagem.SOLICITAR_ESTADO.value:
            self.enviar_estado_completo(cliente_socket)
        elif tipo == TipoMensagem.CHAT.value:
            self.processar_chat(cliente_socket, jogador, mensagem)
        elif tipo == TipoMensagem.PING.value:
            self.enviar_mensagem(cliente_socket, {'tipo': TipoMensagem.PONG.value})
        else:
            self.enviar_erro(cliente_socket, CodigosErro.TIPO_DESCONHECIDO, 
                           f"Tipo de mensagem desconhecido: {tipo}")
    
    def processar_movimento(self, cliente_socket: socket.socket, jogador: Jogador, mensagem: Dict):
        """Processa movimento de peça"""
        with self.lock:
            # Verifica se jogo está ativo
            if self.estado_jogo != EstadoJogo.EM_ANDAMENTO:
                self.enviar_erro(cliente_socket, CodigosErro.JOGO_NAO_INICIADO,
                               "Jogo não está em andamento")
                return
            
            # Verifica se é o turno do jogador
            if jogador.cor != self.turno_atual:
                self.enviar_erro(cliente_socket, CodigosErro.NAO_SEU_TURNO,
                               "Não é seu turno")
                return
            
            origem = tuple(mensagem['origem'])
            destino = tuple(mensagem['destino'])
            
            # Valida movimento usando lógica do jogo existente
            resultado_validacao = self.validar_movimento_completo(origem, destino, jogador.cor)
            
            if not resultado_validacao['valido']:
                mensagem_erro = ProtocoloDamas.criar_mensagem_movimento_invalido(
                    resultado_validacao['motivo']
                )
                self.enviar_mensagem(cliente_socket, mensagem_erro)
                return
            
            # Executa movimento (sem enviar mensagem automaticamente)
            resultado_movimento = self.executar_movimento_completo(origem, destino, jogador, alternar_turno=False)
            
            if resultado_movimento['sucesso']:
                # Verifica condições de vitória
                vencedor = self.verificar_condicoes_vitoria()
                
                if vencedor:
                    self.finalizar_jogo(vencedor, "Vitória por eliminação")
                else:
                    # Alterna turno e envia mensagem atualizada
                    self.alternar_turno()
                    self.verificar_movimentos_obrigatorios()
                    # Envia mensagem com turno atualizado
                    self.enviar_mensagem_turno_atualizado(resultado_movimento['movimento'])
            else:
                mensagem_erro = ProtocoloDamas.criar_mensagem_movimento_invalido(
                    resultado_movimento['erro']
                )
                self.enviar_mensagem(cliente_socket, mensagem_erro)
    
    def validar_movimento_completo(self, origem: Tuple[int, int], destino: Tuple[int, int], 
                                 cor_jogador: str) -> Dict:
        """Valida movimento usando lógica do jogo"""
        if not self.jogo or not self.jogo.tabuleiro:
            return {'valido': False, 'motivo': 'Estado de jogo inválido'}
        
        # Verifica limites do tabuleiro
        if not self.coordenadas_validas(origem) or not self.coordenadas_validas(destino):
            return {'valido': False, 'motivo': 'Coordenadas fora do tabuleiro'}
        
        origem_x, origem_y = origem
        destino_x, destino_y = destino
        
        # Verifica se há peça na origem
        quadrado_origem = self.jogo.tabuleiro.matriz[origem_y][origem_x]
        if not quadrado_origem.ocupante:
            return {'valido': False, 'motivo': 'Não há peça na posição de origem'}
        
        # Verifica se a peça pertence ao jogador
        if quadrado_origem.ocupante.cor != cor_jogador:
            return {'valido': False, 'motivo': 'Peça não pertence ao jogador'}
        
        # Verifica se destino está vazio
        quadrado_destino = self.jogo.tabuleiro.matriz[destino_y][destino_x]
        if quadrado_destino.ocupante:
            return {'valido': False, 'motivo': 'Posição de destino ocupada'}
        
        # Verifica se movimento é diagonal
        diff_x = abs(destino_x - origem_x)
        diff_y = abs(destino_y - origem_y)
        
        if diff_x != diff_y:
            return {'valido': False, 'motivo': 'Movimento deve ser diagonal'}
        
        # Verifica direção para peças normais
        peca = quadrado_origem.ocupante
        if not peca.e_dama:
            direcao_y = destino_y - origem_y
            # VERDE começa na parte inferior e move para cima (y diminui)
            # AMARELO começa na parte superior e move para baixo (y aumenta)
            if cor_jogador == VERDE and direcao_y > 0:
                return {'valido': False, 'motivo': 'Peça verde deve mover para cima'}
            elif cor_jogador == AMARELO and direcao_y < 0:
                return {'valido': False, 'motivo': 'Peça amarela deve mover para baixo'}
        
        # Verifica se é movimento simples (1 casa) ou captura
        if diff_x == 1:
            # Movimento simples - verifica se não há capturas obrigatórias
            if self.movimentos_obrigatorios:
                return {'valido': False, 'motivo': 'Há capturas obrigatórias disponíveis'}
            return {'valido': True, 'motivo': 'Movimento simples válido'}
        
        elif diff_x == 2:
            # Captura - verifica se há peça adversária no meio
            meio_x = origem_x + (destino_x - origem_x) // 2
            meio_y = origem_y + (destino_y - origem_y) // 2
            
            quadrado_meio = self.jogo.tabuleiro.matriz[meio_y][meio_x]
            if not quadrado_meio.ocupante:
                return {'valido': False, 'motivo': 'Não há peça para capturar'}
            
            if quadrado_meio.ocupante.cor == cor_jogador:
                return {'valido': False, 'motivo': 'Não pode capturar própria peça'}
            
            return {'valido': True, 'motivo': 'Captura válida'}
        
        else:
            return {'valido': False, 'motivo': 'Movimento muito longo'}
    
    def executar_movimento_completo(self, origem: Tuple[int, int], destino: Tuple[int, int], 
                                  jogador: Jogador, alternar_turno: bool = True) -> Dict:
        """Executa movimento e atualiza estado"""
        try:
            origem_x, origem_y = origem
            destino_x, destino_y = destino
            
            # Move a peça
            peca = self.jogo.tabuleiro.matriz[origem_y][origem_x].ocupante
            self.jogo.tabuleiro.matriz[origem_y][origem_x].remover_peca()
            self.jogo.tabuleiro.matriz[destino_y][destino_x].colocar_peca(peca)
            
            # Cria objeto movimento
            movimento = Movimento(
                origem=origem,
                destino=destino,
                jogador_id=jogador.id,
                cor_jogador=jogador.cor,
                timestamp=time.time()
            )
            
            # Verifica se foi captura
            diff_x = abs(destino_x - origem_x)
            if diff_x == 2:
                movimento.e_captura = True
                meio_x = origem_x + (destino_x - origem_x) // 2
                meio_y = origem_y + (destino_y - origem_y) // 2
                
                # Remove peça capturada
                self.jogo.tabuleiro.matriz[meio_y][meio_x].remover_peca()
                movimento.pecas_capturadas = [(meio_x, meio_y)]
            
            # Verifica promoção a dama
            if not peca.e_dama:
                # VERDE se move para cima e vira dama no topo (x == 0)
                # AMARELO se move para baixo e vira dama no fundo (x == TAMANHO_TABULEIRO - 1)
                if (jogador.cor == VERDE and destino_x == 0) or \
                   (jogador.cor == AMARELO and destino_x == TAMANHO_TABULEIRO - 1):
                    peca.promover_dama()
                    movimento.promoveu_dama = True
            
            self.logger.info(f"Movimento executado: {jogador.nome} de {origem} para {destino}")
            
            return {'sucesso': True, 'movimento': movimento}
            
        except Exception as e:
            self.logger.error(f"Erro ao executar movimento: {e}")
            return {'sucesso': False, 'erro': 'Erro interno do servidor'}
    
    def iniciar_novo_jogo(self):
        """Inicia um novo jogo"""
        self.estado_jogo = EstadoJogo.EM_ANDAMENTO
        self.jogo = Jogo()
        self.turno_atual = VERDE
        self.movimentos_obrigatorios = []
        
        # Atualiza estado dos jogadores
        for jogador in self.jogadores.values():
            jogador.estado = EstadoJogador.JOGANDO
        
        # Envia mensagem de início
        estado_inicial = self.obter_estado_tabuleiro()
        mensagem_inicio = ProtocoloDamas.criar_mensagem_jogo_iniciado(
            estado_inicial, self.turno_atual
        )
        self.broadcast_mensagem(mensagem_inicio)
        
        self.logger.info("🎯 Novo jogo iniciado")
    
    def enviar_mensagem_turno_atualizado(self, movimento: Movimento):
        """Envia mensagem de movimento com turno atualizado"""
        estado_atual = self.obter_estado_tabuleiro()
        mensagem_movimento = ProtocoloDamas.criar_mensagem_movimento_executado(
            movimento, estado_atual, self.turno_atual
        )
        
        self.logger.info(f"📤 Enviando mensagem de movimento executado")
        self.logger.info(f"   - Movimento: {movimento.origem} -> {movimento.destino}")
        self.logger.info(f"   - Jogador que jogou: {movimento.cor_jogador}")
        self.logger.info(f"   - Próximo turno: {self.turno_atual}")
        self.logger.info(f"   - Número de jogadores conectados: {len(self.jogadores)}")
        
        self.broadcast_mensagem(mensagem_movimento)
        
        self.logger.info(f"✅ Turno atualizado enviado: agora é a vez de {self.turno_atual}")
    
    def alternar_turno(self):
        """Alterna o turno entre jogadores"""
        turno_anterior = self.turno_atual
        self.turno_atual = AMARELO if self.turno_atual == VERDE else VERDE
        
        self.logger.info(f"🔄 Alternando turno: {turno_anterior} -> {self.turno_atual}")
        
        # Atualiza estado dos jogadores
        for jogador in self.jogadores.values():
            if jogador.cor == self.turno_atual:
                jogador.estado = EstadoJogador.JOGANDO
                self.logger.info(f"   - {jogador.nome} ({jogador.cor}) agora está JOGANDO")
            else:
                jogador.estado = EstadoJogador.AGUARDANDO_TURNO
                self.logger.info(f"   - {jogador.nome} ({jogador.cor}) está AGUARDANDO_TURNO")
    
    def verificar_movimentos_obrigatorios(self):
        """Verifica se há capturas obrigatórias"""
        # Implementação simplificada - pode ser expandida
        self.movimentos_obrigatorios = []
        # TODO: Implementar detecção de capturas obrigatórias
    
    def verificar_condicoes_vitoria(self) -> Optional[str]:
        """Verifica condições de vitória"""
        if not self.jogo or not self.jogo.tabuleiro:
            return None
        
        pecas_verdes = 0
        pecas_amarelas = 0
        
        # Conta peças restantes
        for x in range(TAMANHO_TABULEIRO):
            for y in range(TAMANHO_TABULEIRO):
                quadrado = self.jogo.tabuleiro.matriz[y][x]
                if quadrado.ocupante:
                    if quadrado.ocupante.cor == VERDE:
                        pecas_verdes += 1
                    elif quadrado.ocupante.cor == AMARELO:
                        pecas_amarelas += 1
        
        # Verifica vitória por eliminação
        if pecas_verdes == 0:
            return AMARELO
        elif pecas_amarelas == 0:
            return VERDE
        
        return None
    
    def finalizar_jogo(self, vencedor: str, motivo: str):
        """Finaliza o jogo atual"""
        self.estado_jogo = EstadoJogo.FINALIZADO
        self.estatisticas['jogos_concluidos'] += 1
        
        estado_final = self.obter_estado_tabuleiro()
        mensagem_fim = ProtocoloDamas.criar_mensagem_jogo_finalizado(
            vencedor, motivo, estado_final
        )
        self.broadcast_mensagem(mensagem_fim)
        
        self.logger.info(f"🏆 Jogo finalizado! Vencedor: {vencedor} ({motivo})")
        
        # Reset para aguardar novo jogo
        self.estado_jogo = EstadoJogo.AGUARDANDO_JOGADORES
        self.jogo = None
    
    def obter_estado_tabuleiro(self) -> EstadoTabuleiro:
        """Obtém estado atual do tabuleiro"""
        if not self.jogo or not self.jogo.tabuleiro:
            return EstadoTabuleiro(matriz=[], pecas_verdes=0, pecas_amarelas=0, 
                                 damas_verdes=0, damas_amarelas=0)
        
        matriz = []
        pecas_verdes = pecas_amarelas = damas_verdes = damas_amarelas = 0
        
        for x in range(TAMANHO_TABULEIRO):
            linha = []
            for y in range(TAMANHO_TABULEIRO):
                quadrado = self.jogo.tabuleiro.matriz[y][x]
                
                if quadrado.ocupante:
                    linha.append({
                        'cor_quadrado': quadrado.cor,
                        'peca': {
                            'cor': quadrado.ocupante.cor,
                            'e_dama': quadrado.ocupante.e_dama
                        }
                    })
                    
                    # Conta estatísticas
                    if quadrado.ocupante.cor == VERDE:
                        pecas_verdes += 1
                        if quadrado.ocupante.e_dama:
                            damas_verdes += 1
                    else:
                        pecas_amarelas += 1
                        if quadrado.ocupante.e_dama:
                            damas_amarelas += 1
                else:
                    linha.append({
                        'cor_quadrado': quadrado.cor,
                        'peca': None
                    })
            matriz.append(linha)
        
        return EstadoTabuleiro(
            matriz=matriz,
            pecas_verdes=pecas_verdes,
            pecas_amarelas=pecas_amarelas,
            damas_verdes=damas_verdes,
            damas_amarelas=damas_amarelas
        )
    
    def coordenadas_validas(self, coord: Tuple[int, int]) -> bool:
        """Verifica se coordenadas são válidas"""
        x, y = coord
        return 0 <= x < TAMANHO_TABULEIRO and 0 <= y < TAMANHO_TABULEIRO
    
    def processar_chat(self, cliente_socket: socket.socket, jogador: Jogador, mensagem: Dict):
        """Processa mensagem de chat"""
        texto = mensagem.get('texto', '').strip()
        if texto:
            mensagem_chat = ProtocoloDamas.criar_mensagem_chat(jogador, texto)
            self.broadcast_mensagem(mensagem_chat, excluir_socket=cliente_socket)
    
    def enviar_estado_completo(self, cliente_socket: socket.socket):
        """Envia estado completo do jogo"""
        estado_tabuleiro = self.obter_estado_tabuleiro()
        jogadores_lista = list(self.jogadores.values())
        
        mensagem_estado = ProtocoloDamas.criar_mensagem_estado_jogo(
            self.estado_jogo, estado_tabuleiro, self.turno_atual, jogadores_lista
        )
        self.enviar_mensagem(cliente_socket, mensagem_estado)
    
    def enviar_mensagem(self, cliente_socket: socket.socket, mensagem: Dict):
        """Envia mensagem para cliente específico"""
        try:
            dados = json.dumps(mensagem, ensure_ascii=False) + '\n'
            cliente_socket.send(dados.encode('utf-8'))
            self.logger.debug(f"✅ Mensagem enviada com sucesso: {mensagem.get('tipo')}")
        except Exception as e:
            self.logger.error(f"❌ Erro ao enviar mensagem: {e}")
            raise
    
    def broadcast_mensagem(self, mensagem: Dict, excluir_socket: socket.socket = None):
        """Envia mensagem para todos os clientes"""
        sockets_para_remover = []
        
        self.logger.info(f"📡 Fazendo broadcast da mensagem tipo: {mensagem.get('tipo')}")
        self.logger.info(f"   - Jogadores conectados: {len(self.jogadores)}")
        
        for cliente_socket in list(self.jogadores.keys()):
            if cliente_socket != excluir_socket:
                try:
                    jogador = self.jogadores[cliente_socket]
                    self.logger.info(f"   - Enviando para {jogador.nome} ({jogador.cor})")
                    self.enviar_mensagem(cliente_socket, mensagem)
                except Exception as e:
                    self.logger.error(f"   - Erro ao enviar para cliente: {e}")
                    sockets_para_remover.append(cliente_socket)
        
        # Remove sockets com falha
        for socket_falho in sockets_para_remover:
            if socket_falho in self.jogadores:
                jogador = self.jogadores[socket_falho]
                self.desconectar_jogador(socket_falho, jogador)
    
    def enviar_erro(self, cliente_socket: socket.socket, codigo: str, descricao: str):
        """Envia mensagem de erro para cliente"""
        mensagem_erro = ProtocoloDamas.criar_mensagem_erro(codigo, descricao)
        self.enviar_mensagem(cliente_socket, mensagem_erro)
    
    def desconectar_jogador(self, cliente_socket: socket.socket, jogador: Jogador):
        """Remove jogador do servidor"""
        with self.lock:
            if cliente_socket in self.jogadores:
                del self.jogadores[cliente_socket]
                
                self.logger.info(f"❌ {jogador.nome} desconectado")
                
                # Notifica outros jogadores
                if self.jogadores:
                    mensagem_notif = ProtocoloDamas.criar_mensagem_notificacao(
                        f"{jogador.nome} desconectou", "warning"
                    )
                    self.broadcast_mensagem(mensagem_notif)
                
                # Interrompe jogo se estava ativo
                if self.estado_jogo == EstadoJogo.EM_ANDAMENTO:
                    mensagem_interrupcao = {
                        'tipo': TipoMensagem.JOGO_INTERROMPIDO.value,
                        'motivo': 'Jogador desconectou',
                        'mensagem': 'Jogo interrompido - jogador desconectou'
                    }
                    self.broadcast_mensagem(mensagem_interrupcao)
                    self.estado_jogo = EstadoJogo.INTERROMPIDO
                
                # Reset se não há jogadores
                if not self.jogadores:
                    self.estado_jogo = EstadoJogo.AGUARDANDO_JOGADORES
                    self.jogo = None
                    self.proximo_id = 1
        
        try:
            cliente_socket.close()
        except:
            pass
    
    def parar_servidor(self):
        """Para o servidor graciosamente"""
        self.logger.info("🛑 Parando servidor...")
        self.rodando = False
        
        # Notifica clientes
        if self.jogadores:
            mensagem_encerramento = {
                'tipo': TipoMensagem.SERVIDOR_ENCERRANDO.value,
                'mensagem': 'Servidor encerrando'
            }
            self.broadcast_mensagem(mensagem_encerramento)
        
        # Fecha conexões
        for cliente_socket, jogador in list(self.jogadores.items()):
            self.desconectar_jogador(cliente_socket, jogador)
        
        if self.socket_servidor:
            self.socket_servidor.close()
        
        self.logger.info("✅ Servidor encerrado")
        self.logger.info(f"📊 Estatísticas: {self.estatisticas['jogos_concluidos']} jogos, "
                        f"{self.estatisticas['conexoes_totais']} conexões")


def main():
    """Função principal do servidor"""
    print("🎮 Servidor Damas Online")
    print("=" * 30)
    
    host = input("Host (Enter para 0.0.0.0 - aceita qualquer IP): ").strip() or '0.0.0.0'
    porta_input = input("Porta (Enter para 12345): ").strip()
    porta = int(porta_input) if porta_input else 12345
    
    servidor = ServidorDamasAvancado(host, porta)
    
    try:
        servidor.iniciar_servidor()
    except KeyboardInterrupt:
        print("\n🛑 Interrupção pelo usuário")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
    finally:
        servidor.parar_servidor()


if __name__ == "__main__":
    main()
