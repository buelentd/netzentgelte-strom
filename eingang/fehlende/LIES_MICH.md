# eingang/fehlende (Stand 09.11.2026)

Hier legt der Nutzer die PDFs der bisher blockierten Netzbetreiber ab (13 blockierte, evtl. weitere).
**Die Dateien sind zum Großteil von 2026 und 2027 gemischt.** Vor dem Auslesen wird je Datei das Jahr im Dokument bestimmt:
- 2026 (endgültig oder vorläufig, das ganze Jahr gültig): in die 2026-Kette (Text, Beleg-Leser, Tabelle).
- 2027 (vorläufig): nicht in die 2026-Tabelle, sondern nach `eingang/2027_vorlaeufig/` und später in `netzentgelte_2027.csv`.
- Jahr nicht erkennbar: nicht raten, in `ergebnis/restliste.csv` mit Grund.
Schlüssel ist die MaStR-Nummer (`mastr_nr`) in jeder Liste. Dateiname: `<MaStR-Nr>_preis_<Originalname>.pdf` (Zuordnung durch uns, falls anders benannt).
Reihenfolge: erst Skript (Textauszug, Jahr, Netzbetreiber im Dokument), dann nur die unsicheren Fälle selbst lesen.
