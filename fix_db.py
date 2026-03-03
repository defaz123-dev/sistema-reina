# fix_db.py
import MySQLdb

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'passwd': '',
    'db': 'sistema_reina'
}

def fix():
    try:
        db = MySQLdb.connect(**DB_CONFIG)
        cursor = db.cursor()
        
        print("Añadiendo columna 'imagen' a la tabla productos...")
        # Usamos ALTER TABLE para no borrar los productos existentes
        cursor.execute("ALTER TABLE productos ADD COLUMN imagen LONGBLOB AFTER categoria_id")
        
        db.commit()
        cursor.close()
        db.close()
        print("✅ Columna añadida con éxito. Ya puedes subir fotos.")

    except Exception as e:
        if "Duplicate column name" in str(e):
            print("✅ La columna ya existe.")
        else:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    fix()
