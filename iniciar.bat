@echo off
REM Script para iniciar o Visualizador ITBI no Windows

echo.
echo ======================================
echo   Visualizador de Precos ITBI - RJ
echo ======================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo.
    echo Instale Python de: https://www.python.org/downloads/
    echo Certifique-se de marcar "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

REM Procurar porta disponível
set PORT=8888
:check_port
netstat -ano | findstr :%PORT% >nul 2>&1
if not errorlevel 1 (
    set /a PORT=%PORT%+1
    goto check_port
)

echo [INFO] Porta: %PORT%
echo.

REM Iniciar servidor
echo [INFO] Iniciando servidor local...
echo.
start http://localhost:%PORT%/itbi_visualizer.html
timeout /t 2 /nobreak

REM Mostrar informações
echo.
echo ======================================
echo   SERVIDOR INICIADO COM SUCESSO!
echo ======================================
echo.
echo [URL] http://localhost:%PORT%/itbi_visualizer.html
echo.
echo [DICAS]
echo  - A janela do navegador deve abrir automaticamente
echo  - Se nao abrir, copie a URL acima e abra manualmente
echo  - Deixe esta janela aberta enquanto usar a ferramenta
echo  - Feche a janela (X) para parar o servidor
echo.
python -m http.server %PORT%
