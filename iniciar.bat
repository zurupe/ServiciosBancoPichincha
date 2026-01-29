@echo off
REM ========================================
REM Banco Pichincha - Script de Inicio
REM Inicia los 3 servicios en terminales separadas
REM ========================================

echo.
echo ========================================
echo   BANCO PICHINCHA - SISTEMA BANCARIO
echo ========================================
echo.

REM Verificar que estamos en el directorio correcto
if not exist "services_api\app.py" (
    echo ERROR: Ejecutar este script desde el directorio raiz del proyecto
    echo        ProyectoIntegradorGr5\
    pause
    exit /b 1
)

echo Iniciando servicios...
echo.

REM 1. Iniciar API de Servicios (Puerto 5002)
echo [1/3] Iniciando API de Servicios (Puerto 5002)...
start "API Servicios - 5002" cmd /k "cd /d %~dp0services_api && python app.py"

REM Esperar un momento
timeout /t 3 /nobreak >nul

REM 2. Iniciar Backend (Puerto 5001)
echo [2/3] Iniciando Backend (Puerto 5001)...
start "Backend - 5001" cmd /k "cd /d %~dp0backend && python app.py"

REM Esperar un momento
timeout /t 3 /nobreak >nul

REM 3. Iniciar Frontend (Puerto 5000)
echo [3/3] Iniciando Frontend (Puerto 5000)...
start "Frontend - 5000" cmd /k "cd /d %~dp0frontend && python app.py"

echo.
echo ========================================
echo   SERVICIOS INICIADOS
echo ========================================
echo.
echo   Frontend:     http://localhost:5000
echo   Backend:      http://localhost:5001
echo   API Servicios: http://localhost:5002
echo.
echo   Abre tu navegador en: http://localhost:5000
echo.
echo ========================================
echo.
pause
