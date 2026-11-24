@echo off
REM Lanzador de la Interfaz Gráfica del Gestor Seguro

echo ====================================
echo   🔐 GESTOR SEGURO DE CONTRASEÑAS
echo      Interfaz Gráfica
echo ====================================
echo.

REM Activar entorno virtual y ejecutar
call .venv\Scripts\activate
python main_gui.py

pause
