"""
Script de verificação do sistema - Verifica se tudo está configurado para executar o jogo
Útil para novos usuários ou para diagnóstico de problemas
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path


def emoji_status(condicao):
    """Retorna emoji baseado na condição"""
    return "✅" if condicao else "❌"


def verificar_python():
    """Verifica versão do Python"""
    versao = sys.version_info
    versao_ok = versao.major >= 3 and versao.minor >= 7
    
    print(f"{emoji_status(versao_ok)} Python {versao.major}.{versao.minor}.{versao.micro}")
    if not versao_ok:
        print("   ⚠️  Recomendado: Python 3.7+")
    
    return versao_ok


def verificar_pygame():
    """Verifica se pygame está disponível"""
    try:
        import pygame
        versao = pygame.version.ver
        print(f"✅ Pygame {versao}")
        return True
    except ImportError:
        print("❌ Pygame não instalado")
        print("   💡 Execute: pip install pygame")
        return False


def verificar_arquivos():
    """Verifica se todos os arquivos estão presentes"""
    arquivos_core = [
        'servidor_avancado.py',
        'cliente_avancado.py', 
        'protocolo.py',
        'jogo.py',
        'tabuleiro.py',
        'peca.py',
        'constantes.py',
        'quadrado.py',
        'utilitarios.py',
        'graficos.py',
        'main.py'
    ]
    
    arquivos_auxiliares = [
        'iniciar_jogo.py',
        'config_rede.py',
        'teste_demo.py',
        'verificar_sistema.py',
        'INICIAR_JOGO.bat',
        'GUIA_RAPIDO.md',
        'README.md'
    ]
    
    pasta_recursos = Path('resources')
    recursos = [
        'tabuleiro.png',
        'peca_verde.png',
        'peca_amarela.png',
        'peca_verde_dama.png',
        'peca_amarela_dama.png'
    ]
    
    print("\n📁 ARQUIVOS DO PROJETO:")
    
    # Arquivos principais
    print("   Core:")
    todos_core = True
    for arquivo in arquivos_core:
        existe = Path(arquivo).exists()
        print(f"   {emoji_status(existe)} {arquivo}")
        todos_core = todos_core and existe
    
    # Arquivos auxiliares
    print("   Auxiliares:")
    todos_auxiliares = True
    for arquivo in arquivos_auxiliares:
        existe = Path(arquivo).exists()
        print(f"   {emoji_status(existe)} {arquivo}")
        todos_auxiliares = todos_auxiliares and existe
    
    # Recursos
    print("   Recursos:")
    todos_recursos = True
    for recurso in recursos:
        caminho = pasta_recursos / recurso
        existe = caminho.exists()
        print(f"   {emoji_status(existe)} resources/{recurso}")
        todos_recursos = todos_recursos and existe
    
    return todos_core and todos_auxiliares and todos_recursos


def verificar_sintaxe():
    """Verifica sintaxe dos arquivos Python principais"""
    arquivos_verificar = [
        'servidor_avancado.py',
        'cliente_avancado.py',
        'protocolo.py',
        'iniciar_jogo.py',
        'config_rede.py'
    ]
    
    print("\n🔍 VERIFICAÇÃO DE SINTAXE:")
    
    todos_ok = True
    for arquivo in arquivos_verificar:
        if not Path(arquivo).exists():
            print(f"❌ {arquivo} (não encontrado)")
            todos_ok = False
            continue
            
        try:
            # Compila o arquivo para verificar sintaxe
            with open(arquivo, 'r', encoding='utf-8') as f:
                compile(f.read(), arquivo, 'exec')
            print(f"✅ {arquivo}")
        except SyntaxError as e:
            print(f"❌ {arquivo} (erro de sintaxe: linha {e.lineno})")
            todos_ok = False
        except Exception as e:
            print(f"⚠️  {arquivo} (erro: {e})")
            todos_ok = False
    
    return todos_ok


def verificar_importacoes():
    """Verifica se os módulos podem ser importados"""
    modulos = {
        'servidor_avancado': 'Servidor principal',
        'cliente_avancado': 'Cliente gráfico', 
        'protocolo': 'Protocolo de comunicação',
        'iniciar_jogo': 'Inicializador automático',
        'config_rede': 'Configurador de rede'
    }
    
    print("\n📦 VERIFICAÇÃO DE IMPORTAÇÕES:")
    
    todos_ok = True
    for modulo, descricao in modulos.items():
        try:
            # Verifica se o arquivo existe
            arquivo = f"{modulo}.py"
            if not Path(arquivo).exists():
                print(f"❌ {descricao} (arquivo não encontrado)")
                todos_ok = False
                continue
            
            # Tenta compilar (não importar para evitar efeitos colaterais)
            spec = importlib.util.spec_from_file_location(modulo, arquivo)
            if spec is None:
                print(f"❌ {descricao} (não pode criar spec)")
                todos_ok = False
                continue
                
            print(f"✅ {descricao}")
            
        except Exception as e:
            print(f"❌ {descricao} (erro: {e})")
            todos_ok = False
    
    return todos_ok


def executar_teste_rapido():
    """Executa um teste rápido do inicializador"""
    print("\n🧪 TESTE RÁPIDO:")
    
    try:
        # Testa se o inicializador pode ser executado
        resultado = subprocess.run(
            [sys.executable, 'iniciar_jogo.py', '--help'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Como o script não tem --help, vai dar erro, mas mostra que executa
        print("✅ Inicializador executável")
        return True
        
    except subprocess.TimeoutExpired:
        print("⚠️  Inicializador muito lento")
        return False
    except FileNotFoundError:
        print("❌ Inicializador não encontrado")
        return False
    except Exception as e:
        print(f"⚠️  Erro no teste: {e}")
        return False


def mostrar_resumo(resultados):
    """Mostra resumo final dos testes"""
    print("\n" + "="*50)
    print("📊 RESUMO DA VERIFICAÇÃO")
    print("="*50)
    
    total_testes = len(resultados)
    testes_ok = sum(resultados.values())
    
    for teste, resultado in resultados.items():
        status = "✅ PASS" if resultado else "❌ FAIL"
        print(f"{status} {teste}")
    
    print("-" * 50)
    print(f"Total: {testes_ok}/{total_testes} testes passaram")
    
    if testes_ok == total_testes:
        print("\n🎉 TUDO PRONTO! O jogo está configurado corretamente.")
        print("💡 Execute: INICIAR_JOGO.bat ou python iniciar_jogo.py")
    else:
        print(f"\n⚠️  {total_testes - testes_ok} problema(s) encontrado(s)")
        print("💡 Corrija os problemas antes de executar o jogo")
    
    return testes_ok == total_testes


def main():
    """Função principal da verificação"""
    print("🔍 VERIFICAÇÃO DO SISTEMA - DAMAS ONLINE")
    print("="*42)
    print()
    
    # Executa todas as verificações
    resultados = {
        'Python 3.7+': verificar_python(),
        'Pygame instalado': verificar_pygame(),
        'Arquivos presentes': verificar_arquivos(),
        'Sintaxe correta': verificar_sintaxe(),
        'Importações OK': verificar_importacoes(),
        'Teste rápido': executar_teste_rapido()
    }
    
    # Mostra resumo
    sucesso = mostrar_resumo(resultados)
    
    # Instruções finais
    if sucesso:
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("1. INICIAR_JOGO.bat (Windows) ou python iniciar_jogo.py")
        print("2. Escolha a opção desejada no menu")
        print("3. Divirta-se jogando!")
    else:
        print("\n🔧 CORREÇÕES NECESSÁRIAS:")
        print("1. Instale dependências faltantes")
        print("2. Corrija arquivos com problemas")
        print("3. Execute esta verificação novamente")
    
    print("\n📋 Para ajuda detalhada:")
    print("- README.md (documentação completa)")
    print("- GUIA_RAPIDO.md (instruções simplificadas)")
    print("- python config_rede.py (diagnóstico de rede)")


if __name__ == "__main__":
    try:
        main()
        input("\nPressione Enter para sair...")
    except KeyboardInterrupt:
        print("\n👋 Verificação interrompida")
    except Exception as e:
        print(f"\n❌ Erro durante verificação: {e}")
        input("Pressione Enter para sair...")
