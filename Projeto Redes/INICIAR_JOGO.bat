@echo off
title Damas Online - Inicializador
color 0A

echo.
echo ==========================================
echo        🎮 DAMAS ONLINE 🎮
echo      Inicializador Automatico
echo ==========================================
echo.

:: Verifica se Python está disponível
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python nao encontrado!
    echo 💡 Instale Python 3.7+ e tente novamente
    echo.
    pause
    exit /b 1
)

:: Ativa ambiente virtual se existir
if exist "myenv\Scripts\activate.bat" (
    echo 🔧 Ativando ambiente virtual...
    call myenv\Scripts\activate.bat
)

:: Executa o inicializador Python
echo 🚀 Iniciando Damas Online...
echo.
python iniciar_jogo.py

pause
