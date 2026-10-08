#!/usr/bin/env python3
"""Música y efectos del vídeo, sincronizados con tiempos.json.

Sintetiza una base electrónica (tensión en el gancho, golpe al encender, ritmo
a 124 BPM durante los módulos y acorde final en la marca) y los efectos de cada
animación: barrido en cada cambio, chispazo al encenderse cada icono, clics en
las etiquetas. Si hay locución, la mezcla encima y baja la música mientras se
habla. Deja salida/audio.wav (para render.mjs) y salida/audio.m4a (para la
vista previa en el navegador), a -14 LUFS, el nivel de Instagram y TikTok.

    python3 audio.py                         # sin voz (o con la de tiempos.json)
    python3 audio.py --voz voz.mp3           # con locución
    python3 audio.py --musica tema.mp3       # con otra música en vez de la sintetizada
"""
import argparse
import json
import subprocess
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

AQUI = Path(__file__).resolve().parent
SR = 48000
BPM = 124
PULSO = 60 / BPM
rng = np.random.default_rng(7)


# ---------------------------------------------------------------- utilidades

def seg(s):
    return int(round(s * SR))


def tiempo(d):
    return np.arange(seg(d)) / SR


def filtro(x, tipo, f, orden=2):
    sos = butter(orden, f, btype=tipo, fs=SR, output="sos")
    return sosfilt(sos, x)


def ruido(d):
    return rng.standard_normal(seg(d))


def sierra(f, d, fase=0.0):
    t = tiempo(d)
    return 2 * ((t * f + fase) % 1) - 1


def poner(pista, sonido, t0, gan=1.0, pan=0.0):
    """Suma un sonido (mono o estéreo) a la pista estéreo en el segundo t0."""
    i = seg(t0)
    if i >= pista.shape[0] or i + len(sonido) <= 0:
        return
    if sonido.ndim == 1:
        izq, der = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        sonido = np.stack([sonido * izq * 1.414, sonido * der * 1.414], axis=1)
    a, b = max(0, i), min(pista.shape[0], i + len(sonido))
    pista[a:b] += gan * sonido[a - i:b - i]


def sala(x, segundos=2.2, humedo=0.28):
    """Reverberación barata: convolución con ruido que se apaga."""
    t = tiempo(segundos)
    ir = rng.standard_normal(len(t)) * np.exp(-t * 6.5 / segundos)
    ir = filtro(ir, "lowpass", 5000)
    ir /= np.sqrt(np.sum(ir ** 2))
    cola = fftconvolve(x, ir)[: len(x)]
    return x + humedo * cola


# ---------------------------------------------------------------- instrumentos

def bombo():
    t = tiempo(0.5)
    f = 44 + 120 * np.exp(-t * 32)
    cuerpo = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6.5)
    golpe = filtro(ruido(0.5), "highpass", 1500) * np.exp(-t * 260) * 0.35
    return np.tanh(1.6 * (cuerpo + golpe)) * 0.9


def charles(abierto=False):
    d = 0.22 if abierto else 0.06
    t = tiempo(d)
    return filtro(ruido(d), "highpass", 7500) * np.exp(-t * (18 if abierto else 70)) * 0.32


def palmada():
    t = tiempo(0.35)
    n = filtro(ruido(0.35), "bandpass", [900, 3200])
    env = np.exp(-t * 22)
    for retardo in (0.008, 0.017):
        env += 0.8 * np.exp(-np.clip(t - retardo, 0, None) * 140) * (t >= retardo)
    return sala(n * env * 0.4, 0.8, 0.25)


def caja_redoble(d, desde=4, hasta=16):
    """Redoble que se acelera, para la subida antes de la marca."""
    salida = np.zeros(seg(d) + seg(0.2))
    t, k = 0.0, 0
    while t < d:
        frac = t / d
        golpe_ = filtro(ruido(0.12), "bandpass", [1200, 6000]) * np.exp(-tiempo(0.12) * 40)
        poner_mono(salida, golpe_ * (0.25 + 0.75 * frac), t)
        t += PULSO / (desde + (hasta - desde) * frac)
        k += 1
    return salida


def poner_mono(pista, sonido, t0, gan=1.0):
    i = seg(t0)
    b = min(len(pista), i + len(sonido))
    if i < b:
        pista[i:b] += gan * sonido[: b - i]


def nota_bajo(f, d):
    t = tiempo(d)
    x = sierra(f, d) + 0.5 * sierra(f * 1.005, d, 0.3)
    x = filtro(x, "lowpass", 260, 4)
    env = np.minimum(1, t / 0.006) * np.exp(-t * 5)
    return np.tanh(2.0 * x * env) * 0.35


def acorde(frecuencias, d, brillo=1400, ataque=0.25):
    t = tiempo(d)
    izq = sum(sierra(f * 0.997, d, 0.11 * i) for i, f in enumerate(frecuencias))
    der = sum(sierra(f * 1.003, d, 0.37 * i) for i, f in enumerate(frecuencias))
    env = np.minimum(1, t / ataque) * np.minimum(1, (d - t) / 0.4).clip(0)
    izq = filtro(izq, "lowpass", brillo, 2) * env
    der = filtro(der, "lowpass", brillo, 2) * env
    return np.stack([izq, der], axis=1) * (0.09 / len(frecuencias)) * 3


def barrido(d=0.5, subida=True):
    """Whoosh: ruido que pasa de grave a agudo (o al revés)."""
    n = ruido(d)
    t = tiempo(d)
    bandas = [filtro(n, "bandpass", b) for b in ([200, 700], [700, 2500], [2500, 9000])]
    k = t / d if subida else 1 - t / d
    pesos = [np.clip(1 - 2 * k, 0, 1), 1 - np.abs(2 * k - 1), np.clip(2 * k - 1, 0, 1)]
    env = np.sin(np.pi * t / d) ** 1.5
    return sum(b * p for b, p in zip(bandas, pesos)) * env * 0.5


def chispazo(f0=700, f1=1700):
    """El 'clic' de encenderse: un pitido que sube más un chasquido."""
    d = 0.22
    t = tiempo(d)
    f = f0 + (f1 - f0) * (1 - np.exp(-t * 30))
    tono = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 22)
    tono += 0.35 * np.sin(4 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30)
    chasquido = filtro(ruido(d), "highpass", 3000) * np.exp(-t * 400) * 0.6
    return sala((tono * 0.28 + chasquido * 0.3), 1.0, 0.3)


def clic(f=2600):
    t = tiempo(0.04)
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 160) * 0.18


def porrazo():
    """Golpe grave de cada palabra del gancho."""
    t = tiempo(0.45)
    f = 40 + 90 * np.exp(-t * 20)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 8)
    x += filtro(ruido(0.45), "lowpass", 1200) * np.exp(-t * 30) * 0.5
    return np.tanh(1.5 * x) * 0.55


def impacto(d=2.6):
    t = tiempo(d)
    f = 30 + 70 * np.exp(-t * 6)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    estallido = filtro(ruido(d), "lowpass", 3500) * np.exp(-t * 7) * 0.9
    brillo = filtro(ruido(d), "highpass", 5000) * np.exp(-t * 4) * 0.25
    return sala(np.tanh(1.4 * (sub + estallido + brillo)) * 0.8, 3.0, 0.35)


def subida(d):
    """Riser: ruido y tono que suben hasta el golpe."""
    t = tiempo(d)
    k = t / d
    n = filtro(ruido(d), "highpass", 400)
    n = filtro(n, "lowpass", 9000)
    f = 180 + 900 * k ** 2
    tono = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25
    return (n * 0.35 + tono) * k ** 2.2 * 0.6


def tic_reloj():
    t = tiempo(0.05)
    return filtro(ruido(0.05), "bandpass", [2500, 6000]) * np.exp(-t * 180) * 0.25


def dron(d):
    t = tiempo(d)
    x = np.sin(2 * np.pi * 55 * t) + 0.6 * np.sin(2 * np.pi * 82.4 * t + 1) + 0.25 * sierra(110, d)
    x = filtro(x, "lowpass", 400)
    tremolo = 0.75 + 0.25 * np.sin(2 * np.pi * 0.5 * t)
    env = np.minimum(1, t / 0.6)
    return x * tremolo * env * 0.16


# ---------------------------------------------------------------- composición

LA, FA, DO, SOL = 55.0, 43.65, 65.41, 49.0
PROGRESION = [  # acordes de 2 compases: Lam, Fa, Do, Sol
    (LA, [220.0, 261.63, 329.63, 493.88]),
    (FA, [174.61, 220.0, 261.63, 392.0]),
    (DO, [196.0, 261.63, 329.63, 392.0]),
    (SOL, [196.0, 246.94, 293.66, 392.0]),
]


def musica(dur, T):
    esc = {e["id"]: e for e in T["escenas"]}
    flash, marca = T["flash"], esc["marca"]["ini"]
    pista = np.zeros((seg(dur) + SR, 2))
    lateral = np.zeros(seg(dur) + SR)        # envolvente del bombo, para el bombeo

    # gancho: tensión
    poner(pista, dron(flash + 0.2), 0, 1.0)
    t = 0.25
    while t < flash - 0.3:
        poner(pista, tic_reloj(), t, 1.0, -0.3 if int(t * 2) % 2 else 0.3)
        t += 0.5
    poner(pista, subida(1.3), flash - 1.3, 0.9)

    # ritmo desde el destello hasta la subida final
    fin_ritmo = marca - PULSO          # un pulso de silencio antes del golpe de marca
    redoble = 4 * PULSO * 2            # dos compases de redoble
    k = 0
    t = flash
    b = bombo()
    while t < fin_ritmo - 1e-6:
        en_compas = k % 4
        compas = k // 4
        poner(pista, b, t, 0.85)
        poner_mono(lateral, np.exp(-tiempo(0.32) * 9), t)
        if t < fin_ritmo - redoble or en_compas in (0, 2):
            poner(pista, charles(abierto=(en_compas == 3)), t + PULSO / 2, 0.8, 0.35)
            poner(pista, charles(), t + PULSO / 4 * 3, 0.35, -0.35)
        if en_compas in (1, 3) and t < fin_ritmo - redoble:
            poner(pista, palmada(), t, 0.7)
        raiz, notas = PROGRESION[(compas // 2) % 4]
        for c in range(2):                                    # bajo a corcheas
            if t + c * PULSO / 2 < fin_ritmo:
                poner(pista, nota_bajo(raiz * (2 if c else 1), PULSO / 2), t + c * PULSO / 2, 0.9)
        if en_compas == 0 and compas % 2 == 0:
            d = min(8 * PULSO, fin_ritmo - t) + 0.4
            brillo = 900 + 1600 * min(1, (t - flash) / max(1, fin_ritmo - flash))
            poner(pista, acorde(notas, d, brillo), t, 1.0)
        t += PULSO
        k += 1
    poner(pista, caja_redoble(redoble), fin_ritmo - redoble, 0.55)
    poner(pista, subida(redoble + PULSO), fin_ritmo - redoble, 0.8)

    # bombeo: la base respira con el bombo
    bombeo = 1 - 0.45 * np.clip(lateral, 0, 1)
    pista[:, 0] *= bombeo
    pista[:, 1] *= bombeo
    poner(pista, impacto(1.6), flash, 0.9)

    # marca: golpe y acorde final que se apaga
    poner(pista, impacto(), marca, 1.0)
    cola = dur - marca + 0.5
    final = acorde([110.0, 220.0, 261.63, 329.63, 493.88], cola, 1800, 0.05)
    final *= np.linspace(1, 0, len(final))[:, None] ** 1.6
    poner(pista, final * 1.6, marca, 1.0)
    poner(pista, nota_bajo(LA, 2.5) * np.exp(-tiempo(2.5) * 0.5) * 3, marca, 0.6)
    return pista


def efectos(dur, T):
    esc = {e["id"]: e for e in T["escenas"]}
    pista = np.zeros((seg(dur) + SR, 2))
    modulos = [e for e in T["escenas"][2:19]]
    # gancho: un golpe por palabra (mismos instantes que escena.html)
    g = esc["gancho"]
    for trozo in ("Tu", "todavía", "trabaja", "a mano"):
        i = g["texto"].find(trozo)
        t0 = g["vozIni"] + (g["vozFin"] - g["vozIni"]) * i / len(g["texto"]) - 0.06
        poner(pista, porrazo(), t0, 1.3 if trozo == "a mano" else 0.8)
    poner(pista, barrido(0.5, True), esc["encender"]["ini"] - 0.1, 0.5)
    poner(pista, chispazo(400, 1200), T["flash"] - 0.04, 0.9)
    # módulos
    for n, e in enumerate(modulos):
        poner(pista, barrido(0.48, n % 2 == 0), e["ini"] - 0.22, 0.75, -0.25 if n % 2 else 0.25)
        poner(pista, chispazo(650 + 25 * n, 1600 + 40 * n), e["ini"] + 0.45, 0.8)
        for c in range(3):
            poner(pista, clic(2300 + 300 * c), e["ini"] + 0.62 + 0.14 * c + 0.08, 0.6, (c - 1) * 0.4)
    # diecisiete: un chispazo por icono, subiendo de tono
    d = esc["diecisiete"]
    poner(pista, barrido(0.5, True), d["ini"] - 0.22, 0.8)
    for j in range(17):
        f = 440 * 2 ** ((j * 2) / 12 / 2)
        poner(pista, chispazo(f, f * 2.2) * 0.8, d["ini"] + 0.08 + j * 0.055 + 0.1, 0.55, (j % 5 - 2) * 0.3)
    poner(pista, barrido(0.6, False), d["fin"] - 0.45, 0.6)
    # marca: clic del botón web
    m = esc["marca"]
    i = m["texto"].find("Entra")
    t_boton = m["vozIni"] + (m["vozFin"] - m["vozIni"]) * i / len(m["texto"]) - 0.1
    poner(pista, chispazo(900, 2000), t_boton, 0.7)
    return pista


# ---------------------------------------------------------------- mezcla

def leer_audio(ruta, dur):
    crudo = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(ruta), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
        capture_output=True, check=True).stdout
    x = np.frombuffer(crudo, dtype=np.float32).reshape(-1, 2).astype(np.float64)
    salida = np.zeros((seg(dur) + SR, 2))
    n = min(len(x), len(salida))
    salida[:n] = x[:n]
    return salida


def envolvente(x, ataque=0.01, suelta=0.3):
    """Nivel de la voz, suavizado, para saber cuándo se habla."""
    nivel = np.abs(x).max(axis=1)
    paso = 240
    bloques = nivel[: len(nivel) // paso * paso].reshape(-1, paso).max(axis=1)
    a, s = np.exp(-paso / (SR * ataque)), np.exp(-paso / (SR * suelta))
    env = np.zeros_like(bloques)
    v = 0.0
    for i, b in enumerate(bloques):
        v = a * v + (1 - a) * b if b > v else s * v + (1 - s) * b
        env[i] = v
    env = np.repeat(env, paso)
    return np.pad(env, (0, len(nivel) - len(env)), mode="edge")


def guardar_wav(ruta, x):
    datos = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(datos.tobytes())


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--voz", help="locución (si no, la de tiempos.json, si la hay)")
    parser.add_argument("--musica", help="música propia en vez de la sintetizada")
    args = parser.parse_args()

    T = json.loads((AQUI / "tiempos.json").read_text(encoding="utf-8"))
    dur = T["duracion"]
    voz_ruta = args.voz or T.get("voz")

    if args.musica:
        base = leer_audio(args.musica, dur) * 0.5
        base *= np.minimum(1, np.linspace(dur, 0, len(base)) / 2.5)[:, None]   # fundido final
    else:
        base = musica(dur, T)
    fx = efectos(dur, T)

    if voz_ruta:
        voz = leer_audio(voz_ruta, dur)
        voz = np.stack([filtro(voz[:, c], "highpass", 80) for c in range(2)], axis=1)
        voz *= 0.5 / max(1e-6, np.abs(voz).max())
        env = envolvente(voz)
        habla = np.clip(env / 0.12, 0, 1)[:, None]
        mezcla = base * (0.55 - 0.32 * habla) + fx * (0.75 - 0.25 * habla) + voz * 1.0
    else:
        mezcla = base * 0.6 + fx * 0.8

    mezcla = mezcla[: seg(dur)]
    mezcla = np.tanh(mezcla * 1.2) / np.tanh(1.2)            # limitador suave
    mezcla *= 0.9 / max(1e-6, np.abs(mezcla).max())

    salida = AQUI / "salida"
    salida.mkdir(exist_ok=True)
    crudo = salida / "audio-crudo.wav"
    guardar_wav(crudo, mezcla)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(crudo),
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), str(salida / "audio.wav")], check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(salida / "audio.wav"),
                    "-c:a", "aac", "-b:a", "192k", str(salida / "audio.m4a")], check=True)
    crudo.unlink()
    print(f"salida/audio.wav ({dur:.1f} s{', con voz' if voz_ruta else ', sin voz'})")


if __name__ == "__main__":
    main()
