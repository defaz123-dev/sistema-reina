from flask import Flask
from flask_mysqldb import MySQL
import os

app = Flask(__name__)
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'sistema_reina')
app.config['MYSQL_PORT'] = int(os.environ.get('MYSQL_PORT', 3306))
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

def fix_compras_columns():
    with app.app_context():
        cur = mysql.connection.cursor()
        
        # Columnas a verificar y añadir
        columns_to_add = [
            ("numero_autorizacion", "VARCHAR(50) AFTER clave_acceso"),
            ("fecha_caducidad", "DATE AFTER numero_autorizacion")
        ]
        
        for col_name, col_def in columns_to_add:
            cur.execute(f"SHOW COLUMNS FROM compras LIKE '{col_name}'")
            if not cur.fetchone():
                print(f"Añadiendo columna '{col_name}' a la tabla compras...")
                cur.execute(f"ALTER TABLE compras ADD COLUMN {col_def}")
                print(f"Columna '{col_name}' añadida.")
            else:
                print(f"La columna '{col_name}' ya existe.")
        
        mysql.connection.commit()
        cur.close()

if __name__ == '__main__':
    fix_compras_columns()
