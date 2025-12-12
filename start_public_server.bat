@echo off
echo ========================================
echo    INICIANDO SERVIDOR PUBLICO
echo ========================================
echo.

echo Verificando se o servidor Django esta rodando...
echo.

echo OPCOES DISPONIVEIS:
echo.
echo 1. Iniciar apenas o servidor Django (localhost)
echo 2. Iniciar servidor + Ngrok (publico)
echo 3. Iniciar servidor + Serveo (publico - sem instalacao)
echo 4. Mostrar instrucoes completas
echo.

set /p choice="Escolha uma opcao (1-4): "

if "%choice%"=="1" goto django_only
if "%choice%"=="2" goto ngrok_setup
if "%choice%"=="3" goto serveo_setup
if "%choice%"=="4" goto instructions
goto invalid

:django_only
echo.
echo Iniciando servidor Django...
echo Acesse: http://localhost:8000
echo Para parar: Ctrl+C
echo.
python manage.py runserver 0.0.0.0:8000
goto end

:ngrok_setup
echo.
echo Verificando ngrok...
where ngrok >nul 2>nul
if %errorlevel% neq 0 (
    echo ERRO: Ngrok nao encontrado!
    echo.
    echo Por favor:
    echo 1. Baixe ngrok em: https://ngrok.com/
    echo 2. Extraia para uma pasta
    echo 3. Adicione a pasta ao PATH do Windows
    echo 4. Configure com: ngrok authtoken SEU_TOKEN
    echo.
    pause
    goto end
)

echo Ngrok encontrado! Iniciando...
echo.
echo IMPORTANTE: Execute este comando em outro terminal:
echo python manage.py runserver 0.0.0.0:8000
echo.
echo Pressione qualquer tecla quando o servidor Django estiver rodando...
pause >nul

echo Criando tunel publico...
ngrok http 8000
goto end

:serveo_setup
echo.
echo Usando Serveo (sem instalacao necessaria)...
echo.
echo IMPORTANTE: Execute este comando em outro terminal:
echo python manage.py runserver 0.0.0.0:8000
echo.
echo Pressione qualquer tecla quando o servidor Django estiver rodando...
pause >nul

echo Criando tunel publico via SSH...
echo Seu link publico aparecera abaixo:
echo.
ssh -R 80:localhost:8000 serveo.net
goto end

:instructions
echo.
echo ========================================
echo           INSTRUCOES COMPLETAS
echo ========================================
echo.
type setup_public_access.md
echo.
pause
goto end

:invalid
echo.
echo Opcao invalida! Tente novamente.
echo.
pause
goto end

:end
echo.
echo Script finalizado.
pause