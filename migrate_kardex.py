from app import app, mysql

def migrate():
    with app.app_context():
        cur = mysql.connection.cursor()
        
        print("Borrando ajustes_inventario y creando kardex...")
        cur.execute("DROP TABLE IF EXISTS ajustes_inventario;")
        cur.execute("""
            CREATE TABLE `kardex` (
              `id` int(11) NOT NULL AUTO_INCREMENT,
              `insumo_id` int(11) NOT NULL,
              `sucursal_id` int(11) NOT NULL,
              `tipo_movimiento` varchar(50) NOT NULL,
              `motivo` varchar(255) DEFAULT NULL,
              `referencia_id` int(11) DEFAULT NULL,
              `cantidad_entrada` decimal(10,4) DEFAULT '0.0000',
              `cantidad_salida` decimal(10,4) DEFAULT '0.0000',
              `saldo_anterior` decimal(10,4) NOT NULL,
              `saldo_posterior` decimal(10,4) NOT NULL,
              `costo_unitario` decimal(10,4) DEFAULT NULL,
              `usuario_id` int(11) NOT NULL,
              `fecha` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
              PRIMARY KEY (`id`),
              KEY `insumo_id` (`insumo_id`),
              KEY `sucursal_id` (`sucursal_id`),
              KEY `usuario_id` (`usuario_id`),
              CONSTRAINT `kardex_ibfk_1` FOREIGN KEY (`insumo_id`) REFERENCES `insumos` (`id`),
              CONSTRAINT `kardex_ibfk_2` FOREIGN KEY (`sucursal_id`) REFERENCES `sucursales` (`id`),
              CONSTRAINT `kardex_ibfk_3` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        mysql.connection.commit()
        cur.close()
        print("Migración completada con éxito.")

if __name__ == "__main__":
    migrate()
