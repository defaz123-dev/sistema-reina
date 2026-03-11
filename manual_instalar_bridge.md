# 👑 Manual de Instalación: Reina Bridge v1.0

Este manual detalla los pasos para instalar y configurar el **Reina Bridge**, el agente local que permite al Sistema Reina (Web) abrir la caja registradora física automáticamente.

---

## 📋 Requisitos Previos
1.  Computadora con **Windows 10 o superior**.
2.  Impresora de tickets (térmica) conectada y configurada en el Panel de Control.
3.  Cajón de dinero conectado a la impresora mediante cable **RJ11**.

---

## 🚀 Paso 1: Instalación del Programa
1.  **Descargar:** Obtenga el archivo ejecutable `reina_bridge.exe`.
2.  **Ubicación:** Cree una carpeta llamada `C:\ReinaBridge` y mueva el archivo allí (evite dejarlo en "Descargas").
3.  **Ejecutar:** Haga doble clic en `reina_bridge.exe`.
4.  **Permisos Críticos:**
    *   **SmartScreen:** Si Windows muestra una ventana azul indicando que "protegió su PC", haga clic en **"Más información"** y luego en **"Ejecutar de todas formas"**.
    *   **Firewall:** Si aparece una alerta del Firewall de Windows, marque las casillas de **"Redes privadas"** y **"Redes públicas"**, luego haga clic en **"Permitir acceso"**. Esto es vital para que la web pueda comunicarse con la impresora.

---

## 🔍 Paso 2: Verificación de Estado
1.  Busque en la barra de tareas (junto al reloj de Windows) un icono de una **corona amarilla**.
2.  Pase el ratón sobre el icono; debería ver el mensaje: `Reina Bridge v1.0.0 - Estado: Activo`.
3.  **Configuración de Impresora:** El programa detectará automáticamente impresoras con nombres como `POS`, `TICKET`, `EPSON` o `80mm`. Si tiene un nombre distinto, asegúrese de establecer su impresora de tickets como **Predeterminada** en Windows.

---

## ⚙️ Paso 3: Inicio Automático con Windows
Para que el cajero no deba abrir el programa manualmente cada vez que encienda la PC:

1.  Haga **clic derecho** sobre `reina_bridge.exe` y seleccione **"Crear acceso directo"**.
2.  Presione la combinación de teclas **Windows + R**.
3.  En el cuadro "Ejecutar", escriba exactamente: `shell:startup` y presione **Enter**.
4.  Se abrirá la carpeta de "Inicio" de Windows. **Mueva** el acceso directo creado en el punto 1 dentro de esta carpeta.
5.  **Resultado:** Al reiniciar la PC, el Reina Bridge se activará solo.

---

## 💻 Paso 4: Uso desde el Sistema Reina (Web)
1.  Inicie sesión en el Sistema Reina desde su navegador.
2.  **En el POS:** La caja se abrirá automáticamente al confirmar una venta en **EFECTIVO**. También puede usar el icono del candado amarillo para una apertura manual.
3.  **En el Dashboard:** Los administradores tienen un botón directo llamado **"Abrir Caja"**.

---

## 🛠️ Solución de Problemas
*   **"Sin Conexión Local":** Significa que el `reina_bridge.exe` no está abierto. Ábralo y verifique la corona amarilla en la barra de tareas.
*   **La caja no abre pero no hay error:** 
    *   Revise que el cable RJ11 esté bien conectado.
    *   Verifique que la impresora tenga papel (muchas impresoras bloquean el pulso del cajón si están en error por falta de papel).
*   **Error de permisos:** Intente ejecutar el programa como Administrador (Clic derecho -> Ejecutar como administrador).

---
*Sistema Reina - Software de Gestión Profesional (2026)*
