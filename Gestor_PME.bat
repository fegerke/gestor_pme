@echo off
ECHO ==================================================
ECHO       INICIANDO SERVIDOR DO GESTOR PME...
ECHO ==================================================

:: 1. Ativa o Anaconda (usando o caminho que você forneceu)
call C:\Users\fgerke\anaconda3\Scripts\activate.bat C:\Users\fgerke\anaconda3

:: 2. Ativa o ambiente virtual específico
ECHO Ativando ambiente 'gestor_env'...
call conda activate gestor_env

:: 3. Muda para o drive correto
ECHO Mudando para o Drive E:
E:

:: 4. Navega para a pasta exata do projeto
ECHO Acessando a pasta do projeto...
cd "E:\Meus Documentos\Dropbox\Frank\git_gestor_pme"

:: 5. Inicia o navegador na tela de admin (o & no final faz ele rodar em paralelo)
ECHO Abrindo o navegador em http://127.0.0.1:8000/admin/
start http://127.0.0.1:8000/admin/

:: 6. Finalmente, liga o servidor Django
ECHO Servidor iniciado. Pressione Ctrl+C para desligar.
python manage.py runserver