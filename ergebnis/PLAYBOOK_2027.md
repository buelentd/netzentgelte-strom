# Playbook 2027: Netzentgelte, Hochlastzeitfenster und Modul 3 bis zum Jahreswechsel

Stand 12.11.2026, 50 Tage bis 01.01.2027. Zahlen aus den Dateien, nicht aus dem Gedächtnis. Ergänzt `PLAYBOOK_NETZENTGELTE_JAHR.md` (Allgemeines) und `ARBEITSTEILUNG.md` (Wer macht was).

## 1. Ziel und "fertig"
Für jeden der 831 Netzbetreiber (Schlüssel MaStR-Nr.) liegt vor und ist geprüft:
1. **Preise 2027** (vorläufig, § 20 Abs. 1 EnWG): SLP und RLM (NS, MS/NS, MS), beide Preissysteme.
2. **Hochlastzeitfenster** (§ 19 Abs. 2 StromNEV): 2026 oder 2027, was zuerst gefunden wird, zählt für beide Jahre.
3. **Modul 3** (§ 14a): HT/ST/NT-Zeiten, Quartale, Preise.
"Fertig" heißt: gelesen, Plausibilität bestanden, Stichprobe am Dokument bestätigt, im Export. Nicht "Datei vorhanden".

## 2. Ausgangslage (aus den Dateien)
| Strang | fertig | offen | Hauptproblem |
|---|---:|---:|---|
| Preise 2027 | 144 gelesen, 62 teilweise, 4 prüfen | **571 ohne Preisblatt** (rund 67 % der Einwohner) | Dokumente fehlen, die Großen zuerst |
| Hochlastzeitfenster | 595 | **236** (106 nicht lesbar, 89 kein Dokument, 11 Raster, Rest Prüfung) | Lesen von Hand und Suchen |
| Modul 3 | 231 (200 maschinell) | **541 offen**, davon 426 mit Uhrzeiten | Zeit steht über/unter dem Tarifnamen, braucht das Bild |

## 3. Reihenfolge nach Wirkung (Einwohnerzahl)
Die 571 Netzbetreiber ohne Preisblatt sind nach Einwohnern im Netzgebiet sortiert (`ergebnis/browser_preise_2027_571.csv`). Die ersten N decken von deren Bevölkerung ab: **20 → 55 %, 50 → 73 %, 100 → 83 %, 200 → 92 %.**
Daraus die Etappen (Bevölkerungsabdeckung 2027 gesamt, heute 27 %):
| Etappe | Ziel | Abdeckung 2027 danach (rund) | Frist |
|---|---|---:|---|
| 1 | Top 20 (Westnetz, Berlin, EWE, MITNETZ, E.DIS, Hamburg, Syna, EAM …) holen und lesen | 64 % | 20.11. |
| 2 | Top 100 | 82 % | 30.11. |
| 3 | Top 200 + alle 62 "teilweise" und 4 "prüfen" klären | 90 % | 10.12. |
| 4 | Rest (371 kleine Netzbetreiber), Restliste mit Gründen | über 95 % | 22.12. |
Bei HLZF und Modul 3 gilt dieselbe Rangfolge: erst die großen Netzbetreiber, die kleinen dürfen länger dauern.

## 4. Die drei Stränge
**A. Preise 2027**
1. *Holen* (Nutzer im Browser, Auftrag 8): Liste `browser_preise_2027_571.csv` von oben nach unten. Zuerst die abgeleiteten Adressen `lauf/url_kandidaten_2027.csv` (2026 → 2027 in der Adresse, 460 Stück, ungetestet), dann die Suchlinks.
2. *Ablegen*: `eingang/2027_vorlaeufig/<MaStR-Nr>_preis_2027.pdf`.
3. *Lesen* (Claude, 0 Tokens): `PYTHONPATH=. python daten/netzentgelte_2027.py --nur-lokal`. Plausibilität wie 2026, dazu **Vorjahresvergleich**: Abweichung über 40 % → Belegprüfung am Dokument.
4. *Export*: `daten/conplot_export.py`. Ergebnis `preise_2027_vorlaeufig` je Netzbetreiber.

**B. Hochlastzeitfenster** (Auftrag 7, Kollege): 116 ablesen, 5 prüfen, 132 suchen. 2026 oder 2027, was zuerst gefunden wird. Format und Regeln: `hlzf_ANLEITUNG_KOLLEGE_253.md`. Lieferungen prüft Claude (Zeiten im PDF-Text wiederfinden, `daten/hlzf_lieferung_pruefen.py`). Draft-Hilfe: `daten/hlzf_entwurf.py`.

**C. Modul 3** (Auftrag 5, Kollege): 426 Fälle, Anleitung `modul3_ANLEITUNG_KOLLEGE.md`. Claude prüft Stichproben. Preise HT/ST/NT liest Claude nach (Zweitleser). Fälle ohne Uhrzeit im Preisblatt (gut 110) brauchen zuerst das Dokument oder die Aussage "nicht ausgewiesen".

## 5. Wochenrhythmus
- **Montag/Donnerstag:** Claude liest alle neuen Dateien ein (Preise, HLZF, Modul 3), erzeugt Export, meldet Zahlen: fertig/offen je Strang, Bevölkerungsabdeckung 2027, verloren = 0.
- **Täglich:** Kollege liefert in Stapeln von 10 bis 20 (Zeilen + Prüfskript grün), nicht am Ende alles auf einmal.
- **Nutzer:** Browser-Liste in Blöcken von 20. Nach jedem Block pushen.
- **Freitag:** Stichprobe 20 Zeilen quer über alle Stränge gegen das Dokument; Fehlerquote wird gemeldet (2026 war 2,5 %).

## 6. Qualitätsregeln (unverändert)
- Nichts raten: leer lassen und begründen. Text und Bild vergleichen. Jede Zeit rückwärts prüfen.
- Vor jedem Einlesen Stand sichern, danach vergleichen: **verloren = 0**. Eine bereits gelesene Zeile wird nie überschrieben.
- Tests grün vor dem Push. Kein Push auf rote oder flackernde Tests.
- 403, Cloudflare und robots.txt werden nicht umgangen; solche Dokumente holt der Nutzer im Browser.
- Mittelspannung ist nicht MS/NS. `keins` nur bei "entfällt" im Dokument; fehlende Ebene = leer + Bemerkung.

## 7. Was wir verbessern, damit es nicht wieder so lange dauert
1. **Dokumentweise Bibliothek der Layouts:** Jede neue Tabellenform, die ein Mensch löst, wird einmal in den Leser eingebaut (nicht in den Chat geschrieben). Die 106 "nicht lesbar" sind eine Liste der noch fehlenden Formen.
2. **Zeitstempel-Konvention klären:** Netzbetreiber, die die Zeit als Ende der Messperiode angeben (Rostock, Aalen, ODR, Düsseldorf), brauchen eine einheitliche Umrechnung (Entscheidung offen).
3. **Quartals-/Ja-Nein-Tabellen** bei Modul 3 als eigene Leserform bauen (kommt in 100 Fällen vor).
4. **Rückkanal:** Jede Lieferung mit Anzahl gelesen/unklar/blockiert; Zahlen nur aus `lauf/hlzf_zusammen.csv` und den Export-Dateien.

## 8. Entscheidungen, die offen sind
| Entscheidung | Wer | Wirkung |
|---|---|---|
| Zeitstempel = Ende der Messperiode: 15 Minuten nach vorn verschieben? | Nutzer | Zeitreihe für Conplot |
| Repo öffentlich oder nur Partner (REST-API, Daten) | Nutzer | Zugriff |
| Marktdaten (Day-Ahead, Regelenergie) Rechte | Nutzer | Datenpaket |
| Importformat Conplot für 2027 / Modul 3 / Konzessionsabgabe | Conplot | Export |

## 9. Risiken
- 571 Preisblätter in 50 Tagen von Hand zu holen ist viel. Gegenmittel: Rangfolge (Etappe 1 und 2 bringen 82 %), abgeleitete Adressen, Crawler des Kollegen für die Kleinen.
- Gefundene Datei ≠ gelesen: bei 2026 lag der Engpass im Lesen. Deshalb Lesen und Prüfen im Wochenrhythmus fest einplanen.
