-- =========================================================
-- SCRIPT ÚNICO DE DESPLIEGUE - SISTEMA REINA V3.1 (ENTERPRISE PRO PLUS)
-- Generado el: 30 de abril de 2026
-- =========================================================

SET FOREIGN_KEY_CHECKS=0;

-- 1. CREACIÓN DE ESTRUCTURAS --

DROP TABLE IF EXISTS `categorias`;
CREATE TABLE `categorias` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `usuario_creacion_id` int(11) DEFAULT NULL,
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `usuario_modificacion_id` int(11) DEFAULT NULL,
  `fecha_modificacion` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `tipos_identificacion`;
CREATE TABLE `tipos_identificacion` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `codigo_sri` varchar(2) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `roles`;
CREATE TABLE `roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `menus`;
CREATE TABLE `menus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `url` varchar(100) NOT NULL,
  `icono` varchar(50) DEFAULT NULL,
  `categoria` varchar(50) DEFAULT NULL,
  `orden` int(11) DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

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
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `productos`;
CREATE TABLE `productos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `codigo` varchar(50) DEFAULT NULL,
  `nombre` varchar(150) NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `precios_json` text DEFAULT NULL,
  `categoria_id` int(11) DEFAULT NULL,
  `imagen` varchar(255) DEFAULT NULL,
  `mimetype` varchar(50) DEFAULT NULL,
  `usuario_creacion_id` int(11) DEFAULT NULL,
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `usuario_modificacion_id` int(11) DEFAULT NULL,
  `fecha_modificacion` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`),
  KEY `categoria_id` (`categoria_id`),
  CONSTRAINT `productos_ibfk_1` FOREIGN KEY (`categoria_id`) REFERENCES `categorias` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `plataformas`;
CREATE TABLE `plataformas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `unidades_medida`;
CREATE TABLE `unidades_medida` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `abreviatura` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `maquinas_autorizadas`;
CREATE TABLE `maquinas_autorizadas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `hwid` varchar(255) NOT NULL,
  `nombre_terminal` varchar(100) NOT NULL,
  `sucursal_id` int(11) DEFAULT NULL,
  `fecha_registro` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `hwid` (`hwid`),
  KEY `sucursal_id` (`sucursal_id`),
  CONSTRAINT `maquinas_autorizadas_ibfk_1` FOREIGN KEY (`sucursal_id`) REFERENCES `sucursales` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `cat_tarjetas`;
CREATE TABLE `cat_tarjetas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `activo` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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

DROP TABLE IF EXISTS `promocion_productos`;
CREATE TABLE `promocion_productos` (
  `promocion_id` int(11) NOT NULL,
  `producto_id` int(11) NOT NULL,
  PRIMARY KEY (`promocion_id`,`producto_id`),
  KEY `promocion_productos_ibfk_2` (`producto_id`),
  CONSTRAINT `promocion_productos_ibfk_1` FOREIGN KEY (`promocion_id`) REFERENCES `promociones` (`id`) ON DELETE CASCADE,
  CONSTRAINT `promocion_productos_ibfk_2` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`) ON DELETE CASCADE
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
  `saldo_final_caja` decimal(10,2) DEFAULT 0.00,
  `observaciones` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `sucursal_id` (`sucursal_id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `cierres_diarios_ibfk_1` FOREIGN KEY (`sucursal_id`) REFERENCES `sucursales` (`id`),
  CONSTRAINT `cierres_diarios_ibfk_2` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
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
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 2. CARGA DE DATOS MAESTROS --

-- Datos para categorias
INSERT INTO `categorias` (`id`, `nombre`, `usuario_creacion_id`, `fecha_creacion`, `usuario_modificacion_id`, `fecha_modificacion`) VALUES (1, 'SANDUCHES DE 12 CM', 1, '2026-03-07 12:50:26', 1, '2026-03-07 12:50:26');
INSERT INTO `categorias` (`id`, `nombre`, `usuario_creacion_id`, `fecha_creacion`, `usuario_modificacion_id`, `fecha_modificacion`) VALUES (2, 'SANDUCHES DE 24 CM', 1, '2026-03-07 12:50:39', 1, '2026-03-07 12:50:39');
INSERT INTO `categorias` (`id`, `nombre`, `usuario_creacion_id`, `fecha_creacion`, `usuario_modificacion_id`, `fecha_modificacion`) VALUES (3, 'COMBOS', 1, '2026-03-07 12:50:56', 1, '2026-03-07 12:51:15');
INSERT INTO `categorias` (`id`, `nombre`, `usuario_creacion_id`, `fecha_creacion`, `usuario_modificacion_id`, `fecha_modificacion`) VALUES (4, 'DESAYUNOS', 1, '2026-03-07 12:51:25', 1, '2026-03-07 12:51:25');
INSERT INTO `categorias` (`id`, `nombre`, `usuario_creacion_id`, `fecha_creacion`, `usuario_modificacion_id`, `fecha_modificacion`) VALUES (5, 'ADICIONALES/EXTRAS', 1, '2026-03-07 12:51:39', 1, '2026-03-07 12:51:39');
INSERT INTO `categorias` (`id`, `nombre`, `usuario_creacion_id`, `fecha_creacion`, `usuario_modificacion_id`, `fecha_modificacion`) VALUES (6, 'BEBIDAS', 1, '2026-03-07 12:52:02', 1, '2026-03-07 12:52:02');

-- Datos para tipos_identificacion
INSERT INTO `tipos_identificacion` (`id`, `nombre`, `codigo_sri`) VALUES (1, 'CEDULA', '05');
INSERT INTO `tipos_identificacion` (`id`, `nombre`, `codigo_sri`) VALUES (2, 'RUC', '04');
INSERT INTO `tipos_identificacion` (`id`, `nombre`, `codigo_sri`) VALUES (3, 'PASAPORTE', '06');
INSERT INTO `tipos_identificacion` (`id`, `nombre`, `codigo_sri`) VALUES (4, 'CONSUMIDOR FINAL', '07');

-- Datos para sucursales
INSERT INTO `sucursales` (`id`, `nombre`, `establecimiento`, `punto_emision`, `usuario_creacion_id`, `fecha_creacion`, `usuario_modificacion_id`, `fecha_modificacion`, `ultimo_secuencial`) VALUES (1, 'REINA VICTORIA PRINCIPAL', '001', '001', NULL, '2026-03-07 12:18:40', 1, '2026-03-21 22:05:51', 58);
INSERT INTO `sucursales` (`id`, `nombre`, `establecimiento`, `punto_emision`, `usuario_creacion_id`, `fecha_creacion`, `usuario_modificacion_id`, `fecha_modificacion`, `ultimo_secuencial`) VALUES (2, 'GRANADOS NORTE', '002', '001', NULL, '2026-03-07 12:18:40', 1, '2026-03-08 19:51:14', 0);

-- Datos para roles
INSERT INTO `roles` (`id`, `nombre`) VALUES (1, 'ADMINISTRADOR');
INSERT INTO `roles` (`id`, `nombre`) VALUES (2, 'CAJERO');

-- Datos para menus
INSERT INTO `menus` (`id`, `nombre`, `url`, `icono`, `categoria`, `orden`) VALUES (1, 'Nueva Orden', 'pos', 'fas fa-cash-register', 'OPERATIVO', 1);
INSERT INTO `menus` (`id`, `nombre`, `url`, `icono`, `categoria`, `orden`) VALUES (2, 'Egresos', 'listar_egresos', 'fas fa-hand-holding-usd', 'OPERATIVO', 2);
INSERT INTO `menus` (`id`, `nombre`, `url`, `icono`, `categoria`, `orden`) VALUES (3, 'Turno Caja', 'sesion_caja', 'fas fa-lock', 'OPERATIVO', 3);
INSERT INTO `menus` (`id`, `nombre`, `url`, `icono`, `categoria`, `orden`) VALUES (4, 'Cierre Día', 'cierre_diario', 'fas fa-calendar-check', 'OPERATIVO', 4);
INSERT INTO `menus` (`id`, `nombre`, `url`, `icono`, `categoria`, `orden`) VALUES (5, 'Ventas', 'historial_ventas', 'fas fa-receipt', 'OPERATIVO', 5);
INSERT INTO `menus` (`id`, `nombre`, `url`, `icono`, `categoria`, `orden`) VALUES (6, 'Clientes', 'clientes', 'fas fa-address-book', 'OPERATIVO', 6);
INSERT INTO `menus` (`id`, `nombre`, `url`, `icono`, `categoria`, `orden`) VALUES (7, 'Compras', 'compras', 'fas fa-shopping-cart', 'ABASTECIMIENTO', 7);
INSERT INTO `menus` (`id`, `nombre`, `url`, `icono`, `categoria`, `orden`) VALUES (8, 'Proveedores', 'proveedores', 'fas fa-truck', 'ABASTECIMIENTO', 8);
INSERT INTO `menus` (`id`, `nombre`, `url`, `icono`, `categoria`, `orden`) VALUES (9, 'Usuarios', 'usuarios', 'fas fa-user-shield', 'ADMINISTRATIVO', 9);
INSERT INTO `menus` (`id`, `nombre`, `url`, `icono`, `categoria`, `orden`) VALUES (10, 'Inventario', 'inventario', 'fas fa-boxes', 'ADMINISTRATIVO', 10);
INSERT INTO `menus` (`id`, `nombre`, `url`, `icono`, `categoria`, `orden`) VALUES (11, 'Producto', 'productos', 'fas fa-hamburger', 'ADMINISTRATIVO', 11);
INSERT INTO `menus` (`id`, `nombre`, `url`, `icono`, `categoria`, `orden`) VALUES (12, 'Sucursales', 'sucursales', 'fas fa-store', 'ADMINISTRATIVO', 12);
INSERT INTO `menus` (`id`, `nombre`, `url`, `icono`, `categoria`, `orden`) VALUES (13, 'Categorías', 'categorias', 'fas fa-list', 'ADMINISTRATIVO', 13);
INSERT INTO `menus` (`id`, `nombre`, `url`, `icono`, `categoria`, `orden`) VALUES (14, 'Empresa', 'configuracion_empresa', 'fas fa-building', 'ADMINISTRATIVO', 14);
INSERT INTO `menus` (`id`, `nombre`, `url`, `icono`, `categoria`, `orden`) VALUES (15, 'Auditoría', 'ver_auditoria', 'fas fa-history', 'ADMINISTRATIVO', 15);
INSERT INTO `menus` (`id`, `nombre`, `url`, `icono`, `categoria`, `orden`) VALUES (16, 'Reportes', 'reportes', 'fas fa-chart-pie', 'ADMINISTRATIVO', 16);
INSERT INTO `menus` (`id`, `nombre`, `url`, `icono`, `categoria`, `orden`) VALUES (17, 'Anulaciones', 'listar_anulaciones', 'fas fa-ban', 'OPERATIVO', 17);
INSERT INTO `menus` (`id`, `nombre`, `url`, `icono`, `categoria`, `orden`) VALUES (18, 'Kardex', 'kardex_movimientos', 'fas fa-exchange-alt', 'ADMINISTRATIVO', 18);
INSERT INTO `menus` (`id`, `nombre`, `url`, `icono`, `categoria`, `orden`) VALUES (19, 'Promociones', 'listar_promociones', 'fas fa-gift', 'ADMINISTRATIVO', 19);
INSERT INTO `menus` (`id`, `nombre`, `url`, `icono`, `categoria`, `orden`) VALUES (20, 'Tarjetas/Plat.', 'tarjetas_plataformas', 'fas fa-credit-card', 'ADMINISTRATIVO', 20);
INSERT INTO `menus` (`id`, `nombre`, `url`, `icono`, `categoria`, `orden`) VALUES (21, 'Abrir Caja', 'sesion_caja', 'fas fa-unlock-alt', 'OPERATIVO', 0);
INSERT INTO `menus` (`id`, `nombre`, `url`, `icono`, `categoria`, `orden`) VALUES (22, 'Roles', 'listar_roles', 'fas fa-user-tag', 'SISTEMA', 100);
INSERT INTO `menus` (`id`, `nombre`, `url`, `icono`, `categoria`, `orden`) VALUES (23, 'Máquinas', 'listar_maquinas', 'fas fa-desktop', 'ADMINISTRATIVO', 21);

-- Datos para rol_menus
INSERT INTO `rol_menus` (`id`, `rol_id`, `menu_id`) VALUES (1, 1, 1);
INSERT INTO `rol_menus` (`id`, `rol_id`, `menu_id`) VALUES (2, 1, 2);
INSERT INTO `rol_menus` (`id`, `rol_id`, `menu_id`) VALUES (3, 1, 3);
INSERT INTO `rol_menus` (`id`, `rol_id`, `menu_id`) VALUES (4, 1, 4);
INSERT INTO `rol_menus` (`id`, `rol_id`, `menu_id`) VALUES (5, 1, 5);
INSERT INTO `rol_menus` (`id`, `rol_id`, `menu_id`) VALUES (6, 1, 6);
INSERT INTO `rol_menus` (`id`, `rol_id`, `menu_id`) VALUES (7, 1, 7);
INSERT INTO `rol_menus` (`id`, `rol_id`, `menu_id`) VALUES (8, 1, 8);
INSERT INTO `rol_menus` (`id`, `rol_id`, `menu_id`) VALUES (9, 1, 9);
INSERT INTO `rol_menus` (`id`, `rol_id`, `menu_id`) VALUES (10, 1, 10);
INSERT INTO `rol_menus` (`id`, `rol_id`, `menu_id`) VALUES (11, 1, 11);
INSERT INTO `rol_menus` (`id`, `rol_id`, `menu_id`) VALUES (12, 1, 12);
INSERT INTO `rol_menus` (`id`, `rol_id`, `menu_id`) VALUES (13, 1, 13);
INSERT INTO `rol_menus` (`id`, `rol_id`, `menu_id`) VALUES (14, 1, 14);
INSERT INTO `rol_menus` (`id`, `rol_id`, `menu_id`) VALUES (15, 1, 15);
INSERT INTO `rol_menus` (`id`, `rol_id`, `menu_id`) VALUES (16, 1, 16);
INSERT INTO `rol_menus` (`id`, `rol_id`, `menu_id`) VALUES (22, 1, 17);
INSERT INTO `rol_menus` (`id`, `rol_id`, `menu_id`) VALUES (23, 1, 18);
INSERT INTO `rol_menus` (`id`, `rol_id`, `menu_id`) VALUES (24, 1, 19);
INSERT INTO `rol_menus` (`id`, `rol_id`, `menu_id`) VALUES (25, 1, 20);
INSERT INTO `rol_menus` (`id`, `rol_id`, `menu_id`) VALUES (26, 1, 21);
INSERT INTO `rol_menus` (`id`, `rol_id`, `menu_id`) VALUES (27, 1, 22);
INSERT INTO `rol_menus` (`id`, `rol_id`, `menu_id`) VALUES (28, 1, 23);
INSERT INTO `rol_menus` (`id`, `rol_id`, `menu_id`) VALUES (17, 2, 1);
INSERT INTO `rol_menus` (`id`, `rol_id`, `menu_id`) VALUES (18, 2, 2);
INSERT INTO `rol_menus` (`id`, `rol_id`, `menu_id`) VALUES (19, 2, 3);
INSERT INTO `rol_menus` (`id`, `rol_id`, `menu_id`) VALUES (20, 2, 5);
INSERT INTO `rol_menus` (`id`, `rol_id`, `menu_id`) VALUES (21, 2, 6);

-- Datos para usuarios
INSERT INTO `usuarios` (`id`, `cedula`, `tipo_identificacion_id`, `usuario`, `password`, `sucursal_id`, `rol_id`, `activo`, `usuario_creacion_id`, `fecha_creacion`, `usuario_modificacion_id`, `fecha_modificacion`) VALUES (1, '1002597886', 1, 'CHRISTIAN DEFAZ', 'scrypt:32768:8:1$aMgnwvz2kmlCAbeU$0faa2b09d46b93a49b127171fbdafea440fc6ffb652887fdaf39a9a3f1329d75f47ad43b21fe519fb6b5df5f087173d70cdcd0b2a03423e19386ffbcc72eb330', 1, 1, 1, NULL, '2026-03-07 12:18:40', NULL, '2026-03-07 12:18:40');
INSERT INTO `usuarios` (`id`, `cedula`, `tipo_identificacion_id`, `usuario`, `password`, `sucursal_id`, `rol_id`, `activo`, `usuario_creacion_id`, `fecha_creacion`, `usuario_modificacion_id`, `fecha_modificacion`) VALUES (2, '1714990726', 1, 'LILANA TADAY', 'scrypt:32768:8:1$yNbECha0koWV3lez$3718b2aa226db0a915a130292f3631bd7f52a8f7ef510311b521d83067873a572bcb1fe58348d14910c7c9d7e7505cc418de43aa907dc234190b3eb0d106d2f7', 1, 1, 1, NULL, '2026-03-07 12:18:40', NULL, '2026-03-07 12:18:40');
INSERT INTO `usuarios` (`id`, `cedula`, `tipo_identificacion_id`, `usuario`, `password`, `sucursal_id`, `rol_id`, `activo`, `usuario_creacion_id`, `fecha_creacion`, `usuario_modificacion_id`, `fecha_modificacion`) VALUES (3, '12345', 3, 'JUAN LOPEZ', 'scrypt:32768:8:1$DQfw5FfUmA8WyDrT$bdd38e6da066e8079792d0518b0f5744eb33a8ea00df6329b56cf324ec961126177e718fb7924550819c8c4979926d931ad7a6525e8f1b5f6c680721f95d622d', 1, 2, 1, NULL, '2026-04-30 18:15:32', NULL, '2026-04-30 19:24:06');

-- Datos para plataformas
INSERT INTO `plataformas` (`id`, `nombre`) VALUES (1, 'LOCAL');
INSERT INTO `plataformas` (`id`, `nombre`) VALUES (2, 'PEDIDOS YA');
INSERT INTO `plataformas` (`id`, `nombre`) VALUES (3, 'UBER EATS');

-- Datos para unidades_medida
INSERT INTO `unidades_medida` (`id`, `nombre`, `abreviatura`) VALUES (1, 'UNIDAD', 'und');
INSERT INTO `unidades_medida` (`id`, `nombre`, `abreviatura`) VALUES (2, 'KILOGRAMO', 'kg');
INSERT INTO `unidades_medida` (`id`, `nombre`, `abreviatura`) VALUES (3, 'GRAMO', 'g');
INSERT INTO `unidades_medida` (`id`, `nombre`, `abreviatura`) VALUES (4, 'LIBRA', 'lb');
INSERT INTO `unidades_medida` (`id`, `nombre`, `abreviatura`) VALUES (5, 'LITRO', 'l');
INSERT INTO `unidades_medida` (`id`, `nombre`, `abreviatura`) VALUES (6, 'MILILITRO', 'ml');
INSERT INTO `unidades_medida` (`id`, `nombre`, `abreviatura`) VALUES (7, 'PAQUETE', 'paq');
INSERT INTO `unidades_medida` (`id`, `nombre`, `abreviatura`) VALUES (8, 'CAJA', 'caja');
INSERT INTO `unidades_medida` (`id`, `nombre`, `abreviatura`) VALUES (9, 'GALON', 'gal');
INSERT INTO `unidades_medida` (`id`, `nombre`, `abreviatura`) VALUES (10, 'ONZA', 'oz');
INSERT INTO `unidades_medida` (`id`, `nombre`, `abreviatura`) VALUES (11, 'DOCENA', 'doc');
INSERT INTO `unidades_medida` (`id`, `nombre`, `abreviatura`) VALUES (12, 'SACO', 'saco');
INSERT INTO `unidades_medida` (`id`, `nombre`, `abreviatura`) VALUES (13, 'BOTELLA', 'bot');
INSERT INTO `unidades_medida` (`id`, `nombre`, `abreviatura`) VALUES (14, 'PORCION', 'por');
INSERT INTO `unidades_medida` (`id`, `nombre`, `abreviatura`) VALUES (15, 'ATADO', 'atado');

-- Datos para cat_tarjetas
INSERT INTO `cat_tarjetas` (`id`, `nombre`, `activo`) VALUES (1, 'VISA', 1);
INSERT INTO `cat_tarjetas` (`id`, `nombre`, `activo`) VALUES (2, 'MASTERCARD', 1);
INSERT INTO `cat_tarjetas` (`id`, `nombre`, `activo`) VALUES (3, 'AMERICAN EXPRESS', 1);
INSERT INTO `cat_tarjetas` (`id`, `nombre`, `activo`) VALUES (4, 'DINERS CLUB', 1);
INSERT INTO `cat_tarjetas` (`id`, `nombre`, `activo`) VALUES (5, 'DISCOVER', 1);

-- Datos para empresa
INSERT INTO `empresa` (`id`, `ruc`, `razon_social`, `nombre_comercial`, `direccion_matriz`, `iva_porcentaje`, `obligado_contabilidad`, `agente_retencion`, `contribuyente_especial`, `ambiente`, `color_tema`, `firma_password`, `usuario_creacion_id`, `fecha_creacion`, `usuario_modificacion_id`, `fecha_modificacion`, `icono_espera`, `email_host`, `email_port`, `email_user`, `email_pass`, `email_use_tls`, `email_envio_automatico`) VALUES (1, '1768041140001', 'SERVICIO ECUATORIANO DE CAPACITACION PROFESIONAL', 'SANDUCHES LA REINA', 'QUITO', '15.00', 'SI', NULL, NULL, 1, '#008a4e', 'gAAAAABpruTj4QHL3iPK-BqHWuVfKENGcY8QlIJV3MrMxLSqPEuWl66eBYKOz17mhAS4EdUrEUyHdMNokLZeRifhoE1zNfA40w==', NULL, '2026-03-07 12:18:40', 1, '2026-03-09 10:18:59', 'fa-crown', 'smtp.gmail.com', 587, 'cdgo28@gmail.com', 'bmfk gcpp nrcu qxfx', 1, 1);

-- Datos para productos
INSERT INTO `productos` (`id`, `codigo`, `nombre`, `precio`, `precios_json`, `categoria_id`, `imagen`, `mimetype`, `usuario_creacion_id`, `fecha_creacion`, `usuario_modificacion_id`, `fecha_modificacion`) VALUES (1, 'P01', 'PERNIL 12CM', '3.50', NULL, 1, 'prod_1.jpg', 'image/jpeg', 1, '2026-03-07 13:27:42', 1, '2026-04-30 19:48:04');
INSERT INTO `productos` (`id`, `codigo`, `nombre`, `precio`, `precios_json`, `categoria_id`, `imagen`, `mimetype`, `usuario_creacion_id`, `fecha_creacion`, `usuario_modificacion_id`, `fecha_modificacion`) VALUES (2, 'P02', 'PERNIL 24CM', '6.50', NULL, 2, 'prod_2.jpg', 'image/jpeg', 1, '2026-03-07 13:28:47', 1, '2026-04-30 19:48:04');

SET FOREIGN_KEY_CHECKS=1;
-- FIN DEL SCRIPT --
