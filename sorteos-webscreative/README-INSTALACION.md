# Panel de sorteos — instalación en sorteos.webscreative.es

Aplicación PHP autocontenida (sin dependencias externas, sin necesidad de
MySQL: usa un fichero SQLite propio). Pensada para instalarse en un
subdominio de vuestro hosting actual y reutilizarse en futuras campañas,
no solo en el sorteo de cupones.

## Requisitos

- Hosting con PHP 7.4 o superior (cualquier hosting compartido de
  cPanel/Plesk que ya use WordPress cumple esto de sobra).
- Extensión `pdo_sqlite` habilitada (viene activada por defecto en la
  inmensa mayoría de hostings; si no cargara, contacta con el soporte de
  tu hosting para que la activen).
- Una carpeta escribible por PHP (para guardar la base de datos).

## 1. Crear el subdominio

En el panel de tu hosting (cPanel: "Dominios" → "Subdominios"; Plesk:
"Sitios web y dominios" → "Añadir subdominio"):

1. Crea el subdominio **`sorteos`** sobre `webscreative.es`, de forma que
   quede como `sorteos.webscreative.es`.
2. Indica una carpeta de destino nueva y vacía (por ejemplo
   `sorteos.webscreative.es` o `public_html/sorteos`, según lo que te
   proponga el asistente).
3. Guarda. El DNS del subdominio normalmente se activa solo, al ser el
   mismo dominio (puede tardar unos minutos).

## 2. Subir los archivos

1. Descomprime el zip de este panel en tu ordenador.
2. Conéctate por FTP (o usa el "Administrador de archivos" del panel de
   hosting) a la carpeta que has creado en el paso anterior.
3. Sube **todo el contenido** de la carpeta (no la carpeta en sí, sino lo
   que hay dentro: `index.php`, `admin.php`, `export_csv.php`, `.htaccess`,
   `includes/`, `assets/`, `data/`) directamente a la raíz del subdominio.
4. Asegúrate de que la carpeta `data/` tiene permisos de escritura para
   PHP: `755` o `775` suele bastar; si el primer acceso da un error de
   permisos, prueba con `775` o `777` sobre esa carpeta concreta (nunca
   sobre las demás).

## 3. Activar SSL (recomendado)

Desde el panel de hosting, activa el certificado gratuito (cPanel:
"Seguridad" → "SSL/TLS Status" → "Run AutoSSL"; suele emitirse en minutos
para un subdominio nuevo). Cuando esté activo, abre `.htaccess` en la raíz
del proyecto y descomenta las 3 líneas de "Force HTTPS" quitando el `#`
inicial.

## 4. Primer acceso: configurar el código de acceso

1. Abre `https://sorteos.webscreative.es/admin.php`.
2. Como es la primera vez, te pedirá que **crees el código de acceso** del
   equipo (mínimo 8 caracteres). Elige uno que no uséis en ningún otro
   sitio y guardadlo en vuestro gestor de contraseñas.
3. Ya estás dentro del panel. Veréis una campaña ya creada por defecto:
   el sorteo de cupones 30/50/70% con las fechas del 15 y 20 de octubre
   de 2026 — revisadlas y ajustadlas si hace falta desde "Ajustes de esta
   campaña".

## 5. Comprobar la página pública

Abre `https://sorteos.webscreative.es/` en una ventana de incógnito (sin
sesión de nada iniciada) y rellena una inscripción de prueba con un correo
tuyo. Comprueba que aparece en el panel de administración. Después puedes
borrarla desde "Eliminar" en la fila de esa inscripción, o vaciar la
campaña de prueba desde "Vaciar inscripciones".

## 6. Enviar la campaña de correo

El botón "Quiero participar" de `sorteo-cupones-descuento.html` ya apunta
a `https://sorteos.webscreative.es/`. No hace falta tocar nada más en el
correo: solo importar la plantilla en vuestro sistema de envío y
mandarla cuando queráis lanzar el sorteo.

## Usar el panel para futuras campañas

El panel ya no está atado a un único sorteo:

- En "Nueva campaña" puedes crear otra campaña (nombre, fechas, premios
  libres — no tienen que ser porcentajes, pueden ser "3 meses de
  mantenimiento gratis", "1 hora de consultoría", etc.) sin tocar código.
- Al crearla puedes marcarla como activa directamente, o dejarla
  preparada y activarla más tarde con el botón "Activar" de la tabla de
  campañas: la página pública siempre muestra la campaña marcada como
  activa.
- Las campañas anteriores (y sus inscritos) quedan guardadas; puedes
  volver a "Gestionar" cualquiera de ellas para consultar el histórico, o
  "Eliminar" las que ya no necesites.

## Copias de seguridad

Todo vive en un único fichero: `data/sorteo.sqlite`. Descárgalo
periódicamente por FTP como copia de seguridad (o pide a tu hosting que
incluya esa carpeta en sus backups automáticos).

## Solución de problemas

- **Error 500 en la primera visita**: normalmente es que PHP no puede
  escribir en `data/`. Sube los permisos de esa carpeta a `775` (o `777`
  si tu hosting lo exige) desde el administrador de archivos.
- **"Class PDO not found" o similar**: la extensión PDO SQLite no está
  activa en tu hosting. Pide a soporte que habilite `pdo_sqlite` para tu
  cuenta (es una extensión estándar, no debería tener coste).
- **Olvidaste el código de acceso**: borra (o renombra) el fichero
  `data/sorteo.sqlite` por FTP — perderás las inscripciones guardadas,
  así que exporta antes un CSV si puedes — y vuelve a entrar en
  `admin.php` para configurarlo de nuevo.
