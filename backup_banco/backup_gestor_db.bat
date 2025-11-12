@echo off
ECHO ===================================
ECHO INICIANDO BACKUP AUTOMATICO
ECHO ===================================

:: --- 1. CONFIGURE ESTAS 4 VARIAVEIS ---
:: Pasta ONDE os backups serao guardados (SEM ASPAS)
SET BACKUP_DIR=E:\Meus Documentos\Dropbox\Frank\git_gestor_pme\backup_banco

:: Caminho para os programas do Postgres (SEM ASPAS)
SET PG_BIN_PATH=C:\Program Files\PostgreSQL\17\bin

:: Nome do banco de dados que voce quer copiar
SET DB_NAME=gestor_db

:: Quantos dias de backups quer manter?
SET DAYS_TO_KEEP=7

:: --- 2. PREPARACAO ---
FOR /f "tokens=1-3 delims=/ " %%a IN ('date /t') DO (SET HOJE=%%c-%%b-%%a)
SET FILENAME=%DB_NAME%_%HOJE%.dump
SET BACKUP_PATH=%BACKUP_DIR%\%FILENAME%

ECHO A criar backup de %DB_NAME% para %BACKUP_PATH%...

:: --- 3. O COMANDO DE BACKUP ---
:: As aspas aqui agora funcionam corretamente
"%PG_BIN_PATH%\pg_dump.exe" -U postgres -h localhost -F c -f "%BACKUP_PATH%" %DB_NAME%

IF %ERRORLEVEL% NEQ 0 (
    ECHO !!! ERRO AO GERAR O BACKUP !!!
    GOTO end
)

ECHO Backup de %DB_NAME% concluido com sucesso.

:: --- 4. O COMANDO DE LIMPEZA ---
ECHO A apagar backups com mais de %DAYS_TO_KEEP% dias...
:: As aspas no /p também são importantes por causa dos espaços
forfiles /p "%BACKUP_DIR%" /s /m *.dump /d -%DAYS_TO_KEEP% /c "cmd /c del @path"

ECHO Limpeza concluida.
ECHO ===================================
ECHO SCRIPT DE BACKUP FINALIZADO
ECHO ===================================

:end