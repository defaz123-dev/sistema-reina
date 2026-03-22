SET FOREIGN_KEY_CHECKS=0;

DROP TABLE IF EXISTS `anulaciones_factura`;
CREATE TABLE `anulaciones_factura` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `venta_id` int(11) NOT NULL,
  `motivo_anulacion` text NOT NULL,
  `fecha_solicitud` timestamp NOT NULL DEFAULT current_timestamp(),
  `estado_anulacion` enum('PENDIENTE','PROCESADO','ERROR') DEFAULT 'PENDIENTE',
  `comprobante_anulacion` longtext DEFAULT NULL,
  `mensaje_sri` text DEFAULT NULL,
  `usuario_id` int(11) DEFAULT NULL,
  `nc_clave_acceso` varchar(49) DEFAULT NULL,
  `nc_numero_autorizacion` varchar(50) DEFAULT NULL,
  `nc_xml_autorizado` longtext DEFAULT NULL,
  `intentos_envio` int(11) DEFAULT 0,
  `proximo_reintento` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `venta_id` (`venta_id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `anulaciones_factura_ibfk_1` FOREIGN KEY (`venta_id`) REFERENCES `ventas` (`id`),
  CONSTRAINT `anulaciones_factura_ibfk_2` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `auditoria`;
CREATE TABLE `auditoria` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp(),
  `usuario_id` int(11) DEFAULT NULL,
  `accion` varchar(100) DEFAULT NULL,
  `detalle` text DEFAULT NULL,
  `ip` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `auditoria_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `caja_detalle_fisico`;
CREATE TABLE `caja_detalle_fisico` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sesion_caja_id` int(11) NOT NULL,
  `tipo` enum('APERTURA','CIERRE') NOT NULL,
  `denominacion` decimal(10,2) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `subtotal` decimal(10,2) NOT NULL,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `sesion_caja_id` (`sesion_caja_id`),
  CONSTRAINT `caja_detalle_fisico_ibfk_1` FOREIGN KEY (`sesion_caja_id`) REFERENCES `sesiones_caja` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `cat_tarjetas`;
CREATE TABLE `cat_tarjetas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `activo` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `categorias`;
CREATE TABLE `categorias` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `usuario_creacion_id` int(11) DEFAULT NULL,
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `usuario_modificacion_id` int(11) DEFAULT NULL,
  `fecha_modificacion` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `cierre_diario_detalle_fisico`;
CREATE TABLE `cierre_diario_detalle_fisico` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cierre_diario_id` int(11) NOT NULL,
  `denominacion` decimal(10,2) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `subtotal` decimal(10,2) NOT NULL,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `cierre_diario_id` (`cierre_diario_id`),
  CONSTRAINT `cierre_diario_detalle_fisico_ibfk_1` FOREIGN KEY (`cierre_diario_id`) REFERENCES `cierres_diarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `cierres_diarios`;
CREATE TABLE `cierres_diarios` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sucursal_id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `cantidad_turnos` int(11) DEFAULT 1,
  `fecha_cierre` timestamp NOT NULL DEFAULT current_timestamp(),
  `fecha_dia` date NOT NULL,
  `total_ventas` decimal(10,2) DEFAULT 0.00,
  `total_efectivo` decimal(10,2) DEFAULT 0.00,
  `total_tarjetas` decimal(10,2) DEFAULT 0.00,
  `total_transferencias` decimal(10,2) DEFAULT 0.00,
  `total_egresos` decimal(10,2) DEFAULT 0.00,
  `real_efectivo` decimal(10,2) DEFAULT 0.00,
  `real_tarjeta` decimal(10,2) DEFAULT 0.00,
  `real_transferencia` decimal(10,2) DEFAULT 0.00,
  `dif_efectivo` decimal(10,2) DEFAULT 0.00,
  `dif_tarjeta` decimal(10,2) DEFAULT 0.00,
  `dif_transferencia` decimal(10,2) DEFAULT 0.00,
  `obs_efe` text DEFAULT NULL,
  `obs_tar` text DEFAULT NULL,
  `obs_tra` text DEFAULT NULL,
  `saldo_final_caja` decimal(10,2) DEFAULT 0.00,
  `observaciones` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `sucursal_id` (`sucursal_id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `cierres_diarios_ibfk_1` FOREIGN KEY (`sucursal_id`) REFERENCES `sucursales` (`id`),
  CONSTRAINT `cierres_diarios_ibfk_2` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `clientes`;
CREATE TABLE `clientes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cedula_ruc` varchar(13) NOT NULL,
  `tipo_identificacion_id` int(11) DEFAULT NULL,
  `tipo_documento` enum('CEDULA','RUC') DEFAULT NULL,
  `nombres` varchar(255) NOT NULL,
  `apellidos` varchar(255) NOT NULL,
  `direccion` varchar(255) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `usuario_creacion_id` int(11) DEFAULT NULL,
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `usuario_modificacion_id` int(11) DEFAULT NULL,
  `fecha_modificacion` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `cedula_ruc` (`cedula_ruc`),
  KEY `tipo_identificacion_id` (`tipo_identificacion_id`),
  CONSTRAINT `clientes_ibfk_1` FOREIGN KEY (`tipo_identificacion_id`) REFERENCES `tipos_identificacion` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `compras`;
CREATE TABLE `compras` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fecha` date NOT NULL,
  `proveedor_id` int(11) DEFAULT NULL,
  `establecimiento` varchar(3) DEFAULT '001',
  `punto_emision` varchar(3) DEFAULT '001',
  `sucursal_id` int(11) DEFAULT NULL,
  `numero_comprobante` varchar(50) DEFAULT NULL,
  `clave_acceso` varchar(49) DEFAULT NULL,
  `numero_autorizacion` varchar(50) DEFAULT NULL,
  `fecha_caducidad` date DEFAULT NULL,
  `total` decimal(10,2) DEFAULT NULL,
  `usuario_creacion_id` int(11) DEFAULT NULL,
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `usuario_modificacion_id` int(11) DEFAULT NULL,
  `fecha_modificacion` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `sesion_caja_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `proveedor_id` (`proveedor_id`),
  KEY `sucursal_id` (`sucursal_id`),
  KEY `fk_compras_sesion` (`sesion_caja_id`),
  CONSTRAINT `compras_ibfk_1` FOREIGN KEY (`proveedor_id`) REFERENCES `proveedores` (`id`),
  CONSTRAINT `compras_ibfk_2` FOREIGN KEY (`sucursal_id`) REFERENCES `sucursales` (`id`),
  CONSTRAINT `fk_compras_sesion` FOREIGN KEY (`sesion_caja_id`) REFERENCES `sesiones_caja` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `detalles_compras`;
CREATE TABLE `detalles_compras` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `compra_id` int(11) DEFAULT NULL,
  `insumo_id` int(11) DEFAULT NULL,
  `cantidad` decimal(10,2) DEFAULT NULL,
  `costo_unitario` decimal(10,4) DEFAULT NULL,
  `subtotal` decimal(10,2) DEFAULT NULL,
  `iva_valor` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `compra_id` (`compra_id`),
  KEY `insumo_id` (`insumo_id`),
  CONSTRAINT `detalles_compras_ibfk_1` FOREIGN KEY (`compra_id`) REFERENCES `compras` (`id`),
  CONSTRAINT `detalles_compras_ibfk_2` FOREIGN KEY (`insumo_id`) REFERENCES `insumos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `detalles_ventas`;
CREATE TABLE `detalles_ventas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `venta_id` int(11) DEFAULT NULL,
  `producto_id` int(11) DEFAULT NULL,
  `cantidad` int(11) DEFAULT NULL,
  `precio_unitario` decimal(10,2) DEFAULT NULL,
  `subtotal` decimal(10,2) DEFAULT NULL,
  `iva_valor` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `venta_id` (`venta_id`),
  KEY `producto_id` (`producto_id`),
  CONSTRAINT `detalles_ventas_ibfk_1` FOREIGN KEY (`venta_id`) REFERENCES `ventas` (`id`),
  CONSTRAINT `detalles_ventas_ibfk_2` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `egresos`;
CREATE TABLE `egresos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp(),
  `sucursal_id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `proveedor_id` int(11) DEFAULT NULL,
  `descripcion` text NOT NULL,
  `monto` decimal(10,2) NOT NULL,
  `tipo_documento` enum('FACTURA','NOTA_DE_VENTA','RECIBO_INTERNO') DEFAULT 'RECIBO_INTERNO',
  `numero_documento` varchar(50) DEFAULT NULL,
  `categoria` varchar(100) DEFAULT 'GASTOS VARIOS',
  `sesion_caja_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `sucursal_id` (`sucursal_id`),
  KEY `usuario_id` (`usuario_id`),
  KEY `proveedor_id` (`proveedor_id`),
  KEY `fk_egresos_sesion` (`sesion_caja_id`),
  CONSTRAINT `egresos_ibfk_1` FOREIGN KEY (`sucursal_id`) REFERENCES `sucursales` (`id`),
  CONSTRAINT `egresos_ibfk_2` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `egresos_ibfk_3` FOREIGN KEY (`proveedor_id`) REFERENCES `proveedores` (`id`),
  CONSTRAINT `fk_egresos_sesion` FOREIGN KEY (`sesion_caja_id`) REFERENCES `sesiones_caja` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `empresa`;
CREATE TABLE `empresa` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ruc` varchar(13) NOT NULL,
  `razon_social` varchar(255) NOT NULL,
  `nombre_comercial` varchar(255) DEFAULT NULL,
  `direccion_matriz` varchar(255) NOT NULL,
  `iva_porcentaje` decimal(5,2) DEFAULT 15.00,
  `obligado_contabilidad` varchar(2) DEFAULT 'NO',
  `agente_retencion` varchar(50) DEFAULT NULL,
  `contribuyente_especial` varchar(50) DEFAULT NULL,
  `ambiente` int(11) DEFAULT 1,
  `color_tema` varchar(7) DEFAULT '#008938',
  `firma_password` text DEFAULT NULL,
  `usuario_creacion_id` int(11) DEFAULT NULL,
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `usuario_modificacion_id` int(11) DEFAULT NULL,
  `fecha_modificacion` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `icono_espera` varchar(50) DEFAULT 'fa-crown',
  `email_host` varchar(100) DEFAULT NULL,
  `email_port` int(11) DEFAULT NULL,
  `email_user` varchar(100) DEFAULT NULL,
  `email_pass` varchar(100) DEFAULT NULL,
  `email_use_tls` tinyint(1) DEFAULT 1,
  `email_envio_automatico` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `flujo_caja`;
CREATE TABLE `flujo_caja` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp(),
  `sucursal_id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `tipo` enum('INGRESO','EGRESO') NOT NULL,
  `monto` decimal(10,2) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `referencia_id` int(11) DEFAULT NULL,
  `tipo_referencia` enum('VENTA','COMPRA','EGRESO_VARIO','APERTURA','CIERRE') NOT NULL,
  PRIMARY KEY (`id`),
  KEY `sucursal_id` (`sucursal_id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `flujo_caja_ibfk_1` FOREIGN KEY (`sucursal_id`) REFERENCES `sucursales` (`id`),
  CONSTRAINT `flujo_caja_ibfk_2` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `insumos`;
CREATE TABLE `insumos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) NOT NULL,
  `stock_actual` decimal(10,2) DEFAULT 0.00,
  `stock_minimo` decimal(10,2) DEFAULT 0.00,
  `unidad_medida_id` int(11) DEFAULT NULL,
  `sucursal_id` int(11) DEFAULT NULL,
  `usuario_creacion_id` int(11) DEFAULT NULL,
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `usuario_modificacion_id` int(11) DEFAULT NULL,
  `fecha_modificacion` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `unidad_medida_id` (`unidad_medida_id`),
  KEY `sucursal_id` (`sucursal_id`),
  CONSTRAINT `insumos_ibfk_1` FOREIGN KEY (`unidad_medida_id`) REFERENCES `unidades_medida` (`id`),
  CONSTRAINT `insumos_ibfk_2` FOREIGN KEY (`sucursal_id`) REFERENCES `sucursales` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `kardex`;
CREATE TABLE `kardex` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `insumo_id` int(11) NOT NULL,
  `sucursal_id` int(11) NOT NULL,
  `tipo_movimiento` varchar(50) NOT NULL,
  `motivo` varchar(255) DEFAULT NULL,
  `referencia_id` int(11) DEFAULT NULL,
  `cantidad_entrada` decimal(10,4) DEFAULT 0.0000,
  `cantidad_salida` decimal(10,4) DEFAULT 0.0000,
  `saldo_anterior` decimal(10,4) NOT NULL,
  `saldo_posterior` decimal(10,4) NOT NULL,
  `costo_unitario` decimal(10,4) DEFAULT NULL,
  `usuario_id` int(11) NOT NULL,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `insumo_id` (`insumo_id`),
  KEY `sucursal_id` (`sucursal_id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `kardex_ibfk_1` FOREIGN KEY (`insumo_id`) REFERENCES `insumos` (`id`),
  CONSTRAINT `kardex_ibfk_2` FOREIGN KEY (`sucursal_id`) REFERENCES `sucursales` (`id`),
  CONSTRAINT `kardex_ibfk_3` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `menus`;
CREATE TABLE `menus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `url` varchar(100) NOT NULL,
  `icono` varchar(50) DEFAULT NULL,
  `categoria` varchar(50) DEFAULT NULL,
  `orden` int(11) DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

DROP TABLE IF EXISTS `plataformas`;
CREATE TABLE `plataformas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `producto_precios`;
CREATE TABLE `producto_precios` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `producto_id` int(11) DEFAULT NULL,
  `plataforma_id` int(11) DEFAULT NULL,
  `precio` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_prod_plat` (`producto_id`,`plataforma_id`),
  KEY `plataforma_id` (`plataforma_id`),
  CONSTRAINT `producto_precios_ibfk_1` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `producto_precios_ibfk_2` FOREIGN KEY (`plataforma_id`) REFERENCES `plataformas` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `productos`;
CREATE TABLE `productos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `codigo` varchar(50) DEFAULT NULL,
  `nombre` varchar(150) NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `precios_json` text DEFAULT NULL,
  `categoria_id` int(11) DEFAULT NULL,
  `imagen` longblob DEFAULT NULL,
  `mimetype` varchar(50) DEFAULT NULL,
  `usuario_creacion_id` int(11) DEFAULT NULL,
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `usuario_modificacion_id` int(11) DEFAULT NULL,
  `fecha_modificacion` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`),
  KEY `categoria_id` (`categoria_id`),
  CONSTRAINT `productos_ibfk_1` FOREIGN KEY (`categoria_id`) REFERENCES `categorias` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `promocion_plataformas`;
CREATE TABLE `promocion_plataformas` (
  `promocion_id` int(11) NOT NULL,
  `plataforma_id` int(11) NOT NULL,
  `valor_especifico` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`promocion_id`,`plataforma_id`),
  KEY `promocion_plataformas_ibfk_2` (`plataforma_id`),
  CONSTRAINT `promocion_plataformas_ibfk_1` FOREIGN KEY (`promocion_id`) REFERENCES `promociones` (`id`) ON DELETE CASCADE,
  CONSTRAINT `promocion_plataformas_ibfk_2` FOREIGN KEY (`plataforma_id`) REFERENCES `plataformas` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `promocion_productos`;
CREATE TABLE `promocion_productos` (
  `promocion_id` int(11) NOT NULL,
  `producto_id` int(11) NOT NULL,
  PRIMARY KEY (`promocion_id`,`producto_id`),
  KEY `promocion_productos_ibfk_2` (`producto_id`),
  CONSTRAINT `promocion_productos_ibfk_1` FOREIGN KEY (`promocion_id`) REFERENCES `promociones` (`id`) ON DELETE CASCADE,
  CONSTRAINT `promocion_productos_ibfk_2` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `promociones`;
CREATE TABLE `promociones` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `tipo` enum('DESCUENTO','PRECIO_FIJO','2X1') NOT NULL,
  `valor` decimal(10,2) NOT NULL,
  `fecha_inicio` date DEFAULT NULL,
  `fecha_fin` date DEFAULT NULL,
  `activo` tinyint(1) DEFAULT 1,
  `usuario_creacion_id` int(11) DEFAULT NULL,
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `usuario_modificacion_id` int(11) DEFAULT NULL,
  `fecha_modificacion` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `proveedores`;
CREATE TABLE `proveedores` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ruc` varchar(13) NOT NULL,
  `razon_social` varchar(255) NOT NULL,
  `nombre_comercial` varchar(255) DEFAULT NULL,
  `direccion` varchar(255) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `tipo_comprobante_id` int(11) DEFAULT NULL,
  `usuario_creacion_id` int(11) DEFAULT NULL,
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `usuario_modificacion_id` int(11) DEFAULT NULL,
  `fecha_modificacion` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `ruc` (`ruc`),
  KEY `tipo_comprobante_id` (`tipo_comprobante_id`),
  CONSTRAINT `proveedores_ibfk_1` FOREIGN KEY (`tipo_comprobante_id`) REFERENCES `tipos_comprobantes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `recetas`;
CREATE TABLE `recetas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `producto_id` int(11) DEFAULT NULL,
  `insumo_id` int(11) DEFAULT NULL,
  `cantidad_requerida` decimal(10,4) NOT NULL,
  `usuario_creacion_id` int(11) DEFAULT NULL,
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `usuario_modificacion_id` int(11) DEFAULT NULL,
  `fecha_modificacion` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `producto_id` (`producto_id`),
  KEY `insumo_id` (`insumo_id`),
  CONSTRAINT `recetas_ibfk_1` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`),
  CONSTRAINT `recetas_ibfk_2` FOREIGN KEY (`insumo_id`) REFERENCES `insumos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `rol_menus`;
CREATE TABLE `rol_menus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `rol_id` int(11) DEFAULT NULL,
  `menu_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_rol_menu` (`rol_id`,`menu_id`),
  KEY `menu_id` (`menu_id`),
  CONSTRAINT `rol_menus_ibfk_1` FOREIGN KEY (`rol_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE,
  CONSTRAINT `rol_menus_ibfk_2` FOREIGN KEY (`menu_id`) REFERENCES `menus` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

DROP TABLE IF EXISTS `roles`;
CREATE TABLE `roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `sesiones_caja`;
CREATE TABLE `sesiones_caja` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sucursal_id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `fecha_apertura` timestamp NOT NULL DEFAULT current_timestamp(),
  `monto_inicial` decimal(10,2) NOT NULL DEFAULT 0.00,
  `fecha_cierre` timestamp NULL DEFAULT NULL,
  `monto_ventas_efectivo` decimal(10,2) DEFAULT 0.00,
  `monto_ventas_tarjeta` decimal(10,2) DEFAULT 0.00,
  `monto_ventas_transferencia` decimal(10,2) DEFAULT 0.00,
  `monto_egresos` decimal(10,2) DEFAULT 0.00,
  `monto_final_esperado` decimal(10,2) DEFAULT 0.00,
  `monto_final_real` decimal(10,2) DEFAULT 0.00,
  `diferencia` decimal(10,2) DEFAULT 0.00,
  `estado` enum('ABIERTA','CERRADA') DEFAULT 'ABIERTA',
  `observaciones` text DEFAULT NULL,
  `real_efectivo` decimal(10,2) DEFAULT 0.00,
  `real_tarjeta` decimal(10,2) DEFAULT 0.00,
  `real_transferencia` decimal(10,2) DEFAULT 0.00,
  `obs_efectivo` text DEFAULT NULL,
  `obs_tarjeta` text DEFAULT NULL,
  `obs_transferencia` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `sucursal_id` (`sucursal_id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `sesiones_caja_ibfk_1` FOREIGN KEY (`sucursal_id`) REFERENCES `sucursales` (`id`),
  CONSTRAINT `sesiones_caja_ibfk_2` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `sucursales`;
CREATE TABLE `sucursales` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `establecimiento` varchar(3) DEFAULT '001',
  `punto_emision` varchar(3) DEFAULT '001',
  `usuario_creacion_id` int(11) DEFAULT NULL,
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `usuario_modificacion_id` int(11) DEFAULT NULL,
  `fecha_modificacion` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `ultimo_secuencial` int(11) DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `tipos_comprobantes`;
CREATE TABLE `tipos_comprobantes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `tipos_identificacion`;
CREATE TABLE `tipos_identificacion` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `codigo_sri` varchar(2) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `unidades_medida`;
CREATE TABLE `unidades_medida` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `abreviatura` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `usuarios`;
CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cedula` varchar(13) NOT NULL,
  `tipo_identificacion_id` int(11) DEFAULT NULL,
  `usuario` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `sucursal_id` int(11) DEFAULT NULL,
  `rol_id` int(11) DEFAULT NULL,
  `activo` tinyint(1) DEFAULT 1,
  `usuario_creacion_id` int(11) DEFAULT NULL,
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `usuario_modificacion_id` int(11) DEFAULT NULL,
  `fecha_modificacion` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `cedula` (`cedula`),
  KEY `sucursal_id` (`sucursal_id`),
  KEY `tipo_identificacion_id` (`tipo_identificacion_id`),
  KEY `rol_id` (`rol_id`),
  CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`sucursal_id`) REFERENCES `sucursales` (`id`),
  CONSTRAINT `usuarios_ibfk_2` FOREIGN KEY (`tipo_identificacion_id`) REFERENCES `tipos_identificacion` (`id`),
  CONSTRAINT `usuarios_ibfk_3` FOREIGN KEY (`rol_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `ventas`;
CREATE TABLE `ventas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp(),
  `usuario_id` int(11) DEFAULT NULL,
  `sucursal_id` int(11) DEFAULT NULL,
  `cliente_id` int(11) DEFAULT NULL,
  `plataforma_id` int(11) DEFAULT NULL,
  `subtotal_0` decimal(10,2) DEFAULT NULL,
  `subtotal_15` decimal(10,2) DEFAULT NULL,
  `iva_valor` decimal(10,2) DEFAULT NULL,
  `total` decimal(10,2) DEFAULT NULL,
  `forma_pago` varchar(50) DEFAULT NULL,
  `clave_acceso_sri` varchar(49) DEFAULT NULL,
  `numero_autorizacion` varchar(50) DEFAULT NULL,
  `xml_autorizado` longtext DEFAULT NULL,
  `estado_sri` varchar(500) DEFAULT 'PENDIENTE',
  `autorizado_sri` tinyint(1) DEFAULT 0,
  `establecimiento` varchar(3) DEFAULT '001',
  `punto_emision` varchar(3) DEFAULT '001',
  `secuencial` varchar(9) DEFAULT NULL,
  `usuario_creacion_id` int(11) DEFAULT NULL,
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `usuario_modificacion_id` int(11) DEFAULT NULL,
  `fecha_modificacion` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `email_enviado` tinyint(1) DEFAULT 0,
  `id_tarjeta` int(11) DEFAULT NULL,
  `sesion_caja_id` int(11) DEFAULT NULL,
  `descuento_promo_id` int(11) DEFAULT NULL,
  `descuento_manual_instante` decimal(10,2) DEFAULT 0.00,
  `motivo_descuento_manual` varchar(255) DEFAULT NULL,
  `anulada` tinyint(1) DEFAULT 0,
  `intentos_envio` int(11) DEFAULT 0,
  `proximo_reintento` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  KEY `sucursal_id` (`sucursal_id`),
  KEY `cliente_id` (`cliente_id`),
  KEY `plataforma_id` (`plataforma_id`),
  KEY `fk_ventas_tarjeta` (`id_tarjeta`),
  KEY `fk_ventas_sesion` (`sesion_caja_id`),
  KEY `fk_ventas_promo` (`descuento_promo_id`),
  CONSTRAINT `fk_ventas_promo` FOREIGN KEY (`descuento_promo_id`) REFERENCES `promociones` (`id`),
  CONSTRAINT `fk_ventas_sesion` FOREIGN KEY (`sesion_caja_id`) REFERENCES `sesiones_caja` (`id`),
  CONSTRAINT `fk_ventas_tarjeta` FOREIGN KEY (`id_tarjeta`) REFERENCES `cat_tarjetas` (`id`),
  CONSTRAINT `ventas_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `ventas_ibfk_2` FOREIGN KEY (`sucursal_id`) REFERENCES `sucursales` (`id`),
  CONSTRAINT `ventas_ibfk_3` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`id`),
  CONSTRAINT `ventas_ibfk_4` FOREIGN KEY (`plataforma_id`) REFERENCES `plataformas` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `ventas_pagos`;
CREATE TABLE `ventas_pagos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `venta_id` int(11) NOT NULL,
  `metodo_pago` varchar(50) NOT NULL,
  `monto` decimal(10,2) NOT NULL,
  `id_tarjeta` int(11) DEFAULT NULL,
  `referencia` varchar(100) DEFAULT NULL,
  `cambio` decimal(10,2) DEFAULT 0.00,
  `fecha_pago` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `venta_id` (`venta_id`),
  KEY `id_tarjeta` (`id_tarjeta`),
  CONSTRAINT `ventas_pagos_ibfk_1` FOREIGN KEY (`venta_id`) REFERENCES `ventas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `ventas_pagos_ibfk_2` FOREIGN KEY (`id_tarjeta`) REFERENCES `cat_tarjetas` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

SET FOREIGN_KEY_CHECKS=1;
