@echo off
title NASDAQ Magnificent Seven Tracker
echo.
echo ========================================
echo   NASDAQ Magnificent Seven Tracker
echo ========================================
echo.
echo Iniciando aplicacion...
echo.
echo La web se abrira en: http://localhost:8501
echo.
echo Presiona Ctrl+C para detener el servidor
echo.
cd /d "%~dp0"
python -m streamlit run app.py --server.headless true
pause
