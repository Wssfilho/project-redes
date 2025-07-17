# Damas Online
Um jogo de damas multiplayer online construído com Python e Pygame, featuring um protocolo de rede personalizado para comunicação cliente-servidor. O projeto implementa uma arquitetura modular e flexível para jogos online com componentes para física, renderização, interface e comunicação de rede.

## 📋 Nota

Clique aqui para a versão em [English](README_EN.md).

## 🎮 Protocolo de Comunicação

O jogo utiliza um protocolo personalizado para comunicação de rede, definido no módulo `protocolo.py`. O protocolo inclui vários tipos de pacotes para diferentes eventos e estados do jogo.

### Formato dos Pacotes

| Status | Cliente | Servidor |
|--------|---------|----------|
| Ping | ✅ | ❌ |
| Pong | ❌ | ✅ |
| Jogo | Cliente | Servidor |
| Keep Alive | ✅ | ✅ |
| Conectar | ✅ | ❌ |
| Desconectar | ✅ | ❌ |
| Movimento | ✅ | ✅ |
| Chat | ✅ | ✅ |

### Estrutura do Protocolo

O formato do protocolo é uma estrutura JSON que inclui um cabeçalho com tipo e dados. O cabeçalho contém o tipo do pacote, enquanto o payload contém os dados específicos.

| Nome | Tipo | Descrição |
|------|------|-----------|
| tipo | string | O tipo/identificador do pacote |
| dados | object | O payload de dados do pacote. Varia dependendo do tipo de pacote |

## 🔄 Estados de Comunicação

### Status
O status é usado para verificar se há um servidor de jogo executando neste endereço. O cliente pode enviar um pacote ping para a porta 12345 para verificar se o servidor está disponível. O servidor responderá com um pacote pong se estiver em execução.

#### Cliente
**Ping**
| Tipo | Estado | Destinado Para | Nome do Campo | Tipo do Campo | Descrição |
|------|--------|----------------|---------------|---------------|-----------|
| `ping` | Status | Servidor | timestamp | float | Timestamp do ping para calcular latência |

#### Servidor  
**Pong**
| Tipo | Estado | Destinado Para | Nome do Campo | Tipo do Campo | Descrição |
|------|--------|----------------|---------------|---------------|-----------|
| `pong` | Status | Cliente | timestamp | float | Timestamp original retornado para calcular latência |

## 🎯 Estado de Jogo
O estado de jogo é usado durante a partida. Inclui pacotes para ações do jogador, atualizações de estado do jogo e outros eventos relacionados à jogabilidade.

### Cliente

**Keep Alive**
| Tipo | Estado | Destinado Para | Nome do Campo | Tipo do Campo | Descrição |
|------|--------|----------------|---------------|---------------|-----------|
| `ping` | Jogo | Servidor | timestamp | float | Valor esperado para verificar se o cliente ainda está conectado |

**Conectar**
| Tipo | Estado | Destinado Para | Nome do Campo | Tipo do Campo | Descrição |
|------|--------|----------------|---------------|---------------|-----------|
| `conexao_solicitada` | Jogo | Servidor | nome | string | O nome do jogador se conectando ao jogo |

**Desconectar**
| Tipo | Estado | Destinado Para | Nome do Campo | Tipo do Campo | Descrição |
|------|--------|----------------|---------------|---------------|-----------|
| `jogador_desconectado` | Jogo | Servidor | - | - | Indica que o jogador está se desconectando do jogo |

**Movimento**
| Tipo | Estado | Destinado Para | Nome do Campo | Tipo do Campo | Descrição |
|------|--------|----------------|---------------|---------------|-----------|
| `movimento_solicitado` | Jogo | Servidor | origem | int[2] | Coordenadas de origem da peça [x, y] |
| | | | destino | int[2] | Coordenadas de destino da peça [x, y] |

**Chat**
| Tipo | Estado | Destinado Para | Nome do Campo | Tipo do Campo | Descrição |
|------|--------|----------------|---------------|---------------|-----------|
| `chat` | Jogo | Servidor | texto | string | Mensagem de chat do jogador (máximo 500 caracteres) |

### Servidor

**Keep Alive**
| Tipo | Estado | Destinado Para | Nome do Campo | Tipo do Campo | Descrição |
|------|--------|----------------|---------------|---------------|-----------|
| `pong` | Jogo | Cliente | timestamp | float | Valor enviado pelo servidor para verificar conectividade |

**Bem-vindo**
| Tipo | Estado | Destinado Para | Nome do Campo | Tipo do Campo | Descrição |
|------|--------|----------------|---------------|---------------|-----------|
| `conexao_aceita` | Jogo | Cliente | jogador_id | int | O ID do jogador se aceito na partida |
| | | | cor | string | A cor das peças do jogador ("verde" ou "amarelo") |
| | | | nome | string | Nome do jogador confirmado |
| | | | mensagem | string | Mensagem de boas-vindas |

**Conexão Rejeitada**
| Tipo | Estado | Destinado Para | Nome do Campo | Tipo do Campo | Descrição |
|------|--------|----------------|---------------|---------------|-----------|
| `conexao_rejeitada` | Jogo | Cliente | motivo | string | Motivo da rejeição da conexão |
| | | | mensagem | string | Mensagem explicativa do erro |

**Movimento Executado**
| Tipo | Estado | Destinado Para | Nome do Campo | Tipo do Campo | Descrição |
|------|--------|----------------|---------------|---------------|-----------|
| `movimento_executado` | Jogo | Cliente | movimento | object | Dados completos do movimento executado |
| | | | turno | string | De quem é o próximo turno ("verde" ou "amarelo") |
| | | | tabuleiro | array | Estado atual completo do tabuleiro 8x8 |
| | | | estatisticas | object | Contadores de peças e damas de cada cor |

**Movimento Inválido**
| Tipo | Estado | Destinado Para | Nome do Campo | Tipo do Campo | Descrição |
|------|--------|----------------|---------------|---------------|-----------|
| `movimento_invalido` | Jogo | Cliente | motivo | string | Razão pela qual o movimento foi rejeitado |
| | | | mensagem | string | Mensagem explicativa do erro |

**Início de Jogo**
| Tipo | Estado | Destinado Para | Nome do Campo | Tipo do Campo | Descrição |
|------|--------|----------------|---------------|---------------|-----------|
| `jogo_iniciado` | Jogo | Cliente | turno | string | Cor do jogador que inicia ("verde" sempre) |
| | | | tabuleiro | array | Estado inicial do tabuleiro 8x8 |
| | | | estatisticas | object | Contadores iniciais de peças |

**Fim de Jogo**
| Tipo | Estado | Destinado Para | Nome do Campo | Tipo do Campo | Descrição |
|------|--------|----------------|---------------|---------------|-----------|
| `jogo_finalizado` | Jogo | Cliente | vencedor | string | Cor do jogador vencedor |
| | | | motivo | string | Motivo da vitória (eliminação, desistência, etc.) |
| | | | tabuleiro_final | array | Estado final do tabuleiro |

**Chat**
| Tipo | Estado | Destinado Para | Nome do Campo | Tipo do Campo | Descrição |
|------|--------|----------------|---------------|---------------|-----------|
| `chat` | Jogo | Cliente | remetente | object | Dados do jogador que enviou (id, nome, cor) |
| | | | texto | string | Mensagem de chat |
| | | | timestamp | float | Timestamp da mensagem |

## 🚀 Como Executar

### Requisitos
- Python 3.8+
- Pygame 2.6+
- Sistema operacional: Windows, Linux ou macOS

### Instalação Rápida

1. **Clone o repositório:**
```bash
git clone https://github.com/Wssfilho/project-redes.git
cd project-redes/Projeto\ Redes
```

2. **Instale as dependências:**
```bash
pip install pygame
```

3. **Execute o launcher automático:**
```bash
python iniciar_jogo.py
```

### Execução Manual

#### Servidor
```bash
python servidor_avancado.py
```
- Host padrão: `0.0.0.0` (aceita conexões de qualquer IP)
- Porta padrão: `12345`

#### Cliente
```bash
python cliente_avancado.py
```
- Host padrão: `localhost`
- Porta padrão: `12345`

## 🌐 Configuração de Rede

### Firewall (Windows)
```powershell
# PowerShell (Administrador)
New-NetFirewallRule -DisplayName "Damas Online" -Direction Inbound -Protocol TCP -LocalPort 12345 -Action Allow
```

### Firewall (Linux)
```bash
# UFW
sudo ufw allow 12345

# iptables
sudo iptables -A INPUT -p tcp --dport 12345 -j ACCEPT
```

### Jogo em Rede Local
1. Execute o servidor no PC host
2. Anote o IP do servidor (exibido no console)
3. Execute o cliente nos outros PCs
4. Conecte usando o IP do servidor e porta 12345

### Diagnósticos de Rede
```bash
python config_rede.py
```
Este script oferece:
- Teste de conectividade
- Verificação de firewall
- Instruções detalhadas de configuração
- Diagnóstico de problemas

## 🎮 Como Jogar

### Regras das Damas
- **Objetivo:** Capturar todas as peças do adversário
- **Movimento:** Peças se movem diagonalmente em casas escuras
- **Captura:** Pule sobre peças adversárias para capturá-las
- **Dama:** Peças que alcançam a última fileira viram damas
- **Turno:** Peças verdes sempre começam

### Controles
- **Mouse:** Clique para selecionar e mover peças
- **Chat:** Digite mensagens na interface
- **ESC:** Menu de pausa/sair

### Interface
- **Status da Conexão:** Canto superior direito
- **Turno Atual:** Indicação visual
- **Contador de Peças:** Estatísticas em tempo real
- **Chat:** Comunicação entre jogadores

## 📁 Estrutura do Projeto

```
project-redes/
├── Projeto Redes/
│   ├── main.py              # Menu principal e launcher
│   ├── servidor_avancado.py # Servidor multiplayer
│   ├── cliente_avancado.py  # Cliente com interface
│   ├── protocolo.py         # Protocolo de comunicação
│   ├── jogo.py             # Lógica principal do jogo
│   ├── tabuleiro.py        # Gerenciamento do tabuleiro
│   ├── peca.py             # Classe das peças
│   ├── constantes.py       # Configurações e cores
│   ├── config_rede.py      # Utilitários de rede
│   ├── iniciar_jogo.py     # Launcher automatizado
│   └── resources/          # Recursos gráficos
│       ├── icon.png
│       ├── tabuleiro.png
│       ├── peca_verde.png
│       ├── peca_amarela.png
│       └── ...
```

## 🔧 Arquitetura Técnica

### Servidor (`servidor_avancado.py`)
- **Modelo:** Multi-threaded server
- **Protocolo:** TCP com mensagens JSON
- **Capacidade:** 2 jogadores simultâneos
- **Features:** 
  - Validação de movimentos
  - Controle de turnos
  - Chat multiplayer
  - Logs detalhados
  - Recuperação de erros

### Cliente (`cliente_avancado.py`)
- **Engine:** Pygame
- **Interface:** Gráfica interativa
- **Comunicação:** Assíncrona com threads
- **Features:**
  - Renderização em tempo real
  - Interface intuitiva
  - Chat integrado
  - Indicadores visuais
  - Tratamento de desconexões

### Protocolo (`protocolo.py`)
- **Formato:** JSON sobre TCP
- **Validação:** Estrutura e tipos de dados
- **Estados:** Enum-based state machine
- **Extensibilidade:** Fácil adição de novos tipos

## 🐛 Solução de Problemas

### Problemas Comuns

**Erro de Conexão Recusada:**
```bash
# Verifique se o servidor está rodando
python servidor_avancado.py

# Teste conectividade
python config_rede.py
```

**Firewall Bloqueando:**
- Windows: Execute `wf.msc` e adicione regra para porta 12345
- Linux: `sudo ufw allow 12345`
- macOS: Preferências > Segurança > Firewall

**Porta Ocupada:**
```bash
# Encontre processo usando a porta
netstat -ano | findstr :12345

# Kill processo se necessário
taskkill /PID <process_id> /F
```

### Logs
- Servidor: `servidor_damas.log`
- Nível: INFO, WARNING, ERROR
- Localização: Pasta do projeto

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📜 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Contato

- **Autor:** Wilson Silva Filho, Anderson Morbeck, Marco Túlio e Hingrid Queiroz
- **GitHub:** [@Wssfilho](https://github.com/Wssfilho)
- **Projeto:** [project-redes](https://github.com/Wssfilho/project-redes)

---

⭐ **Se este projeto te ajudou, considere dar uma estrela!** ⭐
