import MySQLdb
import os

def standardize_roles():
    try:
        conn = MySQLdb.connect(
            host=os.environ.get('MYSQL_HOST', 'localhost'),
            user=os.environ.get('MYSQL_USER', 'root'),
            passwd=os.environ.get('MYSQL_PASSWORD', ''),
            db=os.environ.get('MYSQL_DB', 'sistema_reina')
        )
        cur = conn.cursor()
        # Estandarizar nombres exactos para que el Dashboard los reconozca
        cur.execute("UPDATE roles SET nombre = 'ADMINISTRADOR' WHERE id = 1")
        cur.execute("UPDATE roles SET nombre = 'CAJERO' WHERE id = 2")
        conn.commit()
        print("ÉXITO: Nombres de roles corregidos en la base de datos local.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    standardize_roles()
