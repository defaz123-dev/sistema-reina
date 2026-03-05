# update_compras_caducidad.py
import MySQLdb

def update_db():
    try:
        db = MySQLdb.connect(host='localhost', user='root', passwd='', db='sistema_reina')
        cur = db.cursor()
        
        # Añadir columna fecha_caducidad si no existe
        cur.execute("SHOW COLUMNS FROM compras LIKE 'fecha_caducidad'")
        if not cur.fetchone():
            print("Añadiendo columna fecha_caducidad a compras...")
            cur.execute("ALTER TABLE compras ADD COLUMN fecha_caducidad DATE NULL")
        
        db.commit()
        db.close()
        print("✅ Base de datos actualizada con éxito.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    update_db()
