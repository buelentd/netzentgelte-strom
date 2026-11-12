# Rückmeldung zur Lieferung (164 + 105 Zeilen)

**Danke, das war ein großer Schritt:** 37 Zeilen sind neu in `main` (alle Zeiten im PDF-Text wiedergefunden), 173 waren schon fertig. Damit sind **632 von 831** fertig. Verloren ging nichts (Vorher/Nachher-Vergleich: 0 verloren, 0 geändert).

## Nicht übernommen (14), bitte nachbessern
| Netzbetreiber | Grund |
|---|---|
| Selb-Marktredwitz | 8 von 8 Zeiten stehen nicht im PDF-Text (zum zweiten Mal). Bitte Stelle nennen oder Datei prüfen. |
| Heikendorf | 4 von 4 Zeiten nicht im Text |
| Waldbüttelbrunn | 4 von 4 Zeiten nicht im Text |
| werkkraft | 5 von 5 Zeiten nicht im Text (du schreibst "formatkorrigiert"; im Text finde ich die Zeiten nicht) |
| Bielefelder Netz | 3 von 3 Zeiten nicht im Text (Datei trägt 2026 im Namen, Inhalt 2027?) |
| Senftenberg | Datei hat keinen Text (Bild): bitte Seite und Zelle im `bemerkung` nennen |
| Bad Hersfeld, Angermünde, Halberstadt | Quelldatei nicht im Repo (Halberstadt: nur "Nutzer-Tabelle (Webseite)"; bitte Datei oder Adresse ablegen) |

Liste mit Gründen: `lauf/hlzf_lieferung_zurueck.csv`.

## 43 Zeilen ohne Zeiten
Staßfurt, Reußenköge (nur MS), Bad Rodach, Bielefelder, RheinNetz, nvb u. a.: "nur MS", "separat veröffentlicht", "keine Fenster im Preisblatt". Das ist gut dokumentiert, aber **noch keine Lösung**: Wo "separat veröffentlicht" steht, fehlt noch das eigene Hochlastzeitfenster-Dokument. Diese Netzbetreiber bleiben offen und gehören in die Suche (Auftrag 7, `suchen`).

## Weiter so
Stapel, Beleg pro Zeile, Prüfskript grün. Nächste Lieferung bitte mit den 14 oben und den Fällen "suchen". Übernahme läuft ab jetzt mit einem Befehl: `PYTHONPATH=. python daten/hlzf_lieferung_uebernehmen.py`.
