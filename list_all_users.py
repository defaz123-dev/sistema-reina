import MySQLdb
import os

def list_users():
    try:
        conn = MySQLdb.connect(
            host=os.environ.get('MYSQL_HOST', 'localhost'),
            user=os.environ.get('MYSQL_USER', 'root'),
            passwd=os.environ.get('MYSQL_PASSWORD', ''),
            db=os.environ.get('MYSQL_DB', 'sistema_reina')
        )
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT u.id, u.usuario, u.cedula, r.nombre as rol FROM usuarios u JOIN roles r ON u.rol_id = r.id')
        users = cur.fetchall()
        for u in users:
            print(u)
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_users()
