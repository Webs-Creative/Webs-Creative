#!/usr/bin/env python3
"""Monta las voces de ElevenLabs (01..10) en el vídeo de Gestoría Creative.

Uso: python3 montar-voz.py <carpeta-voces> <carpeta-video>
  1. Mide cada voz y ajusta la duración de su escena (escenas-voz.json).
  2. Vuelve a generar el vídeo y la música con esos tiempos.
  3. Coloca cada voz en su escena, baja la música mientras se habla y normaliza a -14 LUFS.
Salida: <carpeta-video>/gestoria-creative-video.mp4 (16:9), gestoria-creative-video-vertical.mp4 (9:16) y .srt
"""
import json, pathlib, subprocess, sys

VOCES = pathlib.Path(sys.argv[1]); V = pathlib.Path(sys.argv[2]); T = pathlib.Path(__file__).parent
base = json.loads((V / "escenas.json").read_text(encoding="utf-8"))
MIN = {"gancho": 4.2, "logo": 3.0, "cierre": 6.0}
DESFASE = {"logo": 0.45, "cierre": 0.6}


def duracion(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(f)], capture_output=True, text=True)
    return float(r.stdout.strip())


def buscar(clave):
    for ext in (".mp3", ".wav", ".m4a", ".ogg"):
        f = VOCES / f"{clave}{ext}"
        if f.exists():
            return f
    raise SystemExit(f"Falta la voz {clave} en {VOCES}")


escenas, t, entradas = [], 0.0, []
for e in base["escenas"]:
    f = buscar(e["voz"]); d = duracion(f)
    des = DESFASE.get(e["id"], 0.25)
    dur = max(MIN.get(e["id"], 3.6), des + d + 0.55)
    escenas.append(dict(e, dur=round(dur, 3), voz_desfase=des))
    entradas.append((f, t + des))
    print(f"  {e['voz']} {e['id']:<11} voz {d:5.2f} s → escena {dur:5.2f} s")
    t += dur
datos = dict(base, escenas=escenas)
(V / "escenas-voz.json").write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"Duración total: {t:.2f} s")

import os
SIN_RENDER = os.environ.get("PRUEBA_SIN_RENDER") == "1"  # solo para probar la mezcla de audio
for html, ancho, alto, nombre in (("video.html", 1920, 1080, "video-voz-sin-audio.mp4"), ("video-vertical.html", 1080, 1920, "video-vertical-voz-sin-audio.mp4")):
    if SIN_RENDER:
        continue
    subprocess.run(["node", str(T / "render-video.js"), "completo", str(V / nombre)], check=True,
                   env={**os.environ, "CARPETA": str(V.resolve()), "ESCENAS": "escenas-voz.json", "HTML": html, "ANCHO": str(ancho), "ALTO": str(alto)})
subprocess.run(["python3", str(T / "musica.py"), str(V / "escenas-voz.json"), str(V / "musica-voz.wav")], check=True)
subprocess.run(["python3", str(T / "srt.py"), str(V / "escenas-voz.json"), str(V / "gestoria-creative-video.srt")], check=True)

# Pista de voz: cada frase en su sitio
cmd = ["ffmpeg", "-y", "-v", "error"]
for f, _ in entradas:
    cmd += ["-i", str(f)]
filtros = []
for i, (_, ini) in enumerate(entradas):
    ms = int(ini * 1000)
    filtros.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms}[v{i}]")
filtros.append("".join(f"[v{i}]" for i in range(len(entradas))) + f"amix=inputs={len(entradas)}:normalize=0,apad=whole_dur={t + 1.5}[voz]")
cmd += ["-filter_complex", ";".join(filtros), "-map", "[voz]", str(V / "voz.wav")]
subprocess.run(cmd, check=True)

# Mezcla: la música baja cuando habla la voz (una sola pista para las dos versiones)
subprocess.run([
    "ffmpeg", "-y", "-v", "error", "-i", str(V / "musica-voz.wav"), "-i", str(V / "voz.wav"),
    "-filter_complex",
    "[0:a]volume=0.55[m];[1:a]asplit=2[v1][v2];[m][v1]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=350[md];"
    "[md][v2]amix=inputs=2:normalize=0:weights=1 1.6,loudnorm=I=-14:TP=-1.5:LRA=11[a]",
    "-map", "[a]", "-ar", "48000", str(V / "mezcla.wav")], check=True)
for video, salida in ([] if SIN_RENDER else (("video-voz-sin-audio.mp4", "gestoria-creative-video.mp4"), ("video-vertical-voz-sin-audio.mp4", "gestoria-creative-video-vertical.mp4"))):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(V / video), "-i", str(V / "mezcla.wav"), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(V / salida)], check=True)
    print("Vídeo con voz:", V / salida)
