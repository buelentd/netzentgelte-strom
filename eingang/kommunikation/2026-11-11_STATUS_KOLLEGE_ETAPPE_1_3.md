# Statusmeldung Etappen 1–3 (2026-11-11)

## Korrektur nach Rückmeldung Etappe 1/2 (bildgeprüft gegen die Original-PDFs)

- **Aalen (SNB982726407335), 2026:** NS Winter `11:15-12:15, 17:00-18:45`, NS Herbst `17:45-18:00`; MS/NS Winter `17:00-18:45`, Herbst `17:45-18:00`; Frühling/Sommer `keins`. Kopfzeile im Dokument ist Winter-Frühling-Sommer-Herbst. Hinweis: `14:00-15:30` steht laut Bild in der Zeile **Mittelspannung**, nicht MS/NS.
- **Borna (SNB946013720880), 2026:** MS/NS Herbst ergänzt: `17:00-20:00` (Winter `10:00-13:00, 17:00-20:00`, NS Winter `10:30-13:30` unverändert).
- **Schonstett (SNB950882682972), 2026:** NS Winter `09:00-11:45, 17:30-19:30`; MS/NS Winter nur `17:00-19:15`.
- **Walldorf (SNB946790148600), 2026:** MS/NS `10:30-11:45` von Frühling nach **Herbst** verschoben.
- **Zeil a. Main (SNB935626894156), 2026:** `13:00-13:15` (Frühling) und `12:45-13:00` (Sommer) gehören laut Bild zum Block **Umspg. MS/NS** und sind dort jetzt eingetragen.

## Etappe 3 (50 Netzbetreiber)

- `hlzf_etappe3.csv`: 55 Zeilen (50×2026, 5×2027), davon **5 Netzbetreiber mit 2026-Werten**: Limburg/EVL, VBH Hoyerswerda, Emmendingen, VersorgungsBetriebe Elbe, Bad Nauheim. 2027-Zeilen (vorläufig): VBH Hoyerswerda, Ochtrup, Eberbach, Stockach, Leine-Solling.
- `hlzf_etappe3_originale.zip`: 12 Originaldokumente.
- 45 Netzbetreiber ohne 2026-Werte, jeweils mit Begründung in `bemerkung` (403: Olching, Weilheim, Westnetz, Syna; 404: Traunstein, Stockach-2026; nur ältere Jahre: Uslar, Spremberg, Oberwössen, Gemünden; Scan/garbled: Wittenberg, Verden; nicht gefunden: u. a. Güstrow, Waldkirchen, Windsbach, RheinNetz, Schleswig, MITNETZ, E.DIS und die 27 Gruppe-G-Betreiber).

## Stand gesamt

150/201 Netzbetreiber bearbeitet (Etappen 1–3). 46 mit 2026-Werten. Offene Fälle siehe `offene_urls_etappe1_2.csv` plus Etappe-3-Bemerkungen. Nächste: Etappe 4 (50× Gruppe G).

## Regeln ab jetzt

Text und Bild werden bei jeder Zeile gegeneinander geprüft (Bild gilt), Spaltenreihenfolge je Dokument aus der Kopfzeile, jede Ebene getrennt, alle Fenster einer Zelle, `keins` nur bei „entfällt“/„-“, Rückwärtsprüfung, unklar = leer + Bemerkung.
