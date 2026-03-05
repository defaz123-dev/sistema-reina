-- database.sql (ESQUEMA LOCAL ACTUALIZADO)
SET FOREIGN_KEY_CHECKS=0;
DROP TABLE IF EXISTS auditoria, detalles_ventas, ventas, detalles_compras, compras, recetas, insumos, productos, categorias, proveedores, usuarios, sucursales, empresa, tipos_identificacion, tipos_comprobantes, unidades_medida, ajustes_inventario;
SET FOREIGN_KEY_CHECKS=1;

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
    ambiente INT DEFAULT 1,
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
