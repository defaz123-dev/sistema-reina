
import MySQLdb
import os

def fix_ventas_columns():
    host = os.environ.get('MYSQL_HOST', 'localhost')
    user = os.environ.get('MYSQL_USER', 'root')
    password = os.environ.get('MYSQL_PASSWORD', '')
    database = os.environ.get('MYSQL_DB', 'sistema_reina')
    port = int(os.environ.get('MYSQL_PORT', 3306))

    try:
        db = MySQLdb.connect(host=host, user=user, passwd=password, db=database, port=port)
        cur = db.cursor()
        
        print(f"Conectado a la base de datos {database}...")

        # Verificar si las columnas ya existen
        cur.execute("SHOW COLUMNS FROM ventas")
        columns = [row[0] for row in cur.fetchall()]
        
        if 'descuento_promo_id' not in columns:
            print("Agregando columna descuento_promo_id...")
            cur.execute("ALTER TABLE ventas ADD COLUMN descuento_promo_id INT DEFAULT NULL AFTER sesion_caja_id")
            cur.execute("ALTER TABLE ventas ADD CONSTRAINT fk_ventas_promo FOREIGN KEY (descuento_promo_id) REFERENCES promociones(id)")
        else:
            print("La columna descuento_promo_id ya existe.")

        if 'descuento_manual_instante' not in columns:
            print("Agregando columna descuento_manual_instante...")
            cur.execute("ALTER TABLE ventas ADD COLUMN descuento_manual_instante DECIMAL(10,2) DEFAULT 0.00 AFTER descuento_promo_id")
        else:
            print("La columna descuento_manual_instante ya existe.")

        if 'motivo_descuento_manual' not in columns:
            print("Agregando columna motivo_descuento_manual...")
            cur.execute("ALTER TABLE ventas ADD COLUMN motivo_descuento_manual VARCHAR(255) DEFAULT NULL AFTER descuento_manual_instante")
        else:
            print("La columna motivo_descuento_manual ya existe.")

        db.commit()
        print("Proceso completado con éxito.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    fix_ventas_columns()
