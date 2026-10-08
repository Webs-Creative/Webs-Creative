# Vídeo promocional · Módulos para Dolibarr

Vídeo vertical (1080 × 1920, 30 fps, unos 70 s) para Reels, TikTok y Shorts con
los 17 módulos de la tienda. Concepto: **«Enciende tu Dolibarr»**, con el botón
de encendido del logo. Sin precios.

1. **Gancho:** «¿Tu Dolibarr todavía trabaja a mano?», en gris y con «copiar →
   pegar → repetir» de fondo.
2. **Encendido:** se pulsa el botón, destello y todo pasa a naranja.
3. **Los 17 módulos**, uno cada ~3 s: categoría, icono que se enciende, nombre,
   lema y tres etiquetas. Arriba, la barra de progreso tipo «stories».
4. **«17 módulos · Cero trabajo a mano»** con los 17 iconos.
5. **Marca:** logo, «Enciende tu Dolibarr», webscreative.es y WhatsApp.

## Ficheros

| Fichero | Qué es |
|---|---|
| `guion.json` | Las 21 frases de la locución, una por escena. |
| `guion-elevenlabs.txt` | Las mismas frases, listas para pegar en ElevenLabs. |
| `escena.html` | Las animaciones. Abierto en el navegador se reproduce (clic: pausa; flechas: ±1 s). |
| `tiempos.py` | Calcula cuándo empieza cada escena: estimado o leyendo la locución real. |
| `audio.py` | Sintetiza la música y los efectos y los mezcla con la voz. |
| `render.mjs` | Graba `escena.html` fotograma a fotograma y saca el MP4. |
| `fuentes/` | Inter Display y JetBrains Mono (licencia OFL). |

Lo generado va a `salida/` (no se sube al repositorio).

## Poner la voz

1. En ElevenLabs, pega `guion-elevenlabs.txt` tal cual, con las líneas en
   blanco entre frases: son las pausas con las que se sincroniza cada escena.
   Modelo **Eleven Multilingual v2**, una voz de España enérgica, de anuncio.
   Ajustes de partida: estabilidad 40 %, similitud 75 %, estilo 25 %,
   velocidad 1,05–1,1.
2. Descarga el MP3 en una sola pieza y guárdalo como `voz.mp3` en esta carpeta.
3. Vuelve a montar:

```bash
python3 tiempos.py --voz voz.mp3   # cada escena entra cuando empieza su frase
python3 audio.py                   # música + efectos + voz, a -14 LUFS
node render.mjs                    # → salida/video.mp4
```

Si `tiempos.py` dice que faltan pausas, vuelve a generar la voz dejando las
líneas en blanco. Para usar otra música (por ejemplo, de Eleven Music):
`python3 audio.py --musica tema.mp3`.

## Requisitos

Python 3 con `numpy` y `scipy`, Node 18+ con `playwright` (Chromium) y `ffmpeg`.
Para revisar escenas sueltas sin grabar todo: `node render.mjs --fotos 4,12.5,60`.
