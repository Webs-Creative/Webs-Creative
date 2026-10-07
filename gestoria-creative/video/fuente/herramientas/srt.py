#!/usr/bin/env python3
"""Subtítulos .srt a partir de escenas.json (mismo texto y tiempos que los rótulos del vídeo).
Uso: python3 srt.py <escenas.json> <salida.srt>"""
import json, sys

d = json.load(open(sys.argv[1], encoding="utf-8"))


def hms(x):
    ms = int(round(x * 1000))
    h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


t, out = 0.0, []
for i, e in enumerate(d["escenas"], 1):
    ini = t + e.get("voz_desfase", 0.25)
    fin = t + e["dur"] - 0.1
    out.append(f"{i}\n{hms(ini)} --> {hms(fin)}\n{e['texto']}\n")
    t += e["dur"]
open(sys.argv[2], "w", encoding="utf-8").write("\n".join(out))
print("subtítulos:", sys.argv[2])
