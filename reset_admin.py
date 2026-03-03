# reset_admin.py
import MySQLdb
from werkzeug.security import generate_password_hash

# Configuración (Igual que en app.py)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'passwd': '',
    'db': 'sistema_reina'
}

def reset():
    try:
        nueva_pass = "admin123"
        hash_nuevo = generate_password_hash(nueva_pass)
        
        db = MySQLdb.connect(**DB_CONFIG)
        cursor = db.cursor()
        
        query = "UPDATE usuarios SET password = %s WHERE usuario = 'admin'"
        cursor.execute(query, (hash_nuevo,))
        
        db.commit()
        cursor.close()
        db.close()
        print(f"✅ Contraseña de 'admin' reseteada a: {nueva_pass}")
        print("Intenta loguearte ahora en la sucursal 'Centro Histórico'.")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    reset()
