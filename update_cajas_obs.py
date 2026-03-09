import MySQLdb
import os

DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'passwd': os.environ.get('MYSQL_PASSWORD', ''),
    'db': os.environ.get('MYSQL_DB', 'sistema_reina'),
    'port': int(os.environ.get('MYSQL_PORT', 3306))
}

def update():
    try:
        db = MySQLdb.connect(**DB_CONFIG)
        cursor = db.cursor()
        print("Agregando columnas de justificación por método de pago...")

        cols = [
            ("obs_efectivo", "TEXT NULL"),
            ("obs_tarjeta", "TEXT NULL"),
            ("obs_transferencia", "TEXT NULL")
        ]

        for col_name, col_type in cols:
            cursor.execute(f"SHOW COLUMNS FROM sesiones_caja LIKE '{col_name}'")
            if not cursor.fetchone():
                cursor.execute(f"ALTER TABLE sesiones_caja ADD COLUMN {col_name} {col_type}")
                print(f"Columna {col_name} agregada.")

        db.commit()
        print("✅ Base de datos actualizada.")
        cursor.close(); db.close()
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    update()
