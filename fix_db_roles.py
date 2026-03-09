import MySQLdb
import os

def fix_roles():
    try:
        conn = MySQLdb.connect(
            host=os.environ.get('MYSQL_HOST', 'localhost'),
            user=os.environ.get('MYSQL_USER', 'root'),
            passwd=os.environ.get('MYSQL_PASSWORD', ''),
            db=os.environ.get('MYSQL_DB', 'sistema_reina')
        )
        cur = conn.cursor()
        # Actualizar nombres de roles para que coincidan con el código del Dashboard
        cur.execute("UPDATE roles SET nombre = 'ADMINISTRADOR' WHERE nombre = 'ADMIN'")
        cur.execute("UPDATE roles SET nombre = 'CAJERO' WHERE nombre = 'USER'")
        conn.commit()
        print("Roles actualizados en la base de datos local.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_roles()
