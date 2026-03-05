# update_empresa_visual.py
import MySQLdb

def update_db():
    try:
        db = MySQLdb.connect(host='localhost', user='root', passwd='', db='sistema_reina')
        cur = db.cursor()
        
        # Añadir columna color_tema si no existe
        cur.execute("SHOW COLUMNS FROM empresa LIKE 'color_tema'")
        if not cur.fetchone():
            print("Añadiendo columna color_tema...")
            cur.execute("ALTER TABLE empresa ADD COLUMN color_tema VARCHAR(7) DEFAULT '#008938'")
        
        db.commit()
        db.close()
        print("✅ Base de datos actualizada con éxito.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    update_db()
