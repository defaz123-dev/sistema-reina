# clean_db.py
import MySQLdb
import os

config = {
    'host': 'localhost',
    'user': 'root',
    'passwd': '',
    'db': 'sistema_reina'
}

def clean_database():
    db = None
    try:
        db = MySQLdb.connect(host=config['host'], user=config['user'], passwd=config['passwd'], db=config['db'], charset='utf8mb4')
        cur = db.cursor()
        print(">>> PASO 1: Borrando datos transaccionales (Ventas, Turnos, Caja)...")

        cur.execute("SET FOREIGN_KEY_CHECKS=0;")
        
        tablas = [
            'ventas_pagos', 'detalles_ventas', 'anulaciones_factura', 'ventas',
            'egresos', 'detalles_compras', 'compras', 'flujo_caja', 'kardex',
            'caja_detalle_fisico', 'sesiones_caja', 'cierre_diario_detalle_fisico',
            'cierres_diarios', 'auditoria'
        ]
        
        for t in tablas:
            cur.execute(f"TRUNCATE TABLE {t};")
            print(f"  [OK] {t} vaciada.")

        db.commit() # Aseguramos el borrado antes de seguir
        print(">>> PASO 2: Restaurando catálogos desde seed_data.sql...")

        if os.path.exists('seed_data.sql'):
            with open('seed_data.sql', 'r', encoding='utf-8') as f:
                content = f.read()
            
            statements = content.split(';')
            for i, stmt in enumerate(statements):
                sql = stmt.strip()
                if not sql: continue
                
                # Saltar sentencias extremadamente largas (imágenes pesadas) para evitar caídas
                if len(sql) > 100000: 
                    print(f"  [AVISO] Saltando sentencia {i} por tamaño excesivo (Imagen).")
                    continue
                    
                try:
                    cur.execute(sql)
                except Exception as e:
                    print(f"  [!] Error en seed línea {i}: {str(e)[:50]}")
        
        cur.execute("UPDATE sucursales SET ultimo_secuencial = 0;")
        cur.execute("SET FOREIGN_KEY_CHECKS=1;")
        db.commit()
        print("\n>>> LIMPIEZA TOTAL COMPLETADA.")
        
    except Exception as e:
        print(f"\n[!!!] Error crítico: {e}")
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    clean_database()
