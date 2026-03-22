# vaciado_rapido.py
import MySQLdb

config = {'host': 'localhost', 'user': 'root', 'passwd': '', 'db': 'sistema_reina'}

def vaciar():
    try:
        db = MySQLdb.connect(**config)
        cur = db.cursor()
        cur.execute("SET FOREIGN_KEY_CHECKS=0;")
        tablas = [
            'sesiones_caja', 'caja_detalle_fisico', 'cierres_diarios', 
            'cierre_diario_detalle_fisico', 'ventas', 'ventas_pagos', 
            'detalles_ventas', 'egresos', 'flujo_caja', 'auditoria'
        ]
        for t in tablas:
            cur.execute(f"TRUNCATE TABLE {t};")
            print(f"Vaciada: {t}")
        cur.execute("SET FOREIGN_KEY_CHECKS=1;")
        db.commit()
        print(">>> PROCESO COMPLETADO.")
        cur.close()
        db.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    vaciar()
