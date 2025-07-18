# 🎮 Jogo de Damas Online

Um jogo de damas multiplayer desenvolvido em Python com interface gráfica usando Pygame, suportando jogos locais e em rede.

#### DESENVOLVIDO POR Anderson Morbeck, Hingrid Querioz, Marco Túlio Macedo e Wilson Filho

## 📋 Índice
- [Propósito do Software](#-propósito-do-software)
- [Funcionamento do Software](#-funcionamento-do-software)
- [Características](#-características)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Como Executar](#-como-executar)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Documentação do Protocolo](#-documentação-do-protocolo)
- [Motivação da Escolha do Protocolo de Transporte](#-motivação-da-escolha-do-protocolo-de-transporte)
- [Controles do Jogo](#-controles-do-jogo)
- [Configuração de Rede](#-configuração-de-rede)
- [Arquivos Principais](#-arquivos-principais)
- [Solução de Problemas](#-solução-de-problemas)

## 🎯 Propósito do Software

Este software foi desenvolvido para proporcionar uma experiência clássica e acessível do jogo de damas, com suporte a partidas locais e online, promovendo o entretenimento e a interação entre jogadores, seja no mesmo computador ou via rede local/internet.

## 🕹️ Funcionamento do Software

O software é composto por dois componentes principais:

### Servidor:
Responsável por manter o estado do jogo, validar os movimentos, sincronizar os jogadores conectados e gerenciar a comunicação de rede.

### Cliente:
Apresenta a interface gráfica ao usuário, recebe os comandos de movimentação, exibe o tabuleiro e peças, além do chat integrado, enviando e recebendo mensagens do servidor para manter o jogo sincronizado.

A comunicação é feita via sockets TCP usando o protocolo de aplicação personalizado para troca de mensagens JSON.

## ✨ Características

- 🎯 **Jogo de damas clássico** com regras tradicionais
- 🌐 **Multiplayer online** - jogue pela internet ou rede local
- 🖥️ **Interface gráfica moderna** com Pygame
- 🎨 **Recursos visuais avançados** - imagens personalizadas para peças e tabuleiro
- 💬 **Sistema de chat integrado** para comunicação entre jogadores
- 🔧 **Instalação automática** de dependências
- 📊 **Sistema de diagnóstico** para verificar problemas
- 🎮 **Controles intuitivos** - clique para selecionar e mover

## 🔧 Pré-requisitos

- **Python 3.7+** (recomendado Python 3.8 ou superior)
- **Pygame** (será instalado automaticamente)
- **Conexão de rede** (para jogos online)

## 📥 Instalação

1. **Clone ou baixe o repositório:**
   ```bash
   git clone https://github.com/Wssfilho/project-redes.git
   cd project-redes
   ```

2. **Verifique se tudo está funcionando:**
   ```bash
   python scr/verificar_sistema.py
   ```

3. **Pronto!** O pygame será instalado automaticamente quando necessário.

## 🚀 Como Executar

### Método Recomendado (Automático)

Execute o inicializador principal que cuida de tudo:

```bash
python scr/iniciar_jogo.py
```

Este comando irá:
- ✅ Verificar se todos os arquivos estão presentes
- ✅ Instalar pygame automaticamente se necessário
- ✅ Mostrar menu com opções de execução
- ✅ Gerenciar servidor e cliente automaticamente

### Opções do Menu Principal

Quando executar o inicializador, você verá estas opções:

```
🎮 === DAMAS ONLINE ===

1. 🖥️  Servidor + Cliente (mesmo PC)
2. 🌐 Apenas Servidor (para rede) 
3. 👤 Apenas Cliente (conectar a servidor)
4. 📋 Instruções detalhadas
5. ❌ Sair
```

### Para Jogar no Mesmo Computador

1. Escolha **opção 1**
2. O servidor iniciará automaticamente
3. O cliente abrirá em seguida
4. Pressione **'C'** no cliente para conectar
5. Comece a jogar!

### Para Jogar em Rede

**No computador que será o servidor:**
1. Execute: `python scr/iniciar_jogo.py`
2. Escolha **opção 2** (Apenas Servidor)
3. Anote o IP mostrado (ex: `192.168.1.100:12345`)
4. Compartilhe esse IP com outros jogadores

**Nos computadores clientes:**
1. Execute: `python scr/iniciar_jogo.py`
2. Escolha **opção 3** (Apenas Cliente)
3. Digite o IP do servidor quando solicitado
4. Pressione **'C'** para conectar

### Execução Manual (Alternativa)

Se preferir executar manualmente:

```bash
# Para o servidor (em um terminal):
python scr/servidor_avancado.py

# Para o cliente (em outro terminal):
python scr/cliente_avancado.py
```

###  Informações Principais Trocadas
🎮 Estado do Jogo
Tabuleiro completo: Posição de todas as peças no jogo
Turno atual: Qual jogador deve jogar agora
Estatísticas: Número de peças e damas de cada cor
👤 Informações dos Jogadores
Nome do jogador: Identificação de cada cliente
Cor atribuída: Verde ou amarela
Status da conexão: Conectado/desconectado
🔄 Movimentos
Origem e destino: Coordenadas do movimento realizado
Tipo de movimento: Movimento simples ou captura
Validação: Se o movimento foi aceito ou rejeitado
💬 Comunicação
Mensagens de chat: Texto enviado entre jogadores
Notificações do sistema: Avisos sobre o jogo
Mensagens de erro: Quando algo dá errado

## 📁 Estrutura do Projeto

```
project-redes/
├── scr/                          # Código fonte principal
│   ├── iniciar_jogo.py          # 🚀 ARQUIVO PRINCIPAL - Execute este!
│   ├── servidor_avancado.py     # Servidor de jogo
│   ├── cliente_avancado.py      # Cliente gráfico
│   ├── protocolo.py             # Protocolo de comunicação
│   ├── jogo.py                  # Lógica principal do jogo
│   ├── tabuleiro.py             # Gerenciamento do tabuleiro
│   ├── peca.py                  # Classe das peças
│   ├── graficos.py              # Interface gráfica
│   ├── constantes.py            # Configurações do jogo
│   ├── utilitarios.py           # Funções auxiliares
│   ├── config_rede.py           # Configurações de rede
│   └── verificar_sistema.py     # Script de diagnóstico
└── resources/                    # Recursos visuais (opcional)
    ├── tabuleiro.png            # Imagem do tabuleiro
    ├── peca_verde.png           # Peça verde normal
    ├── peca_amarela.png         # Peça amarela normal
    ├── peca_verde_dama.png      # Dama verde
    ├── peca_amarela_dama.png    # Dama amarela
    └── icon.png                 # Ícone da janela
```
## 📚 Documentação do Protocolo

### Protocolo de Transporte: TCP

O software utiliza o protocolo TCP para comunicação, conforme evidenciado no código-fonte:

- **Tipo de Socket:** `socket.SOCK_STREAM` (implementa TCP)
- **Família de Endereço:** `socket.AF_INET` (IPv4)

**Isso pode ser conferido nos arquivos:**

- **No Servidor (`servidor_avancado.py`)**:
  ```python
  # linha 97
  self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  ```

- **No Cliente (`cliente_avancado.py`)**:
  ```python
  # linha 89
  self.socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  ```

### Protocolo de Aplicação Personalizado

Além do TCP, foi implementado um protocolo de aplicação personalizado definido no arquivo `protocolo.py`, que inclui:

- Tipos de mensagem definidos no `enum TipoMensagem`
- Formato de mensagem: **JSON com delimitador `\n`**
- Validação de mensagens por meio da classe `ProtocoloDamas`
- Códigos de erro padronizados na classe `CodigosErro`

### Características da Comunicação

- **Porta padrão:** `12345`
- **Formato das mensagens:** JSON + quebra de linha (`\n`)
- **Comunicação bidirecional:** cliente e servidor podem enviar mensagens
- **Controle de turno** implementado no protocolo de aplicação
- **Chat integrado** para mensagens entre jogadores

## 🧠 Motivação da Escolha do Protocolo de Transporte

O protocolo TCP foi escolhido por oferecer:

- ✅ **Confiabilidade** — garante a entrega das mensagens
- ✅ **Ordem** — mensagens chegam na sequência correta
- ✅ **Controle de fluxo** — importante para o funcionamento correto do jogo em turnos

Essas características asseguram a integridade e sincronização da partida, tornando TCP a melhor opção para a comunicação entre cliente e servidor neste jogo de damas online.

## 🎮 Controles do Jogo

### Durante o Jogo
- **Click do mouse**: Selecionar e mover peças
- **C**: Conectar ao servidor
- **T**: Abrir/fechar chat
- **H**: Mostrar/ocultar coordenadas do tabuleiro
- **ESC**: Sair do jogo

### No Chat
- **Enter**: Enviar mensagem
- **ESC**: Fechar chat

## 🌐 Configuração de Rede

### Portas Utilizadas
- **Porta padrão**: 12345
- **Protocolo**: TCP

### Configurações de Firewall
Se tiver problemas de conexão, certifique-se de que a porta 12345 está liberada no firewall.

### Para Jogos pela Internet
1. Configure port forwarding no seu roteador (porta 12345)
2. Use seu IP público externo
3. Certifique-se de que o firewall permite conexões

## 📄 Arquivos Principais

| Arquivo | Descrição |
|---------|-----------|
| `iniciar_jogo.py` | **Arquivo principal** - Execute este para começar |
| `servidor_avancado.py` | Servidor do jogo com suporte a múltiplos clientes |
| `cliente_avancado.py` | Cliente gráfico com interface rica |
| `protocolo.py` | Protocolo de comunicação cliente-servidor |
| `jogo.py` | Lógica principal do jogo de damas |
| `graficos.py` | Sistema de renderização gráfica |
| `verificar_sistema.py` | Script de diagnóstico do sistema |

## 🛠️ Solução de Problemas

### Problema: "Pygame não encontrado"
**Solução**: Execute o inicializador que instalará automaticamente:
```bash
python scr/iniciar_jogo.py
```

### Problema: "Não consigo conectar ao servidor"
**Soluções**:
1. Verifique se o servidor está rodando
2. Confirme o IP e porta corretos
3. Verifique configurações do firewall
4. Teste primeiro no mesmo computador

### Problema: "Arquivos não encontrados"
**Solução**: Certifique-se de estar na pasta raiz do projeto:
```bash
cd project-redes
python scr/iniciar_jogo.py
```

### Problema: "Erro de sintaxe ou importação"
**Solução**: Execute o diagnóstico completo:
```bash
python scr/verificar_sistema.py
```

### Problema: "Jogo está lento"
**Soluções**:
1. Feche outros programas
2. Verifique se tem Python 3.8+ instalado
3. Reinstale pygame: `pip install --upgrade pygame`

### Recursos Visuais Opcionais
As imagens na pasta `resources/` são opcionais. Se não estiverem presentes, o jogo usará desenhos geométricos simples.

## 🎯 Dicas de Uso

1. **Primeiro uso**: Sempre execute `iniciar_jogo.py` primeiro
2. **Rede local**: Use a opção "Servidor + Cliente" para testes
3. **Problemas**: Execute `verificar_sistema.py` para diagnóstico
4. **Performance**: Mantenha apenas um cliente por computador

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir melhorias
- Enviar pull requests

## 📞 Suporte

Se encontrar problemas:
1. Execute primeiro: `python scr/verificar_sistema.py`
2. Verifique se está na pasta correta do projeto
3. Certifique-se de ter Python 3.7+ instalado
4. Conecte com os desenvolvedores: Anderson Morbeck, Hingrid Querioz, Marco Túlio Macedo e Wilson Filho
---

**🎮 Divirta-se jogando damas online!**







