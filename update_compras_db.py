# update_compras_db.py
import MySQLdb

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'passwd': '',
    'db': 'sistema_reina'
}

def update():
    try:
        db = MySQLdb.connect(**DB_CONFIG)
        cursor = db.cursor()
        print("Creando tablas de proveedores y compras...")
        
        # 1. Tipos de Comprobantes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tipos_comprobantes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(50) NOT NULL
        )
        """)
        
        # 2. Proveedores
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS proveedores (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ruc VARCHAR(13) UNIQUE NOT NULL,
            razon_social VARCHAR(255) NOT NULL,
            nombre_comercial VARCHAR(255),
            direccion VARCHAR(255),
            telefono VARCHAR(20),
            email VARCHAR(100),
            tipo_comprobante_id INT,
            FOREIGN KEY (tipo_comprobante_id) REFERENCES tipos_comprobantes(id)
        )
        """)
        
        # 3. Compras (Cabecera)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS compras (
            id INT AUTO_INCREMENT PRIMARY KEY,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            proveedor_id INT,
            sucursal_id INT,
            numero_comprobante VARCHAR(50),
            total DECIMAL(10,2),
            FOREIGN KEY (proveedor_id) REFERENCES proveedores(id),
            FOREIGN KEY (sucursal_id) REFERENCES sucursales(id)
        )
        """)
        
        # 4. Detalles de Compras (Donde se registran los insumos comprados)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS detalles_compras (
            id INT AUTO_INCREMENT PRIMARY KEY,
            compra_id INT,
            insumo_id INT,
            cantidad DECIMAL(10,2),
            costo_unitario DECIMAL(10,2),
            subtotal DECIMAL(10,2),
            FOREIGN KEY (compra_id) REFERENCES compras(id),
            FOREIGN KEY (insumo_id) REFERENCES insumos(id)
        )
        """)
        
        # Inserts iniciales
        cursor.execute("SELECT COUNT(*) FROM tipos_comprobantes")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO tipos_comprobantes (nombre) VALUES ('FACTURA'), ('NOTA DE VENTA')")
            
        db.commit()
        print("✅ Módulo de compras preparado en la base de datos.")
        cursor.close()
        db.close()
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    update()
