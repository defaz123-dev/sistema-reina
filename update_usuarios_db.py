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

def check_and_add_cedula():
    with app.app_context():
        cur = mysql.connection.cursor()
        # Verificar si la columna cedula existe
        cur.execute("SHOW COLUMNS FROM usuarios LIKE 'cedula'")
        column = cur.fetchone()
        
        if not column:
            print("Añadiendo columna 'cedula' a la tabla usuarios...")
            # Añadir la columna cedula, con un valor por defecto temporal para los actuales
            cur.execute("ALTER TABLE usuarios ADD COLUMN cedula VARCHAR(13) AFTER id")
            # Para los usuarios existentes, usamos su nombre de usuario como cedula temporal si no tienen una
            cur.execute("UPDATE usuarios SET cedula = usuario WHERE cedula IS NULL")
            # Hacerla única para evitar duplicados
            cur.execute("ALTER TABLE usuarios ADD UNIQUE (cedula)")
            mysql.connection.commit()
            print("Columna 'cedula' añadida con éxito.")
        else:
            print("La columna 'cedula' ya existe.")
        cur.close()

if __name__ == '__main__':
    check_and_add_cedula()
