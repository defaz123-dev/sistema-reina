-- database_nube.sql (SISTEMA REINA - ESPEJO DE LOCAL ACTUALIZADO)
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS auditoria;
DROP TABLE IF EXISTS detalles_ventas;
DROP TABLE IF EXISTS ventas;
DROP TABLE IF EXISTS detalles_compras;
DROP TABLE IF EXISTS compras;
DROP TABLE IF EXISTS recetas;
DROP TABLE IF EXISTS ajustes_inventario;
DROP TABLE IF EXISTS insumos;
DROP TABLE IF EXISTS productos;
DROP TABLE IF EXISTS categorias;
DROP TABLE IF EXISTS clientes;
DROP TABLE IF EXISTS tipos_identificacion;
DROP TABLE IF EXISTS proveedores;
DROP TABLE IF EXISTS tipos_comprobantes;
DROP TABLE IF EXISTS usuarios;
DROP TABLE IF EXISTS sucursales;
DROP TABLE IF EXISTS unidades_medida;
DROP TABLE IF EXISTS empresa;
SET FOREIGN_KEY_CHECKS = 1;

-- 1. Empresa
CREATE TABLE empresa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ruc VARCHAR(13),
    razon_social VARCHAR(255),
    nombre_comercial VARCHAR(255),
    direccion_matriz VARCHAR(255),
    iva_porcentaje DECIMAL(5,2) DEFAULT 15.00,
    ambiente INT DEFAULT 1,
    usuario_creacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_modificacion_id INT,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
INSERT INTO empresa (id, ruc, razon_social, nombre_comercial, direccion_matriz, iva_porcentaje) 
VALUES (1, '1790000000001', 'SANDUCHES LA REINA', 'LA REINA', 'QUITO', 15.00);

-- 2. Sucursales
CREATE TABLE sucursales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    usuario_creacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_modificacion_id INT,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
INSERT INTO sucursales (id, nombre) VALUES 
(1, 'Reina Victoria Principal'),
(2, 'GRANADOS NORTE');

-- 3. Usuarios (Sincronizados con Local)
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    sucursal_id INT,
    rol ENUM('ADMIN', 'CAJERO') DEFAULT 'ADMIN',
    activo TINYINT(1) DEFAULT 1,
    usuario_creacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_modificacion_id INT,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (sucursal_id) REFERENCES sucursales(id)
);
INSERT INTO usuarios (id, usuario, password, sucursal_id, rol, activo) VALUES 
(1, 'admin', 'scrypt:32768:8:1$OSyt2StROGDDPy4f$7a2ff17725e547c97110d2560d400e6126d2172d277fd22c61b7342b7a34b0bc07a7cd6e57a997202b3887261e6da9f79e933d46a33f239c4613891a95d0825b', 1, 'ADMIN', 1),
(2, 'liliana', 'scrypt:32768:8:1$0KzrMh3tnG7kEoxZ$ded6e5fc4aad675c0debb2af7caa2338dd6e51c3f04fc412a06a3d8104424c2a65bd938701ed0ec0701e49b2961037ad276cc5a9a6c684f2ef014d0c77b862f5', 1, 'ADMIN', 1);

-- 4. Catálogos Base
CREATE TABLE unidades_medida (id INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(50) NOT NULL);
INSERT INTO unidades_medida (id, nombre) VALUES (1, 'UNIDAD'), (2, 'KILO'), (3, 'LITRO'), (4, 'GRAMO'), (5, 'PORCION');

CREATE TABLE tipos_comprobantes (id INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(50) NOT NULL);
INSERT INTO tipos_comprobantes (id, nombre) VALUES (1, 'FACTURA'), (2, 'NOTA DE VENTA');

CREATE TABLE tipos_identificacion (id INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(50) NOT NULL);
INSERT INTO tipos_identificacion (id, nombre) VALUES (1, 'CEDULA'), (2, 'RUC'), (3, 'PASAPORTE'), (4, 'CONSUMIDOR FINAL');

-- 5. Clientes
CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cedula_ruc VARCHAR(13) UNIQUE NOT NULL,
    tipo_identificacion_id INT,
    nombres VARCHAR(100),
    apellidos VARCHAR(100),
    direccion VARCHAR(255),
    telefono VARCHAR(20),
    email VARCHAR(100),
    usuario_creacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_modificacion_id INT,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (tipo_identificacion_id) REFERENCES tipos_identificacion(id)
);
INSERT INTO clientes (id, cedula_ruc, tipo_identificacion_id, nombres, apellidos, direccion) 
VALUES (1, '9999999999', 4, 'CONSUMIDOR', 'FINAL', 'QUITO');

-- 6. Proveedores
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

-- 7. Categorías y Productos
CREATE TABLE categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    usuario_creacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_modificacion_id INT,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

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

-- 8. Inventario
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
    FOREIGN KEY (unidad_medida_id) REFERENCES unidades_medida(id),
    FOREIGN KEY (sucursal_id) REFERENCES sucursales(id)
);

CREATE TABLE ajustes_inventario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    insumo_id INT,
    cantidad DECIMAL(10,2),
    tipo ENUM('INGRESO', 'EGRESO'),
    motivo VARCHAR(255),
    usuario_id INT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_modificacion_id INT,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (insumo_id) REFERENCES insumos(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

CREATE TABLE recetas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT,
    insumo_id INT,
    cantidad_requerida DECIMAL(10,4),
    usuario_creacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_modificacion_id INT,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id) REFERENCES productos(id),
    FOREIGN KEY (insumo_id) REFERENCES insumos(id)
);

-- 9. Ventas
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
    forma_pago VARCHAR(50),
    clave_acceso_sri VARCHAR(49),
    estado_sri VARCHAR(50),
    usuario_creacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_modificacion_id INT,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (sucursal_id) REFERENCES sucursales(id),
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

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

-- 10. Compras
CREATE TABLE compras (
    id INT AUTO_INCREMENT PRIMARY KEY,
    proveedor_id INT,
    establecimiento VARCHAR(3),
    punto_emision VARCHAR(3),
    numero_comprobante VARCHAR(50),
    total DECIMAL(10,2),
    fecha DATE,
    clave_acceso VARCHAR(49),
    numero_autorizacion VARCHAR(50),
    usuario_creacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_modificacion_id INT,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id),
    FOREIGN KEY (sucursal_id) REFERENCES sucursales(id)
);

CREATE TABLE detalles_compras (
    id INT AUTO_INCREMENT PRIMARY KEY,
    compra_id INT,
    insumo_id INT,
    cantidad DECIMAL(10,2),
    costo_unitario DECIMAL(10,4),
    subtotal DECIMAL(10,2),
    iva_valor DECIMAL(10,2) DEFAULT 0,
    FOREIGN KEY (compra_id) REFERENCES compras(id),
    FOREIGN KEY (insumo_id) REFERENCES insumos(id)
);

-- 11. Auditoría
CREATE TABLE auditoria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_id INT,
    accion VARCHAR(50),
    detalle TEXT,
    ip VARCHAR(45),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);
