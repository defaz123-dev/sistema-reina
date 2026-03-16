from flask import Flask
from flask_mysqldb import MySQL
import os

app = Flask(__name__)

# Configuración de la base de datos (basada en lo común en estos proyectos)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'sistema_reina'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

def create_table():
    with app.app_context():
        cur = mysql.connection.cursor()
        print("Creando tabla ventas_pagos...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ventas_pagos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                venta_id INT NOT NULL,
                metodo_pago VARCHAR(50) NOT NULL,
                monto DECIMAL(10, 2) NOT NULL,
                id_tarjeta INT DEFAULT NULL,
                referencia VARCHAR(100) DEFAULT NULL,
                cambio DECIMAL(10, 2) DEFAULT 0.00,
                fecha_pago TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
                FOREIGN KEY (id_tarjeta) REFERENCES cat_tarjetas(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        mysql.connection.commit()
        print("✅ Tabla ventas_pagos creada exitosamente.")
        cur.close()

if __name__ == "__main__":
    create_table()
