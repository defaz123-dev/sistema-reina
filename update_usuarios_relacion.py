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

def update_usuarios_table():
    with app.app_context():
        cur = mysql.connection.cursor()
        # Verificar si la columna tipo_identificacion_id existe
        cur.execute("SHOW COLUMNS FROM usuarios LIKE 'tipo_identificacion_id'")
        column = cur.fetchone()
        
        if not column:
            print("Añadiendo columna 'tipo_identificacion_id' a la tabla usuarios...")
            # Añadir columna y relación foránea
            cur.execute("ALTER TABLE usuarios ADD COLUMN tipo_identificacion_id INT AFTER cedula")
            # Por defecto, poner a todos como Cédula (ID 1)
            cur.execute("UPDATE usuarios SET tipo_identificacion_id = 1")
            # Añadir la restricción de clave foránea
            cur.execute("ALTER TABLE usuarios ADD CONSTRAINT fk_usuarios_tipo_id FOREIGN KEY (tipo_identificacion_id) REFERENCES tipos_identificacion(id)")
            mysql.connection.commit()
            print("Columna y relación foránea añadidas con éxito.")
        else:
            print("La columna 'tipo_identificacion_id' ya existe.")
        cur.close()

if __name__ == '__main__':
    update_usuarios_table()
