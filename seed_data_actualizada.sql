-- DATOS SEMILLA ACTUALIZADOS PARA LA NUBE
SET FOREIGN_KEY_CHECKS=0;

-- MENUS --
INSERT INTO menus (id, nombre, url, icono, categoria, orden) VALUES (1, 'Nueva Orden', 'pos', 'fas fa-cash-register', 'OPERATIVO', 1) ON DUPLICATE KEY UPDATE nombre='Nueva Orden', url='pos', icono='fas fa-cash-register', categoria='OPERATIVO', orden=1;
INSERT INTO menus (id, nombre, url, icono, categoria, orden) VALUES (2, 'Egresos', 'listar_egresos', 'fas fa-hand-holding-usd', 'OPERATIVO', 2) ON DUPLICATE KEY UPDATE nombre='Egresos', url='listar_egresos', icono='fas fa-hand-holding-usd', categoria='OPERATIVO', orden=2;
INSERT INTO menus (id, nombre, url, icono, categoria, orden) VALUES (3, 'Turno Caja', 'sesion_caja', 'fas fa-lock', 'OPERATIVO', 3) ON DUPLICATE KEY UPDATE nombre='Turno Caja', url='sesion_caja', icono='fas fa-lock', categoria='OPERATIVO', orden=3;
INSERT INTO menus (id, nombre, url, icono, categoria, orden) VALUES (4, 'Cierre Día', 'cierre_diario', 'fas fa-calendar-check', 'OPERATIVO', 4) ON DUPLICATE KEY UPDATE nombre='Cierre Día', url='cierre_diario', icono='fas fa-calendar-check', categoria='OPERATIVO', orden=4;
INSERT INTO menus (id, nombre, url, icono, categoria, orden) VALUES (5, 'Ventas', 'historial_ventas', 'fas fa-receipt', 'OPERATIVO', 5) ON DUPLICATE KEY UPDATE nombre='Ventas', url='historial_ventas', icono='fas fa-receipt', categoria='OPERATIVO', orden=5;
INSERT INTO menus (id, nombre, url, icono, categoria, orden) VALUES (6, 'Clientes', 'clientes', 'fas fa-address-book', 'OPERATIVO', 6) ON DUPLICATE KEY UPDATE nombre='Clientes', url='clientes', icono='fas fa-address-book', categoria='OPERATIVO', orden=6;
INSERT INTO menus (id, nombre, url, icono, categoria, orden) VALUES (7, 'Compras', 'compras', 'fas fa-shopping-cart', 'ABASTECIMIENTO', 7) ON DUPLICATE KEY UPDATE nombre='Compras', url='compras', icono='fas fa-shopping-cart', categoria='ABASTECIMIENTO', orden=7;
INSERT INTO menus (id, nombre, url, icono, categoria, orden) VALUES (8, 'Proveedores', 'proveedores', 'fas fa-truck', 'ABASTECIMIENTO', 8) ON DUPLICATE KEY UPDATE nombre='Proveedores', url='proveedores', icono='fas fa-truck', categoria='ABASTECIMIENTO', orden=8;
INSERT INTO menus (id, nombre, url, icono, categoria, orden) VALUES (9, 'Usuarios', 'usuarios', 'fas fa-user-shield', 'ADMINISTRATIVO', 9) ON DUPLICATE KEY UPDATE nombre='Usuarios', url='usuarios', icono='fas fa-user-shield', categoria='ADMINISTRATIVO', orden=9;
INSERT INTO menus (id, nombre, url, icono, categoria, orden) VALUES (10, 'Inventario', 'inventario', 'fas fa-boxes', 'ADMINISTRATIVO', 10) ON DUPLICATE KEY UPDATE nombre='Inventario', url='inventario', icono='fas fa-boxes', categoria='ADMINISTRATIVO', orden=10;
INSERT INTO menus (id, nombre, url, icono, categoria, orden) VALUES (11, 'Producto', 'productos', 'fas fa-hamburger', 'ADMINISTRATIVO', 11) ON DUPLICATE KEY UPDATE nombre='Producto', url='productos', icono='fas fa-hamburger', categoria='ADMINISTRATIVO', orden=11;
INSERT INTO menus (id, nombre, url, icono, categoria, orden) VALUES (12, 'Sucursales', 'sucursales', 'fas fa-store', 'ADMINISTRATIVO', 12) ON DUPLICATE KEY UPDATE nombre='Sucursales', url='sucursales', icono='fas fa-store', categoria='ADMINISTRATIVO', orden=12;
INSERT INTO menus (id, nombre, url, icono, categoria, orden) VALUES (13, 'Categorías', 'categorias', 'fas fa-list', 'ADMINISTRATIVO', 13) ON DUPLICATE KEY UPDATE nombre='Categorías', url='categorias', icono='fas fa-list', categoria='ADMINISTRATIVO', orden=13;
INSERT INTO menus (id, nombre, url, icono, categoria, orden) VALUES (14, 'Empresa', 'configuracion_empresa', 'fas fa-building', 'ADMINISTRATIVO', 14) ON DUPLICATE KEY UPDATE nombre='Empresa', url='configuracion_empresa', icono='fas fa-building', categoria='ADMINISTRATIVO', orden=14;
INSERT INTO menus (id, nombre, url, icono, categoria, orden) VALUES (15, 'Auditoría', 'ver_auditoria', 'fas fa-history', 'ADMINISTRATIVO', 15) ON DUPLICATE KEY UPDATE nombre='Auditoría', url='ver_auditoria', icono='fas fa-history', categoria='ADMINISTRATIVO', orden=15;
INSERT INTO menus (id, nombre, url, icono, categoria, orden) VALUES (16, 'Reportes', 'reportes', 'fas fa-chart-pie', 'ADMINISTRATIVO', 16) ON DUPLICATE KEY UPDATE nombre='Reportes', url='reportes', icono='fas fa-chart-pie', categoria='ADMINISTRATIVO', orden=16;
INSERT INTO menus (id, nombre, url, icono, categoria, orden) VALUES (17, 'Anulaciones', 'listar_anulaciones', 'fas fa-ban', 'OPERATIVO', 17) ON DUPLICATE KEY UPDATE nombre='Anulaciones', url='listar_anulaciones', icono='fas fa-ban', categoria='OPERATIVO', orden=17;
INSERT INTO menus (id, nombre, url, icono, categoria, orden) VALUES (18, 'Kardex', 'kardex_movimientos', 'fas fa-exchange-alt', 'ADMINISTRATIVO', 18) ON DUPLICATE KEY UPDATE nombre='Kardex', url='kardex_movimientos', icono='fas fa-exchange-alt', categoria='ADMINISTRATIVO', orden=18;
INSERT INTO menus (id, nombre, url, icono, categoria, orden) VALUES (19, 'Promociones', 'listar_promociones', 'fas fa-gift', 'ADMINISTRATIVO', 19) ON DUPLICATE KEY UPDATE nombre='Promociones', url='listar_promociones', icono='fas fa-gift', categoria='ADMINISTRATIVO', orden=19;
INSERT INTO menus (id, nombre, url, icono, categoria, orden) VALUES (20, 'Tarjetas/Plat.', 'tarjetas_plataformas', 'fas fa-credit-card', 'ADMINISTRATIVO', 20) ON DUPLICATE KEY UPDATE nombre='Tarjetas/Plat.', url='tarjetas_plataformas', icono='fas fa-credit-card', categoria='ADMINISTRATIVO', orden=20;
INSERT INTO menus (id, nombre, url, icono, categoria, orden) VALUES (21, 'Abrir Caja', 'sesion_caja', 'fas fa-unlock-alt', 'OPERATIVO', 0) ON DUPLICATE KEY UPDATE nombre='Abrir Caja', url='sesion_caja', icono='fas fa-unlock-alt', categoria='OPERATIVO', orden=0;
INSERT INTO menus (id, nombre, url, icono, categoria, orden) VALUES (22, 'Roles', 'listar_roles', 'fas fa-user-tag', 'SISTEMA', 100) ON DUPLICATE KEY UPDATE nombre='Roles', url='listar_roles', icono='fas fa-user-tag', categoria='SISTEMA', orden=100;
INSERT INTO menus (id, nombre, url, icono, categoria, orden) VALUES (23, 'Máquinas', 'listar_maquinas', 'fas fa-desktop', 'ADMINISTRATIVO', 21) ON DUPLICATE KEY UPDATE nombre='Máquinas', url='listar_maquinas', icono='fas fa-desktop', categoria='ADMINISTRATIVO', orden=21;

-- ROLES --
INSERT INTO roles (id, nombre) VALUES (1, 'ADMINISTRADOR') ON DUPLICATE KEY UPDATE nombre='ADMINISTRADOR';
INSERT INTO roles (id, nombre) VALUES (2, 'CAJERO') ON DUPLICATE KEY UPDATE nombre='CAJERO';

-- ROL_MENUS --
INSERT INTO rol_menus (rol_id, menu_id) VALUES (1, 1) ON DUPLICATE KEY UPDATE rol_id=rol_id;
INSERT INTO rol_menus (rol_id, menu_id) VALUES (1, 2) ON DUPLICATE KEY UPDATE rol_id=rol_id;
INSERT INTO rol_menus (rol_id, menu_id) VALUES (1, 3) ON DUPLICATE KEY UPDATE rol_id=rol_id;
INSERT INTO rol_menus (rol_id, menu_id) VALUES (1, 4) ON DUPLICATE KEY UPDATE rol_id=rol_id;
INSERT INTO rol_menus (rol_id, menu_id) VALUES (1, 5) ON DUPLICATE KEY UPDATE rol_id=rol_id;
INSERT INTO rol_menus (rol_id, menu_id) VALUES (1, 6) ON DUPLICATE KEY UPDATE rol_id=rol_id;
INSERT INTO rol_menus (rol_id, menu_id) VALUES (1, 7) ON DUPLICATE KEY UPDATE rol_id=rol_id;
INSERT INTO rol_menus (rol_id, menu_id) VALUES (1, 8) ON DUPLICATE KEY UPDATE rol_id=rol_id;
INSERT INTO rol_menus (rol_id, menu_id) VALUES (1, 9) ON DUPLICATE KEY UPDATE rol_id=rol_id;
INSERT INTO rol_menus (rol_id, menu_id) VALUES (1, 10) ON DUPLICATE KEY UPDATE rol_id=rol_id;
INSERT INTO rol_menus (rol_id, menu_id) VALUES (1, 11) ON DUPLICATE KEY UPDATE rol_id=rol_id;
INSERT INTO rol_menus (rol_id, menu_id) VALUES (1, 12) ON DUPLICATE KEY UPDATE rol_id=rol_id;
INSERT INTO rol_menus (rol_id, menu_id) VALUES (1, 13) ON DUPLICATE KEY UPDATE rol_id=rol_id;
INSERT INTO rol_menus (rol_id, menu_id) VALUES (1, 14) ON DUPLICATE KEY UPDATE rol_id=rol_id;
INSERT INTO rol_menus (rol_id, menu_id) VALUES (1, 15) ON DUPLICATE KEY UPDATE rol_id=rol_id;
INSERT INTO rol_menus (rol_id, menu_id) VALUES (1, 16) ON DUPLICATE KEY UPDATE rol_id=rol_id;
INSERT INTO rol_menus (rol_id, menu_id) VALUES (1, 17) ON DUPLICATE KEY UPDATE rol_id=rol_id;
INSERT INTO rol_menus (rol_id, menu_id) VALUES (1, 18) ON DUPLICATE KEY UPDATE rol_id=rol_id;
INSERT INTO rol_menus (rol_id, menu_id) VALUES (1, 19) ON DUPLICATE KEY UPDATE rol_id=rol_id;
INSERT INTO rol_menus (rol_id, menu_id) VALUES (1, 20) ON DUPLICATE KEY UPDATE rol_id=rol_id;
INSERT INTO rol_menus (rol_id, menu_id) VALUES (1, 21) ON DUPLICATE KEY UPDATE rol_id=rol_id;
INSERT INTO rol_menus (rol_id, menu_id) VALUES (1, 22) ON DUPLICATE KEY UPDATE rol_id=rol_id;
INSERT INTO rol_menus (rol_id, menu_id) VALUES (1, 23) ON DUPLICATE KEY UPDATE rol_id=rol_id;
INSERT INTO rol_menus (rol_id, menu_id) VALUES (2, 1) ON DUPLICATE KEY UPDATE rol_id=rol_id;
INSERT INTO rol_menus (rol_id, menu_id) VALUES (2, 2) ON DUPLICATE KEY UPDATE rol_id=rol_id;
INSERT INTO rol_menus (rol_id, menu_id) VALUES (2, 3) ON DUPLICATE KEY UPDATE rol_id=rol_id;
INSERT INTO rol_menus (rol_id, menu_id) VALUES (2, 5) ON DUPLICATE KEY UPDATE rol_id=rol_id;
INSERT INTO rol_menus (rol_id, menu_id) VALUES (2, 6) ON DUPLICATE KEY UPDATE rol_id=rol_id;

-- SUCURSALES --
INSERT INTO sucursales (id, nombre, establecimiento, punto_emision, ultimo_secuencial) VALUES (1, 'REINA VICTORIA PRINCIPAL', '001', '001', 58) ON DUPLICATE KEY UPDATE nombre='REINA VICTORIA PRINCIPAL';
INSERT INTO sucursales (id, nombre, establecimiento, punto_emision, ultimo_secuencial) VALUES (2, 'GRANADOS NORTE', '002', '001', 0) ON DUPLICATE KEY UPDATE nombre='GRANADOS NORTE';

-- USUARIOS (ADMIN POR DEFECTO) --
INSERT INTO usuarios (id, cedula, usuario, password, sucursal_id, rol_id, activo, tipo_identificacion_id) VALUES (1, '1002597886', 'CHRISTIAN DEFAZ', 'scrypt:32768:8:1$aMgnwvz2kmlCAbeU$0faa2b09d46b93a49b127171fbdafea440fc6ffb652887fdaf39a9a3f1329d75f47ad43b21fe519fb6b5df5f087173d70cdcd0b2a03423e19386ffbcc72eb330', 1, 1, 1, 1) ON DUPLICATE KEY UPDATE usuario='CHRISTIAN DEFAZ';
INSERT INTO usuarios (id, cedula, usuario, password, sucursal_id, rol_id, activo, tipo_identificacion_id) VALUES (2, '1714990726', 'LILANA TADAY', 'scrypt:32768:8:1$yNbECha0koWV3lez$3718b2aa226db0a915a130292f3631bd7f52a8f7ef510311b521d83067873a572bcb1fe58348d14910c7c9d7e7505cc418de43aa907dc234190b3eb0d106d2f7', 1, 1, 1, 1) ON DUPLICATE KEY UPDATE usuario='LILANA TADAY';
INSERT INTO usuarios (id, cedula, usuario, password, sucursal_id, rol_id, activo, tipo_identificacion_id) VALUES (3, '12345', 'JUAN LOPEZ', 'scrypt:32768:8:1$DQfw5FfUmA8WyDrT$bdd38e6da066e8079792d0518b0f5744eb33a8ea00df6329b56cf324ec961126177e718fb7924550819c8c4979926d931ad7a6525e8f1b5f6c680721f95d622d', 1, 2, 1, 3) ON DUPLICATE KEY UPDATE usuario='JUAN LOPEZ';

SET FOREIGN_KEY_CHECKS=1;
