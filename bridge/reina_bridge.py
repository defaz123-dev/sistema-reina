# bridge/reina_bridge.py
import os
import sys
import threading
import socket
from flask import Flask, jsonify
from flask_cors import CORS
import win32print
import win32api
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

# Configuración
APP_NAME = "Reina Bridge"
PORT = 5001
VERSION = "1.0.0"

app = Flask(__name__)
CORS(app) # Permitir que el Sistema Reina en la nube se conecte

def get_pos_printer():
    """Busca automáticamente una impresora POS en el sistema."""
    try:
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        
        # Palabras clave para identificar impresoras térmicas
        keywords = ["POS", "80mm", "58mm", "TICKET", "EPSON", "ZJIANG", "TERMIC"]
        
        # 1. Buscar por palabras clave
        for (_, _, name, _) in printers:
            if any(kw in name.upper() for kw in keywords):
                return name, True
                
        # 2. Si no hay coincidencias, informar que no se halló impresora específica
        return None, False
    except Exception:
        return None, False

def open_cash_drawer(printer_name):
    """Envía el pulso ESC/POS para abrir el cajón."""
    try:
        # Comando estándar ESC/POS para apertura de cajón: ESC p m t1 t2
        # \x1b\x70\x00\x19\xfa (Abre el pin 2)
        # Algunos drivers aceptan \x07 (Pulse)
        COMMAND = b"\x1b\x70\x00\x19\xfa"
        
        handle = win32print.OpenPrinter(printer_name)
        try:
            job = win32print.StartDocPrinter(handle, 1, ("Abrir Cajon", None, "RAW"))
            win32print.StartPagePrinter(handle)
            win32print.WritePrinter(handle, COMMAND)
            win32print.EndPagePrinter(handle)
            win32print.EndDocPrinter(handle)
        finally:
            win32print.ClosePrinter(handle)
        return True, f"Cajón abierto en: {printer_name}"
    except Exception as e:
        return False, str(e)

@app.route('/status', methods=['GET'])
def status():
    printer, found = get_pos_printer()
    return jsonify({
        "status": "online",
        "app": APP_NAME,
        "version": VERSION,
        "detected_printer": printer if found else "NINGUNA DETECTADA"
    })

@app.route('/abrir-caja', methods=['GET'])
def trigger_open():
    printer, found = get_pos_printer()
    if not found:
        return jsonify({
            "success": False, 
            "error": "No se detectó ninguna impresora térmica (POS) instalada. Por favor, asegúrese de que el nombre de su impresora contenga 'POS', 'TICKET' o '80mm' en el Panel de Control."
        }), 404
    
    success, msg = open_cash_drawer(printer)
    return jsonify({"success": success, "message": msg})

def create_image():
    # Generar un icono simple (Una corona amarilla)
    width = 64
    height = 64
    color1 = "yellow"
    color2 = "black"
    image = Image.new('RGB', (width, height), color2)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 4, height // 4, width * 3 // 4, height * 3 // 4), fill=color1)
    return image

def on_quit(icon, item):
    icon.stop()
    os._exit(0)

def run_server():
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

def setup_tray():
    image = create_image()
    menu = Menu(
        MenuItem(f"{APP_NAME} v{VERSION}", lambda: None, enabled=False),
        MenuItem("Estado: Activo", lambda: None, enabled=False),
        MenuItem("Salir", on_quit)
    )
    icon = Icon(APP_NAME, image, APP_NAME, menu)
    icon.run()

if __name__ == "__main__":
    # Ejecutar servidor en un hilo aparte
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Mantener el icono en el hilo principal
    print(f"{APP_NAME} ejecutándose en el puerto {PORT}")
    print(f"Impresora detectada: {get_pos_printer()}")
    setup_tray()
