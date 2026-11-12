# Wer macht was und wie (Stand 12.11.2026)

Ziel: Daten für Conplot, Schlüssel überall die MaStR-Nr. Drei Beteiligte: **Nutzer** (du), **Claude** (diese Sitzung), **Kollege** (eigener Branch `vibe/hlzf-etappen-1-2-705031`, liest Dokumente am Original, führt den Crawler).
Austausch nur über das Git: Aufträge und Antworten in `eingang/kommunikation/`, Lieferungen des Kollegen auf seinem Branch, Claude prüft und übernimmt nach `main`.

## Aufgaben

| # | Aufgabe | Wer | Eingabe | Ausgabe | Prüfung | Stand |
|---|---|---|---|---|---|---|
| 1 | Preisblätter holen, die der Crawler nicht findet oder die gesperrt sind (Avacon, Westnetz, Bayernwerk, E.DIS, Syna, Stuttgart Netze, SH Netz, Energienetze Bayern u. a.) | **Nutzer** im Browser | `ergebnis/arbeitsliste.csv`, `kollege_preise.csv` (Suchlinks nach Netzbetreiber-Name) | PDFs nach `eingang/` | Claude liest sie ein | offen |
| 2 | Crawler laufen lassen (`vnb/hlzf_crawl.py`), neue Dokumente sammeln | **Kollege** | `lauf/hlzf_offen_crawl.csv`, Auftrag 3/4 | Dokumente + Statusliste auf seinem Branch | Claude nimmt die Funde in die Kette | läuft |
| 3 | **HLZF 2027 offen (91 Dokumente)** am Dokument ablesen | **Kollege** | Auftrag 6, `AUFTRAG_6_hlzf_2027_offen.csv` | `ergebnis/hlzf/hlzf_2027_offen_gelesen.csv` | Claude gleicht Stichproben am Dokument ab, dann `lauf/hlzf_kollege_verifiziert.csv` | neu |
| 4 | **Modul 3 offen**: zweite Hälfte (nach MaStR-Nr. sortiert) | **Kollege** | Auftrag 5, `ergebnis/modul3_offen_kollege.csv` | `ergebnis/modul3_manuell.csv` | `daten/modul3_manuell_pruefen.py` (24 h, Überlappung) vor dem Commit; Claude prüft Stichproben | neu |
| 5 | **Modul 3 offen**: erste Hälfte | **Claude** | `ergebnis/modul3_offen_claude.csv` | `ergebnis/modul3_manuell.csv` | gleiche Prüfregeln (Skript) | läuft |
| 6 | Modul 3: Preise HT/ST/NT zu den Zeiten | **Claude** | Preisblatt-Texte | `ergebnis/modul3_zeiten.csv` | Zweitleser, Widerspruch = leer | 132 von 200 maschinell |
| 7 | HLZF 2026/2027 lesen (maschinell, Leser `vnb/hlzf.py`) und zusammenführen | **Claude** | Dokumente in `eingang/` | `lauf/hlzf_zusammen.csv` über `bash daten/hlzf_kette.sh` | Tests, Konfliktliste | 568 von 831 |
| 8 | Lieferungen des Kollegen prüfen und übernehmen | **Claude** | sein Branch | `main`, Rückmeldung in `eingang/kommunikation/` | am Dokumenttext gegengeprüft | laufend |
| 9 | Netzentgelte 2027 (Preise vorläufig) einlesen | **Claude** | `eingang/2027_vorlaeufig/*_preis_2027.pdf` (150) | `preise_2027_vorlaeufig` im Export | wie 2026 (Plausibilität) | 32 von 831 |
| 10 | Export für Conplot: `ergebnis/conplot/*.json`, `FORMAT.md` | **Claude** | Tabellen aus 6–9 | JSON je Netzbetreiber, PLZ, Umlagen | Tests | fertig, wächst mit |
| 11 | Importformat von Conplot erfragen (`scripts/netzentgelte_import.py`, Beispiel aus `data_quellen/netzentgelte_2026/`) | **Nutzer** (Weitergabe an Conplot) | Anfragetext liegt vor | Dateien in `eingang/kommunikation/` | Claude passt den Export an | offen |
| 12 | Entscheidungen: Sichtbarkeit des Repos (öffentlich vs. nur Partner), Marktdaten-Rechte | **Nutzer** | | Antwort im Chat | | offen |

## Regeln für alle
- Nichts raten. Unklar heißt leer lassen und im `hinweis`/`bemerkung` begründen.
- Jede Zeile rückwärts prüfen (jeder Wert zeigt auf eine Stelle im Dokument und umgekehrt).
- MaStR-Nr. steht in jeder Datei als erste Spalte.
- 2027 zuerst, 2026 nur wenn 2027 fehlt. Ein 2027-Fund zählt für 2026 und 2027 (`gelesen_aus_2027`).
- Zwei Arten Zeitfenster getrennt: § 19 (Hochlastzeitfenster) und Modul 3 (HT/ST/NT).
- Robots.txt, 403 und Cloudflare werden nicht umgangen. Gesperrte Dokumente holt der Nutzer im Browser.
- Erst im Git nachsehen, dann liefern; Listen und Zahlen nicht aus dem Gedächtnis.

## Wo steht was
- Aufträge/Antworten: `eingang/kommunikation/`
- Anleitungen: `ergebnis/modul3_ANLEITUNG_KOLLEGE.md`, `ergebnis/arbeitsliste_ANLEITUNG.md`, `eingang/kommunikation/ANLEITUNG_KOLLEGE_CRAWLER*`
- Ergebnisse: `ergebnis/netzentgelte_2026.csv`, `lauf/hlzf_zusammen.csv`, `ergebnis/modul3_zeiten.csv`, `ergebnis/conplot/`
