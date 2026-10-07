#!/usr/bin/env python3
"""Versión en tema claro de la animación del vídeo (misma línea de tiempo, efectos en tonos claros).

Uso: python3 tema-claro.py <video.html> <video-claro.html>
Cambia las pantallas a pantallas-claro/, añade al final del CSS los colores claros y aclara el fondo
animado (degradado crema, partículas, estelas y salto de luz).
"""
import re, sys

src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf-8").read()

# Pantallas del programa en tema claro
s = s.replace('src="pantallas/', 'src="pantallas-claro/').replace('="pantallas/', '="pantallas-claro/')

# En la captura clara la tarjeta del conciliador es algo más alta: el recuadro del zoom la abarca entera
assert 'data-zoom="0.631,0.634,0.981,0.80"' in s
s = s.replace('data-zoom="0.631,0.634,0.981,0.80"', 'data-zoom="0.631,0.636,0.981,0.843"')

# El destello mantiene la posición de cada versión (horizontal o vertical)
pos = re.search(r"#destello \{[^}]*circle at (50% \d+%)", s).group(1)

CSS = """
/* ================= tema claro ================= */
:root { --ink: #FBF6EE; --tx: #0B0F14; --mut: #5B6573; --tqd: #0891B2; }
html, body { background: #FBF6EE; }
#stage { background: #FBF6EE; color: var(--tx); }
.papel { background: linear-gradient(160deg, #FFFFFF, #F5EFE6); border: 1px solid rgba(11,15,20,.08); box-shadow: 0 26px 44px -18px rgba(110,70,30,.35); }
.papel i { background: rgba(11,15,20,.10); }
.papel i:nth-child(1) { background: rgba(248,132,26,.8); }
.papel b { color: var(--tqd); }
.kw { color: var(--tx); text-shadow: 0 16px 44px rgba(110,70,30,.20); }
.kw.or { color: var(--or); text-shadow: 0 0 50px rgba(248,132,26,.40), 0 14px 30px rgba(248,132,26,.25); }
.logo-icon { filter: drop-shadow(0 30px 40px rgba(110,60,15,.30)) drop-shadow(0 0 50px rgba(248,132,26,.50)) drop-shadow(0 0 30px rgba(34,211,238,.35)); }
.tagline { color: var(--tx); }
.pills span { border-color: rgba(6,182,212,.65); color: #0E7490; background: rgba(34,211,238,.12); }
.contacto { color: var(--mut); }
.contacto b { color: var(--tx); }
.pantalla { background: #FFFFFF; border: 1px solid rgba(11,15,20,.10); box-shadow: 0 60px 120px -40px rgba(110,70,30,.45), 0 0 0 1px rgba(248,132,26,.16), 0 0 90px -10px rgba(34,211,238,.38); }
.barra { background: #F5F1EB; border-bottom: 1px solid rgba(11,15,20,.07); }
.barra i { background: #DCD5CB; }
.barra span { background: #FFFFFF; border: 1px solid rgba(11,15,20,.08); color: #7A828E; }
.foco { border-color: #06B6D4; box-shadow: 0 0 40px rgba(34,211,238,.65), inset 0 0 30px rgba(34,211,238,.18); }
.escaner { background: linear-gradient(180deg, rgba(34,211,238,0), rgba(34,211,238,.16) 70%, rgba(6,182,212,.75) 97%, rgba(8,145,178,.95)); mix-blend-mode: multiply; }
.rotulo .ceja { color: var(--tqd); }
.rotulo .linea.or span { color: var(--or); text-shadow: 0 0 36px rgba(248,132,26,.32); }
.marco::before, .marco::after { border-color: #06B6D4; filter: drop-shadow(0 0 8px rgba(34,211,238,.6)); }
.chip { border-color: rgba(248,132,26,.7); color: #C25A06; background: rgba(248,132,26,.10); }
.chip.tq { border-color: rgba(6,182,212,.65); color: #0E7490; background: rgba(34,211,238,.10); }
.check em { background: rgba(34,211,238,.14); border-color: #06B6D4; color: var(--tqd); }
.movil { background: #FFFFFF; border: 2px solid #E4DED4; box-shadow: 0 50px 100px -30px rgba(110,70,30,.45), 0 0 60px -10px rgba(34,211,238,.40); }
#sub { color: var(--tx); background: rgba(255,255,255,.88); text-shadow: none; border: 1px solid rgba(11,15,20,.06); box-shadow: 0 14px 40px -16px rgba(110,70,30,.35); }
#barrido { background: linear-gradient(90deg, rgba(34,211,238,0), rgba(34,211,238,.38) 40%, rgba(255,255,255,.95) 50%, rgba(248,132,26,.42) 60%, rgba(248,132,26,0)); mix-blend-mode: normal; }
#viñeta { background: radial-gradient(ellipse at 50% 45%, rgba(241,230,214,0) 60%, rgba(214,188,155,.38) 100%); }
#destello { background: radial-gradient(circle at POS, rgba(255,255,255,.98), rgba(255,214,170,.65) 25%, rgba(248,132,26,.18) 45%, rgba(255,255,255,0) 65%); mix-blend-mode: normal; }
""".replace("POS", pos)
s = s.replace("</style>", CSS + "</style>", 1)

# Fondo animado: solo dentro del script
cab, js = s.split("<script>", 1)
cambios = [
    ("gr.addColorStop(0, '#16202B'); gr.addColorStop(0.45, '#0C1117'); gr.addColorStop(1, '#05070A');",
     "gr.addColorStop(0, '#FFFFFF'); gr.addColorStop(0.45, '#FCF8F2'); gr.addColorStop(1, '#F1E5D3');"),
    ("34,211,238", "6,182,212"),          # turquesa algo más profundo para que se vea sobre crema
    ("'255,255,255'", "'255,170,80'"),    # las partículas blancas pasan a naranja claro
    ("'rgba(0,0,0,0)'", "'rgba(255,255,255,0)'"),
    ("rgba(0,0,0,.8)`", "rgba(150,70,10,.35)`"),  # sombra del botón final
]
for a, b in cambios:
    assert a in js, a
    js = js.replace(a, b)
open(dst, "w", encoding="utf-8").write(cab + "<script>" + js)
print("tema claro:", dst)
