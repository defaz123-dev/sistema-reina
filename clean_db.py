import MySQLdb
import os

DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'passwd': os.environ.get('MYSQL_PASSWORD', ''),
    'db': os.environ.get('MYSQL_DB', 'sistema_reina'),
    'port': int(os.environ.get('MYSQL_PORT', 3306))
}

def clean_database():
    try:
        db = MySQLdb.connect(**DB_CONFIG)
        cursor = db.cursor()
        print("Conectado a la base de datos...")

        # Desactivar verificación de claves foráneas
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

        # Tablas Transaccionales a vaciar (Trunca y reinicia AUTO_INCREMENT)
        tablas_a_vaciar = [
            'detalles_ventas',
            'ventas',
            'detalles_compras',
            'compras',
            'egresos',
            'flujo_caja',
            'sesiones_caja',
            'cierres_diarios',
            'auditoria',
            'ajustes_inventario'
        ]

        print("Vaciando tablas transaccionales...")
        for tabla in tablas_a_vaciar:
            try:
                cursor.execute(f"TRUNCATE TABLE {tabla};")
                print(f" - {tabla} vaciada.")
            except Exception as e:
                print(f" - Error al vaciar {tabla}: {e}")

        # Reiniciar el stock de los insumos a 0
        print("Reiniciando stock de insumos a 0...")
        cursor.execute("UPDATE insumos SET stock_actual = 0;")
        
        # Reiniciar los secuenciales de las sucursales
        print("Reiniciando secuenciales de sucursales...")
        cursor.execute("UPDATE sucursales SET ultimo_secuencial = 0;")

        # Opcional: Eliminar clientes de prueba excepto el Consumidor Final (id=1)
        # Si quieres conservarlos, comenta estas dos líneas
        print("Limpiando clientes (manteniendo Consumidor Final)...")
        cursor.execute("DELETE FROM clientes WHERE id != 1;")
        cursor.execute("ALTER TABLE clientes AUTO_INCREMENT = 2;")

        # Reactivar verificación de claves foráneas
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        
        db.commit()
        print("\n✅ Base de datos local limpiada exitosamente. Lista para pruebas desde cero.")
        
        cursor.close()
        db.close()
    except Exception as e:
        print(f"❌ Error crítico: {str(e)}")

if __name__ == "__main__":
    clean_database()
