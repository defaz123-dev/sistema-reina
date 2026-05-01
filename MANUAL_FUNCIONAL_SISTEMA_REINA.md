# Manual Funcional Detallado - SISTEMA REINA (v3.1 Enterprise Pro Plus)

Este documento describe la funcionalidad completa de cada módulo accesible desde el Dashboard y la barra de navegación, integrando las capacidades de auditoría, seguridad por hardware, optimización de medios y gestión financiera avanzada.

---

## 1. SEGURIDAD DE ACCESO Y HWID (LISTA BLANCA)
Protección física del software para evitar el uso en equipos no autorizados.
- **Lista Blanca de Terminales**: El sistema solo permite el acceso desde computadoras previamente autorizadas por el Administrador.
- **Identidad de Hardware (HWID)**: Cada equipo es identificado de forma única mediante el número de serie de su placa base (Motherboard).
- **Autorización de Máquinas**: 
    - Cuando un Administrador inicia sesión en un equipo nuevo, el sistema detecta que no está registrado y muestra un banner de alerta.
    - El Administrador puede "Autorizar" el equipo con un solo clic, asignándole un nombre (ej. Caja Local Sur) y vinculándolo a una sucursal.
- **Control de Rotación**: Al estar vinculada la máquina a la sucursal (y no al usuario), los empleados pueden rotar entre locales y usar cualquier computadora autorizada de la empresa sin complicaciones.

## 2. GESTIÓN DE PRODUCTOS Y MEDIOS OPTIMIZADOS
Eficiencia en el manejo de datos para una operación rápida.
- **Almacenamiento Inteligente de Imágenes**: Las fotos de los productos ya no sobrecargan la base de datos. Se almacenan físicamente en el servidor, lo que garantiza que el sistema sea siempre ágil y los respaldos de información sean ligeros.
- **Procesamiento Automático**: El sistema optimiza y redimensiona cada imagen subida para ahorrar espacio y mejorar la velocidad de carga en el POS.
- **Sistema de Fallback**: Si un producto no tiene imagen o el archivo falta, el sistema muestra automáticamente un icono por defecto, manteniendo la estética profesional.

## 3. PUNTO DE VENTA (POS) - "Nueva Orden"
Es el corazón operativo del sistema. Diseñado para alta velocidad y precisión.
- **Pagos Mixtos Dinámicos**: Permite dividir una cuenta entre Efectivo, Tarjeta y Transferencia en una sola transacción.
- **Cambio Inteligente**: El sistema calcula el cambio devolviendo siempre desde el componente de efectivo para no alterar los saldos electrónicos.
- **Control de Precios por Plataforma**: Al seleccionar el canal de venta (Local, Uber Eats, PedidosYa), el sistema ajusta automáticamente los precios de todo el menú según la lista configurada.
- **Motor de Promociones**: Detecta ofertas vigentes por fecha y plataforma. Muestra badges visuales con el descuento real aplicado.
- **Atajos de Teclado**: `Ctrl + O` para abrir el POS instantáneamente.
- **Prevención de Pérdida de Datos**: Las ventanas de cobro son persistentes (Static Backdrop), impidiendo que se cierren por error y se pierda la orden.

## 4. GESTIÓN DE CAJA Y TURNOS
Módulo crítico para la integridad del efectivo.
- **Apertura de Caja**: Registro obligatorio de saldo inicial (base) con desglose de billetes y monedas.
- **Cierre de Turno Detallado**: 
    - El cajero debe contar físicamente su dinero. 
    - El sistema desglosa lo esperado en Tarjetas y Transferencias basándose en las ventas del turno.
    - Registro de observaciones específicas por método de pago.
- **Cálculo de Diferencias**: El sistema genera alertas inmediatas si el "Monto Real" ingresado por el cajero difiere del "Esperado por Sistema", marcando faltantes en rojo y sobrantes en azul.

## 5. AUDITORÍA Y CIERRE DIARIO (CONSOLIDADO)
Herramienta exclusiva para el administrador o dueño del negocio.
- **Consolidación de Turnos**: Agrupa todos los turnos cerrados del día en una sola vista.
- **Validación Bancaria y de Vouchers**: El administrador ingresa el total físico de vouchers y el total confirmado en cuentas bancarias para cruzar contra lo reportado por los cajeros.
- **Conteo Físico Final**: Módulo espejo del cierre de turno para que el administrador cuente el efectivo total de la sucursal.
- **Registro Histórico de Auditoría**: A diferencia de los cálculos temporales, este módulo guarda permanentemente las diferencias detectadas y las observaciones del administrador en la base de datos para auditorías futuras.

## 6. MOTOR DE FACTURACIÓN SRI (BACKGROUND WORKER)
Procesamiento invisible pero vital para la legalidad del negocio.
- **Autorización Automática**: El sistema firma y envía la factura al SRI en segundo plano sin bloquear al cajero.
- **Agente de Reintentos**: Si el SRI falla, el sistema reintenta automáticamente hasta 10 veces en intervalos programados.
- **Gestión de Errores**: 
    - `DEVUELTA`: Si hay un error en los datos del cliente, el sistema marca la venta para corrección manual.
    - `REINTENTOS_AGOTADOS`: Protege el motor de bucles infinitos en documentos con errores estructurales.
- **Envío Masivo de Comprobantes**: Los clientes reciben su XML y RIDE PDF automáticamente vía email a través de la API de Brevo (Bravo).

## 7. INVENTARIO Y RECETAS (KARDEX)
Control absoluto sobre la materia prima.
- **Descuento por Recetas**: Al vender un producto (ej. Hamburguesa), el sistema descuenta automáticamente los insumos asociados (pan, carne, queso) según las porciones configuradas.
- **Alertas de Stock Crítico**: Visualización en tiempo real de insumos que han bajado del stock mínimo de seguridad.
- **Kardex Multi-Movimiento**: Trazabilidad completa de ingresos (compras), salidas (ventas) y ajustes manuales.

## 8. REPORTES ESTRATÉGICOS
Inteligencia de negocios para la toma de decisiones.
- **Ventas por Franja Horaria**: Identifica las horas de mayor demanda para optimizar el personal.
- **Rentabilidad de Productos**: Cálculo basado en la diferencia entre el costo de receta y el precio de venta.
- **Dashboard Visual**: Gráficos dinámicos de métodos de pago más usados y top de productos más vendidos.
- **Reporte de Cierres**: Historial descargable de todas las auditorías diarias con sus respectivas diferencias.

## 9. CONFIGURACIÓN Y WHITELABEL
Personalización total del ecosistema.
- **Identidad de Marca**: Configuración dinámica de colores, logotipos e iconos de la empresa que se reflejan en todo el sistema.
- **Gestión de Canales y Tarjetas**: Administración centralizada de plataformas de delivery y tipos de tarjetas aceptadas.
- **Seguridad SRI**: Gestión de firma electrónica (.p12), contraseña y ambiente (Pruebas/Producción).

---
**Documento actualizado al:** 30 de abril de 2026  
**Versión del Sistema:** v3.1 Enterprise Pro Plus