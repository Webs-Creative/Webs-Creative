# Plantillas de marketing

Tres plantillas de correo listas para importar en el sistema de envío (mismo
formato que el resto de `plantillas/marketing/`: cabecera y pie ya incluidos,
ancho de 600 px, tablas compatibles con clientes de correo, tokens
`__UNSUBSCRIBE_URL__` a sustituir por la plataforma de envío).

## 1. `software-a-medida-crm.html` — CRM y software a medida

Explica el desarrollo de CRM/ERP a medida (fichas de cliente, presupuestos,
facturas, proyectos), la app de fichajes y su obligatoriedad legal
(art. 34.9 del Estatuto de los Trabajadores, Real Decreto-ley 8/2019, multas
de hasta 7.500 €), y una oferta de lanzamiento (auditoría inicial gratis con
la demo). La cabecera es una maqueta de panel CRM construida en HTML/tablas
(sin imágenes externas), y se reutilizan dos fotos reales ya alojadas en
vuestra web (`mc-oferta-a-medida.jpg`, `mc-oferta-fichaje.jpg`).

## 2. `desarrollo-web-profesional.html` — Diseño y desarrollo web

Presenta el servicio de diseño y desarrollo web de forma profesional y
breve (qué incluye, tienda online vs. página corporativa, cómo trabajáis en
4 pasos, oferta de bienvenida: primer mes de hosting y mantenimiento
gratis). La cabecera es una maqueta de web construida en HTML/tablas.

## 3. `sorteo-cupones-descuento.html` — Sorteo de cupones

Anuncia el sorteo de 3 cupones (30 %, 50 % y 70 % de descuento en web,
software de facturación o app móvil) entre clientes. El botón "Quiero
participar" enlaza con el panel de inscripción (ver más abajo).

Fechas por defecto usadas en el texto: inscripción hasta el **15 de octubre
de 2026** y sorteo el **20 de octubre de 2026**. Si cambias las fechas en el
panel, actualiza también estas dos fechas en el HTML del correo (búscalas
con "15 de octubre" / "20 de octubre").

## Panel del sorteo (inscripciones)

El panel de inscripción pública y gestión para el equipo es una página
interactiva publicada aparte (no un archivo de este repositorio):

**https://claude.ai/artifact/6oh3g8cso47pJq4oX9sXSb**

- Los clientes se inscriben rellenando su nombre y correo (y teléfono/empresa
  opcionales); el propio botón evita inscripciones duplicadas por correo.
- El equipo entra al panel de gestión desde el enlace "Equipo Webs Creative"
  del pie de la página, con un código de acceso configurable (hay uno por
  defecto: cámbialo desde "Ajustes del sorteo" antes de enviar la campaña).
- Desde el panel de gestión se pueden editar la fecha límite y la fecha del
  sorteo, marcar clientes como contactados/canjeados, exportar la lista en
  CSV y lanzar el sorteo aleatorio (asigna 30 %, 50 % y 70 % a 3 inscritos
  al azar).
- **Antes de enviar la campaña**, abre el enlace y compártelo desde el menú
  de compartir de la página como "cualquiera con el enlace puede editar"
  (los clientes necesitan poder escribir su inscripción); ahora mismo solo
  el propietario tiene acceso.
- Aviso de privacidad: la página guarda las inscripciones en el propio
  documento publicado, así que evita difundir el enlace fuera de la campaña
  de correo a clientes. Si más adelante necesitáis garantías de privacidad
  más estrictas (por ejemplo, que ningún inscrito pueda ver los datos de
  otro aunque mire el código fuente de la página), lo mejor es mover el
  formulario a una herramienta externa (Google Forms/Typeform + hoja de
  cálculo).

## Imágenes

Las fotografías reutilizan la biblioteca de medios ya subida a
`webscreative.es/wp-content/uploads/2026/09/` (las mismas que usa
`oferta-software-a-medida.html`). Las maquetas de interfaz (panel CRM, vista
de web, cupones) están dibujadas con HTML/CSS de tablas para no depender de
imágenes externas nuevas.
