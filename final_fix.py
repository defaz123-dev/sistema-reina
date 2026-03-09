import MySQLdb
import os

def final_fix():
    try:
        conn = MySQLdb.connect(
            host=os.environ.get('MYSQL_HOST', 'localhost'),
            user=os.environ.get('MYSQL_USER', 'root'),
            passwd=os.environ.get('MYSQL_PASSWORD', ''),
            db=os.environ.get('MYSQL_DB', 'sistema_reina')
        )
        cur = conn.cursor()
        
        # Asegurar que el rol 1 se llame exactamente ADMINISTRADOR
        cur.execute("UPDATE roles SET nombre = 'ADMINISTRADOR' WHERE id = 1")
        
        # Asegurar que los usuarios administradores tengan rol_id 1
        cur.execute("UPDATE usuarios SET rol_id = 1 WHERE cedula IN ('1002597886', '1714990726')")
        
        conn.commit()
        print("Sincronización de roles completada.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    final_fix()
