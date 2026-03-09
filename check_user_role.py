import MySQLdb
import os

def check_user():
    try:
        conn = MySQLdb.connect(
            host=os.environ.get('MYSQL_HOST', 'localhost'),
            user=os.environ.get('MYSQL_USER', 'root'),
            passwd=os.environ.get('MYSQL_PASSWORD', ''),
            db=os.environ.get('MYSQL_DB', 'sistema_reina')
        )
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT u.usuario, u.rol_id, r.nombre as rol_nombre FROM usuarios u JOIN roles r ON u.rol_id = r.id WHERE u.cedula="1002597886"')
        user = cur.fetchone()
        print(user)
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_user()
