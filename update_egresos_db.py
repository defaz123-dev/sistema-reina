import MySQLdb
import os

# Configuración de Base de Datos obtenida de variables de entorno
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
        print(f"Conectado a la base de datos en {DB_CONFIG['host']}...")
        print("Iniciando actualización de base de datos para Egresos y Flujo de Caja...")

        # 1. Crear tabla de Egresos (Para gastos varios y recibos internos)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS egresos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sucursal_id INT NOT NULL,
            usuario_id INT NOT NULL,
            proveedor_id INT NULL,
            descripcion TEXT NOT NULL,
            monto DECIMAL(10,2) NOT NULL,
            tipo_documento ENUM('FACTURA', 'NOTA_DE_VENTA', 'RECIBO_INTERNO') DEFAULT 'RECIBO_INTERNO',
            numero_documento VARCHAR(50),
            categoria VARCHAR(100) DEFAULT 'GASTOS VARIOS',
            FOREIGN KEY (sucursal_id) REFERENCES sucursales(id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 2. Crear tabla de Flujo de Caja (Para control de efectivo real)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS flujo_caja (
            id INT AUTO_INCREMENT PRIMARY KEY,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sucursal_id INT NOT NULL,
            usuario_id INT NOT NULL,
            tipo ENUM('INGRESO', 'EGRESO') NOT NULL,
            monto DECIMAL(10,2) NOT NULL,
            descripcion TEXT,
            referencia_id INT NULL, -- ID de venta, compra o egreso
            tipo_referencia ENUM('VENTA', 'COMPRA', 'EGRESO_VARIO', 'APERTURA', 'CIERRE') NOT NULL,
            FOREIGN KEY (sucursal_id) REFERENCES sucursales(id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 3. Crear Proveedor Genérico 'GASTOS VARIOS' si no existe
        cursor.execute("SELECT id FROM proveedores WHERE ruc = '9999999999999'")
        if not cursor.fetchone():
            cursor.execute("""
            INSERT INTO proveedores (ruc, razon_social, nombre_comercial, direccion, telefono, email, tipo_comprobante_id) 
            VALUES ('9999999999999', 'GASTOS VARIOS', 'GASTOS VARIOS', 'QUITO', '0000000000', 'gastos@varios.com', 1)
            """)

        db.commit()
        print("✅ Tablas creadas y proveedor genérico configurado.")
        cursor.close()
        db.close()
    except Exception as e:
        print(f"❌ Error al actualizar la base de datos: {str(e)}")

if __name__ == "__main__":
    update_db()
