# Vídeo de captación · Gestoría Creative

Vídeo de 50 segundos con voz en off para captar gestorías, en horizontal 16:9 (1920×1080) y vertical 9:16 (1080×1920) para Reels,
TikTok y Stories, a 30 fps: gancho, presentación del logo, ocho pantallas
reales del programa y cierre con «Pide tu demo hoy».

| Qué | Archivo |
|---|---|
| Vídeo horizontal con voz y música | [`gestoria-creative-video.mp4`](gestoria-creative-video.mp4) |
| Vídeo vertical con voz y música | [`gestoria-creative-video-vertical.mp4`](gestoria-creative-video-vertical.mp4) |
| Vídeo horizontal, versión clara | [`gestoria-creative-video-claro.mp4`](gestoria-creative-video-claro.mp4) |
| Vídeo vertical, versión clara | [`gestoria-creative-video-vertical-claro.mp4`](gestoria-creative-video-vertical-claro.mp4) |
| Subtítulos | [`gestoria-creative-video.srt`](gestoria-creative-video.srt) |
| Escenas, textos y tiempos | [`fuente/escenas.json`](fuente/escenas.json) (base) y [`fuente/escenas-voz.json`](fuente/escenas-voz.json) (ajustados a la voz) |
| Voces de ElevenLabs (01–10) | [`fuente/voces/`](fuente/voces/) |
| Animación (HTML) y pantallas usadas | [`fuente/`](fuente/) |

## Versión clara

Misma voz, música, tiempos y animaciones, con fondo crema, pantallas del programa en tema claro
([`fuente/pantallas-claro/`](fuente/pantallas-claro/)) y los efectos (partículas, estelas, destello y barridos) en
tonos claros. `video-claro.html` y `video-vertical-claro.html` se generan a partir de los oscuros con
`python3 fuente/herramientas/tema-claro.py fuente/video.html fuente/video-claro.html` (y lo mismo con el vertical),
así que cualquier cambio de textos o tiempos se hace en los oscuros y se vuelve a generar el claro.

## Textos de la voz (ElevenLabs)

Un archivo por frase, `01.mp3` a `10.mp3`, en español de España (Eleven Multilingual v2, Stability 40–50 %,
Similarity 75 %, Style 25–35 %). La versión montada usa la voz «Martin Osborne – Polished and Energetic».

| Archivo | Texto |
|---|---|
| 01 | ¿Tu gestoría sigue persiguiendo papeles, plazos y certificados? |
| 02 | Te presentamos Gestoría Creative. |
| 03 | Todo tu despacho en una sola pantalla. Cada mañana, lo urgente primero. |
| 04 | Los modelos se preparan solos con las facturas de tus clientes. |
| 05 | Cada factura se lee, se comprueba y se coteja con Hacienda. |
| 06 | El banco se concilia solo cada noche, con el porqué de cada propuesta. |
| 07 | Vigila el BOE por ti y te avisa solo de lo que afecta a tus clientes. |
| 08 | Y los certificados de tus clientes, en una bóveda que ni nosotros podemos abrir. |
| 09 | Tus clientes te lo envían todo desde el móvil. |
| 10 | Gestoría Creative. En la nube y con inteligencia artificial incluida. Pide tu demo hoy. |

## Montar las voces

Para cambiar una frase, sustituye su archivo en `fuente/voces/` y ejecuta
`python3 fuente/herramientas/montar-voz.py fuente/voces fuente`. Mide cada frase,
ajusta su escena, vuelve a generar las cuatro versiones (oscura y clara, en horizontal y vertical) y la música, baja la música mientras se habla y normaliza a
−14 LUFS.

Requisitos: ffmpeg, Python con numpy y scipy, y Node con `playwright-core` (`npm i playwright-core` dentro de
`fuente/herramientas/`). Si Chromium no está en la ruta por defecto, indícala con la variable `CHROME`.

La música es original (generada con `musica.py`), sin derechos de terceros. Las pantallas son de la cuenta de
demostración con datos ficticios.
