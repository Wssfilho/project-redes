"""
Protocolo de Aplicação do Jogo de Damas Online
Especificação detalhada das mensagens e estados
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum


class TipoMensagem(Enum):
    """Tipos de mensagens no protocolo"""
    # Conexão e autenticação
    CONEXAO_SOLICITADA = "conexao_solicitada"
    CONEXAO_ACEITA = "conexao_aceita"
    CONEXAO_REJEITADA = "conexao_rejeitada"
    
    # Estado do jogo
    JOGO_INICIADO = "jogo_iniciado"
    JOGO_FINALIZADO = "jogo_finalizado"
    JOGO_INTERROMPIDO = "jogo_interrompido"
    
    # Movimentos
    MOVIMENTO_SOLICITADO = "movimento_solicitado"
    MOVIMENTO_EXECUTADO = "movimento_executado"
    MOVIMENTO_INVALIDO = "movimento_invalido"
    MOVIMENTO_OBRIGATORIO = "movimento_obrigatorio"
    
    # Estado
    SOLICITAR_ESTADO = "solicitar_estado"
    ESTADO_JOGO = "estado_jogo"
    TURNO_ALTERADO = "turno_alterado"
    
    # Chat e comunicação
    CHAT = "chat"
    NOTIFICACAO = "notificacao"
    
    # Controle
    PING = "ping"
    PONG = "pong"
    ERRO = "erro"
    
    # Desconexão
    JOGADOR_DESCONECTADO = "jogador_desconectado"
    SERVIDOR_ENCERRANDO = "servidor_encerrando"


class EstadoJogo(Enum):
    """Estados possíveis do jogo"""
    AGUARDANDO_JOGADORES = "aguardando_jogadores"
    PRONTO_PARA_INICIAR = "pronto_para_iniciar"
    EM_ANDAMENTO = "em_andamento"
    FINALIZADO = "finalizado"
    INTERROMPIDO = "interrompido"


class EstadoJogador(Enum):
    """Estados possíveis de um jogador"""
    CONECTANDO = "conectando"
    CONECTADO = "conectado"
    JOGANDO = "jogando"
    AGUARDANDO_TURNO = "aguardando_turno"
    DESCONECTADO = "desconectado"


@dataclass
class Jogador:
    """Representa um jogador no sistema"""
    id: int
    nome: str
    cor: str
    socket: Any
    endereco: Tuple[str, int]
    estado: EstadoJogador
    conectado_em: float


@dataclass
class Movimento:
    """Representa um movimento no jogo"""
    origem: Tuple[int, int]
    destino: Tuple[int, int]
    jogador_id: int
    cor_jogador: str
    e_captura: bool = False
    pecas_capturadas: List[Tuple[int, int]] = None
    promoveu_dama: bool = False
    timestamp: float = 0.0


@dataclass
class EstadoPeca:
    """Estado de uma peça no tabuleiro"""
    cor: str
    e_dama: bool
    posicao: Tuple[int, int]


@dataclass
class EstadoTabuleiro:
    """Estado completo do tabuleiro"""
    matriz: List[List[Dict]]
    pecas_verdes: int
    pecas_amarelas: int
    damas_verdes: int
    damas_amarelas: int


class ProtocoloDamas:
    """Implementa o protocolo de comunicação do jogo de damas"""
    
    @staticmethod
    def criar_mensagem_conexao_aceita(jogador: Jogador) -> Dict:
        """Cria mensagem de conexão aceita"""
        return {
            'tipo': TipoMensagem.CONEXAO_ACEITA.value,
            'jogador_id': jogador.id,
            'cor': jogador.cor,
            'nome': jogador.nome,
            'timestamp': jogador.conectado_em,
            'mensagem': f'Bem-vindo, {jogador.nome}! Você joga com as peças {jogador.cor}.'
        }
    
    @staticmethod
    def criar_mensagem_conexao_rejeitada(motivo: str) -> Dict:
        """Cria mensagem de conexão rejeitada"""
        return {
            'tipo': TipoMensagem.CONEXAO_REJEITADA.value,
            'motivo': motivo,
            'mensagem': f'Conexão rejeitada: {motivo}'
        }
    
    @staticmethod
    def criar_mensagem_jogo_iniciado(estado_tabuleiro: EstadoTabuleiro, turno_inicial: str) -> Dict:
        """Cria mensagem de início de jogo"""
        return {
            'tipo': TipoMensagem.JOGO_INICIADO.value,
            'turno': turno_inicial,
            'tabuleiro': estado_tabuleiro.matriz,
            'estatisticas': {
                'pecas_verdes': estado_tabuleiro.pecas_verdes,
                'pecas_amarelas': estado_tabuleiro.pecas_amarelas,
                'damas_verdes': estado_tabuleiro.damas_verdes,
                'damas_amarelas': estado_tabuleiro.damas_amarelas
            },
            'mensagem': f'Jogo iniciado! {turno_inicial} joga primeiro.'
        }
    
    @staticmethod
    def criar_mensagem_movimento_executado(movimento: Movimento, estado_tabuleiro: EstadoTabuleiro, 
                                         proximo_turno: str) -> Dict:
        """Cria mensagem de movimento executado"""
        mensagem_base = {
            'tipo': TipoMensagem.MOVIMENTO_EXECUTADO.value,
            'movimento': {
                'origem': movimento.origem,
                'destino': movimento.destino,
                'jogador_id': movimento.jogador_id,
                'cor_jogador': movimento.cor_jogador,
                'timestamp': movimento.timestamp
            },
            'turno': proximo_turno,
            'tabuleiro': estado_tabuleiro.matriz,
            'estatisticas': {
                'pecas_verdes': estado_tabuleiro.pecas_verdes,
                'pecas_amarelas': estado_tabuleiro.pecas_amarelas,
                'damas_verdes': estado_tabuleiro.damas_verdes,
                'damas_amarelas': estado_tabuleiro.damas_amarelas
            }
        }
        
        # Adiciona informações específicas se houve captura
        if movimento.e_captura:
            mensagem_base['movimento']['e_captura'] = True
            mensagem_base['movimento']['pecas_capturadas'] = movimento.pecas_capturadas
            mensagem_base['mensagem'] = f'{movimento.cor_jogador} capturou {len(movimento.pecas_capturadas)} peça(s)!'
        else:
            mensagem_base['mensagem'] = f'{movimento.cor_jogador} moveu de {movimento.origem} para {movimento.destino}'
        
        # Adiciona informação sobre promoção a dama
        if movimento.promoveu_dama:
            mensagem_base['movimento']['promoveu_dama'] = True
            mensagem_base['mensagem'] += ' e virou DAMA!'
        
        return mensagem_base
    
    @staticmethod
    def criar_mensagem_movimento_invalido(motivo: str) -> Dict:
        """Cria mensagem de movimento inválido"""
        return {
            'tipo': TipoMensagem.MOVIMENTO_INVALIDO.value,
            'motivo': motivo,
            'mensagem': f'Movimento inválido: {motivo}'
        }
    
    @staticmethod
    def criar_mensagem_movimento_obrigatorio(movimentos_obrigatorios: List[Tuple[Tuple[int, int], Tuple[int, int]]]) -> Dict:
        """Cria mensagem sobre movimentos obrigatórios de captura"""
        return {
            'tipo': TipoMensagem.MOVIMENTO_OBRIGATORIO.value,
            'movimentos_obrigatorios': movimentos_obrigatorios,
            'mensagem': 'Você deve executar uma captura obrigatória!'
        }
    
    @staticmethod
    def criar_mensagem_jogo_finalizado(vencedor: str, motivo: str, estado_final: EstadoTabuleiro) -> Dict:
        """Cria mensagem de fim de jogo"""
        return {
            'tipo': TipoMensagem.JOGO_FINALIZADO.value,
            'vencedor': vencedor,
            'motivo': motivo,
            'tabuleiro_final': estado_final.matriz,
            'estatisticas_finais': {
                'pecas_verdes': estado_final.pecas_verdes,
                'pecas_amarelas': estado_final.pecas_amarelas,
                'damas_verdes': estado_final.damas_verdes,
                'damas_amarelas': estado_final.damas_amarelas
            },
            'mensagem': f'{vencedor} venceu! Motivo: {motivo}'
        }
    
    @staticmethod
    def criar_mensagem_estado_jogo(estado_jogo: EstadoJogo, estado_tabuleiro: EstadoTabuleiro, 
                                 turno_atual: str, jogadores: List[Jogador]) -> Dict:
        """Cria mensagem com estado completo do jogo"""
        return {
            'tipo': TipoMensagem.ESTADO_JOGO.value,
            'estado_jogo': estado_jogo.value,
            'turno': turno_atual,
            'tabuleiro': estado_tabuleiro.matriz,
            'estatisticas': {
                'pecas_verdes': estado_tabuleiro.pecas_verdes,
                'pecas_amarelas': estado_tabuleiro.pecas_amarelas,
                'damas_verdes': estado_tabuleiro.damas_verdes,
                'damas_amarelas': estado_tabuleiro.damas_amarelas
            },
            'jogadores': [
                {
                    'id': j.id,
                    'nome': j.nome,
                    'cor': j.cor,
                    'estado': j.estado.value
                } for j in jogadores
            ]
        }
    
    @staticmethod
    def criar_mensagem_chat(remetente: Jogador, texto: str) -> Dict:
        """Cria mensagem de chat"""
        return {
            'tipo': TipoMensagem.CHAT.value,
            'remetente': {
                'id': remetente.id,
                'nome': remetente.nome,
                'cor': remetente.cor
            },
            'texto': texto,
            'timestamp': time.time()
        }
    
    @staticmethod
    def criar_mensagem_notificacao(texto: str, nivel: str = "info") -> Dict:
        """Cria mensagem de notificação do sistema"""
        return {
            'tipo': TipoMensagem.NOTIFICACAO.value,
            'nivel': nivel,  # "info", "warning", "error"
            'texto': texto,
            'timestamp': time.time()
        }
    
    @staticmethod
    def criar_mensagem_erro(codigo_erro: str, descricao: str) -> Dict:
        """Cria mensagem de erro"""
        return {
            'tipo': TipoMensagem.ERRO.value,
            'codigo': codigo_erro,
            'descricao': descricao,
            'timestamp': time.time()
        }
    
    @staticmethod
    def validar_mensagem(mensagem: Dict) -> Tuple[bool, str]:
        """Valida estrutura básica de uma mensagem"""
        if not isinstance(mensagem, dict):
            return False, "Mensagem deve ser um dicionário"
        
        if 'tipo' not in mensagem:
            return False, "Mensagem deve conter campo 'tipo'"
        
        tipo = mensagem['tipo']
        
        # Validações específicas por tipo
        if tipo == TipoMensagem.MOVIMENTO_SOLICITADO.value:
            if 'origem' not in mensagem or 'destino' not in mensagem:
                return False, "Movimento deve conter 'origem' e 'destino'"
            
            origem = mensagem['origem']
            destino = mensagem['destino']
            
            if (not isinstance(origem, (list, tuple)) or len(origem) != 2 or
                not isinstance(destino, (list, tuple)) or len(destino) != 2):
                return False, "Coordenadas devem ser tuplas/listas de 2 elementos"
            
            if not all(isinstance(coord, int) for coord in origem + destino):
                return False, "Coordenadas devem ser números inteiros"
        
        elif tipo == TipoMensagem.CHAT.value:
            if 'texto' not in mensagem:
                return False, "Mensagem de chat deve conter 'texto'"
            
            if not isinstance(mensagem['texto'], str):
                return False, "Texto do chat deve ser string"
            
            if len(mensagem['texto']) > 500:
                return False, "Texto do chat muito longo (máximo 500 caracteres)"
        
        return True, "Mensagem válida"


# Códigos de erro padronizados
class CodigosErro:
    """Códigos de erro padronizados do protocolo"""
    
    # Erros de conexão
    SERVIDOR_LOTADO = "E001"
    CONEXAO_RECUSADA = "E002"
    TIMEOUT_CONEXAO = "E003"
    
    # Erros de jogo
    MOVIMENTO_INVALIDO = "E101"
    NAO_SEU_TURNO = "E102"
    JOGO_NAO_INICIADO = "E103"
    PECA_INEXISTENTE = "E104"
    PECA_ADVERSARIA = "E105"
    MOVIMENTO_OBRIGATORIO_IGNORADO = "E106"
    
    # Erros de protocolo
    MENSAGEM_MALFORMADA = "E201"
    TIPO_DESCONHECIDO = "E202"
    DADOS_INSUFICIENTES = "E203"
    
    # Erros de sistema
    ERRO_INTERNO = "E301"
    SERVIDOR_INDISPONIVEL = "E302"


# Importações necessárias
import time
