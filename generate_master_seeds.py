
import MySQLdb
import MySQLdb.cursors
import os

def get_db_connection():
    return MySQLdb.connect(
        host=os.environ.get('MYSQL_HOST', 'localhost'),
        user=os.environ.get('MYSQL_USER', 'root'),
        passwd=os.environ.get('MYSQL_PASSWORD', ''),
        db=os.environ.get('MYSQL_DB', 'sistema_reina'),
        port=int(os.environ.get('MYSQL_PORT', 3306)),
        cursorclass=MySQLdb.cursors.DictCursor
    )

def escape_sql(val):
    if val is None: return "NULL"
    if isinstance(val, (int, float)): return str(val)
    if isinstance(val, bytes): return "0x" + val.hex()
    return "'" + str(val).replace("'", "''") + "'"

def generate_seeds():
    tables = [
        'roles', 'tipos_identificacion', 'tipos_comprobantes', 'unidades_medida',
        'sucursales', 'usuarios', 'categorias', 'productos', 'cat_tarjetas', 
        'plataformas', 'proveedores', 'menus', 'empresa', 'rol_menus', 
        'producto_precios', 'clientes'
    ]
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    with open('seed_data.sql', 'w', encoding='utf-8') as f:
        f.write("SET FOREIGN_KEY_CHECKS=0;\n\n")
        
        for table in tables:
            cur.execute(f"SELECT * FROM `{table}`")
            rows = cur.fetchall()
            if not rows: continue
            
            f.write(f"-- Data for {table}\n")
            f.write(f"TRUNCATE TABLE `{table}`;\n")
            
            cols = list(rows[0].keys())
            f.write(f"INSERT INTO `{table}` (`" + "`, `".join(cols) + "`) VALUES\n")
            
            val_strs = []
            for row in rows:
                vals = [escape_sql(row[c]) for c in cols]
                val_strs.append("(" + ", ".join(vals) + ")")
            
            f.write(",\n".join(val_strs) + ";\n\n")
            
        f.write("SET FOREIGN_KEY_CHECKS=1;\n")
        
    cur.close()
    conn.close()
    print("seed_data.sql updated.")

if __name__ == "__main__":
    generate_seeds()
