#!/usr/bin/env python3
"""Banda sonora original para el vídeo de Gestoría Creative, sincronizada con escenas.json.

Uso: python3 musica.py <escenas.json> <salida.wav>
Capas: dron y tictac en el gancho, subida y golpe al aparecer el logo, ritmo (bombo, bajo, platillos y
acordes) durante las pantallas, barridos de aire en cada cambio de escena y golpe final con acorde largo.
"""
import json, sys
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 48000
datos = json.load(open(sys.argv[1]))
escenas = datos["escenas"]
inicios, t = [], 0.0
for e in escenas:
    inicios.append(t); t += e["dur"]
TOTAL = t
DUR = TOTAL + 1.5
N = int(DUR * SR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(3)
ini = {e["id"]: s for e, s in zip(escenas, inicios)}
T_LOGO, T_PANEL, T_CIERRE = ini["logo"], ini["panel"], ini["cierre"]


def tt(n):
    return np.arange(n) / SR


def add(sig, t0, gl=1.0, gr=None):
    gr = gl if gr is None else gr
    i = int(t0 * SR)
    if i >= N:
        return
    j = min(N, i + len(sig))
    L[i:j] += sig[: j - i] * gl
    R[i:j] += sig[: j - i] * gr


def filtro(sig, tipo, f, orden=2):
    sos = butter(orden, f, btype=tipo, fs=SR, output="sos")
    return sosfilt(sos, sig)


def saw(f, n, fase=0.0):
    x = (tt(n) * f + fase) % 1.0
    return 2 * x - 1


def env_adsr(n, a, d, s, r):
    e = np.ones(n) * s
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    na = max(1, min(na, n)); e[:na] = np.linspace(0, 1, na)
    nd = max(1, min(nd, n - na)); e[na:na + nd] = np.linspace(1, s, nd)
    if nr > 0 and nr < n:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def nota(m):
    return 440.0 * 2 ** ((m - 69) / 12)

# ------------------------------------------------------------------ acordes (La menor · Fa · Do · Sol)
ACORDES = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
RAICES = [45, 41, 36, 43]
COMPAS = 2.0  # segundos por acorde (120 ppm, un compás)


def pad(t0, t1, gan=0.10, corte=1400):
    n = int((t1 - t0) * SR)
    out_l = np.zeros(n); out_r = np.zeros(n)
    k = 0
    pos = 0.0
    while pos < t1 - t0:
        dur = min(COMPAS * 2, t1 - t0 - pos)
        m = int(dur * SR) + int(0.4 * SR)
        voz_l = np.zeros(m); voz_r = np.zeros(m)
        for nm in ACORDES[k % 4]:
            f = nota(nm)
            voz_l += saw(f * 2 ** (-7 / 1200), m, rng.random()) + 0.5 * saw(f * 2, m, rng.random())
            voz_r += saw(f * 2 ** (7 / 1200), m, rng.random()) + 0.5 * saw(f * 2, m, rng.random())
        e = env_adsr(m, 0.35, 0.5, 0.85, 0.5)
        voz_l = filtro(voz_l, "low", corte) * e; voz_r = filtro(voz_r, "low", corte) * e
        i = int(pos * SR); j = min(n, i + m)
        out_l[i:j] += voz_l[: j - i]; out_r[i:j] += voz_r[: j - i]
        pos += COMPAS * 2; k += 1
    add(out_l * gan, t0, 1, 0); add(out_r * gan, t0, 0, 1)


def bombo(t0, gan=0.9):
    n = int(0.45 * SR); x = tt(n)
    f = 45 + 95 * np.exp(-x * 28)
    fase = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(fase) * np.exp(-x * 7.5)
    s[: int(0.004 * SR)] += rng.normal(0, 0.6, int(0.004 * SR))
    add(np.tanh(s * 1.6) * gan, t0)


def plato(t0, gan=0.12, abierto=False):
    n = int((0.35 if abierto else 0.06) * SR)
    s = filtro(rng.normal(0, 1, n), "high", 7500) * np.exp(-tt(n) * (9 if abierto else 60))
    add(s * gan, t0, 0.8, 1.0)


def bajo(t0, m, dur=0.22, gan=0.32):
    n = int(dur * SR); f = nota(m)
    s = filtro(saw(f, n) + 0.6 * np.sin(2 * np.pi * f / 2 * tt(n)), "low", 420) * env_adsr(n, 0.005, 0.08, 0.7, 0.06)
    add(s * gan, t0)


def soplo(t0, dur=0.8, gan=0.35, sube=True):
    """Barrido de aire: ruido filtrado que sube (o baja) de frecuencia."""
    n = int(dur * SR); x = np.linspace(0, 1, n)
    ruido = rng.normal(0, 1, n)
    out = np.zeros(n); trozos = 24
    for k in range(trozos):
        a, b = k * n // trozos, (k + 1) * n // trozos
        c = (k + 0.5) / trozos
        fc = 300 * (40 ** (c if sube else 1 - c))
        out[a:b] = filtro(ruido[a - 2000 if a > 2000 else 0:b], "band", [fc * 0.7, min(fc * 1.4, 20000)])[-(b - a):]
    e = np.sin(np.pi * x) ** 1.5
    add(out * e * gan, t0, 1.0, 0.75)
    add(out[::-1] * e * gan * 0.5, t0 + 0.02, 0.6, 1.0)


def subida(t_fin, dur=1.6, gan=0.32):
    n = int(dur * SR); x = np.linspace(0, 1, n)
    s = filtro(rng.normal(0, 1, n), "high", 1800) * x ** 2.2
    tono = np.sin(2 * np.pi * np.cumsum(220 + 660 * x ** 2) / SR) * x ** 3 * 0.25
    add((s + tono) * gan, t_fin - dur)


def golpe(t0, gan=1.0):
    n = int(2.4 * SR); x = tt(n)
    f = 32 + 70 * np.exp(-x * 9)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 2.1)
    s += filtro(rng.normal(0, 1, n), "low", 900) * np.exp(-x * 5) * 0.7
    s += filtro(rng.normal(0, 1, n), "high", 4000) * np.exp(-x * 9) * 0.25
    add(np.tanh(s * 1.4) * gan, t0)


def tictac(t0, t1, gan=0.10):
    t = t0
    while t < t1:
        n = int(0.03 * SR)
        s = np.sin(2 * np.pi * 2400 * tt(n)) * np.exp(-tt(n) * 220)
        add(s * gan, t, 0.7, 1.0)
        t += 0.5


def dron(t0, t1, gan=0.16):
    n = int((t1 - t0) * SR); x = tt(n)
    s = np.sin(2 * np.pi * nota(33) * x) + 0.5 * saw(nota(45), n)
    s = filtro(s, "low", 300) * np.minimum(1, x / 0.8) * np.minimum(1, (x[-1] - x) / 0.3 + 0.0001)
    add(s * gan, t0)

# ------------------------------------------------------------------ montaje
# Gancho: dron grave, tictac de reloj y subida hacia el logo
dron(0, T_LOGO)
tictac(0.15, T_LOGO - 0.3)
subida(T_LOGO, dur=1.8)
golpe(T_LOGO, 1.0)
pad(T_LOGO, T_CIERRE + 0.6, gan=0.085, corte=1100)

# Ritmo durante las pantallas: bombo en cada pulso, platillo a contratiempo y bajo en corcheas
b = 0.5
t = T_PANEL
k = 0
while t < T_CIERRE - 0.05:
    compas = int((t - T_LOGO) / COMPAS / 2) % 4
    bombo(t, 0.85)
    plato(t + 0.25, 0.10)
    if k % 8 == 7:
        plato(t + 0.25, 0.10, abierto=True)
    for c in range(2):
        bajo(t + c * 0.25, RAICES[compas] + (12 if (k % 4 == 3 and c == 1) else 0))
    t += b; k += 1
# Golpes suaves en el logo antes de que entre el ritmo
for x in np.arange(T_LOGO + 1.0, T_PANEL - 0.1, 1.0):
    bombo(x, 0.5)

# Barridos en cada cambio de escena
for s in inicios[1:]:
    soplo(s - 0.45, dur=0.8, gan=0.30, sube=True)

# Cierre: subida, golpe y acorde final largo
subida(T_CIERRE, dur=1.2, gan=0.25)
golpe(T_CIERRE, 1.0)
n = int((DUR - T_CIERRE) * SR)
fin_l = np.zeros(n); fin_r = np.zeros(n)
for nm in [45, 57, 60, 64, 69, 76]:
    f = nota(nm)
    fin_l += saw(f * 2 ** (-5 / 1200), n) * 0.5; fin_r += saw(f * 2 ** (5 / 1200), n) * 0.5
e = env_adsr(n, 0.6, 1.0, 0.8, 2.2)
add(filtro(fin_l, "low", 1800) * e * 0.07, T_CIERRE, 1, 0); add(filtro(fin_r, "low", 1800) * e * 0.07, T_CIERRE, 0, 1)
# un pulso lento bajo el «Pide tu demo»
for x in np.arange(T_CIERRE + 2.0, TOTAL - 0.8, 1.0):
    bombo(x, 0.45)

# ------------------------------------------------------------------ mezcla
st = np.stack([L, R], axis=1)
st = filtro(st.T, "high", 28).T  # quita el rumor por debajo de lo audible
st = np.tanh(st * 1.15)
fade = int(1.2 * SR)
st[-fade:] *= np.linspace(1, 0, fade)[:, None]
st = st / np.max(np.abs(st)) * 0.89
wavfile.write(sys.argv[2], SR, (st * 32767).astype(np.int16))
print(f"música: {DUR:.2f} s · {sys.argv[2]}")
