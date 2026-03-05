# fix_compras_date_type.py
import MySQLdb

def update_db():
    try:
        db = MySQLdb.connect(host='localhost', user='root', passwd='', db='sistema_reina')
        cur = db.cursor()
        
        print("Cambiando tipo de columna fecha en compras a DATE...")
        cur.execute("ALTER TABLE compras MODIFY COLUMN fecha DATE NOT NULL")
        
        db.commit()
        db.close()
        print("✅ Base de datos corregida con éxito.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    update_db()
