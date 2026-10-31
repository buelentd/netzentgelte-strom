"""Preisblatt-Kandidaten über eine Such-Schnittstelle (Google Programmable Search, Custom Search JSON API).

Für jeden noch nicht fertigen Netzbetreiber eine Abfrage
    "<Kernname>" Netzentgelte Strom 2026 Preisblatt filetype:pdf
Die Treffer (nur Dokument-Links) landen in lauf/suche_treffer.csv und werden im nächsten Lauf wie
Hinweis-URLs geprüft: robots.txt, Drosselung, Jahres-, Sparten-, Namens- und Plausibilitätsprüfung
gelten unverändert. Bereits gesuchte Netzbetreiber werden übersprungen (auch ohne Treffer vermerkt).
Google selbst wird nicht abgerufen, nur die offizielle Schnittstelle mit eigenem Schlüssel.
"""
from __future__ import annotations

import csv
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

from .crawl import ist_dokument

API = "https://www.googleapis.com/customsearch/v1"
SPALTEN = ["website", "url", "herkunft", "nr", "netzbetreiber"]
RECHTSFORM = re.compile(r"\b(gmbh|mbh|ag|kg|eg|e\.\s*g\.|co\.?|ohg|o\.h\.g|kgaa|aör|adör|ku|se|"
                        r"anstalt des öffentlichen rechts.*|eigenbetr\..*|eigenbetrieb.*)\b\.?", re.I)
FREMD = re.compile(r"(?<![a-z])gas(?!se|t)|erdgas|wasser|waerme|wärme|grundversorgung|ersatzversorgung", re.I)


def kernname(name: str) -> str:
    """"Stadtwerke Elmshorn" aus "Stadtwerke Elmshorn GmbH ＆ Co. KG"."""
    n = name.replace("＆", "&").replace("&", " ")
    n = RECHTSFORM.sub(" ", n)
    n = re.sub(r"[\[(].*?[\])]", " ", n)
    return re.sub(r"\s+", " ", n).strip(" ,-")


def abfrage(name: str, jahr: int) -> str:
    return f'"{kernname(name)}" Netzentgelte Strom {jahr} Preisblatt filetype:pdf'


def _abrufen(schluessel: str, kennung: str, q: str) -> dict:
    url = API + "?" + urllib.parse.urlencode({"key": schluessel, "cx": kennung, "q": q, "num": 10, "lr": "lang_de"})
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def gesucht(pfad: Path) -> set[str]:
    if not pfad.exists():
        return set()
    return {z["nr"] for z in csv.DictReader(pfad.read_text(encoding="utf-8").splitlines(), delimiter=";")}


def suchen(zeilen: list[dict], schluessel: str, kennung: str, ziel: Path, jahr: int = 2026,
           max_abfragen: int = 1000, abrufen=_abrufen, log=print) -> int:
    """zeilen: Netzbetreiber (nr, netzbetreiber, website, status). Rückgabe: Anzahl Abfragen."""
    schon = gesucht(ziel)
    neu = not ziel.exists()
    n = 0
    with open(ziel, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        if neu:
            w.writerow(SPALTEN)
        for z in zeilen:
            if str(z["nr"]) in schon or not z.get("website"):
                continue
            if n >= max_abfragen:
                log(f"Suche: Höchstzahl von {max_abfragen} Abfragen erreicht, Rest im nächsten Lauf")
                break
            q = abfrage(z["netzbetreiber"], jahr)
            try:
                antwort = abrufen(schluessel, kennung, q)
            except Exception as e:
                log(f"Suche abgebrochen bei [{z['nr']}] {z['netzbetreiber']}: {type(e).__name__}: {str(e)[:120]}")
                break               # z. B. Kontingent erschöpft: nichts vermerken, nächster Lauf macht weiter
            n += 1
            links = [i.get("link", "") for i in antwort.get("items", [])]
            treffer = [u for u in links if ist_dokument(u) and not FREMD.search(urllib.parse.unquote(u))][:5]
            for u in treffer:
                w.writerow([z["website"], u, f"Suchmaschine: {q}", z["nr"], z["netzbetreiber"]])
            if not treffer:
                w.writerow([z["website"], "", f"Suchmaschine ohne Treffer: {q}", z["nr"], z["netzbetreiber"]])
            f.flush()
            log(f"Suche [{z['nr']}] {z['netzbetreiber']}: {len(treffer)} Dokument(e)")
            time.sleep(0.2)
    return n
