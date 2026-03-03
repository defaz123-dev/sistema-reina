# update_compras_date.py
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
        print("Cambiando columna 'fecha' para permitir ingreso manual...")
        # Cambiamos a DATETIME sin el DEFAULT automático restrictivo
        cursor.execute("ALTER TABLE compras MODIFY COLUMN fecha DATETIME NOT NULL")
        db.commit()
        print("✅ Columna actualizada.")
        cursor.close()
        db.close()
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    update()
