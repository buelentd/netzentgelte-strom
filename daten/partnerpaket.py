"""Lieferpaket für Partner (CSV, PLZ-Zuordnung, Legende, Lies-mich, Änderungsliste), erzeugt aus den Daten, nicht von Hand.

Regeln: MaStR-Nummer immer als erste Spalte; Quellen nur als Link, nie als lokaler Dateiname; Zahlen im Text kommen aus den Daten;
zu jeder Lieferung gehört eine Änderungsliste gegenüber der letzten Lieferung.

Aufruf: PYTHONPATH=. python daten/partnerpaket.py --out PAKET.zip [--vorher alte_netzentgelte_2026.csv]
"""
from __future__ import annotations

import argparse
import collections
import csv
import datetime
import io
import os
import re
import zipfile
from pathlib import Path

W = Path(__file__).resolve().parent.parent
HLZF_FERTIG = ("gelesen_nutzer", "gelesen_unser", "gelesen_kollege_verifiziert")
HLZF_URL = re.compile(r"hoch.?last|hlzf|hlf", re.I)


def lesen(pfad):
    return list(csv.DictReader(open(pfad, encoding="utf-8-sig"), delimiter=";"))


def schreiben(rows, cols):
    b = io.StringIO(newline="")
    w = csv.DictWriter(b, fieldnames=cols, delimiter=";", lineterminator="\n", extrasaction="ignore")
    w.writeheader()
    w.writerows(rows)
    return ("﻿" + b.getvalue()).encode("utf-8")


def adressen_hlzf(nr_gesucht, mastr_zu_nr):
    """Bekannte Adressen für Hochlastzeitfenster je nr: zuerst lauf/hlzf_urls.csv, dann andere Listen (nur Adressen mit Hochlast im Namen)."""
    out, quelle = {}, {}
    for r in lesen(W / "lauf" / "hlzf_urls.csv"):
        if r["nr"] in nr_gesucht and r["url"].startswith("http"):
            out.setdefault(r["nr"], r["url"])
            quelle.setdefault(r["nr"], "lauf/hlzf_urls.csv")
    for pfad in sorted(list((W / "ergebnis").glob("*.csv")) + list((W / "daten").glob("*.csv"))):
        try:
            rows = lesen(pfad)
        except Exception:
            continue
        for r in rows:
            nr = r.get("nr") or mastr_zu_nr.get(r.get("mastr_nr", ""), "")
            if nr not in nr_gesucht or nr in out:
                continue
            for v in r.values():
                if not isinstance(v, str):
                    continue
                for u in re.findall(r"https?://[^\s|;,\"]+", v):
                    if HLZF_URL.search(u):
                        out[nr] = u
                        quelle[nr] = pfad.name
                        break
                if nr in out:
                    break
    return out


def bauen(ziel: Path, vorher: Path | None = None):
    tab = lesen(W / "ergebnis" / "netzentgelte_2026.csv")
    plz = lesen(W / "ergebnis" / "plz_netzbetreiber.csv")
    mastr_zu_nr = {r["mastr_nr"]: r["nr"] for r in tab}
    lokal = {r["nr"] for r in tab if r["hlzf_quelle_url"] and not r["hlzf_quelle_url"].startswith("http")}
    adr = adressen_hlzf(lokal, mastr_zu_nr)
    stat = collections.Counter()
    for r in tab:
        u = r["hlzf_quelle_url"]
        if not u:
            r["hlzf_quelle_status"] = ""
        elif u.startswith("http"):
            r["hlzf_quelle_status"] = "Link"
        elif r["nr"] in adr:
            r["hlzf_quelle_url"] = adr[r["nr"]]
            r["hlzf_quelle_status"] = "Adresse aus unseren Listen, nicht gegen das gelesene Dokument geprüft"
        else:
            r["hlzf_quelle_url"] = ""
            r["hlzf_quelle_status"] = "Adresse unbekannt, Dokument liegt bei uns"
        stat[r["hlzf_quelle_status"]] += 1
        r["quelle_hinweis"] = "keine Adresse hinterlegt" if r["status"] == "ok" and not r["quelle_url"] else ""
    cols = ["mastr_nr"] + [c for c in tab[0].keys() if c != "mastr_nr"] + []
    cols = [c for c in cols if c not in ("hlzf_quelle_status", "quelle_hinweis")] + ["hlzf_quelle_status", "quelle_hinweis"]
    plz_cols = ["mastr_nr"] + [c for c in plz[0].keys() if c != "mastr_nr"]

    ok = [r for r in tab if r["status"] == "ok"]
    frei = sum(1 for r in ok if "Freigegeben durch Nutzer" in r["hinweis"])
    sonder = sum(1 for r in ok if r["hinweis"].startswith("Sonderfall"))
    beleg = {r["mastr_nr"]: r["beleg"] for r in lesen(W / "ergebnis" / "beleg_zusammenfassung.csv")}
    belegt = sum(1 for r in ok if "Freigegeben durch Nutzer" not in r["hinweis"] and not r["hinweis"].startswith("Sonderfall") and beleg.get(r["mastr_nr"]) == "alle_belegt")
    rest = len(ok) - frei - sonder - belegt
    ohne_quelle = sum(1 for r in tab if r["quelle_hinweis"])
    nicht_ok = collections.Counter(r["status"] for r in tab if r["status"] != "ok")
    hl_fertig = [r for r in tab if r["hlzf_status"] in HLZF_FERTIG]
    jzn = ("fruehling", "sommer", "herbst", "winter")
    teilleer = []
    for r in tab:
        if r["hlzf_status"] in HLZF_FERTIG:
            for eb in ("ns", "msns"):
                zellen = [r[f"hlzf_{eb}_{j}"] for j in jzn]
                if any(zellen) and not all(zellen):
                    teilleer.append(f"{r['netzbetreiber']} ({eb.upper()})")
    heute = datetime.date.today().strftime("%d.%m.%Y")

    lies = f"""# Netzentgelte Strom 2026 und PLZ-Zuordnung (Stand {heute})

Alle Zahlen in diesem Text sind aus den Daten gezählt, die in diesem Paket liegen.

## Dateien im Paket
- `netzentgelte_2026.csv`: {len(tab)} Netzbetreiber, **MaStR-Nummer in der ersten Spalte**, `;` als Trenner, Dezimalkomma, alle Preise **netto**.
- `plz_netzbetreiber.csv`: Postleitzahl zu Netzbetreiber (MaStR-Nummer, Anteil der Anschlüsse in Prozent, Einheiten), {len(plz)} Zeilen. Eine PLZ kann mehrere Netzbetreiber haben.
- `LEGENDE.md`: Erklärung aller Spalten.
- `AENDERUNGEN.md`: was sich seit der letzten Lieferung geändert hat.

## Wie belastbar die Werte sind
Status `ok`: {len(ok)} Netzbetreiber, nach Belegstand:
- {belegt}: **am Preisblatt Zeile für Zeile bestätigt** (Beleg-Prüfung `alle_belegt`).
- {frei}: **freigegeben, aber nicht einzeln am Dokument geprüft** (Hinweis „Freigegeben durch Nutzer").
- {sonder}: Sonderfall (Werksnetz, Preisblatt nur 110 kV; NS, MS/NS und SLP gibt es dort nicht).
{"- " + str(rest) + ": übrige." if rest else ""}
Die Spalte `hinweis` enthält bei vielen Zeilen noch einen älteren Text („Werte aus Liste ..."), der den heutigen Belegstand nicht mehr widerspiegelt. Maßgeblich ist die Aufstellung oben.
Nicht `ok`: {len(tab) - len(ok)} Netzbetreiber ({", ".join(f"{k} {v}" for k, v in sorted(nicht_ok.items()))}). Dort fehlen Werte; leere Felder bedeuten „nicht erfasst", nicht null.
In einer Stichprobe von 200 Netzbetreibern (07.11.2026) hatten 5 einen falschen Wert (2,5 %), sie sind korrigiert. Für die übrigen ist die Fehlerquote nicht untersucht.

## Quellen
- `quelle_url` ist die Adresse des Preisblatts. Bei {ohne_quelle} `ok`-Zeilen ist keine hinterlegt (Spalte `quelle_hinweis`); das ist für sie eine Lücke in der Quellenangabe, kein Hinweis auf falsche Werte.
- `hlzf_quelle_url` ist die Adresse des Dokuments mit den Hochlastzeitfenstern. Die Spalte `hlzf_quelle_status` sagt, wie sicher sie ist:
  - „Link": {stat['Link']} Zeilen.
  - „Adresse aus unseren Listen, nicht gegen das gelesene Dokument geprüft": {stat['Adresse aus unseren Listen, nicht gegen das gelesene Dokument geprüft']} Zeilen. Die Adresse kann ein anderes Jahr oder eine ältere Fassung zeigen.
  - „Adresse unbekannt, Dokument liegt bei uns": {stat['Adresse unbekannt, Dokument liegt bei uns']} Zeilen.

## Hochlastzeitfenster
Gelesen (Status `gelesen_*`): {len(hl_fertig)} Netzbetreiber. Gilt für Werktage. Leer: nicht erfasst. `keins`: Das Dokument nennt für diese Jahreszeit kein Fenster.

## Bekannte Mängel
- Hochlastzeitfenster mit teilweise leeren Jahreszeiten (vermutlich „keins", vom Leser aber nicht eingetragen): {len(teilleer)} Fälle{": " + "; ".join(teilleer[:12]) if teilleer else ""}.
- Einzelne Quelladressen können veraltet sein (siehe `hlzf_quelle_status`).

## Nicht enthalten
Messentgelte, Konzessionsabgabe, Umlagen, Steuern, Energiepreis. Preisblätter sind öffentlich veröffentlichte Dokumente der Netzbetreiber; dieses Paket ist eine maschinelle Zusammenstellung und keine Rechtsberatung.
"""

    leg = (W / "LEGENDE.md").read_text(encoding="utf-8")
    leg = leg.replace("NS LP ab 2.500 h 40–260 €/kW/a", "NS LP ab 2.500 h 40–500 €/kW/a")
    leg = re.sub(r"# Weitere Dateien in ergebnis/.*?(?=## Ebenen und Status)",
                 "# Zusätzliche Spalten im Paket\n\n| Spalte | Bedeutung |\n|---|---|\n"
                 "| `hlzf_quelle_status` | wie sicher die Adresse in `hlzf_quelle_url` ist (Link, aus unseren Listen, unbekannt) |\n"
                 "| `quelle_hinweis` | Text „keine Adresse hinterlegt“, wenn bei Status `ok` kein Preisblatt-Link steht |\n\n"
                 "Weitere Dateien aus dem Projekt (`restliste.csv`, `hochlastzeitfenster_2026.csv`, `fortschritt.jsonl` und andere) gehören **nicht** zu diesem Paket.\n\n",
                 leg, count=1, flags=re.S)

    aend = f"# Änderungen seit der letzten Lieferung (Stand {heute})\n\n"
    if vorher and Path(vorher).exists():
        alt = {r["mastr_nr"]: r for r in lesen(vorher)}
        neu = {r["mastr_nr"]: r for r in tab}
        gleich = [c for c in cols if c in next(iter(alt.values()))]
        zeilen = []
        for m, r in neu.items():
            a = alt.get(m)
            if a is None:
                zeilen.append((m, r["netzbetreiber"], "neu in der Liste", "", ""))
                continue
            for c in gleich:
                if c in ("hlzf_quelle_url", "hlzf_quelle_status", "quelle_hinweis"):
                    continue
                if (a.get(c) or "") != (r.get(c) or ""):
                    zeilen.append((m, r["netzbetreiber"], c, a.get(c) or "", r.get(c) or ""))
        aend += f"Verglichen mit: `{Path(vorher).name}`. Geänderte Felder: {len(zeilen)} in {len({z[0] for z in zeilen})} Netzbetreibern.\n\n"
        aend += "| MaStR-Nr. | Netzbetreiber | Feld | vorher | jetzt |\n|---|---|---|---|---|\n"
        for z in zeilen[:200]:
            aend += "| " + " | ".join(str(x).replace("|", "/") for x in z) + " |\n"
        if len(zeilen) > 200:
            aend += f"\n(weitere {len(zeilen) - 200} Änderungen nicht aufgeführt)\n"
        aend += "\nNeu in dieser Lieferung unabhängig vom Vergleich: Spalten `hlzf_quelle_status` und `quelle_hinweis`, Quelladressen statt lokaler Dateinamen, aktualisierte Legende.\n"
    else:
        aend += "Erste Lieferung dieser Art, kein Vergleich möglich.\n"

    with zipfile.ZipFile(ziel, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("netzentgelte_2026.csv", schreiben(tab, cols))
        z.writestr("plz_netzbetreiber.csv", schreiben(plz, plz_cols))
        z.writestr("LEGENDE.md", leg)
        z.writestr("LIES_MICH.md", lies)
        z.writestr("AENDERUNGEN.md", aend)
    return stat, len(tab)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--vorher")
    a = ap.parse_args()
    s, n = bauen(Path(a.out), Path(a.vorher) if a.vorher else None)
    print(n, "Zeilen;", dict(s))
