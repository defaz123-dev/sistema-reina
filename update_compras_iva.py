# update_compras_iva.py
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
        print("Añadiendo columna 'iva_valor' a detalles_compras...")
        try:
            cursor.execute("ALTER TABLE detalles_compras ADD COLUMN iva_valor DECIMAL(10,2) DEFAULT 0 AFTER subtotal")
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
