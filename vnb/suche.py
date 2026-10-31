"""Preisblatt-Kandidaten über eine Such-Schnittstelle (Brave Search, Web-Suche).

Für jeden noch nicht fertigen Netzbetreiber eine Abfrage
    "<Kernname>" Netzentgelte Strom 2026 Preisblatt filetype:pdf
Die Treffer (nur Dokument-Links) landen vorübergehend in lauf/suche_treffer.csv und werden im selben
Lauf wie Hinweis-URLs geprüft: robots.txt, Drosselung, Jahres-, Sparten-, Namens- und
Plausibilitätsprüfung gelten unverändert. Die Trefferdatei wird nicht ins Repository übernommen
(Nutzungsbedingungen: Suchergebnisse nicht dauerhaft speichern). Dauerhaft vermerkt wird nur, welcher
Netzbetreiber schon gesucht wurde (lauf/suche_erledigt.csv: nr;netzbetreiber;anzahl_treffer), damit
kein Netzbetreiber doppelt abgefragt wird.
"""
from __future__ import annotations

import csv
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

from .crawl import ist_dokument, website_domain

API = "https://api.search.brave.com/res/v1/web/search"
SPALTEN = ["website", "url", "herkunft", "nr", "netzbetreiber"]
ERLEDIGT = ["nr", "netzbetreiber", "anzahl_treffer"]
RECHTSFORM = re.compile(r"\b(gmbh|mbh|ag|kg|eg|e\.\s*g\.|co\.?|ohg|o\.h\.g|kgaa|aör|adör|ku|se|"
                        r"anstalt des öffentlichen rechts.*|eigenbetr\..*|eigenbetrieb.*)\b\.?", re.I)
FREMD = re.compile(r"(?<![a-z])gas(?!se|t)|erdgas|wasser|waerme|wärme|grundversorgung|ersatzversorgung", re.I)


def kernname(name: str) -> str:
    """"Stadtwerke Elmshorn" aus "Stadtwerke Elmshorn GmbH ＆ Co. KG"."""
    n = name.replace("＆", "&").replace("&", " ")
    n = RECHTSFORM.sub(" ", n)
    n = re.sub(r"[\[(].*?[\])]", " ", n)
    return re.sub(r"\s+", " ", n).strip(" ,-")


def eigener_treffer(url: str, website: str, name: str) -> bool:
    """Treffer von der eigenen Website des Netzbetreibers oder mit seinem Namen im Link (keine fremden Preisblätter)."""
    if website_domain(url) == website_domain(website):
        return True
    link = re.sub(r"[^a-z0-9äöü]", "", urllib.parse.unquote(url).lower())
    worte = [re.sub(r"[^a-z0-9äöü]", "", w.lower()) for w in kernname(name).split()]
    worte = [w for w in worte if len(w) >= 5 and w not in ("stadtwerke", "stadtwerk", "energie", "netze", "netzgesellschaft",
                                                          "versorgung", "energieversorgung", "elektrizitätswerk", "gemeindewerke")]
    return bool(worte) and all(w in link for w in worte)


def abfrage(name: str, jahr: int) -> str:
    return f'"{kernname(name)}" Netzentgelte Strom {jahr} Preisblatt filetype:pdf'


def _abrufen(schluessel: str, q: str) -> dict:
    url = API + "?" + urllib.parse.urlencode({"q": q, "count": 20, "country": "DE", "search_lang": "de"})
    anfrage = urllib.request.Request(url, headers={"Accept": "application/json", "X-Subscription-Token": schluessel})
    with urllib.request.urlopen(anfrage, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def links(antwort: dict) -> list[str]:
    return [i.get("url", "") for i in (antwort.get("web") or {}).get("results", [])]


def gesucht(pfad: Path) -> set[str]:
    if not pfad.exists():
        return set()
    return {z["nr"] for z in csv.DictReader(pfad.read_text(encoding="utf-8").splitlines(), delimiter=";")}


def suchen(zeilen: list[dict], schluessel: str, ziel: Path, erledigt: Path, jahr: int = 2026,
           max_abfragen: int = 1000, abrufen=_abrufen, log=print, pause: float = 1.1) -> int:
    """zeilen: Netzbetreiber (nr, netzbetreiber, website, status). Rückgabe: Anzahl Abfragen."""
    schon = gesucht(erledigt)
    neu, neu_e = not ziel.exists(), not erledigt.exists()
    n = 0
    with open(ziel, "a", newline="", encoding="utf-8") as f, open(erledigt, "a", newline="", encoding="utf-8") as fe:
        w, we = csv.writer(f, delimiter=";"), csv.writer(fe, delimiter=";")
        if neu:
            w.writerow(SPALTEN)
        if neu_e:
            we.writerow(ERLEDIGT)
        for z in zeilen:
            if str(z["nr"]) in schon or not z.get("website"):
                continue
            if n >= max_abfragen:
                log(f"Suche: Höchstzahl von {max_abfragen} Abfragen erreicht, Rest im nächsten Lauf")
                break
            q = abfrage(z["netzbetreiber"], jahr)
            try:
                antwort = abrufen(schluessel, q)
            except Exception as e:
                log(f"Suche abgebrochen bei [{z['nr']}] {z['netzbetreiber']}: {type(e).__name__}: {str(e)[:120]}")
                break               # z. B. Kontingent erschöpft: nichts vermerken, nächster Lauf macht weiter
            n += 1
            treffer = [u for u in links(antwort) if ist_dokument(u) and not FREMD.search(urllib.parse.unquote(u))
                       and eigener_treffer(u, z["website"], z["netzbetreiber"])][:5]
            for u in treffer:
                w.writerow([z["website"], u, f"Suchmaschine: {q}", z["nr"], z["netzbetreiber"]])
            we.writerow([z["nr"], z["netzbetreiber"], len(treffer)])
            f.flush()
            fe.flush()
            log(f"Suche [{z['nr']}] {z['netzbetreiber']}: {len(treffer)} Dokument(e)")
            time.sleep(pause)               # kostenloser Tarif: höchstens 1 Abfrage pro Sekunde
    return n
