-- database.sql (VERSIÓN LOCAL ACTUALIZADA - MULTITARIFAS Y BI)
SET FOREIGN_KEY_CHECKS=0;
DROP TABLE IF EXISTS auditoria, detalles_ventas, ventas, clientes, detalles_compras, compras, recetas, insumos, producto_precios, plataformas, productos, categorias, proveedores, usuarios, roles, sucursales, empresa, tipos_identificacion, tipos_comprobantes, unidades_medida, ajustes_inventario;
SET FOREIGN_KEY_CHECKS=1;

-- 1. Catálogos Base
CREATE TABLE unidades_medida (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    abreviatura VARCHAR(10)
);

CREATE TABLE tipos_identificacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    codigo_sri VARCHAR(2)
);

CREATE TABLE tipos_comprobantes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE plataformas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

-- 2. Estructura Principal
CREATE TABLE sucursales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    usuario_creacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_modificacion_id INT,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE empresa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ruc VARCHAR(13) NOT NULL,
    razon_social VARCHAR(255) NOT NULL,
    nombre_comercial VARCHAR(255),
    direccion_matriz VARCHAR(255) NOT NULL,
    iva_porcentaje DECIMAL(5,2) DEFAULT 15.00,
    obligado_contabilidad VARCHAR(2) DEFAULT 'NO',
    ambiente INT DEFAULT 1, -- 1: Pruebas, 2: Produccion
    color_tema VARCHAR(7) DEFAULT '#008938',
    usuario_creacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_modificacion_id INT,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cedula VARCHAR(13) NOT NULL UNIQUE,
    tipo_identificacion_id INT,
    usuario VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    sucursal_id INT,
    rol_id INT,
    activo TINYINT(1) DEFAULT 1,
    usuario_creacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_modificacion_id INT,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (sucursal_id) REFERENCES sucursales(id),
    FOREIGN KEY (tipo_identificacion_id) REFERENCES tipos_identificacion(id),
    FOREIGN KEY (rol_id) REFERENCES roles(id)
);

CREATE TABLE categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    usuario_creacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_modificacion_id INT,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE proveedores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ruc VARCHAR(13) NOT NULL UNIQUE,
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

CREATE TABLE productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    nombre VARCHAR(150) NOT NULL,
    precio DECIMAL(10,2) NOT NULL, -- Precio base (Local)
    categoria_id INT,
    imagen LONGBLOB,
    mimetype VARCHAR(50),
    usuario_creacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_modificacion_id INT,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);

CREATE TABLE producto_precios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT,
    plataforma_id INT,
    precio DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE,
    FOREIGN KEY (plataforma_id) REFERENCES plataformas(id) ON DELETE CASCADE,
    UNIQUE KEY unique_prod_plat (producto_id, plataforma_id)
);

CREATE TABLE insumos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
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

CREATE TABLE recetas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT,
    insumo_id INT,
    cantidad_requerida DECIMAL(10,4) NOT NULL,
    usuario_creacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_modificacion_id INT,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id) REFERENCES productos(id),
    FOREIGN KEY (insumo_id) REFERENCES insumos(id)
);

CREATE TABLE compras (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    proveedor_id INT,
    establecimiento VARCHAR(3),
    punto_emision VARCHAR(3),
    sucursal_id INT,
    numero_comprobante VARCHAR(50),
    clave_acceso VARCHAR(49),
    numero_autorizacion VARCHAR(50),
    fecha_caducidad DATE NULL,
    total DECIMAL(10,2),
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
    iva_valor DECIMAL(10,2),
    FOREIGN KEY (compra_id) REFERENCES compras(id),
    FOREIGN KEY (insumo_id) REFERENCES insumos(id)
);

CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cedula_ruc VARCHAR(13) NOT NULL UNIQUE,
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

CREATE TABLE ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_id INT,
    sucursal_id INT,
    cliente_id INT,
    plataforma_id INT,
    subtotal_0 DECIMAL(10,2),
    subtotal_15 DECIMAL(10,2),
    iva_valor DECIMAL(10,2),
    total DECIMAL(10,2),
    forma_pago VARCHAR(50),
    clave_acceso_sri VARCHAR(49),
    estado_sri VARCHAR(20) DEFAULT 'PENDIENTE',
    usuario_creacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
    cantidad INT,
    precio_unitario DECIMAL(10,2),
    subtotal DECIMAL(10,2),
    iva_valor DECIMAL(10,2),
    FOREIGN KEY (venta_id) REFERENCES ventas(id),
    FOREIGN KEY (producto_id) REFERENCES productos(id)
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

CREATE TABLE auditoria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_id INT,
    accion VARCHAR(100),
    detalle TEXT,
    ip VARCHAR(45),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- 3. Inserción de Datos Iniciales
INSERT INTO unidades_medida (id, nombre, abreviatura) VALUES 
(1, 'GRAMOS', 'gr'), (2, 'KILOS', 'kg'), (3, 'LITROS', 'lt'), (4, 'UNIDADES', 'u');

INSERT INTO tipos_identificacion (id, nombre, codigo_sri) VALUES 
(1, 'CEDULA', '05'), (2, 'RUC', '04'), (3, 'PASAPORTE', '06'), (4, 'CONSUMIDOR FINAL', '07');

INSERT INTO tipos_comprobantes (id, nombre) VALUES 
(1, 'FACTURA'), (2, 'NOTA DE VENTA');

INSERT INTO roles (id, nombre) VALUES (1, 'ADMIN'), (2, 'USER');

INSERT INTO plataformas (id, nombre) VALUES (1, 'LOCAL'), (2, 'PEDIDOS YA'), (3, 'UBER EATS');

INSERT INTO sucursales (id, nombre) VALUES 
(1, 'REINA VICTORIA PRINCIPAL'), (2, 'GRANADOS NORTE');

-- USUARIOS (Passwords encriptados con scrypt)
INSERT INTO usuarios (id, cedula, tipo_identificacion_id, usuario, password, sucursal_id, rol_id, activo) VALUES 
(1, '1002597886', 1, 'CHRISTIAN DEFAZ', 'scrypt:32768:8:1$aMgnwvz2kmlCAbeU$0faa2b09d46b93a49b127171fbdafea440fc6ffb652887fdaf39a9a3f1329d75f47ad43b21fe519fb6b5df5f087173d70cdcd0b2a03423e19386ffbcc72eb330', 1, 1, 1),
(2, '1714990726', 1, 'LILANA TADAY', 'scrypt:32768:8:1$yNbECha0koWV3lez$3718b2aa226db0a915a130292f3631bd7f52a8f7ef510311b521d83067873a572bcb1fe58348d14910c7c9d7e7505cc418de43aa907dc234190b3eb0d106d2f7', 1, 1, 1);

INSERT INTO empresa (id, ruc, razon_social, nombre_comercial, direccion_matriz, iva_porcentaje, ambiente, color_tema) VALUES 
(1, '1793023118001', 'ALIMENTOS LA REINA', 'SANDUCHES LA REINA', 'AV. PRINCIPAL Y SECUNDARIA', 15.00, 2, '#008a4e');
