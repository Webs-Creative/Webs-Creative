#!/usr/bin/env python3
"""Decide cuándo empieza y acaba cada escena del vídeo.

Sin voz, estima lo que tarda en decirse cada frase de guion.json.
Con --voz, busca los silencios de la locución (el MP3 de ElevenLabs) y coloca
cada escena donde empieza su frase. Escribe tiempos.json, que leen escena.html
(las animaciones) y audio.py (la música y los efectos).

    python3 tiempos.py                 # tiempos estimados
    python3 tiempos.py --voz voz.mp3   # tiempos de la locución real
"""
import argparse
import json
import math
import os
import re
import subprocess
from pathlib import Path

AQUI = Path(__file__).resolve().parent

LETRAS_POR_SEGUNDO = 16.5   # ritmo de una voz de ElevenLabs a velocidad 1.1
PAUSA_ENTRE_FRASES = 0.45
ENTRADA = 0.45              # silencio antes de la primera palabra
ADELANTO = 0.35             # la escena entra un poco antes que su frase
ADELANTO_ENCENDER = 0.70    # el botón tiene que verse antes de pulsarse
COLA = 3.0                  # lo que sigue en pantalla el final tras la última palabra
MINIMOS = {"encender": 3.4, "diecisiete": 2.8}
MINIMO_MODULO = 2.5


def estimar(texto):
    pausas = 0.22 * len(re.findall(r"[,…:;]", texto))
    pausas += 0.32 * len(re.findall(r"[.?!](?=\s)", texto))
    return len(texto) / LETRAS_POR_SEGUNDO + pausas


def duracion_audio(ruta):
    salida = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ruta)],
        capture_output=True, text=True, check=True).stdout
    return float(salida.strip())


def silencios(ruta, umbral_db, minimo):
    salida = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(ruta),
         "-af", f"silencedetect=noise={umbral_db}dB:d={minimo}", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    inicios = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", salida)]
    finales = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", salida)]
    total = duracion_audio(ruta)
    if len(finales) < len(inicios):
        finales.append(total)
    return [(max(0.0, a), b) for a, b in zip(inicios, finales)], total


def trocear_voz(ruta, frases):
    """Reparte la locución en tantas frases como tiene el guion.

    Entre todos los silencios elige los que mejor separan las frases: los que
    dejan cada trozo con una duración parecida a la estimada y, a igualdad, los
    silencios más largos (los de fin de frase).
    """
    n = len(frases)
    for minimo in (0.18, 0.14, 0.10, 0.07):
        lista, total = silencios(ruta, -38, minimo)
        habla_ini = lista[0][1] if lista and lista[0][0] < 0.05 else 0.0
        habla_fin = lista[-1][0] if lista and lista[-1][1] >= total - 0.05 else total
        huecos = [s for s in lista if s[0] > habla_ini + 0.05 and s[1] < habla_fin - 0.05]
        if len(huecos) >= n - 1:
            break
    else:
        raise SystemExit(
            f"La locución solo tiene {len(huecos) + 1} frases separadas por silencios y el guion "
            f"tiene {n}. Genérala otra vez dejando una línea en blanco entre frases.")

    esperado = [estimar(f["voz"]) for f in frases]
    hueco_tipico = sorted((b - a for a, b in huecos), reverse=True)[n - 2]
    escala = (habla_fin - habla_ini - (n - 1) * hueco_tipico) / sum(esperado)
    esperado = [e * escala for e in esperado]

    k = len(huecos)
    infinito = float("inf")
    # coste[i][j]: mejor reparto de las frases 0..i con la frase i acabando en el hueco j
    coste = [[infinito] * k for _ in range(n - 1)]
    previo = [[-1] * k for _ in range(n - 1)]

    def trozo(i, desde, hasta):
        d = max(hasta - desde, 0.05)
        return 4.0 * math.log(d / esperado[i]) ** 2

    def premio(j):
        a, b = huecos[j]
        return -1.5 * min(b - a, 1.0)

    for j in range(k):
        coste[0][j] = trozo(0, habla_ini, huecos[j][0]) + premio(j)
    for i in range(1, n - 1):
        for j in range(i, k):
            for p in range(i - 1, j):
                c = coste[i - 1][p] + trozo(i, huecos[p][1], huecos[j][0]) + premio(j)
                if c < coste[i][j]:
                    coste[i][j], previo[i][j] = c, p
    mejor, ultimo = infinito, -1
    for j in range(n - 2, k):
        c = coste[n - 2][j] + trozo(n - 1, huecos[j][1], habla_fin)
        if c < mejor:
            mejor, ultimo = c, j
    elegidos = [ultimo]
    for i in range(n - 2, 0, -1):
        elegidos.append(previo[i][elegidos[-1]])
    elegidos.reverse()

    tramos, desde = [], habla_ini
    for j in elegidos:
        tramos.append((desde, huecos[j][0]))
        desde = huecos[j][1]
    tramos.append((desde, habla_fin))
    return tramos, total


def tramos_estimados(frases):
    tramos, t = [], ENTRADA
    for i, f in enumerate(frases):
        d = estimar(f["voz"])
        tramos.append((t, t + d))
        t += d + PAUSA_ENTRE_FRASES
    return tramos


def escenas(frases, tramos, estirar):
    """Pasa de cuándo suena cada frase a cuándo se ve cada escena."""
    tramos = list(tramos)
    salida = []
    for i, f in enumerate(frases):
        voz_ini, voz_fin = tramos[i]
        if i == 0:
            ini = 0.0
        else:
            adelanto = ADELANTO_ENCENDER if f["id"] == "encender" else ADELANTO
            ini = max(tramos[i - 1][1] - 0.05, voz_ini - adelanto)
        salida.append({"id": f["id"], "texto": f["voz"], "ini": ini, "vozIni": voz_ini, "vozFin": voz_fin})
    for i in range(len(salida) - 1):
        salida[i]["fin"] = salida[i + 1]["ini"]
    salida[-1]["fin"] = salida[-1]["vozFin"] + COLA

    if estirar:
        # Sin voz real se puede alargar: lo que falte a una escena empuja a las siguientes.
        for i, e in enumerate(salida[:-1]):
            minimo = MINIMOS.get(e["id"], MINIMO_MODULO if 2 <= i <= 18 else 0)
            falta = minimo - (e["fin"] - e["ini"])
            if falta > 0:
                for siguiente in salida[i + 1:]:
                    for clave in ("ini", "vozIni", "vozFin", "fin"):
                        siguiente[clave] += falta
                e["fin"] += falta
    else:
        for i, e in enumerate(salida[:-1]):
            minimo = MINIMOS.get(e["id"], MINIMO_MODULO if 2 <= i <= 18 else 0)
            if e["fin"] - e["ini"] < minimo - 0.3:
                print(f"Aviso: la escena «{e['id']}» dura {e['fin'] - e['ini']:.2f} s; se verá con prisa.")
    for e in salida:
        for clave in ("ini", "fin", "vozIni", "vozFin"):
            e[clave] = round(e[clave], 3)
    return salida


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--voz", help="MP3 o WAV de la locución completa")
    parser.add_argument("--salida", default=str(AQUI / "tiempos.json"))
    args = parser.parse_args()

    frases = json.loads((AQUI / "guion.json").read_text(encoding="utf-8"))
    if args.voz:
        tramos, _ = trocear_voz(Path(args.voz), frases)
        lista = escenas(frases, tramos, estirar=False)
    else:
        lista = escenas(frases, tramos_estimados(frases), estirar=True)

    encender = next(e for e in lista if e["id"] == "encender")
    datos = {
        "fps": 30,
        "ancho": 1080,
        "alto": 1920,
        "duracion": lista[-1]["fin"],
        "flash": round(encender["vozIni"] + 0.22, 3),
        "voz": os.path.relpath(Path(args.voz).resolve(), AQUI) if args.voz else None,
        "escenas": lista,
    }
    texto = json.dumps(datos, ensure_ascii=False, indent=2)
    Path(args.salida).write_text(texto, encoding="utf-8")
    # La escena abierta a mano en el navegador no puede leer JSON del disco: lo carga como script.
    Path(args.salida).with_suffix(".js").write_text(f"window.TIEMPOS = {texto};\n", encoding="utf-8")
    print(f"{len(lista)} escenas, {datos['duracion']:.1f} s → {args.salida}")
    for e in lista:
        print(f"  {e['id']:<16} {e['ini']:6.2f} → {e['fin']:6.2f}   voz {e['vozIni']:6.2f} → {e['vozFin']:6.2f}")


if __name__ == "__main__":
    main()
