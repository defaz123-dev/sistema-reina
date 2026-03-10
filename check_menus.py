import MySQLdb

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'passwd': '',
    'db': 'sistema_reina'
}

try:
    db = MySQLdb.connect(**DB_CONFIG)
    cursor = db.cursor()
    cursor.execute("SELECT id, nombre, url FROM menus")
    print("Menus:")
    for row in cursor.fetchall():
        print(row)
    
    cursor.execute("SELECT * FROM rol_menus WHERE rol_id=1")
    print("Admin rol_menus:")
    for row in cursor.fetchall():
        print(row)
    db.close()
except Exception as e:
    print(f"Error: {e}")