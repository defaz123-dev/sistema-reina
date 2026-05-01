@echo off
echo ===================================================
echo   COMPILADOR REINA BRIDGE - MODO SEGURIDAD (NUITKA)
echo ===================================================
echo.
echo [1/3] Instalando/Actualizando Nuitka y dependencias...
pip install nuitka zstandard --quiet

echo.
echo [2/3] Iniciando compilacion... (Esto puede tardar varios minutos)
echo La logica de seguridad HWID sera ofuscada y compilada a C++
echo.

python -m nuitka --standalone --onefile --windows-disable-console --output-dir=dist_nuitka reina_bridge.py

echo.
echo [3/3] Proceso finalizado. 
echo El archivo 'reina_bridge.exe' se encuentra en 'dist_nuitka'
echo.
pause
