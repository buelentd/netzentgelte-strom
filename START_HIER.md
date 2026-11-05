# Netzentgelte Strom 2026: Start hier

Stand und Ablauf auf einer Seite. Alles andere im Ordner ist Arbeitsmaterial.

## Die drei Dateien, die zählen
| Datei | Wofür |
|---|---|
| `ergebnis/netzentgelte_2026.csv` | **Das Ergebnis.** Eine Zeile je Netzbetreiber, alle Preise, Hochlastzeitfenster, Status. Spalten in `LEGENDE.md`. |
| `ergebnis/arbeitsliste.csv` | **Was noch fehlt**, wer es macht (Kollege, Nutzer im Browser, Claude), Suchbegriff und Dateiname. Anleitung: `ergebnis/arbeitsliste_ANLEITUNG.md`. |
| `ergebnis/haben_wir_haben_wir_nicht.csv` | Überblick je Netzbetreiber: SLP, NS, MS/NS, MS, HS/MS, Hochlastzeitfenster, ja oder nein, mit Grund. |

## Wohin mit neuen Dateien
- **Alles flach in `eingang/pdfs_neu/`.** Keine Unterordner nötig.
- Hochlastzeitfenster: `SNB…_NNNN_hlzf.pdf` (auch `.xls`, `.xlsx`, `.html`)
- Preisblätter: `SNB…_NNNN.pdf` (auch `.xlsx`, `.html`) oder `pb_<Nummer>.pdf`
- Vorher prüfen: `python3 daten/dokument_pruefen.py preis|hlzf <Datei> "<Netzbetreiber>"`
- Danach Commit, Sync, „synched“ an Claude. Geht der Push nicht: auf github.com „Add file, Upload files“ im Ordner `eingang/pdfs_neu`.

## Was Claude daraus macht
1. Dateien einlesen (`daten/eingang_verarbeiten.py`, `daten/hlzf_eingang.py`, `daten/xlsx_uebernehmen.py`)
2. Leser und Qualitätsprüfung (`daten/hlzf_qualitaet.py`, `daten/korrektur_lesefehler.py`)
3. Tabelle, Arbeitsliste und Übersicht neu erzeugen
4. Die neue Zahl melden

## Regeln
- Nur 2026, nur Strom, endgültig vor vorläufig, kein 2027.
- Nichts schätzen: fehlt etwas, bleibt es leer und steht in der Arbeitsliste.
- robots.txt beachten, Sperren nicht umgehen, kein Web-Reader eines Dritten für gesperrte Seiten.

## Alte Listen
Frühere Teil-Listen liegen in `ergebnis/alt_listen/`. Sie sind durch `arbeitsliste.csv` ersetzt.
