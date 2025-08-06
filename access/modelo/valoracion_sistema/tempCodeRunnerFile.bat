@echo off
echo ========================================
echo   SISTEMA DE VALORACION DE SOFTWARE
echo   Version 1.0 - Colombia 2025
echo ========================================
echo.

echo [1/3] Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python no encontrado. Instale Python 3.8+
    pause
    exit /b 1
)

echo.
echo [2/3] Instalando dependencias...
pip install Flask Flask-CORS
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron instalar las dependencias
    pause
    exit /b 1
)

echo.
echo [3/3] Iniciando servidor...
echo.
echo ========================================
echo   SISTEMA INICIADO CORRECTAMENTE
echo   Acceso: http://localhost:5000
echo   Presione Ctrl+C para detener
echo ========================================
echo.

cd backend
python app.py

pause
