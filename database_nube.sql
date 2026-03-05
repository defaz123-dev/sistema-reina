-- database_nube.sql (VERSIÓN WHITELABEL ACTUALIZADA)
SET FOREIGN_KEY_CHECKS=0;
DROP TABLE IF EXISTS auditoria, detalles_ventas, ventas, clientes, detalles_compras, compras, recetas, insumos, productos, categorias, proveedores, usuarios, sucursales, empresa, tipos_identificacion, tipos_comprobantes, unidades_medida, ajustes_inventario;
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
    usuario VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    sucursal_id INT,
    rol ENUM('ADMIN', 'VENDEDOR') DEFAULT 'VENDEDOR',
    activo TINYINT(1) DEFAULT 1,
    usuario_creacion_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_modificacion_id INT,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (sucursal_id) REFERENCES sucursales(id)
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
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
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

-- 3. Inserción de Datos Iniciales (Usuarios Locales y Catálogos)
INSERT INTO unidades_medida (id, nombre, abreviatura) VALUES 
(1, 'GRAMOS', 'gr'), (2, 'KILOS', 'kg'), (3, 'LITROS', 'lt'), (4, 'UNIDADES', 'u');

INSERT INTO tipos_identificacion (id, nombre, codigo_sri) VALUES 
(1, 'CEDULA', '05'), (2, 'RUC', '04'), (3, 'PASAPORTE', '06'), (4, 'CONSUMIDOR FINAL', '07');

INSERT INTO tipos_comprobantes (id, nombre) VALUES 
(1, 'FACTURA'), (2, 'NOTA DE VENTA');

INSERT INTO sucursales (id, nombre) VALUES 
(1, 'REINA VICTORIA PRINCIPAL'), (2, 'GRANADOS NORTE');

INSERT INTO usuarios (id, usuario, password, sucursal_id, rol, activo) VALUES 
(1, 'admin', 'scrypt:32768:8:1$OSyt2StROGDDPy4f$7a2ff17725e547c97110d2560d400e6126d2172d277fd22c61b7342b7a34b0bc07a7cd6e57a997202b3887261e6da9f79e933d46a33f239c4613891a95d0825b', 1, 'ADMIN', 1),
(2, 'liliana', 'scrypt:32768:8:1$0KzrMh3tnG7kEoxZ$ded6e5fc4aad675c0debb2af7caa2338dd6e51c3f04fc412a06a3d8104424c2a65bd938701ed0ec0701e49b2961037ad276cc5a9a6c684f2ef014d0c77b862f5', 1, 'ADMIN', 1);

INSERT INTO empresa (id, ruc, razon_social, nombre_comercial, direccion_matriz, iva_porcentaje, ambiente, color_tema) VALUES 
(1, '1793023118001', 'ALIMENTOS LA REINA', 'SANDUCHES LA REINA', 'AV. PRINCIPAL Y SECUNDARIA', 15.00, 2, '#008a4e');
