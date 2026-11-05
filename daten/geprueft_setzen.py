"""Setzt in lauf/preise_manuell.csv geprueft=ja für Netzbetreiber, deren RLM-Blöcke und SLP am Dokumenttext bestätigt sind (daten/preise_bestaetigung.py).
Aufruf: PYTHONPATH=. python daten/preise_bestaetigung.py && PYTHONPATH=. python daten/geprueft_setzen.py"""
import csv, io
nrs = set(open("ergebnis/preise_dokument_bestaetigt.txt").read().split())
p = "lauf/preise_manuell.csv"
raw = open(p, encoding="utf-8", newline="").read()
bom = raw.startswith("﻿"); nl = "\r\n" if "\r\n" in raw else "\n"
rows = list(csv.reader(io.StringIO(raw.lstrip("﻿")), delimiter=";"))
I = {h: i for i, h in enumerate(rows[0])}
n = 0
for r in rows[1:]:
    if r[I["nr"]] in nrs and not r[I["geprueft"]]:
        r[I["geprueft"]] = "ja"; n += 1
        note = "am Dokumenttext automatisch bestätigt (05.11.2026)"
        if note not in r[I["hinweis"]]:
            r[I["hinweis"]] = (r[I["hinweis"]] + "; " if r[I["hinweis"]] else "") + note
out = io.StringIO(); csv.writer(out, delimiter=";", lineterminator=nl).writerows(rows)
open(p, "w", encoding="utf-8", newline="").write(("﻿" if bom else "") + out.getvalue())
print(n, "Zeilen auf geprueft=ja gesetzt")
