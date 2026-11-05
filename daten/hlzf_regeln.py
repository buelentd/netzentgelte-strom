"""Gemeinsame Regeln für die Übernahme gelesener Hochlastzeitfenster (hlzf_eingang.py, hlzf_neu_lesen.py)."""
import re
from vnb.hlzf import _vollstaendig

# am Dokumenttext von Hand geprüft (05.11.2026)
VERWORFEN = {"55": "Zeilen vermischt (Fenster doppelt)", "272": "Spalten 2026 und 2027 nebeneinander, vermischt", "302": "Ebenenname geteilt, Zuordnung falsch",
             "350": "Raster mit Tagesliste, Zuordnung unklar", "363": "mehrere Tabellen vermischt", "719": "Zuordnung der Zeilen unklar", "737": "mehrere Tabellen vermischt",
             "142": "Zeiten zwischen den Ebenennamen", "214": "Zeilen den Ebenen nicht eindeutig zuzuordnen"}
VERIFIZIERT = {"15", "89", "90", "92", "103", "212", "229", "343", "462", "642", "445", "697", "320", "463", "714", "205", "558", "160", "184", "559"}
SICHERE_FORMEN = ("Block je Ebene (Netzebene / Jahreszeit / Zeiten)", "Ebenen als Spalten (von/bis)", "Ebene mit Jahreszeiten-Spalten (von/bis)",
                  "Ebenen-Zeilen unter Jahreszeiten-Kopf (von/bis)", "Tabelle nach Positionen")
ALTE_FORMEN = ("Jahreszeiten als Spalten", "Ebenen als Spalten", "ganzjährig")        # früh entwickelt, gelten mit bestandener Zeitenprüfung als sicher


def stufe(nr, text, e):
    """"sicher", "ungeprueft" oder None (nicht übernehmen) für eine vom Leser gelesene Datei."""
    if str(nr) in VERWORFEN or not e.gelesen:
        return None
    if re.search(r"(?m)^.*(?:hochlast|jahreszeit).*2026.*2027.*$|^.*2027.*2026.*(?:hochlast|jahreszeit).*$", text, re.I):
        return None
    if any(len(v) != len(set(v)) for eb in e.fenster.values() for v in eb.values()):
        return None
    if not _vollstaendig(text, e.fenster):
        return None
    if str(nr) in VERIFIZIERT or e.form in SICHERE_FORMEN or e.form in ALTE_FORMEN:
        return "sicher"
    return "ungeprueft"
