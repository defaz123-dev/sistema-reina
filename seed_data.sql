SET FOREIGN_KEY_CHECKS=0;

-- Data for roles
TRUNCATE TABLE `roles`;
INSERT INTO `roles` (`id`, `nombre`) VALUES
(1, 'ADMINISTRADOR'),
(2, 'CAJERO');

-- Data for tipos_identificacion
TRUNCATE TABLE `tipos_identificacion`;
INSERT INTO `tipos_identificacion` (`id`, `nombre`, `codigo_sri`) VALUES
(1, 'CEDULA', '05'),
(2, 'RUC', '04'),
(3, 'PASAPORTE', '06'),
(4, 'CONSUMIDOR FINAL', '07');

-- Data for tipos_comprobantes
TRUNCATE TABLE `tipos_comprobantes`;
INSERT INTO `tipos_comprobantes` (`id`, `nombre`) VALUES
(1, 'FACTURA'),
(2, 'NOTA DE VENTA');

-- Data for sucursales
TRUNCATE TABLE `sucursales`;
INSERT INTO `sucursales` (`id`, `nombre`, `establecimiento`, `punto_emision`, `usuario_creacion_id`, `fecha_creacion`, `usuario_modificacion_id`, `fecha_modificacion`, `ultimo_secuencial`) VALUES
(1, 'REINA VICTORIA PRINCIPAL', '001', '001', NULL, '2026-03-07 12:18:40', 1, '2026-03-15 21:33:24', 56),
(2, 'GRANADOS NORTE', '002', '001', NULL, '2026-03-07 12:18:40', 1, '2026-03-08 19:51:14', 0);

-- Data for usuarios
TRUNCATE TABLE `usuarios`;
INSERT INTO `usuarios` (`id`, `cedula`, `tipo_identificacion_id`, `usuario`, `password`, `sucursal_id`, `rol_id`, `activo`, `usuario_creacion_id`, `fecha_creacion`, `usuario_modificacion_id`, `fecha_modificacion`) VALUES
(1, '1002597886', 1, 'CHRISTIAN DEFAZ', 'scrypt:32768:8:1$aMgnwvz2kmlCAbeU$0faa2b09d46b93a49b127171fbdafea440fc6ffb652887fdaf39a9a3f1329d75f47ad43b21fe519fb6b5df5f087173d70cdcd0b2a03423e19386ffbcc72eb330', 1, 1, 1, NULL, '2026-03-07 12:18:40', NULL, '2026-03-07 12:18:40'),
(2, '1714990726', 1, 'LILANA TADAY', 'scrypt:32768:8:1$yNbECha0koWV3lez$3718b2aa226db0a915a130292f3631bd7f52a8f7ef510311b521d83067873a572bcb1fe58348d14910c7c9d7e7505cc418de43aa907dc234190b3eb0d106d2f7', 1, 1, 1, NULL, '2026-03-07 12:18:40', NULL, '2026-03-07 12:18:40');

-- Data for categorias
TRUNCATE TABLE `categorias`;
INSERT INTO `categorias` (`id`, `nombre`, `usuario_creacion_id`, `fecha_creacion`, `usuario_modificacion_id`, `fecha_modificacion`) VALUES
(1, 'SANDUCHES DE 12 CM', 1, '2026-03-07 12:50:26', 1, '2026-03-07 12:50:26'),
(2, 'SANDUCHES DE 24 CM', 1, '2026-03-07 12:50:39', 1, '2026-03-07 12:50:39'),
(3, 'COMBOS', 1, '2026-03-07 12:50:56', 1, '2026-03-07 12:51:15'),
(4, 'DESAYUNOS', 1, '2026-03-07 12:51:25', 1, '2026-03-07 12:51:25'),
(5, 'ADICIONALES/EXTRAS', 1, '2026-03-07 12:51:39', 1, '2026-03-07 12:51:39'),
(6, 'BEBIDAS', 1, '2026-03-07 12:52:02', 1, '2026-03-07 12:52:02');

-- Data for productos
TRUNCATE TABLE `productos`;
INSERT INTO `productos` (`id`, `codigo`, `nombre`, `precio`, `precios_json`, `categoria_id`, `imagen`, `mimetype`, `usuario_creacion_id`, `fecha_creacion`, `usuario_modificacion_id`, `fecha_modificacion`) VALUES
(1, 'P01', 'PERNIL 12CM', '0.00', NULL, 1, null, 'image/jpeg', 1, '2026-03-07 13:27:42', 1, '2026-03-09 15:29:29'),
(2, 'P02', 'PERNIL 24CM', '6.50', NULL, 2, null, 'image/jpeg', 1, '2026-03-07 13:28:47', 1, '2026-03-15 20:10:43');

-- Data for cat_tarjetas
TRUNCATE TABLE `cat_tarjetas`;
INSERT INTO `cat_tarjetas` (`id`, `nombre`, `activo`) VALUES
(1, 'VISA', 1),
(2, 'MASTERCARD', 1),
(3, 'AMERICAN EXPRESS', 1),
(4, 'DINERS CLUB', 1),
(5, 'DISCOVER', 1);

-- Data for plataformas
TRUNCATE TABLE `plataformas`;
INSERT INTO `plataformas` (`id`, `nombre`) VALUES
(1, 'LOCAL'),
(2, 'PEDIDOS YA'),
(3, 'UBER EATS');

-- Data for proveedores
TRUNCATE TABLE `proveedores`;
INSERT INTO `proveedores` (`id`, `ruc`, `razon_social`, `nombre_comercial`, `direccion`, `telefono`, `email`, `tipo_comprobante_id`, `usuario_creacion_id`, `fecha_creacion`, `usuario_modificacion_id`, `fecha_modificacion`) VALUES
(1, '1709027286001', 'BONIFAZ CHAVEZ FABIAN PATRICIO', 'ORTICAMPO', 'PICHINCHA / QUITO / EL QUINCHE / VIA A SAN MIGUEL EL QUINCHE S/N Y SECUNDARIA', '0998365158', 'FPBONIFAZ@HOTMAIL.COM', 1, 1, '2026-03-07 14:07:53', 1, '2026-03-07 14:07:53'),
(2, '1720829272001', 'AULLA JANETA ROSARIO LUCIA', 'SARAHI', 'VENTE RAMON ROCA Y REINA VICTORIA', '', '', 2, 1, '2026-03-07 14:11:14', 1, '2026-03-07 18:17:54'),
(3, '1768041140001', 'SERVICIO ECUATORIANO DE CAPACITACION PROFESIONAL', 'SECAP', 'JOSE ARIZAGA Y LONDRES', '', '', 1, 1, '2026-03-07 16:10:15', 1, '2026-03-07 16:10:15'),
(4, '9999999999999', 'GASTOS VARIOS', 'GASTOS VARIOS', 'QUITO', '0000000000', 'gastos@varios.com', 1, NULL, '2026-03-08 10:35:57', NULL, '2026-03-08 10:35:57');

-- Data for menus
TRUNCATE TABLE `menus`;
INSERT INTO `menus` (`id`, `nombre`, `url`, `icono`, `categoria`, `orden`) VALUES
(1, 'Nueva Orden', 'pos', 'fas fa-cash-register', 'OPERATIVO', 1),
(2, 'Egresos', 'listar_egresos', 'fas fa-hand-holding-usd', 'OPERATIVO', 2),
(3, 'Turno Caja', 'sesion_caja', 'fas fa-lock', 'OPERATIVO', 3),
(4, 'Cierre Día', 'cierre_diario', 'fas fa-calendar-check', 'OPERATIVO', 4),
(5, 'Ventas', 'historial_ventas', 'fas fa-receipt', 'OPERATIVO', 5),
(6, 'Clientes', 'clientes', 'fas fa-address-book', 'OPERATIVO', 6),
(7, 'Compras', 'compras', 'fas fa-shopping-cart', 'ABASTECIMIENTO', 7),
(8, 'Proveedores', 'proveedores', 'fas fa-truck', 'ABASTECIMIENTO', 8),
(9, 'Usuarios', 'usuarios', 'fas fa-user-shield', 'ADMINISTRATIVO', 9),
(10, 'Inventario', 'inventario', 'fas fa-boxes', 'ADMINISTRATIVO', 10),
(11, 'Producto', 'productos', 'fas fa-hamburger', 'ADMINISTRATIVO', 11),
(12, 'Sucursales', 'sucursales', 'fas fa-store', 'ADMINISTRATIVO', 12),
(13, 'Categorías', 'categorias', 'fas fa-list', 'ADMINISTRATIVO', 13),
(14, 'Empresa', 'configuracion_empresa', 'fas fa-building', 'ADMINISTRATIVO', 14),
(15, 'Auditoría', 'ver_auditoria', 'fas fa-history', 'ADMINISTRATIVO', 15),
(16, 'Reportes', 'reportes', 'fas fa-chart-pie', 'ADMINISTRATIVO', 16),
(17, 'Anulaciones', 'listar_anulaciones', 'fas fa-ban', 'OPERATIVO', 17),
(18, 'Kardex', 'kardex_movimientos', 'fas fa-exchange-alt', 'ADMINISTRATIVO', 18),
(19, 'Promociones', 'listar_promociones', 'fas fa-gift', 'ADMINISTRATIVO', 19),
(20, 'Tarjetas/Plat.', 'tarjetas_plataformas', 'fas fa-credit-card', 'ADMINISTRATIVO', 20),
(21, 'Abrir Caja', 'sesion_caja', 'fas fa-unlock-alt', 'OPERATIVO', 0),
(22, 'Roles', 'listar_roles', 'fas fa-user-tag', 'SISTEMA', 100);

-- Data for empresa
TRUNCATE TABLE `empresa`;
INSERT INTO `empresa` (`id`, `ruc`, `razon_social`, `nombre_comercial`, `direccion_matriz`, `iva_porcentaje`, `obligado_contabilidad`, `agente_retencion`, `contribuyente_especial`, `ambiente`, `color_tema`, `firma_password`, `usuario_creacion_id`, `fecha_creacion`, `usuario_modificacion_id`, `fecha_modificacion`, `icono_espera`, `email_host`, `email_port`, `email_user`, `email_pass`, `email_use_tls`, `email_envio_automatico`) VALUES
(1, '1768041140001', 'SERVICIO ECUATORIANO DE CAPACITACION PROFESIONAL', 'SANDUCHES LA REINA', 'QUITO', '15.00', 'SI', NULL, NULL, 1, '#008a4e', 'gAAAAABpruTj4QHL3iPK-BqHWuVfKENGcY8QlIJV3MrMxLSqPEuWl66eBYKOz17mhAS4EdUrEUyHdMNokLZeRifhoE1zNfA40w==', NULL, '2026-03-07 12:18:40', 1, '2026-03-09 10:18:59', 'fa-crown', 'smtp.gmail.com', 587, 'cdgo28@gmail.com', 'bmfk gcpp nrcu qxfx', 1, 1);

-- Data for rol_menus
TRUNCATE TABLE `rol_menus`;
INSERT INTO `rol_menus` (`id`, `rol_id`, `menu_id`) VALUES
(1, 1, 1),
(2, 1, 2),
(3, 1, 3),
(4, 1, 4),
(5, 1, 5),
(6, 1, 6),
(7, 1, 7),
(8, 1, 8),
(9, 1, 9),
(10, 1, 10),
(11, 1, 11),
(12, 1, 12),
(13, 1, 13),
(14, 1, 14),
(15, 1, 15),
(16, 1, 16),
(22, 1, 17),
(23, 1, 18),
(24, 1, 19),
(25, 1, 20),
(26, 1, 21),
(27, 1, 22),
(17, 2, 1),
(18, 2, 2),
(19, 2, 3),
(20, 2, 5),
(21, 2, 6);

-- Data for producto_precios
TRUNCATE TABLE `producto_precios`;
INSERT INTO `producto_precios` (`id`, `producto_id`, `plataforma_id`, `precio`) VALUES
(1, 1, 1, '3.50'),
(2, 1, 2, '6.00'),
(3, 1, 3, '6.50'),
(4, 2, 1, '6.50'),
(5, 2, 2, '8.00'),
(6, 2, 3, '8.00');

-- Data for clientes
TRUNCATE TABLE `clientes`;
INSERT INTO `clientes` (`id`, `cedula_ruc`, `tipo_identificacion_id`, `tipo_documento`, `nombres`, `apellidos`, `direccion`, `telefono`, `email`, `usuario_creacion_id`, `fecha_creacion`, `usuario_modificacion_id`, `fecha_modificacion`) VALUES
(1, '9999999999999', 4, NULL, 'CONSUMIDOR', 'FINAL', 'CIUDAD', NULL, NULL, NULL, '2026-03-15 22:48:03', NULL, '2026-03-15 22:48:03');

-- Data for unidades_medida
TRUNCATE TABLE `unidades_medida`;
INSERT INTO `unidades_medida` (`id`, `nombre`, `abreviatura`) VALUES
(1, 'UNIDAD', 'und'),
(2, 'KILOGRAMO', 'kg'),
(3, 'GRAMO', 'g'),
(4, 'LIBRA', 'lb'),
(5, 'LITRO', 'l'),
(6, 'MILILITRO', 'ml'),
(7, 'PAQUETE', 'paq'),
(8, 'CAJA', 'caja'),
(9, 'GALON', 'gal'),
(10, 'ONZA', 'oz'),
(11, 'DOCENA', 'doc'),
(12, 'SACO', 'saco'),
(13, 'BOTELLA', 'bot'),
(14, 'PORCION', 'por'),
(15, 'ATADO', 'atado');

SET FOREIGN_KEY_CHECKS=1;
