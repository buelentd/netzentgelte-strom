#!/usr/bin/env python3
"""Prüft vor dem Ablegen, ob eine heruntergeladene Datei das richtige Dokument ist. Eigenständig, nur Python 3 und (für PDF) pdftotext.

Preisblatt:   python3 dokument_pruefen.py preis  <Datei> "<Netzbetreibername>"
Hochlastzeit: python3 dokument_pruefen.py hlzf   <Datei> "<Netzbetreibername>"
Mehrere:      python3 dokument_pruefen.py preis --liste liste.csv      (Spalten: datei;netzbetreiber, Trennzeichen ;)

Ausgabe je Datei: OK, PRUEFEN (Mensch schaut hin) oder FALSCH (nicht ablegen), mit Gründen.
Excel (.xlsx, .xls) und HTML werden gelesen, Scans ohne Text melden PRUEFEN. Es wird nichts geschätzt und nichts umgangen."""
import csv, html as hm, re, subprocess, sys, warnings
warnings.filterwarnings("ignore")
from pathlib import Path

ZEIT = re.compile(r"(?<![\d:.])[0-2]?\d:[0-5]\d(?![\d:])")
FUELL = {"stadtwerke", "stadtwerk", "gemeindewerke", "netzgesellschaft", "verteilnetz", "netze", "netz", "versorgung", "energie",
         "elektrizitäts", "elektrizitätswerk", "genossenschaft", "gmbh", "gesellschaft", "kommunalunternehmen", "betriebe", "werke", "mbh"}


def text_lesen(pfad: str) -> str:
    ext = Path(pfad).suffix.lower()
    if ext == ".pdf":
        try:
            return subprocess.run(["pdftotext", "-layout", pfad, "-"], capture_output=True, timeout=90).stdout.decode("utf-8", "replace")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return ""
    if ext in (".xlsx", ".xlsm"):
        import openpyxl
        wb = openpyxl.load_workbook(pfad, data_only=True, read_only=True)
        return "\n".join("   ".join(str(c) for c in r if c is not None) for ws in wb for r in ws.iter_rows(values_only=True))
    if ext == ".xls":
        import xlrd
        wb = xlrd.open_workbook(pfad)
        return "\n".join("   ".join(str(c) for c in ws.row_values(i) if c != "") for ws in wb.sheets() for i in range(ws.nrows))
    h = Path(pfad).read_text(encoding="utf-8", errors="replace")
    h = re.sub(r"(?is)<(script|style).*?</\1>", " ", h)
    return hm.unescape(re.sub(r"<[^>]+>", " ", h))


def namen_im_text(name: str, t: str) -> bool:
    teile = [w for w in re.findall(r"[A-Za-zÄÖÜäöüß]{4,}", name) if w.lower() not in FUELL]
    return bool(teile) and any(w.lower() in t.lower() for w in teile)


def pruefen(art: str, pfad: str, name: str):
    gruende, falsch = [], False
    t = text_lesen(pfad)
    if len(t.strip()) < 200:
        return "PRUEFEN", ["kaum Text (Scan, Bild oder leere Seite): von Hand ansehen"]
    kopf = t[:4000].lower()
    j26, j27, j25 = len(re.findall(r"2026", t)), len(re.findall(r"2027", t)), len(re.findall(r"2025", t))
    if j26 == 0 and Path(pfad).suffix.lower() in (".xlsx", ".xlsm", ".xls"):
        gruende.append("Excel: Jahr nicht als Text zu finden (Datumsfelder): im Dateinamen oder in der Tabelle nachsehen")
    elif j26 == 0:
        falsch = True; gruende.append("Jahr 2026 kommt nicht vor" + (" (nur 2025/2027)" if j25 or j27 else ""))
    elif j27 > j26 * 2 and j26 < 3:
        gruende.append("meist 2027 (vorläufig?): 2026 suchen")
    if name and not namen_im_text(name, t):
        gruende.append("Netzbetreibername steht nicht im Dokument (andere Firma, geteilte Website?)")
    if art == "preis":
        marken = {"Niederspannung/Umspannung": r"niederspannung|umspann", "ct/kWh": r"ct\s*/\s*kwh|cent", "€/kW": r"€\s*/\s*kw|eur\s*/\s*kw|euro\s*/\s*kw",
                  "Leistungs-/Arbeits-/Grundpreis": r"leistungspreis|arbeitspreis|grundpreis"}
        fehlt = [k for k, p in marken.items() if not re.search(p, t, re.I)]
        if len(fehlt) >= 3:
            falsch = True; gruende.append("kein Preisblatt: es fehlen " + ", ".join(fehlt))
        elif fehlt:
            gruende.append("Preisblatt unvollständig? fehlt: " + ", ".join(fehlt))
        if re.search(r"messstellenbetrieb|gmsb|ergänzende bedingungen|baukostenzuschuss|netzanschlussvertrag|technische anschlussbedingungen|widerruf|datenschutz|eintrittspreis|trinkwasser|bericht", kopf):
            gruende.append("Titel/Anfang klingt nach anderem Dokument (Messstellenbetrieb, Ergänzende Bedingungen, Anschluss, Datenschutz, Bericht)")
        if re.search(r"\bgas\b|erdgas|wärme|wasser", kopf) and not re.search(r"niederspannung", t, re.I):
            falsch = True; gruende.append("Gas/Wärme/Wasser statt Strom")
    else:
        if not re.search(r"hochlast|hlzf|hlfz", t, re.I):
            falsch = True; gruende.append("kommt kein Hochlastzeitfenster vor")
        n = len(ZEIT.findall(t))
        if n < 2:
            gruende.append("kaum Uhrzeiten im Text: Raster, Scan oder verschlüsselte Schrift? von Hand ansehen")
        if re.search(r"(?<!\d)(2022|2023|2024)(?!\d)", kopf) and j26 == 0:
            falsch = True; gruende.append("Jahr im Kopf ist älter als 2026")
    status = "FALSCH" if falsch else ("PRUEFEN" if gruende else "OK")
    return status, gruende or ["Jahr 2026, Name und Inhalt passen"]


def main():
    a = sys.argv[1:]
    if len(a) < 3 or a[0] not in ("preis", "hlzf"):
        print(__doc__); return 1
    art = a[0]
    paare = []
    if a[1] == "--liste":
        for r in csv.DictReader(open(a[2], encoding="utf-8-sig"), delimiter=";"):
            paare.append((r["datei"], r.get("netzbetreiber", "")))
    else:
        paare.append((a[1], a[2]))
    zaehler = {}
    for pfad, name in paare:
        try:
            s, g = pruefen(art, pfad, name)
        except Exception as e:
            s, g = "PRUEFEN", [f"nicht lesbar ({type(e).__name__})"]
        zaehler[s] = zaehler.get(s, 0) + 1
        print(f"{s:8} {Path(pfad).name}  |  {'; '.join(g)}")
    if len(paare) > 1:
        print(zaehler)
    return 0


if __name__ == "__main__":
    sys.exit(main())
