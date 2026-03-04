-- database.sql (SISTEMA REINA - VERSIÓN NORMALIZADA Y SEGURA)
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS detalles_ventas;
DROP TABLE IF EXISTS ventas;
DROP TABLE IF EXISTS detalles_compras;
DROP TABLE IF EXISTS compras;
DROP TABLE IF EXISTS proveedores;
DROP TABLE IF EXISTS tipos_comprobantes;
DROP TABLE IF EXISTS recetas;
DROP TABLE IF EXISTS productos;
DROP TABLE IF EXISTS insumos;
DROP TABLE IF EXISTS categorias;
DROP TABLE IF EXISTS usuarios;
DROP TABLE IF EXISTS sucursales;
DROP TABLE IF EXISTS empresa;
DROP TABLE IF EXISTS clientes;
DROP TABLE IF EXISTS auditoria;
DROP TABLE IF EXISTS ajustes_inventario;
DROP TABLE IF EXISTS unidades_medida;
DROP TABLE IF EXISTS tipos_identificacion;
SET FOREIGN_KEY_CHECKS = 1;

-- 1. Catálogo: Unidades de Medida
CREATE TABLE unidades_medida (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    abreviatura VARCHAR(10)
);

-- 2. Catálogo: Tipos de Identificación (SRI)
CREATE TABLE tipos_identificacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    codigo_sri VARCHAR(2)
);

-- 3. Sucursales
CREATE TABLE sucursales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    usuario_creacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_modificacion_id INT,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 4. Usuarios
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    sucursal_id INT,
    rol ENUM('ADMIN', 'VENDEDOR', 'SUPERVISOR') DEFAULT 'VENDEDOR',
    activo TINYINT(1) DEFAULT 1,
    usuario_creacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_modificacion_id INT,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (sucursal_id) REFERENCES sucursales(id)
);

-- 5. Categorías
CREATE TABLE categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    usuario_creacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_modificacion_id INT,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 6. Insumos
CREATE TABLE insumos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    stock_actual DECIMAL(10,2) DEFAULT 0,
    stock_minimo DECIMAL(10,2) DEFAULT 0,
    unidad_medida_id INT,
    sucursal_id INT,
    usuario_creacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_modificacion_id INT,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (sucursal_id) REFERENCES sucursales(id),
    FOREIGN KEY (unidad_medida_id) REFERENCES unidades_medida(id)
);

-- 7. Productos
CREATE TABLE productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    categoria_id INT,
    imagen LONGBLOB,
    mimetype VARCHAR(50),
    usuario_creacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_modificacion_id INT,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);

-- 8. Recetas
CREATE TABLE recetas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT,
    insumo_id INT,
    cantidad_requerida DECIMAL(10,2),
    usuario_creacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_modificacion_id INT,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id) REFERENCES productos(id),
    FOREIGN KEY (insumo_id) REFERENCES insumos(id)
);

-- 9. Clientes
CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cedula_ruc VARCHAR(20) UNIQUE NOT NULL,
    tipo_identificacion_id INT,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    direccion VARCHAR(255),
    telefono VARCHAR(20),
    email VARCHAR(100),
    usuario_creacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_modificacion_id INT,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (tipo_identificacion_id) REFERENCES tipos_identificacion(id)
);

-- 10. Tipos de Comprobantes (Catalogo de Compras)
CREATE TABLE tipos_comprobantes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

-- 11. Proveedores
CREATE TABLE proveedores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ruc VARCHAR(13) UNIQUE NOT NULL,
    razon_social VARCHAR(255) NOT NULL,
    nombre_comercial VARCHAR(255),
    direccion VARCHAR(255),
    telefono VARCHAR(20),
    email VARCHAR(100),
    tipo_comprobante_id INT,
    usuario_creacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_modificacion_id INT,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (tipo_comprobante_id) REFERENCES tipos_comprobantes(id)
);

-- 12. Compras
CREATE TABLE compras (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    proveedor_id INT,
    sucursal_id INT,
    establecimiento VARCHAR(3),
    punto_emision VARCHAR(3),
    numero_comprobante VARCHAR(50),
    clave_acceso VARCHAR(49),
    numero_autorizacion VARCHAR(50),
    total DECIMAL(10,2),
    usuario_creacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_modificacion_id INT,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id),
    FOREIGN KEY (sucursal_id) REFERENCES sucursales(id)
);

-- 13. Detalles Compras
CREATE TABLE detalles_compras (
    id INT AUTO_INCREMENT PRIMARY KEY,
    compra_id INT,
    insumo_id INT,
    cantidad DECIMAL(10,2),
    costo_unitario DECIMAL(10,2),
    subtotal DECIMAL(10,2),
    iva_valor DECIMAL(10,2) DEFAULT 0,
    FOREIGN KEY (compra_id) REFERENCES compras(id),
    FOREIGN KEY (insumo_id) REFERENCES insumos(id)
);

-- 14. Ventas
CREATE TABLE ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_id INT,
    sucursal_id INT,
    cliente_id INT,
    subtotal_0 DECIMAL(10,2) DEFAULT 0,
    subtotal_15 DECIMAL(10,2) DEFAULT 0,
    iva_valor DECIMAL(10,2) DEFAULT 0,
    total DECIMAL(10,2),
    forma_pago VARCHAR(50) DEFAULT 'EFECTIVO',
    clave_acceso_sri VARCHAR(49),
    estado_sri VARCHAR(50) DEFAULT 'AUTORIZADO',
    usuario_creacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_modificacion_id INT,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (sucursal_id) REFERENCES sucursales(id),
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

-- 15. Detalles Ventas
CREATE TABLE detalles_ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    venta_id INT,
    producto_id INT,
    cantidad INT,
    precio_unitario DECIMAL(10,2),
    subtotal DECIMAL(10,2),
    iva_valor DECIMAL(10,2) DEFAULT 0,
    FOREIGN KEY (venta_id) REFERENCES ventas(id),
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);

-- 16. Empresa
CREATE TABLE empresa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ruc VARCHAR(13) NOT NULL,
    razon_social VARCHAR(255) NOT NULL,
    nombre_comercial VARCHAR(255),
    direccion_matriz VARCHAR(255) NOT NULL,
    obligado_contabilidad VARCHAR(2) DEFAULT 'NO',
    ambiente INT DEFAULT 1,
    usuario_creacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_modificacion_id INT,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 17. Auditoría Global
CREATE TABLE auditoria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_id INT,
    accion VARCHAR(100),
    detalle TEXT,
    ip VARCHAR(45),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- 18. Ajustes de Inventario
CREATE TABLE ajustes_inventario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    insumo_id INT,
    cantidad DECIMAL(10,2),
    tipo ENUM('INGRESO', 'EGRESO'),
    motivo VARCHAR(255),
    usuario_id INT,
    usuario_creacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_modificacion_id INT,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (insumo_id) REFERENCES insumos(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- DATOS MAESTROS (CATÁLOGOS) --
INSERT INTO unidades_medida (id, nombre, abreviatura) VALUES 
(1, 'GRAMOS', 'gr'), (2, 'KILOS', 'kg'), (3, 'LITROS', 'lt'), (4, 'UNIDADES', 'u');

INSERT INTO tipos_identificacion (id, nombre, codigo_sri) VALUES 
(1, 'CEDULA', '05'), (2, 'RUC', '04'), (3, 'PASAPORTE', '06'), (4, 'CONSUMIDOR FINAL', '07');

INSERT INTO sucursales (id, nombre) VALUES (1, 'MATRIZ - LA REINA');

INSERT INTO tipos_comprobantes (id, nombre) VALUES (1, 'FACTURA'), (2, 'NOTA DE VENTA');

INSERT INTO categorias (id, nombre) VALUES (1, 'Sándwiches Pernil'), (2, 'Sándwiches Pollo'), (3, 'Sándwiches Atún'), (4, 'Bebidas'), (5, 'Adicionales');

INSERT INTO usuarios (usuario, password, sucursal_id, rol, activo) VALUES 
('admin', 'scrypt:32768:8:1$DXvK5GgRv6PghYpo$2cd3f172bafcbe4eda2c7007e74ce30be244b5f46c0907a1406cf7012e2492767f110e883edfef4a1084d4165383a572a8321b1c671880d7b0d705ece6e2ca3c', 1, 'ADMIN', 1);

INSERT INTO clientes (cedula_ruc, tipo_identificacion_id, nombres, apellidos, direccion) 
VALUES ('9999999999', 4, 'CONSUMIDOR', 'FINAL', 'QUITO');
