#!/usr/bin/env python3
"""Une el contenido de los cuatro grupos con la portada, la presentación y el cierre, y prepara las imágenes.

Uso: python3 montar.py <carpeta-salida>
Crea <salida>/capturas/*.jpg, <salida>/marca/*.svg y <salida>/contenido.json (para build.py).
"""
import json, pathlib, re, shutil, sys
from PIL import Image

W = pathlib.Path(__file__).resolve().parent.parent
OUT = pathlib.Path(sys.argv[1]).resolve()
(OUT / "capturas").mkdir(parents=True, exist_ok=True)
(OUT / "marca").mkdir(parents=True, exist_ok=True)

for f in (W / "brand/out").glob("*.svg"):
    shutil.copy(f, OUT / "marca" / f.name)

grupos = {k: json.loads((W / f"contenido/{k}.json").read_text(encoding="utf-8")) for k in ("principal", "trabajo", "contabilidad", "despacho") if (W / f"contenido/{k}.json").exists()}
extra = json.loads((W / "doc/extra.json").read_text(encoding="utf-8")) if (W / "doc/extra.json").exists() else {}

usadas = {}


def jpg(src):
    """Convierte una captura PNG a JPEG para la guía y devuelve la ruta publicada."""
    origen = W / src
    nombre = re.sub(r"[^a-z0-9-]", "-", src.split("/", 1)[1].rsplit(".", 1)[0].replace("/", "-").lower()) + ".jpg"
    destino = OUT / "capturas" / nombre
    if src not in usadas:
        im = Image.open(origen).convert("RGB")
        im.save(destino, "JPEG", quality=84, optimize=True, progressive=True)
        usadas[src] = "capturas/" + nombre
    return usadas[src]


def limpiar_url(u):
    u = (u or "").replace("http://127.0.0.1:8091", "")
    if u and not u.startswith("/"):
        u = "/" + u
    return u


def preparar(mod):
    for s in mod.get("shots", []):
        s["src"] = jpg(s["src"])
        s["url"] = limpiar_url(s.get("url"))
    return mod


# Bóveda: capturas hechas aparte
boveda_shots = extra.get("boveda_shots", [])

groups = []
for clave, nombre in (("principal", "Inicio y clientes"), ("trabajo", "Trabajo diario"), ("contabilidad", "Contabilidad"), ("despacho", "Despacho")):
    if clave not in grupos:
        continue
    g = grupos[clave]
    mods = [preparar(m) for m in g["modules"]]
    for m in mods:
        if m["id"] == "boveda" and boveda_shots:
            m["shots"] = [preparar({"shots": [dict(s)]})["shots"][0] for s in boveda_shots]
    groups.append({"name": nombre, "desc": g.get("group_desc", ""), "modules": mods})

portal = grupos["despacho"].get("portal_modules", [])
for pm in portal:
    pm["shots"] = pm.get("shots", []) + [dict(x) for x in extra.get("portal_extra_shots", {}).get(pm["id"], [])]
if portal:
    groups.append({"name": "Portal del cliente", "desc": "Lo que ven y hacen tus clientes desde su móvil o su ordenador, con el logo y el color de tu despacho.",
                   "modules": [preparar(m) for m in portal]})

# Lo que genera: se juntan y se quitan repetidos
salidas = []
vistos = set()
for clave in ("principal", "trabajo", "contabilidad", "despacho"):
    for o in grupos.get(clave, {}).get("generated_outputs", []):
        k = o["name"].strip().lower()
        if o["name"] in extra.get("outputs_skip", []):
            continue
        if o["name"] in extra.get("outputs_where", {}):
            o = dict(o, where=extra["outputs_where"][o["name"]])
        if k in vistos:
            continue
        vistos.add(k)
        salidas.append(o)

hero = jpg(extra["hero"]) if extra.get("hero") else None
content = extra["base"]
content["meta"]["hero"] = hero
content["groups"] = groups
content["outputs"] = salidas
(OUT / "contenido.json").write_text(json.dumps(content, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(usadas), "capturas;", sum(len(g["modules"]) for g in groups), "secciones;", len(salidas), "salidas")
