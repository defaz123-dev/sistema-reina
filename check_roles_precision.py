import MySQLdb
import os

def check_roles_precision():
    try:
        conn = MySQLdb.connect(
            host=os.environ.get('MYSQL_HOST', 'localhost'),
            user=os.environ.get('MYSQL_USER', 'root'),
            passwd=os.environ.get('MYSQL_PASSWORD', ''),
            db=os.environ.get('MYSQL_DB', 'sistema_reina')
        )
        cur = conn.cursor()
        cur.execute('SELECT id, nombre FROM roles')
        roles = cur.fetchall()
        for r_id, nombre in roles:
            print(f"ID: {r_id}, Nombre: '{nombre}' (Largo: {len(nombre)})")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_roles_precision()
