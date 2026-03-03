# update_img_db.py
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
        print("Añadiendo columna 'mimetype' a productos...")
        try:
            cursor.execute("ALTER TABLE productos ADD COLUMN mimetype VARCHAR(50) AFTER imagen")
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
