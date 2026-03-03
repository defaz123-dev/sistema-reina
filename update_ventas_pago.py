# update_ventas_pago.py
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
        print("Añadiendo columna 'forma_pago' a ventas...")
        try:
            cursor.execute("ALTER TABLE ventas ADD COLUMN forma_pago VARCHAR(50) DEFAULT 'EFECTIVO' AFTER total")
            db.commit()
            print("✅ Columna añadida.")
        except:
            print("✅ La columna ya existía.")
        cursor.close()
        db.close()
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    update()
