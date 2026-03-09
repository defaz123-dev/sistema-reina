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

        # 1. Crear tabla de Catálogo de Tarjetas
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cat_tarjetas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(50) NOT NULL UNIQUE,
            activo TINYINT(1) DEFAULT 1
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 2. Insertar valores por defecto
        tarjetas = ['VISA', 'MASTERCARD', 'AMERICAN EXPRESS', 'DINERS']
        for t in tarjetas:
            cursor.execute("INSERT IGNORE INTO cat_tarjetas (nombre) VALUES (%s)", (t,))

        # 3. Modificar tabla ventas para agregar id_tarjeta
        # Primero verificamos si la columna ya existe
        cursor.execute("SHOW COLUMNS FROM ventas LIKE 'id_tarjeta'")
        if not cursor.fetchone():
            print("Agregando columna id_tarjeta a la tabla ventas...")
            cursor.execute("""
            ALTER TABLE ventas 
            ADD COLUMN id_tarjeta INT NULL,
            ADD CONSTRAINT fk_ventas_tarjeta FOREIGN KEY (id_tarjeta) REFERENCES cat_tarjetas(id)
            """)

        db.commit()
        print("✅ Base de datos actualizada con el catálogo de tarjetas.")
        cursor.close()
        db.close()
    except Exception as e:
        print(f"❌ Error al actualizar la base de datos: {str(e)}")

if __name__ == "__main__":
    update_db()
