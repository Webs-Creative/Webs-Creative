#!/usr/bin/env python3
"""Genera la guía de Gestoría Creative (HTML) a partir de contenido.json.

Uso: python3 build.py <carpeta> [--print <dir-fuentes>]
  Lee <carpeta>/contenido.json y escribe <carpeta>/index.html (o guia-impresion.html con --print,
  que usa las fuentes locales en vez de Google Fonts y añade el esqueleto completo para Chromium).
"""
import html, json, pathlib, re, sys

carpeta = pathlib.Path(sys.argv[1])
PRINT = "--print" in sys.argv
font_dir = sys.argv[sys.argv.index("--print") + 1] if PRINT else ""
here = pathlib.Path(__file__).parent
data = json.loads((carpeta / "contenido.json").read_text(encoding="utf-8"))
css = (here / "styles.css").read_text(encoding="utf-8")
e = lambda s: html.escape(str(s), quote=True)
LAZY = 'loading="eager"' if PRINT else 'loading="lazy" decoding="async"'


def rich(s):
    """Escapa y admite `código` y **negrita**."""
    s = e(s)
    parts = s.split("`")
    s = "".join(f"<code>{p}</code>" if i % 2 else p for i, p in enumerate(parts))
    parts = s.split("**")
    return "".join(f"<strong>{p}</strong>" if i % 2 else p for i, p in enumerate(parts))


m = data["meta"]
icon = m["icon"]
url_base = m.get("url_base", "")


def lockup():
    return (f'<span class="lockup"><img src="{e(icon)}" alt="" width="62" height="62">'
            f'<span class="wordmark">Gestoría<b>Creative</b></span></span>')


def shot(s):
    cap = f"<figcaption>{rich(s['caption'])}</figcaption>" if s.get("caption") else ""
    alt = e(s.get("alt") or s.get("caption", ""))
    if s.get("mobile"):
        return (f'<figure class="shot shot--phone"><div class="phone"><img src="{e(s["src"])}" alt="{alt}" {LAZY}></div>{cap}</figure>')
    url = s.get("url", "")
    return (f'<figure class="shot"><div class="shot-bar" aria-hidden="true"><span class="shot-dots"><i></i><i></i><i></i></span>'
            f'<span class="shot-url">{e(url_base + url)}</span></div>'
            f'<img src="{e(s["src"])}" alt="{alt}" {LAZY}>{cap}</figure>')


def shots_html(shots):
    phones = [s for s in shots if s.get("mobile")]
    desks = [s for s in shots if not s.get("mobile")]
    out = ""
    if phones:
        lead = desks[:1]
        rest = desks[1:]
        out += '<div class="shots-mix">' + "".join(shot(s) for s in phones) + "".join(shot(s) for s in lead) + "</div>"
    else:
        lead = desks[:1]
        rest = desks[1:]
        out += "".join(shot(s) for s in lead)
    if rest:
        out += '<div class="shots-2">' + "".join(shot(s) for s in rest) + "</div>"
    return out


def li(items):
    return "".join(f"<li>{rich(i)}</li>" for i in items)


def trio(cols):
    return '<div class="trio">' + "".join(f'<div class="{c}"><h3>{e(t)}</h3><ul>{li(v)}</ul></div>' for c, t, v in cols if v) + "</div>"


def band(b):
    body = "".join(f"<p>{rich(p)}</p>" for p in b.get("paragraphs", []))
    prose = f'<div class="prose band-prose">{body}</div>' if body else ""
    return (f'<section class="band" id="{e(b["id"])}"><div class="wrap">'
            f'<p class="eyebrow">{e(b["eyebrow"])}</p><h2 class="h-sec">{e(b["title"])}</h2>'
            f'{prose}{trio(b["trio"]) if b.get("trio") else ""}{b.get("html", "")}</div></section>')


VISOR = """<dialog class="visor" id="visor" aria-label="Captura ampliada"><button type="button" class="visor-cerrar" aria-label="Cerrar">Cerrar ✕</button><img alt=""><p></p></dialog>
<script>
(() => {
  const d = document.getElementById('visor');
  if (!d || !d.showModal) return;
  const img = d.querySelector('img'), txt = d.querySelector('p');
  document.querySelectorAll('.shot img').forEach((i) => {
    i.tabIndex = 0; i.setAttribute('role', 'button'); i.title = 'Ampliar la captura';
    const abrir = () => { img.src = i.src; img.alt = i.alt; const c = i.closest('figure').querySelector('figcaption'); txt.textContent = c ? c.textContent : ''; d.showModal(); };
    i.addEventListener('click', abrir);
    i.addEventListener('keydown', (ev) => { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); abrir(); } });
  });
  d.addEventListener('click', (ev) => { if (ev.target === d || ev.target.closest('.visor-cerrar')) d.close(); });
})();
</script>"""

# ---------------------------------------------------------------- cabecera
H = []
if PRINT:
    faces = [("Montserrat", w, f"montserrat/files/montserrat-latin-{w}-normal.woff2") for w in (700, 800, 900)]
    faces += [("Figtree", w, f"figtree/files/figtree-latin-{w}-normal.woff2") for w in (400, 500, 600, 700)]
    faces += [("JetBrains Mono", w, f"jetbrains-mono/files/jetbrains-mono-latin-{w}-normal.woff2") for w in (500, 600, 700)]
    fonts = "<style>" + "".join(
        f'@font-face{{font-family:"{f}";font-weight:{w};src:url("{font_dir}/{p}") format("woff2")}}' for f, w, p in faces) + "</style>"
    H.append('<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">')
else:
    fonts = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
             '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700'
             '&family=JetBrains+Mono:wght@500;600;700&family=Montserrat:wght@700;800;900&display=swap">')
H.append(f"<title>{e(m['title'])}</title>")
H.append(f'<meta name="description" content="{e(m["description"])}">')
H.append(f'<link rel="icon" href="{e(icon)}" type="image/svg+xml">')
H.append(fonts)
H.append(f"<style>{css}</style>")
if PRINT:
    H.append("</head><body>")

# ---------------------------------------------------------------- portada
hero = f'<img class="cover-hero" src="{e(m["hero"])}" alt="{e(m.get("hero_alt", ""))}">' if m.get("hero") else ""
H.append(f'''<header class="cover"><div class="wrap">
  {lockup()}
  <div class="cover-text">
    <p class="cover-kicker">{e(m["kicker"])}</p>
    <h1>{m["headline_html"]}</h1>
    <p class="cover-lead">{rich(m["lead"])}</p>
  </div>
  {hero}
  <div class="cover-meta">{"".join(f"<span>{e(k)} <strong>{e(v)}</strong></span>" for k, v in m["cover_meta"])}</div>
</div></header>''')
H.append("<main>")

# ---------------------------------------------------------------- presentación
it = data["intro"]
facts = "".join(f'<div class="fact"><b>{e(f[0])}</b><span>{e(f[1])}</span></div>' for f in it.get("facts", []))
paras = "".join(f"<p>{rich(p)}</p>" for p in it["paragraphs"])
H.append(f'''<section class="band" id="que-es"><div class="wrap">
  <p class="eyebrow">{e(it["eyebrow"])}</p>
  <h2 class="h-sec">{e(it["title"])}</h2>
  <div class="prose band-prose">{paras}</div>
  {f'<div class="facts">{facts}</div>' if facts else ""}
</div></section>''')
for b in data.get("bands_before", []):
    H.append(band(b))

# ---------------------------------------------------------------- índice
n = 0
toc = []
for g in data["groups"]:
    for mod in g["modules"]:
        n += 1
        mod["_n"] = f"{n:02d}"
        toc.append(f'<li><a href="#{e(mod["id"])}"><span class="toc-n">{mod["_n"]}</span><span class="toc-t">{e(mod["title"])}</span><span class="toc-g">{e(g["name"])}</span></a></li>')
extra_toc = [("genera", "Todo lo que genera"), ("seguridad", "Seguridad y protección de datos"), ("instalacion", "Instalación y requisitos")]
for i, (anchor, t) in enumerate(extra_toc):
    toc.append(f'<li><a href="#{anchor}"><span class="toc-n">{chr(65 + i)}</span><span class="toc-t">{e(t)}</span><span class="toc-g">Anexo</span></a></li>')
H.append(f'''<section class="band" id="indice"><div class="wrap">
  <p class="eyebrow">Índice</p><h2 class="h-sec">{e(data.get("toc_title", "Las secciones del programa"))}</h2>
  <p class="lead">{rich(data.get("toc_lead", ""))}</p>
  <ol class="toc">{"".join(toc)}</ol>
</div></section>''')

# ---------------------------------------------------------------- secciones
for g in data["groups"]:
    lista = "".join(f'<li><a href="#{e(x["id"])}"><span>{x["_n"]}</span>{e(x["title"])}</a></li>' for x in g["modules"])
    H.append(f'<div class="group-wrap"><div class="wrap group-head"><p class="eyebrow">Grupo del menú</p><h2>{e(g["name"])}</h2>'
             f'<p>{rich(g.get("desc", ""))}</p><ol class="group-list">{lista}</ol></div></div>')
    for mod in g["modules"]:
        cols = [("t-hace", "Qué hace", mod.get("hace")), ("t-ves", "Qué ves", mod.get("ves")), ("t-gen", "Qué genera", mod.get("genera"))]
        tip = f'<p class="tip"><strong>Consejo</strong><span>{rich(mod["tip"])}</span></p>' if mod.get("tip") else ""
        menu = mod.get("menu") or mod["title"]
        ruta = menu if ("›" in menu or menu.lower().startswith(g["name"].lower())) else f"{g['name']} › {menu}"
        ruta = " <span>›</span> ".join(e(x.strip()) for x in ruta.split("›"))
        H.append(f'''<section class="mod wrap" id="{e(mod["id"])}">
  <div class="mod-head"><span class="mod-num">{mod["_n"]}</span><div>
    <p class="mod-path">{ruta}</p>
    <h2 class="mod-title">{e(mod["title"])}</h2>
    <p class="mod-lead">{rich(mod["lead"])}</p></div></div>
  {shots_html(mod.get("shots", []))}{trio(cols)}{tip}
</section>''')

# ---------------------------------------------------------------- todo lo que genera
FICHERO = re.compile(r"pdf|txt|zip|csv|xlsx|xml|impresi|ics", re.I)
AVISO = re.compile(r"aviso|correo|mensaje", re.I)
ficheros, avisos, registros = [], [], []
for o in data.get("outputs", []):
    f = o.get("format", "")
    if f.lower().startswith("registro") or "pantalla" in f.lower():
        registros.append(o)
    else:
        (ficheros if FICHERO.search(f) else avisos if AVISO.search(f) else registros).append(o)


def tabla(filas):
    rows = "".join(
        f'<tr><td><strong>{rich(o["name"])}</strong><span class="td-desc">{rich(o["desc"])}</span></td>'
        f'<td><span class="fmt">{e(o["format"])}</span></td><td>{rich(o["where"])}</td></tr>' for o in filas)
    return ('<div class="tbl-wrap"><table><thead><tr><th>Qué sale</th><th>Formato</th><th>Dónde se genera</th></tr></thead>'
            f"<tbody>{rows}</tbody></table></div>")


H.append(f'''<section class="band" id="genera"><div class="wrap">
  <p class="eyebrow">Anexo A</p><h2 class="h-sec">Todo lo que genera el programa</h2>
  <p class="lead">Reunido en un solo sitio: los ficheros y documentos que puedes descargar o enviar, los avisos y correos que salen solos, y los registros que quedan guardados.</p>
  <h3 class="h-sub">Ficheros y documentos <small>{len(ficheros)}</small></h3>{tabla(ficheros)}
  <h3 class="h-sub">Avisos, correos y mensajes <small>{len(avisos)}</small></h3>{tabla(avisos)}
  <h3 class="h-sub">Registros, datos y comprobaciones <small>{len(registros)}</small></h3>{tabla(registros)}
</div></section>''')

for i, b in enumerate(data.get("bands_after", [])):
    b = dict(b, eyebrow=f"Anexo {chr(66 + i)} · {b['eyebrow']}")
    H.append(band(b))
H.append("</main>")

# ---------------------------------------------------------------- cierre
c = data["closing"]
contacts = "".join(f"<div><span>{e(k)}</span><b>{e(v)}</b></div>" for k, v in c["contacts"])
H.append(f'''<footer class="closing"><div class="wrap">
  {lockup()}
  <h2>{c["headline_html"]}</h2>
  <p class="cover-lead">{rich(c["lead"])}</p>
  <div class="contact">{contacts}</div>
  <p class="legal">{rich(c["legal"])}</p>
</div></footer>''')
if not PRINT:
    H.append(VISOR)
if PRINT:
    H.append("</body></html>")

out = carpeta / ("guia-impresion.html" if PRINT else "index.html")
out.write_text("\n".join(H), encoding="utf-8")
print("escrito", out, f"{out.stat().st_size // 1024} KB;", n, "secciones;", len(ficheros), len(avisos), len(registros), "salidas")
