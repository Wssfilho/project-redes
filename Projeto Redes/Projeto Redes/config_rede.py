"""
Script auxiliar para configuração de rede do jogo de damas online
"""

import socket
import platform
import subprocess
import sys


def obter_ip_local():
    """Obtém o IP local da máquina"""
    try:
        # Método 1: Conecta a um endereço externo
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
        s.close()
        return ip_local
    except:
        return "127.0.0.1"


def obter_todos_ips():
    """Obtém todos os IPs da máquina"""
    ips = []
    try:
        hostname = socket.gethostname()
        # Obtém todos os IPs associados ao hostname
        ip_list = socket.gethostbyname_ex(hostname)[2]
        ips.extend([ip for ip in ip_list if not ip.startswith("127.")])
    except:
        pass
    
    # Adiciona IP principal
    ip_principal = obter_ip_local()
    if ip_principal not in ips:
        ips.insert(0, ip_principal)
    
    return ips


def testar_porta(porta=12345):
    """Testa se a porta está disponível"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('0.0.0.0', porta))
        s.close()
        return True
    except:
        return False


def verificar_firewall():
    """Verifica configurações básicas de firewall"""
    sistema = platform.system()
    
    if sistema == "Windows":
        return verificar_firewall_windows()
    elif sistema == "Linux":
        return verificar_firewall_linux()
    elif sistema == "Darwin":  # macOS
        return verificar_firewall_macos()
    else:
        return "Sistema não suportado para verificação automática"


def verificar_firewall_windows():
    """Verifica firewall do Windows"""
    try:
        # Tenta verificar status do firewall
        result = subprocess.run(['netsh', 'advfirewall', 'show', 'allprofiles', 'state'],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return "Firewall Windows detectado - pode precisar configurar regra para porta 12345"
        else:
            return "Não foi possível verificar firewall automaticamente"
    except:
        return "Erro ao verificar firewall - configure manualmente se necessário"


def verificar_firewall_linux():
    """Verifica firewall do Linux"""
    # Verifica UFW
    try:
        result = subprocess.run(['ufw', 'status'], capture_output=True, text=True, timeout=5)
        if 'Status: active' in result.stdout:
            return "UFW ativo - execute: sudo ufw allow 12345"
    except:
        pass
    
    # Verifica iptables
    try:
        result = subprocess.run(['iptables', '-L'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return "iptables detectado - pode precisar configurar regra"
    except:
        pass
    
    return "Firewall não detectado ou já configurado"


def verificar_firewall_macos():
    """Verifica firewall do macOS"""
    try:
        result = subprocess.run(['/usr/libexec/ApplicationFirewall/socketfilterfw', '--getglobalstate'],
                              capture_output=True, text=True, timeout=5)
        if 'enabled' in result.stdout.lower():
            return "Firewall macOS ativo - pode precisar permitir Python/Terminal"
        else:
            return "Firewall macOS desabilitado"
    except:
        return "Não foi possível verificar firewall do macOS"


def mostrar_informacoes_rede():
    """Mostra informações completas de rede"""
    print("🌐 INFORMAÇÕES DE REDE - DAMAS ONLINE")
    print("=" * 45)
    
    # Sistema operacional
    sistema = platform.system()
    print(f"💻 Sistema: {sistema} {platform.release()}")
    
    # Hostname
    try:
        hostname = socket.gethostname()
        print(f"🏷️  Hostname: {hostname}")
    except:
        print("🏷️  Hostname: Não disponível")
    
    # IPs disponíveis
    print("\n📍 ENDEREÇOS IP:")
    ips = obter_todos_ips()
    
    if ips:
        for i, ip in enumerate(ips, 1):
            print(f"   {i}. {ip}")
        
        ip_recomendado = ips[0]
        print(f"\n✅ IP recomendado para outros PCs: {ip_recomendado}")
    else:
        print("   ❌ Nenhum IP encontrado")
        ip_recomendado = "127.0.0.1"
    
    # Teste de porta
    print(f"\n🔌 TESTE DE PORTA:")
    porta_disponivel = testar_porta(12345)
    if porta_disponivel:
        print("   ✅ Porta 12345 disponível")
    else:
        print("   ❌ Porta 12345 ocupada - tente outra porta")
    
    # Firewall
    print(f"\n🛡️  FIREWALL:")
    status_firewall = verificar_firewall()
    print(f"   {status_firewall}")
    
    # Instruções
    print(f"\n📋 INSTRUÇÕES PARA OUTROS PCs:")
    print(f"   1. Execute: cliente_avancado.py")
    print(f"   2. Digite host: {ip_recomendado}")
    print(f"   3. Digite porta: 12345")
    print(f"   4. Pressione 'C' para conectar")
    
    if sistema == "Windows":
        print(f"\n💡 CONFIGURAÇÃO FIREWALL WINDOWS:")
        print(f"   1. Painel de Controle > Sistema e Segurança > Firewall do Windows")
        print(f"   2. Configurações Avançadas > Regras de Entrada > Nova Regra")
        print(f"   3. Tipo: Porta > TCP > Porta específica: 12345")
        print(f"   4. Ação: Permitir conexão")
    
    elif sistema == "Linux":
        print(f"\n💡 CONFIGURAÇÃO FIREWALL LINUX:")
        print(f"   UFW: sudo ufw allow 12345")
        print(f"   iptables: sudo iptables -A INPUT -p tcp --dport 12345 -j ACCEPT")
    
    elif sistema == "Darwin":
        print(f"\n💡 CONFIGURAÇÃO FIREWALL MACOS:")
        print(f"   Preferências > Segurança > Firewall > Opções")
        print(f"   Permitir aplicações específicas: Python ou Terminal")


def testar_conectividade(host, porta=12345):
    """Testa conectividade com um servidor"""
    print(f"\n🔍 TESTANDO CONEXÃO COM {host}:{porta}")
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        resultado = s.connect_ex((host, porta))
        s.close()
        
        if resultado == 0:
            print("   ✅ Conexão bem-sucedida!")
            return True
        else:
            print("   ❌ Conexão falhou")
            print(f"   💡 Verifique se o servidor está rodando em {host}:{porta}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
        return False


def menu_principal():
    """Menu principal das ferramentas de rede"""
    while True:
        print("\n🌐 FERRAMENTAS DE REDE - DAMAS ONLINE")
        print("=" * 40)
        print("1. 📊 Mostrar informações de rede")
        print("2. 🔍 Testar conectividade")
        print("3. 💡 Mostrar instruções de firewall")
        print("4. 📋 Gerar comando para outros PCs")
        print("0. ❌ Sair")
        
        try:
            opcao = input("\nEscolha uma opção: ").strip()
            
            if opcao == '1':
                mostrar_informacoes_rede()
            
            elif opcao == '2':
                host = input("Digite o IP do servidor: ").strip()
                porta_input = input("Digite a porta (Enter = 12345): ").strip()
                porta = int(porta_input) if porta_input else 12345
                testar_conectividade(host, porta)
            
            elif opcao == '3':
                mostrar_instrucoes_firewall()
            
            elif opcao == '4':
                gerar_comando_clientes()
            
            elif opcao == '0':
                print("👋 Até logo!")
                break
            
            else:
                print("❌ Opção inválida")
                
        except KeyboardInterrupt:
            print("\n👋 Até logo!")
            break
        except ValueError:
            print("❌ Por favor, digite um número válido")
        except Exception as e:
            print(f"❌ Erro: {e}")


def mostrar_instrucoes_firewall():
    """Mostra instruções detalhadas de firewall"""
    sistema = platform.system()
    
    print(f"\n🛡️  INSTRUÇÕES DE FIREWALL - {sistema}")
    print("=" * 40)
    
    if sistema == "Windows":
        print("""
📋 WINDOWS FIREWALL:

Método 1 - Interface Gráfica:
1. Pressione Win + R, digite 'wf.msc'
2. Clique em 'Regras de Entrada' 
3. 'Nova Regra' > Porta > TCP > 12345
4. Permitir a conexão > Aplicar a todos os perfis
5. Nome: "Damas Online"

Método 2 - Linha de Comando (Admin):
netsh advfirewall firewall add rule name="Damas Online" dir=in action=allow protocol=TCP localport=12345

Método 3 - PowerShell (Admin):
New-NetFirewallRule -DisplayName "Damas Online" -Direction Inbound -Protocol TCP -LocalPort 12345 -Action Allow
""")
    
    elif sistema == "Linux":
        print("""
📋 LINUX FIREWALL:

UFW (Ubuntu/Debian):
sudo ufw allow 12345
sudo ufw status

iptables (Geral):
sudo iptables -A INPUT -p tcp --dport 12345 -j ACCEPT
sudo iptables -L

firewalld (CentOS/RHEL):
sudo firewall-cmd --permanent --add-port=12345/tcp
sudo firewall-cmd --reload
""")
    
    elif sistema == "Darwin":
        print("""
📋 MACOS FIREWALL:

Interface Gráfica:
1. Apple Menu > Preferências do Sistema
2. Segurança e Privacidade > Firewall
3. Opções do Firewall
4. Adicionar aplicação: Python ou Terminal
5. Permitir conexões de entrada

Linha de Comando:
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off
(Desabilita firewall - use com cuidado)
""")
    
    else:
        print("Sistema não reconhecido. Configure o firewall manualmente.")


def gerar_comando_clientes():
    """Gera comandos para os clientes"""
    ip_local = obter_ip_local()
    
    print(f"\n📋 COMANDOS PARA OUTROS PCs")
    print("=" * 30)
    print(f"📍 IP do servidor: {ip_local}")
    print(f"🔌 Porta: 12345")
    
    print(f"\n💻 Para conectar de outro PC:")
    print(f"   1. Copie os arquivos do jogo para o outro PC")
    print(f"   2. Execute: python cliente_avancado.py")
    print(f"   3. Digite host: {ip_local}")
    print(f"   4. Digite porta: 12345")
    
    print(f"\n📋 Ou use este comando direto:")
    print(f"   python cliente_avancado.py")
    print(f"   (Na interface, conecte com {ip_local}:12345)")


if __name__ == "__main__":
    try:
        menu_principal()
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        input("Pressione Enter para sair...")
