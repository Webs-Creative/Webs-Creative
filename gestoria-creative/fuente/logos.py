#!/usr/bin/env python3
"""Genera los logos de Gestoría Creative en SVG con el texto convertido a trazos (Montserrat Black)."""
import io, pathlib, re
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

HERE = pathlib.Path(__file__).parent
FONT = HERE.parent / "tools/node_modules/@fontsource/montserrat/files/montserrat-latin-900-normal.woff2"
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)

tt = TTFont(str(FONT))
buf = io.BytesIO(); tt.flavor = None; tt.save(buf); data = buf.getvalue()
face = hb.Face(data); font = hb.Font(face)
upm = face.upem
gs = tt.getGlyphSet()
order = tt.getGlyphOrder()
ASC = tt["OS/2"].sCapHeight or 700


def text_path(text, size, x0, baseline, tracking=0.0):
    """Devuelve (d, ancho) del texto como trazo SVG."""
    b = hb.Buffer(); b.add_str(text); b.guess_segment_properties()
    hb.shape(font, b, {"kern": True, "liga": False})
    scale = size / upm
    x = 0.0
    parts = []
    for info, pos in zip(b.glyph_infos, b.glyph_positions):
        name = order[info.codepoint]
        pen = SVGPathPen(gs)
        # y hacia abajo en SVG: se invierte el eje
        tp = TransformPen(pen, (scale, 0, 0, -scale, x0 + (x + pos.x_offset) * scale, baseline - pos.y_offset * scale))
        gs[name].draw(tp)
        d = pen.getCommands()
        if d:
            parts.append(d)
        x += pos.x_advance + tracking * upm
    width = (x - tracking * upm) * scale
    return " ".join(parts), width


ICON = (HERE / "gc-icon.svg").read_text()
icon_defs = re.search(r"<defs>(.*?)</defs>", ICON, re.S).group(1)
icon_body = ICON.split("</defs>")[1].split("</svg>")[0]


def icon_group(x, y, s):
    return f'<g transform="translate({x} {y}) scale({s / 100})">{icon_body}</g>'


def lockup(fg, name, bg=None):
    s = 120                      # tamaño del icono
    gap = 30
    size = 62                    # cuerpo de letra
    cap = ASC / upm * size
    acento = (tt["glyf"]["Iacute"].yMax if "Iacute" in tt["glyf"].keys() else ASC) / upm * size
    line = cap + 14
    alto_texto = acento + line   # del acento de la Í a la línea base de CREATIVE
    H = max(s, alto_texto + 4)
    top = (H - alto_texto) / 2 + acento
    d1, w1 = text_path("GESTORÍA", size, s + gap, top, 0.01)
    d2, w2 = text_path("CREATIVE", size, s + gap, top + line, 0.01)
    W = s + gap + max(w1, w2) + 4
    rect = f'<rect width="{W}" height="{H}" fill="{bg}"/>' if bg else ""
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.1f} {H:.1f}" width="{W:.0f}" height="{H:.0f}" role="img" aria-label="Gestoría Creative">'
           f'<defs>{icon_defs}</defs>{rect}{icon_group(0, (H - s) / 2, s)}'
           f'<path d="{d1}" fill="{fg}"/><path d="{d2}" fill="#F8841A"/></svg>')
    (OUT / name).write_text(svg)
    return W, H


def stacked(fg, name):
    """Icono arriba y nombre debajo, centrado (para portadas y redes)."""
    s = 220; size = 70
    cap = ASC / upm * size
    d1, w1 = text_path("GESTORÍA", size, 0, 0, 0.01)
    d2, w2 = text_path("CREATIVE", size, 0, 0, 0.01)
    W = max(w1, w2, s) + 20
    acento = (tt['glyf']['Iacute'].yMax if 'Iacute' in tt['glyf'].keys() else ASC) / upm * size
    y1 = s + 40 + acento; y2 = y1 + cap + 16
    d1, _ = text_path("GESTORÍA", size, (W - w1) / 2, y1, 0.01)
    d2, _ = text_path("CREATIVE", size, (W - w2) / 2, y2, 0.01)
    H = y2 + 4
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.1f} {H:.1f}" width="{W:.0f}" height="{H:.0f}" role="img" aria-label="Gestoría Creative">'
           f'<defs>{icon_defs}</defs>{icon_group((W - s) / 2, 0, s)}'
           f'<path d="{d1}" fill="{fg}"/><path d="{d2}" fill="#F8841A"/></svg>')
    (OUT / name).write_text(svg)


(OUT / "gestoria-creative-icono.svg").write_text(ICON)
print(lockup("#FFFFFF", "gestoria-creative-logo-fondo-oscuro.svg"))
print(lockup("#12161C", "gestoria-creative-logo-fondo-claro.svg"))
stacked("#FFFFFF", "gestoria-creative-logo-vertical-fondo-oscuro.svg")
stacked("#12161C", "gestoria-creative-logo-vertical-fondo-claro.svg")
print("ok")
