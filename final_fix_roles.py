import MySQLdb
import os

def final_check():
    try:
        conn = MySQLdb.connect(
            host=os.environ.get('MYSQL_HOST', 'localhost'),
            user=os.environ.get('MYSQL_USER', 'root'),
            passwd=os.environ.get('MYSQL_PASSWORD', ''),
            db=os.environ.get('MYSQL_DB', 'sistema_reina')
        )
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        
        # 1. Asegurar roles exactos
        cur.execute("UPDATE roles SET nombre = 'ADMINISTRADOR' WHERE id = 1")
        cur.execute("UPDATE roles SET nombre = 'CAJERO' WHERE id = 2")
        
        # 2. Asegurar que el usuario tenga rol_id = 1
        cur.execute("UPDATE usuarios SET rol_id = 1 WHERE cedula = '1002597886'")
        
        # 3. Ver qué devuelve la consulta de login exactamente
        cur.execute("SELECT u.*, r.nombre as rol_nombre FROM usuarios u JOIN roles r ON u.rol_id = r.id WHERE u.cedula='1002597886'")
        user = cur.fetchone()
        print(f"ROL NOMBRE: [{user['rol_nombre']}] - TIPO: {type(user['rol_nombre'])}")
        
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    final_check()
