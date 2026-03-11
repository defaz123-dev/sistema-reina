@echo off
echo --- Generador de Reina Bridge (.exe) ---
echo Instalando dependencias necesarias...
pip install -r requirements_bridge.txt
echo.
echo Compilando archivo ejecutable...
pyinstaller --noconsole --onefile --name "reina_bridge" --icon=NONE reina_bridge.py
echo.
echo --- PROCESO FINALIZADO ---
echo El archivo ejecutable se encuentra en la carpeta 'dist'
pause
