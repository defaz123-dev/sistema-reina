import MySQLdb
import os

DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'passwd': os.environ.get('MYSQL_PASSWORD', ''),
    'db': os.environ.get('MYSQL_DB', 'sistema_reina'),
    'port': int(os.environ.get('MYSQL_PORT', 3306))
}

def update_db():
    try:
        db = MySQLdb.connect(**DB_CONFIG)
        cursor = db.cursor()
        print("Conectado a la base de datos...")

        # 1. Tabla de Sesiones de Caja (Turnos)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sesiones_caja (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sucursal_id INT NOT NULL,
            usuario_id INT NOT NULL,
            fecha_apertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            monto_inicial DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            fecha_cierre TIMESTAMP NULL,
            monto_ventas_efectivo DECIMAL(10,2) DEFAULT 0.00,
            monto_ventas_tarjeta DECIMAL(10,2) DEFAULT 0.00,
            monto_ventas_transferencia DECIMAL(10,2) DEFAULT 0.00,
            monto_egresos DECIMAL(10,2) DEFAULT 0.00,
            monto_final_esperado DECIMAL(10,2) DEFAULT 0.00,
            monto_final_real DECIMAL(10,2) DEFAULT 0.00,
            diferencia DECIMAL(10,2) DEFAULT 0.00,
            estado ENUM('ABIERTA', 'CERRADA') DEFAULT 'ABIERTA',
            observaciones TEXT NULL,
            FOREIGN KEY (sucursal_id) REFERENCES sucursales(id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 2. Tabla Cierre Diario (Consolidado Administrador)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cierres_diarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sucursal_id INT NOT NULL,
            usuario_id INT NOT NULL, -- Admin que cierra
            fecha_cierre TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_dia DATE NOT NULL,
            total_ventas DECIMAL(10,2) DEFAULT 0.00,
            total_efectivo DECIMAL(10,2) DEFAULT 0.00,
            total_tarjetas DECIMAL(10,2) DEFAULT 0.00,
            total_transferencias DECIMAL(10,2) DEFAULT 0.00,
            total_egresos DECIMAL(10,2) DEFAULT 0.00,
            saldo_final_caja DECIMAL(10,2) DEFAULT 0.00,
            observaciones TEXT NULL,
            FOREIGN KEY (sucursal_id) REFERENCES sucursales(id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 3. Para integridad perfecta, vinculamos las transacciones a la sesión de caja
        # Agregar columna sesion_caja_id a ventas y egresos si no existe
        cursor.execute("SHOW COLUMNS FROM ventas LIKE 'sesion_caja_id'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE ventas ADD COLUMN sesion_caja_id INT NULL, ADD CONSTRAINT fk_ventas_sesion FOREIGN KEY (sesion_caja_id) REFERENCES sesiones_caja(id)")
            print("Agregada columna sesion_caja_id a ventas.")

        cursor.execute("SHOW COLUMNS FROM egresos LIKE 'sesion_caja_id'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE egresos ADD COLUMN sesion_caja_id INT NULL, ADD CONSTRAINT fk_egresos_sesion FOREIGN KEY (sesion_caja_id) REFERENCES sesiones_caja(id)")
            print("Agregada columna sesion_caja_id a egresos.")
            
        cursor.execute("SHOW COLUMNS FROM compras LIKE 'sesion_caja_id'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE compras ADD COLUMN sesion_caja_id INT NULL, ADD CONSTRAINT fk_compras_sesion FOREIGN KEY (sesion_caja_id) REFERENCES sesiones_caja(id)")
            print("Agregada columna sesion_caja_id a compras.")

        db.commit()
        print("✅ Tablas de Sesiones de Caja y Cierres Diarios creadas/actualizadas correctamente.")
        cursor.close()
        db.close()
    except Exception as e:
        print(f"❌ Error al actualizar la base de datos: {str(e)}")

if __name__ == "__main__":
    update_db()