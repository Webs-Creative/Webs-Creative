# Plantillas de marketing

Tres plantillas de correo listas para importar en el sistema de envío (mismo
formato que el resto de `plantillas/marketing/`: cabecera y pie ya incluidos,
ancho de 600 px, tablas compatibles con clientes de correo, tokens
`__UNSUBSCRIBE_URL__` a sustituir por la plataforma de envío). Las tres
incluyen un pequeño efecto animado (brillo pulsante en los botones y en el
punto de la insignia superior) que se ve en Apple Mail, iOS Mail y
Outlook.com; en clientes que no soportan animaciones en correo (Gmail,
Outlook de escritorio) se ven exactamente igual pero estáticas, sin ningún
problema de compatibilidad.

## 1. `software-a-medida-crm.html` — CRM y software a medida

Explica el desarrollo de CRM/ERP a medida con una maqueta de interfaz mucho
más detallada y realista: barra de pestañas (Resumen/Clientes/Presupuestos/
Facturas/Proyectos), indicadores en vivo y una lista de clientes real con
avatares, estado (Activo/Pendiente/Cerrado) e importe — construida en
HTML/tablas, sin imágenes externas. Añade también una cuadrícula de 4
funciones (fichas de cliente, presupuestos y facturas, proyectos y tareas,
paneles al momento), la app de fichajes y su obligatoriedad legal
(art. 34.9 del Estatuto de los Trabajadores, Real Decreto-ley 8/2019, multas
de hasta 7.500 €), una sección de integraciones (facturación electrónica y
agente de IA) y una oferta de lanzamiento. Reutiliza tres fotos reales ya
alojadas en vuestra web (`mc-oferta-a-medida.jpg`, `mc-oferta-fichaje.jpg`,
`mc-oferta-facturacion.jpg`, `mc-oferta-agente-ia.jpg`).

## 2. `desarrollo-web-profesional.html` — Diseño y desarrollo web

Presenta el servicio de diseño y desarrollo web de forma profesional y
breve (qué incluye, tienda online vs. página corporativa, cómo trabajáis en
4 pasos, oferta de bienvenida: primer mes de hosting y mantenimiento
gratis). La cabecera es una maqueta de web construida en HTML/tablas.

## 3. `sorteo-cupones-descuento.html` — Sorteo de cupones

Anuncia el sorteo de 3 cupones (30 %, 50 % y 70 % de descuento en web,
software de facturación o app móvil) entre clientes. El botón "Quiero
participar" enlaza con **https://sorteos.webscreative.es/** (el panel de
inscripción, ver más abajo).

Fechas por defecto usadas en el texto: inscripción hasta el **15 de octubre
de 2026** y sorteo el **20 de octubre de 2026**. Si cambias las fechas desde
el panel, actualiza también estas dos fechas en el HTML del correo (búscalas
con "15 de octubre" / "20 de octubre").

## Panel de sorteos (inscripciones)

El panel de inscripción pública y gestión para el equipo **no vive en este
repositorio**: es una aplicación PHP autoinstalable, pensada para desplegarse
en `sorteos.webscreative.es`. Está en el paquete `sorteos-webscreative/` de
este mismo repositorio (o en el zip que te hemos entregado aparte); sus
pasos de instalación completos están en
`sorteos-webscreative/README-INSTALACION.md`.

Puntos clave:

- No depende de cuentas de Claude ni de ningún servicio externo: es PHP +
  SQLite, se sube por FTP a vuestro propio hosting y funciona para
  cualquier cliente sin necesidad de iniciar sesión en nada.
- Ya no está atado a un único sorteo: desde el panel de administración se
  pueden crear y activar nuevas campañas (nombre, fechas y premios libres)
  para futuras promociones, sin tocar código.
- El equipo entra en `/admin.php` con un código de acceso que se configura
  la primera vez que se abre (no hay contraseña por defecto).
- Desde el panel: editar fechas y premios de la campaña activa, marcar
  inscritos como contactados/canjeados, exportar la lista en CSV y lanzar
  el sorteo aleatorio.

## Imágenes

Las fotografías reutilizan la biblioteca de medios ya subida a
`webscreative.es/wp-content/uploads/2026/09/` (las mismas que usa
`oferta-software-a-medida.html`). Las maquetas de interfaz (panel CRM, vista
de web, cupones) están dibujadas con HTML/CSS de tablas para no depender de
imágenes externas nuevas.
