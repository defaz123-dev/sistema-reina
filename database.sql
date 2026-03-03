-- database.sql (SISTEMA REINA - VERSIÓN CONSOLIDADA)
CREATE DATABASE IF NOT EXISTS sistema_reina;
USE sistema_reina;

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
SET FOREIGN_KEY_CHECKS = 1;

-- 1. Sucursales
CREATE TABLE sucursales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

-- 2. Usuarios
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    sucursal_id INT,
    rol ENUM('ADMIN', 'VENDEDOR', 'SUPERVISOR') DEFAULT 'VENDEDOR',
    activo TINYINT(1) DEFAULT 1,
    FOREIGN KEY (sucursal_id) REFERENCES sucursales(id)
);

-- 3. Categorías
CREATE TABLE categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

-- 4. Insumos
CREATE TABLE insumos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    stock_actual DECIMAL(10,2) DEFAULT 0,
    stock_minimo DECIMAL(10,2) DEFAULT 0,
    unidad_medida VARCHAR(20) NOT NULL,
    sucursal_id INT,
    FOREIGN KEY (sucursal_id) REFERENCES sucursales(id)
);

-- 4.1 Ajustes de Inventario
CREATE TABLE ajustes_inventario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    insumo_id INT,
    cantidad DECIMAL(10,2),
    tipo ENUM('INGRESO', 'EGRESO'),
    motivo VARCHAR(255),
    usuario_id INT,
    FOREIGN KEY (insumo_id) REFERENCES insumos(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- 5. Productos
CREATE TABLE productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    categoria_id INT,
    imagen LONGBLOB,
    mimetype VARCHAR(50),
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);

-- 6. Recetas
CREATE TABLE recetas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT,
    insumo_id INT,
    cantidad_requerida DECIMAL(10,2),
    FOREIGN KEY (producto_id) REFERENCES productos(id),
    FOREIGN KEY (insumo_id) REFERENCES insumos(id)
);

-- 7. Clientes
CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cedula_ruc VARCHAR(20) UNIQUE NOT NULL,
    tipo_documento ENUM('CEDULA', 'RUC'),
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    direccion VARCHAR(255),
    telefono VARCHAR(20),
    email VARCHAR(100)
);

-- 8. Tipos de Comprobantes
CREATE TABLE tipos_comprobantes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

-- 9. Proveedores
CREATE TABLE proveedores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ruc VARCHAR(13) UNIQUE NOT NULL,
    razon_social VARCHAR(255) NOT NULL,
    nombre_comercial VARCHAR(255),
    direccion VARCHAR(255),
    telefono VARCHAR(20),
    email VARCHAR(100),
    tipo_comprobante_id INT,
    FOREIGN KEY (tipo_comprobante_id) REFERENCES tipos_comprobantes(id)
);

-- 10. Compras
CREATE TABLE compras (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATETIME NOT NULL,
    proveedor_id INT,
    sucursal_id INT,
    numero_comprobante VARCHAR(50),
    clave_acceso VARCHAR(49),
    total DECIMAL(10,2),
    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id),
    FOREIGN KEY (sucursal_id) REFERENCES sucursales(id)
);

-- 11. Detalles Compras
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

-- 12. Ventas
CREATE TABLE ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_id INT,
    sucursal_id INT,
    cliente_id INT,
    total DECIMAL(10,2),
    forma_pago VARCHAR(50) DEFAULT 'EFECTIVO',
    clave_acceso_sri VARCHAR(49),
    estado_sri VARCHAR(50) DEFAULT 'CREADA',
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (sucursal_id) REFERENCES sucursales(id),
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

-- 13. Detalles Ventas
CREATE TABLE detalles_ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    venta_id INT,
    producto_id INT,
    cantidad INT,
    precio_unitario DECIMAL(10,2),
    subtotal DECIMAL(10,2),
    FOREIGN KEY (venta_id) REFERENCES ventas(id),
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);

-- 14. Empresa
CREATE TABLE empresa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ruc VARCHAR(13) NOT NULL,
    razon_social VARCHAR(255) NOT NULL,
    nombre_comercial VARCHAR(255),
    direccion_matriz VARCHAR(255) NOT NULL,
    obligado_contabilidad VARCHAR(2) DEFAULT 'NO',
    ambiente INT DEFAULT 1
);

-- 15. Auditoría Global
CREATE TABLE auditoria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_id INT,
    accion VARCHAR(100),
    detalle TEXT,
    ip VARCHAR(45),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- INSERTS INICIALES --
INSERT INTO sucursales (nombre) VALUES ('Reina Victoria Principal'), ('Granados');

INSERT INTO tipos_comprobantes (nombre) VALUES ('FACTURA'), ('NOTA DE VENTA');

INSERT INTO empresa (ruc, razon_social, nombre_comercial, direccion_matriz, obligado_contabilidad, ambiente) 
VALUES ('1790000000001', 'EMPRESA DE PRUEBA S.A.', 'SANDUCHES LA REINA', 'Av. Principal y Secundaria', 'SI', 1);

INSERT INTO clientes (cedula_ruc, tipo_documento, nombres, apellidos, direccion) 
VALUES ('9999999999', 'CEDULA', 'CONSUMIDOR', 'FINAL', 'S/N');

INSERT INTO categorias (nombre) VALUES ('Sándwiches Pernil'), ('Sándwiches Pollo'), ('Sándwiches Atún'), ('Bebidas'), ('Adicionales');

INSERT INTO insumos (nombre, stock_actual, unidad_medida, sucursal_id) VALUES 
('Carne de Pernil', 5000.00, 'gramos', 1),
('Pechuga de Pollo', 5000.00, 'gramos', 1),
('Mezcla de Atún', 3000.00, 'gramos', 1),
('Pan 15cm', 100, 'unidades', 1),
('Pan 30cm', 100, 'unidades', 1),
('Pan 12cm', 50, 'unidades', 1),
('Pan 24cm', 50, 'unidades', 1),
('Coca Cola 500ml', 48, 'unidades', 1),
('Queso', 2000.00, 'gramos', 1),
('Tocino', 1000.00, 'gramos', 1);

INSERT INTO productos (codigo, nombre, precio, categoria_id) VALUES 
('P12', 'Pernil 12cm', 12.00, 1),
('P24', 'Pernil 24cm', 22.00, 1),
('L15', 'Pollo 15cm', 14.50, 2),
('L30', 'Pollo 30cm', 24.50, 2),
('T15', 'Atún 15cm', 13.50, 3),
('T30', 'Atún 30cm', 23.50, 3),
('C01', 'Coca Cola', 3.50, 4),
('EXT01', 'Extra Queso', 1.50, 5),
('EXT02', 'Extra Tocino', 2.00, 5);

INSERT INTO usuarios (usuario, password, sucursal_id, rol) VALUES 
('admin', 'pbkdf2:sha256:600000$u8U7W6zY$d8a7e56b4f5c9d2a1b3e4f5c6d7a8b9c0d1e2f3g4h5i6j7k8l9m0n1o2p3q4r5s', 1, 'ADMIN');
