import MySQLdb
import os

def run():
    host = os.environ.get('MYSQL_HOST', 'localhost')
    user = os.environ.get('MYSQL_USER', 'root')
    password = os.environ.get('MYSQL_PASSWORD', '')
    database = os.environ.get('MYSQL_DB', 'sistema_reina')
    port = int(os.environ.get('MYSQL_PORT', 3306))

    db = MySQLdb.connect(host=host, user=user, passwd=password, db=database, port=port)
    cur = db.cursor()

    # check if it already exists
    cur.execute("SELECT id FROM menus WHERE url = 'tarjetas_plataformas'")
    row = cur.fetchone()
    
    if not row:
        cur.execute("INSERT INTO menus (nombre, url, icono, categoria, orden) VALUES ('Tarjetas/Plat.', 'tarjetas_plataformas', 'fas fa-credit-card', 'ADMINISTRATIVO', 20)")
        menu_id = cur.lastrowid
        print(f"Menu creado con ID {menu_id}")
    else:
        menu_id = row[0]
        print(f"Menu ya existia con ID {menu_id}")

    # get admin role
    cur.execute("SELECT id FROM roles WHERE nombre='ADMINISTRADOR'")
    admin_id = cur.fetchone()[0]

    # check mapping
    cur.execute("SELECT * FROM rol_menus WHERE rol_id=%s AND menu_id=%s", (admin_id, menu_id))
    if not cur.fetchone():
        cur.execute("INSERT INTO rol_menus (rol_id, menu_id) VALUES (%s, %s)", (admin_id, menu_id))
        print("Menu asignado al ADMINISTRADOR")
    else:
        print("El ADMINISTRADOR ya tenia este menu asignado")

    db.commit()
    db.close()

if __name__ == '__main__':
    run()
