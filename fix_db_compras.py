from flask import Flask
from flask_mysqldb import MySQL
import os

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'sistema_reina'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

def fix_compras_db():
    with app.app_context():
        cur = mysql.connection.cursor()
        
        # Verificar fecha_caducidad
        cur.execute("SHOW COLUMNS FROM compras LIKE 'fecha_caducidad'")
        if not cur.fetchone():
            print("Añadiendo columna 'fecha_caducidad'...")
            cur.execute("ALTER TABLE compras ADD COLUMN fecha_caducidad DATE")
            print("Columna añadida.")
        
        # Verificar numero_autorizacion (por si acaso)
        cur.execute("SHOW COLUMNS FROM compras LIKE 'numero_autorizacion'")
        if not cur.fetchone():
            print("Añadiendo columna 'numero_autorizacion'...")
            cur.execute("ALTER TABLE compras ADD COLUMN numero_autorizacion VARCHAR(50)")
            print("Columna añadida.")
            
        mysql.connection.commit()
        cur.close()

if __name__ == '__main__':
    fix_compras_db()
