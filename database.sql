-- database.sql (VERSIÓN PRO PLUS ENTERPRISE - FINAL)
SET FOREIGN_KEY_CHECKS=0;
DROP TABLE IF EXISTS auditoria, detalles_ventas, ventas, clientes, detalles_compras, compras, recetas, insumos, producto_precios, productos, categorias, sucursales, empresa, roles, tipos_identificacion, tipos_comprobantes, unidades_medida, plataformas;

-- 1. Tablas de Configuración Base
CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE tipos_identificacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    codigo_sri VARCHAR(2)
);

CREATE TABLE tipos_comprobantes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    codigo_sri VARCHAR(2)
);

CREATE TABLE unidades_medida (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE plataformas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE sucursales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    establecimiento VARCHAR(3) DEFAULT '001',
    punto_emision VARCHAR(3) DEFAULT '001',
    ultimo_secuencial INT DEFAULT 0,
    usuario_creacion_id INT,
    usuario_modificacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE empresa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ruc VARCHAR(13) NOT NULL,
    razon_social VARCHAR(255) NOT NULL,
    nombre_comercial VARCHAR(255),
    direccion_matriz TEXT,
    iva_porcentaje DECIMAL(5,2) DEFAULT 15.00,
    ambiente INT DEFAULT 1,
    color_tema VARCHAR(7) DEFAULT '#008938',
    icono_espera VARCHAR(50) DEFAULT 'fa-crown',
    firma_password VARCHAR(255),
    email_host VARCHAR(100),
    email_port INT,
    email_user VARCHAR(100),
    email_pass VARCHAR(100),
    email_use_tls TINYINT(1) DEFAULT 1,
    email_envio_automatico TINYINT(1) DEFAULT 0,
    obligado_contabilidad VARCHAR(2) DEFAULT 'NO',
    usuario_creacion_id INT,
    usuario_modificacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cedula VARCHAR(10) NOT NULL UNIQUE,
    tipo_identificacion_id INT DEFAULT 1,
    usuario VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    rol_id INT,
    sucursal_id INT,
    activo TINYINT(1) DEFAULT 1,
    FOREIGN KEY (rol_id) REFERENCES roles(id),
    FOREIGN KEY (sucursal_id) REFERENCES sucursales(id)
);

CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cedula_ruc VARCHAR(13) NOT NULL UNIQUE,
    tipo_identificacion_id INT,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    direccion TEXT,
    telefono VARCHAR(20),
    email VARCHAR(100),
    usuario_creacion_id INT,
    usuario_modificacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (tipo_identificacion_id) REFERENCES tipos_identificacion(id)
);

CREATE TABLE categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    usuario_creacion_id INT,
    usuario_modificacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    nombre VARCHAR(255) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    categoria_id INT,
    imagen LONGBLOB,
    mimetype VARCHAR(50),
    usuario_creacion_id INT,
    usuario_modificacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);

CREATE TABLE producto_precios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT,
    plataforma_id INT,
    precio DECIMAL(10,2) NOT NULL,
    UNIQUE(producto_id, plataforma_id),
    FOREIGN KEY (producto_id) REFERENCES productos(id),
    FOREIGN KEY (plataforma_id) REFERENCES plataformas(id)
);

CREATE TABLE insumos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    stock_actual DECIMAL(10,2) DEFAULT 0,
    stock_minimo DECIMAL(10,2) DEFAULT 0,
    unidad_medida_id INT,
    sucursal_id INT,
    usuario_creacion_id INT,
    usuario_modificacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (unidad_medida_id) REFERENCES unidades_medida(id),
    FOREIGN KEY (sucursal_id) REFERENCES sucursales(id)
);

CREATE TABLE recetas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT,
    insumo_id INT,
    cantidad_requerida DECIMAL(10,4) NOT NULL,
    usuario_creacion_id INT,
    usuario_modificacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id) REFERENCES productos(id),
    FOREIGN KEY (insumo_id) REFERENCES insumos(id)
);

CREATE TABLE ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_id INT,
    sucursal_id INT,
    cliente_id INT,
    plataforma_id INT,
    subtotal_0 DECIMAL(10,2) DEFAULT 0,
    subtotal_15 DECIMAL(10,2) DEFAULT 0,
    iva_valor DECIMAL(10,2) DEFAULT 0,
    total DECIMAL(10,2) NOT NULL,
    forma_pago VARCHAR(50),
    clave_acceso_sri VARCHAR(49),
    numero_autorizacion VARCHAR(50),
    autorizado_sri TINYINT(1) DEFAULT 0,
    estado_sri VARCHAR(100) DEFAULT 'PENDIENTE',
    xml_autorizado LONGTEXT,
    establecimiento VARCHAR(3),
    punto_emision VARCHAR(3),
    secuencial VARCHAR(9),
    email_enviado TINYINT(1) DEFAULT 0,
    usuario_creacion_id INT,
    usuario_modificacion_id INT,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (sucursal_id) REFERENCES sucursales(id),
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (plataforma_id) REFERENCES plataformas(id)
);

CREATE TABLE detalles_ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    venta_id INT,
    producto_id INT,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    iva_valor DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (venta_id) REFERENCES ventas(id),
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);

CREATE TABLE compras (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    proveedor_id INT,
    sucursal_id INT,
    establecimiento VARCHAR(3),
    punto_emision VARCHAR(3),
    numero_comprobante VARCHAR(20),
    total DECIMAL(10,2) NOT NULL,
    clave_acceso VARCHAR(49),
    numero_autorizacion VARCHAR(50),
    fecha_caducidad DATE,
    usuario_creacion_id INT,
    usuario_modificacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (sucursal_id) REFERENCES sucursales(id)
);

CREATE TABLE detalles_compras (
    id INT AUTO_INCREMENT PRIMARY KEY,
    compra_id INT,
    insumo_id INT,
    cantidad DECIMAL(10,2) NOT NULL,
    costo_unitario DECIMAL(10,4) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    iva_valor DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (compra_id) REFERENCES compras(id),
    FOREIGN KEY (insumo_id) REFERENCES insumos(id)
);

CREATE TABLE proveedores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ruc VARCHAR(13) NOT NULL UNIQUE,
    razon_social VARCHAR(255) NOT NULL,
    nombre_comercial VARCHAR(255),
    direccion TEXT,
    telefono VARCHAR(20),
    email VARCHAR(100),
    tipo_comprobante_id INT,
    usuario_creacion_id INT,
    usuario_modificacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (tipo_comprobante_id) REFERENCES tipos_comprobantes(id)
);

CREATE TABLE auditoria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_id INT,
    accion VARCHAR(50),
    detalle TEXT,
    ip VARCHAR(45),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

CREATE TABLE ajustes_inventario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    insumo_id INT,
    cantidad DECIMAL(10,2) NOT NULL,
    tipo ENUM('INGRESO', 'EGRESO') NOT NULL,
    motivo TEXT,
    usuario_id INT,
    usuario_creacion_id INT,
    usuario_modificacion_id INT,
    FOREIGN KEY (insumo_id) REFERENCES insumos(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- DATA INICIAL
INSERT INTO roles (id, nombre) VALUES (1, 'ADMINISTRADOR'), (2, 'CAJERO');
INSERT INTO tipos_identificacion (id, nombre, codigo_sri) VALUES (1, 'CEDULA', '05'), (2, 'RUC', '04'), (3, 'PASAPORTE', '06'), (4, 'CONSUMIDOR FINAL', '07');
INSERT INTO tipos_comprobantes (id, nombre, codigo_sri) VALUES (1, 'FACTURA', '01'), (2, 'NOTA DE VENTA', '02');
INSERT INTO unidades_medida (id, nombre) VALUES (1, 'UNIDAD'), (2, 'KILO'), (3, 'LITRO'), (4, 'LIBRA'), (5, 'GRAMO');
INSERT INTO plataformas (id, nombre) VALUES (1, 'LOCAL'), (2, 'PEDIDOS YA'), (3, 'UBER EATS');

INSERT INTO clientes (id, cedula_ruc, tipo_identificacion_id, nombres, apellidos, direccion) VALUES 
(1, '9999999999', 4, 'CONSUMIDOR', 'FINAL', 'S/N');

INSERT INTO sucursales (id, nombre, establecimiento, punto_emision) VALUES 
(1, 'MATRIZ QUITO', '001', '001');

INSERT INTO usuarios (cedula, usuario, password, sucursal_id, rol_id) VALUES 
('1002597886', 'ADMIN REINA', 'scrypt:32768:8:1$yNbECha0koWV3lez$3718b2aa226db0a915a130292f3631bd7f52a8f7ef510311b521d83067873a572bcb1fe58348d14910c7c9d7e7505cc418de43aa907dc234190b3eb0d106d2f7', 1, 1);

INSERT INTO empresa (id, ruc, razon_social, nombre_comercial, direccion_matriz, iva_porcentaje, ambiente, color_tema, obligado_contabilidad) VALUES 
(1, '1768041140001', 'SERVICIO ECUATORIANO DE CAPACITACION PROFESIONAL', 'SANDUCHES LA REINA', 'QUITO', 15.00, 1, '#008a4e', 'NO');

SET FOREIGN_KEY_CHECKS=1;
