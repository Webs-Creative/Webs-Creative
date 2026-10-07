# Vídeo de captación · Gestoría Creative

Vídeo de 47 segundos para captar gestorías, en horizontal 16:9 (1920×1080) y vertical 9:16 (1080×1920) para Reels,
TikTok y Stories, a 30 fps: gancho, presentación del logo, ocho pantallas
reales del programa y cierre con «Pide tu demo hoy».

| Qué | Archivo |
|---|---|
| Vídeo horizontal con música (sin voz) | [`gestoria-creative-video.mp4`](gestoria-creative-video.mp4) |
| Vídeo vertical con música (sin voz) | [`gestoria-creative-video-vertical.mp4`](gestoria-creative-video-vertical.mp4) |
| Subtítulos | [`gestoria-creative-video.srt`](gestoria-creative-video.srt) |
| Escenas, textos y tiempos | [`fuente/escenas.json`](fuente/escenas.json) |
| Animación (HTML) y pantallas usadas | [`fuente/`](fuente/) |

## Textos de la voz (ElevenLabs)

Un archivo por frase, `01.mp3` a `10.mp3`, en español de España (Eleven Multilingual v2, Stability 40–50 %,
Similarity 75 %, Style 25–35 %).

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

Con las voces en una carpeta: `python3 fuente/herramientas/montar-voz.py <carpeta-voces> fuente`. Mide cada frase,
ajusta su escena, vuelve a generar las dos versiones y la música, baja la música mientras se habla y normaliza a
−14 LUFS.

La música es original (generada con `musica.py`), sin derechos de terceros. Las pantallas son de la cuenta de
demostración con datos ficticios.
