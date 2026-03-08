-- database_nube.sql (VERSIÓN PRO PLUS ENTERPRISE - FINAL - LIMPIEZA TOTAL)
SET FOREIGN_KEY_CHECKS=0;

-- BORRADO TOTAL DE TABLAS (ORDENADO POR DEPENDENCIAS)
DROP TABLE IF EXISTS ajustes_inventario;
DROP TABLE IF EXISTS auditoria;
DROP TABLE IF EXISTS detalles_ventas;
DROP TABLE IF EXISTS ventas;
DROP TABLE IF EXISTS detalles_compras;
DROP TABLE IF EXISTS compras;
DROP TABLE IF EXISTS producto_precios;
DROP TABLE IF EXISTS recetas;
DROP TABLE IF EXISTS productos;
DROP TABLE IF EXISTS insumos;
DROP TABLE IF EXISTS categorias;
DROP TABLE IF EXISTS clientes;
DROP TABLE IF EXISTS usuarios;
DROP TABLE IF EXISTS proveedores;
DROP TABLE IF EXISTS empresa;
DROP TABLE IF EXISTS sucursales;
DROP TABLE IF EXISTS plataformas;
DROP TABLE IF EXISTS unidades_medida;
DROP TABLE IF EXISTS tipos_comprobantes;
DROP TABLE IF EXISTS tipos_identificacion;
DROP TABLE IF EXISTS roles;

-- 1. TABLAS DE CONFIGURACIÓN BASE
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

-- 2. TABLAS ESTRUCTURALES
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
    firma_password TEXT,
    email_host VARCHAR(100),
    email_port INT,
    email_user VARCHAR(100),
    email_pass VARCHAR(100),
    email_use_tls TINYINT(1) DEFAULT 1,
    email_envio_automatico TINYINT(1) DEFAULT 0,
    obligado_contabilidad VARCHAR(2) DEFAULT 'NO',
    agente_retencion VARCHAR(50),
    contribuyente_especial VARCHAR(50),
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
    usuario_creacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_modificacion_id INT,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
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

-- 3. DATA ESTRUCTURAL
INSERT INTO tipos_identificacion (id, nombre, codigo_sri) VALUES (1, 'CEDULA', '05'), (2, 'RUC', '04'), (3, 'PASAPORTE', '06'), (4, 'CONSUMIDOR FINAL', '07');
INSERT INTO tipos_comprobantes (id, nombre, codigo_sri) VALUES (1, 'FACTURA', '01'), (2, 'NOTA DE VENTA', '02');
INSERT INTO unidades_medida (id, nombre) VALUES (1, 'UNIDAD'), (2, 'KILO'), (3, 'LITRO'), (4, 'LIBRA'), (5, 'GRAMO');
INSERT INTO plataformas (id, nombre) VALUES (1, 'LOCAL'), (2, 'PEDIDOS YA'), (3, 'UBER EATS');

-- 4. DATA REAL (USUARIOS, SUCURSALES, EMPRESA, ROLES, CATEGORIAS)
INSERT INTO roles (id, nombre) VALUES (1, 'ADMINISTRADOR'), (2, 'CAJERO');

INSERT INTO sucursales (id, nombre, establecimiento, punto_emision, ultimo_secuencial) VALUES
(1, 'REINA VICTORIA PRINCIPAL', '001', '001', 16),
(2, 'GRANADOS NORTE', '002', '001', 10);

INSERT INTO categorias (id, nombre, usuario_creacion_id, usuario_modificacion_id) VALUES
(1, 'SANDUCHES DE 12 CM', 1, 1),
(2, 'SANDUCHES DE 24 CM', 1, 1),
(3, 'COMBOS', 1, 1),
(4, 'DESAYUNOS', 1, 1),
(5, 'ADICIONALES/EXTRAS', 1, 1),
(6, 'BEBIDAS', 1, 1);

INSERT INTO empresa (id, ruc, razon_social, nombre_comercial, direccion_matriz, iva_porcentaje, obligado_contabilidad, ambiente, color_tema, firma_password, icono_espera, email_host, email_port, email_user, email_pass, email_use_tls, email_envio_automatico) VALUES
(1, '1768041140001', 'SERVICIO ECUATORIANO DE CAPACITACION PROFESIONAL', 'SANDUCHES LA REINA', 'QUITO', 15.00, 'SI', 1, '#008a4e', 'gAAAAABprKPD19ZzB5VWNyNKdlrX51PGx2j6n_fVgIQQinNjk_db3Fhf_REAwfvYrW3_dRnu1F4xRH0Lc5Vmnuqq_hdZSrvffw==', 'fa-crown', 'smtp.gmail.com', 587, 'cdgo28@gmail.com', 'bmfk gcpp nrcu qxfx', 1, 1);

INSERT INTO usuarios (id, cedula, tipo_identificacion_id, usuario, password, sucursal_id, rol_id, activo) VALUES
(1, '1002597886', 1, 'CHRISTIAN DEFAZ', 'scrypt:32768:8:1$aMgnwvz2kmlCAbeU$0faa2b09d46b93a49b127171fbdafea440fc6ffb652887fdaf39a9a3f1329d75f47ad43b21fe519fb6b5df5f087173d70cdcd0b2a03423e19386ffbcc72eb330', 1, 1, 1),
(2, '1714990726', 1, 'LILANA TADAY', 'scrypt:32768:8:1$yNbECha0koWV3lez$3718b2aa226db0a915a130292f3631bd7f52a8f7ef510311b521d83067873a572bcb1fe58348d14910c7c9d7e7505cc418de43aa907dc234190b3eb0d106d2f7', 1, 1, 1);

INSERT INTO clientes (id, cedula_ruc, tipo_identificacion_id, nombres, apellidos, direccion) VALUES 
(1, '9999999999', 4, 'CONSUMIDOR', 'FINAL', 'S/N');

SET FOREIGN_KEY_CHECKS=1;
