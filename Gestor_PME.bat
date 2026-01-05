@echo off
TITLE GESTOR PME - Servidor Local

:: 1. Garante que o script rode a partir da pasta onde o arquivo .bat está salvo
:: (Isso elimina o risco de errar o caminho do Dropbox se você mover a pasta)
cd /d "%~dp0"

ECHO ==================================================
ECHO       INICIANDO SERVIDOR DO GESTOR PME...
ECHO ==================================================
ECHO.

:: 2. Ativa o Anaconda e o ambiente 'gestor_dev_env'
:: (Ajustado para o ambiente que estamos usando no desenvolvimento novo)
ECHO Ativando ambiente virtual 'gestor_pme_env'...
call "C:\Users\fgerke\anaconda3\Scripts\activate.bat" gestor_pme_env

:: 3. Abre o navegador (espera 3 segundos pro servidor ter tempo de subir)
:: Agora aponta para /gestao/ em vez de /admin/
timeout /t 3 >nul
start http://127.0.0.1:8000/gestao/

:: 4. Inicia o servidor Django
ECHO.
ECHO Servidor rodando! Pressione Ctrl+C para parar.
python manage.py runserver

pause