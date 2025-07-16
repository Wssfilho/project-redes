"""
Script de inicialização automática para o jogo de damas online
Simplifica o processo de configuração e início do jogo
"""

import os
import sys
import time
import subprocess
import socket
import threading
from pathlib import Path


def obter_ip_local():
    """Obtém o IP local da máquina"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
        s.close()
        return ip_local
    except:
        return "127.0.0.1"


def verificar_arquivos():
    """Verifica se todos os arquivos necessários estão presentes"""
    arquivos_necessarios = [
        'servidor_avancado.py',
        'cliente_avancado.py',
        'protocolo.py',
        'jogo.py',
        'tabuleiro.py',
        'peca.py',
        'constantes.py'
    ]
    
    arquivos_faltando = []
    for arquivo in arquivos_necessarios:
        if not Path(arquivo).exists():
            arquivos_faltando.append(arquivo)
    
    return arquivos_faltando


def verificar_pygame():
    """Verifica se pygame está instalado"""
    try:
        import pygame
        return True
    except ImportError:
        return False


def instalar_pygame():
    """Instala pygame automaticamente"""
    print("🔧 Instalando pygame...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pygame'])
        print("✅ Pygame instalado com sucesso!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar pygame")
        return False


def iniciar_servidor(ip='0.0.0.0', porta=12345):
    """Inicia o servidor em uma thread separada"""
    def run_servidor():
        try:
            subprocess.run([sys.executable, 'servidor_avancado.py'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao iniciar servidor: {e}")
        except KeyboardInterrupt:
            print("🛑 Servidor interrompido pelo usuário")
    
    thread_servidor = threading.Thread(target=run_servidor, daemon=True)
    thread_servidor.start()
    return thread_servidor


def iniciar_cliente():
    """Inicia o cliente"""
    try:
        subprocess.run([sys.executable, 'cliente_avancado.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao iniciar cliente: {e}")
    except KeyboardInterrupt:
        print("🛑 Cliente interrompido pelo usuário")


def mostrar_menu_principal():
    """Mostra o menu principal de opções"""
    ip_local = obter_ip_local()
    
    print("🎮 DAMAS ONLINE - INICIALIZADOR AUTOMÁTICO")
    print("=" * 45)
    print(f"📍 IP local: {ip_local}")
    print(f"🔌 Porta padrão: 12345")
    print()
    print("Escolha uma opção:")
    print("1. 🖥️  Iniciar servidor + cliente (PC local)")
    print("2. 🌐 Iniciar apenas servidor (para rede)")
    print("3. 👤 Iniciar apenas cliente (conectar a servidor)")
    print("4. 🔧 Configurações e diagnósticos")
    print("5. 📋 Instruções de uso")
    print("0. ❌ Sair")
    print()


def mostrar_instrucoes():
    """Mostra instruções detalhadas"""
    ip_local = obter_ip_local()
    
    print("\n📋 INSTRUÇÕES DE USO")
    print("=" * 30)
    print()
    print("🏠 PARA JOGAR NO MESMO PC:")
    print("   1. Escolha opção 1 (servidor + cliente)")
    print("   2. Aguarde servidor iniciar")
    print("   3. Cliente abrirá automaticamente")
    print("   4. Pressione 'C' para conectar")
    print()
    print("🌐 PARA JOGAR EM REDE:")
    print("   📡 No PC servidor:")
    print("   1. Escolha opção 2 (apenas servidor)")
    print("   2. Compartilhe seu IP com outros jogadores")
    print()
    print("   👤 Nos PCs clientes:")
    print("   1. Execute este script")
    print("   2. Escolha opção 3 (apenas cliente)")
    print("   3. Digite IP do servidor quando solicitado")
    print("   4. Pressione 'C' para conectar")
    print()
    print(f"🔗 ENDEREÇO PARA OUTROS PCs: {ip_local}:12345")
    print()
    print("🎯 CONTROLES DO JOGO:")
    print("   - Click: Selecionar e mover peças")
    print("   - C: Conectar ao servidor")
    print("   - T: Abrir chat")
    print("   - H: Mostrar coordenadas")
    print("   - ESC: Sair")
    print()


def executar_diagnosticos():
    """Executa diagnósticos de rede"""
    try:
        print("🔍 Executando diagnósticos de rede...")
        subprocess.run([sys.executable, 'config_rede.py'], check=True)
    except FileNotFoundError:
        print("❌ Arquivo config_rede.py não encontrado")
        print("💡 Execute o diagnóstico manual:")
        ip_local = obter_ip_local()
        print(f"   IP local: {ip_local}")
        print(f"   Porta: 12345")
        print(f"   Configure firewall para permitir porta 12345")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar diagnósticos: {e}")


def main():
    """Função principal"""
    print("🚀 Iniciando Damas Online...")
    
    # Verificar arquivos necessários
    arquivos_faltando = verificar_arquivos()
    if arquivos_faltando:
        print(f"❌ Arquivos necessários não encontrados:")
        for arquivo in arquivos_faltando:
            print(f"   - {arquivo}")
        print("💡 Certifique-se de estar na pasta correta do projeto")
        input("Pressione Enter para sair...")
        return
    
    # Verificar pygame
    if not verificar_pygame():
        print("❌ Pygame não encontrado")
        resposta = input("Instalar pygame automaticamente? (s/n): ").lower()
        if resposta in ['s', 'sim', 'y', 'yes']:
            if not instalar_pygame():
                print("❌ Não foi possível instalar pygame")
                input("Pressione Enter para sair...")
                return
        else:
            print("💡 Instale pygame manualmente: pip install pygame")
            input("Pressione Enter para sair...")
            return
    
    # Menu principal
    while True:
        try:
            print("\n" + "="*50)
            mostrar_menu_principal()
            
            opcao = input("Digite sua escolha: ").strip()
            
            if opcao == '1':
                print("🖥️  Iniciando servidor + cliente...")
                print("⏳ Aguarde alguns segundos para o servidor inicializar...")
                
                # Inicia servidor
                thread_servidor = iniciar_servidor()
                time.sleep(3)  # Aguarda servidor inicializar
                
                print("🎮 Iniciando cliente...")
                iniciar_cliente()
                
            elif opcao == '2':
                print("🌐 Iniciando servidor para rede...")
                ip_local = obter_ip_local()
                print(f"📍 Servidor será acessível em: {ip_local}:12345")
                print("🔗 Compartilhe este endereço com outros jogadores")
                print("🛑 Pressione Ctrl+C para parar o servidor")
                
                try:
                    subprocess.run([sys.executable, 'servidor_avancado.py'], check=True)
                except KeyboardInterrupt:
                    print("\n🛑 Servidor interrompido")
                
            elif opcao == '3':
                print("👤 Iniciando cliente...")
                ip_servidor = input("Digite o IP do servidor (Enter = localhost): ").strip()
                if not ip_servidor:
                    ip_servidor = "localhost"
                print(f"🔗 Conectando a: {ip_servidor}:12345")
                iniciar_cliente()
                
            elif opcao == '4':
                executar_diagnosticos()
                
            elif opcao == '5':
                mostrar_instrucoes()
                
            elif opcao == '0':
                print("👋 Até logo!")
                break
                
            else:
                print("❌ Opção inválida! Digite um número de 0 a 5.")
                
        except KeyboardInterrupt:
            print("\n👋 Até logo!")
            break
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            input("Pressione Enter para continuar...")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        input("Pressione Enter para sair...")
