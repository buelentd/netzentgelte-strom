# Rückmeldung zur Lieferung von 16:30 (12.11.2026)

Von deinen 21 Zeilen (20 in `hlzf_2027_gelesen.csv`, 1 in `hlzf_auftrag7_gelesen.csv`) habe ich jede Zeit im PDF-Text gesucht.

## Übernommen (5 neu, 5 schon fertig)
Hütschenhausen, Tübingen, Bliestal, St. Ingbert, WEMAG sind neu in `main` (`gelesen_aus_2027`). EnergieSüdwest, Alzenau, Wernigerode, Bad Dürkheim und Duisburg waren schon fertig; Zeiten stimmen. Danke.

## Noch nicht übernommen: Zeiten im PDF-Text nicht gefunden
Bitte pro Zeile die Stelle im Dokument nennen (Seite, Zelle, Spalte) in `bemerkung`. Ist die Zeit nur im Bild, schreib das ausdrücklich ("nur im Bild, Seite 2, Zeile MS/NS Winter").

| MaStR-Nr. | Netzbetreiber | Datei | deine Werte |
|---|---|---|---|
| SNB911696239035 | Energieversorgung Selb-Marktredw | SNB911696239035_0167_hlzf_2027.pdf | msns_herbst=09:45-11:45, 12:00-13:00; msns_winter=07:45-13:00, 13:15-13:30 |
| SNB913130054136 | Netzgesellschaft Schwerin mbH (N | SNB913130054136_0331_hlzf_2027.pdf | ns_sommer=08:45-10:15; msns_herbst=07:45-10:15; msns_winter=07:45-13:15 |
| SNB915186313908 | Energieversorgung Guben GmbH | SNB915186313908_0159_hlzf_2027.pdf | ns_winter=17:00-19:30; msns_winter=17:00-19:30 |
| SNB977374861035 | Halberstadtwerke GmbH | Nutzer-Tabelle (Webseite) | ns_winter=10:15-13:15, 17:00-20:00; msns_winter=09:30-12:30, 16:15-19:15 |
| SNB916269213931 | Mitteldeutsche Netzgesellschaft  | SNB916269213931_0006_hlzf_2027.pdf | ns_winter=11:00-12:00; msns_winter=16:45-20:00 |
| SNB924747450655 | EWR GmbH (Remscheid) | SNB924747450655_0191_hlzf_2027.pdf | ns_winter=16:30-19:30; msns_winter=16:15-19:30 |
| SNB916927144072 | Stadtwerke Villingen-Schwenninge | eingang/pdfs_neu/SNB916927144072_hlzf_SVS_Hoch | ns_herbst=17:15-18:30; ns_winter=17:15-19:15; msns_herbst=17:30-18:15; msns_winter=17:15-19:15 |
Besonderheiten:
- **Selb-Marktredwitz:** Du trägst MS-Werte unter `msns` ein und hast ns auf `keins`. Das Dokument hat laut deiner `bemerkung` nur MS. Mittelspannung ist nicht MS/NS; MS-Werte gehören **nicht** nach `msns`. Zeile bitte neu: ns und msns leer, `bemerkung = nur MS ausgewiesen (Werte: …)`.
- **Villingen-Schwenningen:** Das Dokument im Repo ist `SVS_Hochlastzeitfenster_2026.pdf`, nicht 2027. Im Text steht `HLZF 1 17:15 18:30 … HLZF 1 17:00 19:15`; deine `17:30-18:15` (msns Herbst) und `17:15-19:15` (ns Winter) finde ich so nicht. Bitte Jahr und Werte prüfen.
- **Halberstadtwerke:** Quelle "Nutzer-Tabelle (Webseite)". Bitte die URL angeben (HTML-Quelle), damit sie im Ergebnis steht.
- **Staßfurt, Gaggenau:** keine Zeiten in der Zeile. Wenn das Dokument keine Hochlastzeitfenster nennt, `bemerkung = keine im Dokument, Stelle: …`.

## Für das Tempo
Siehe `eingang/kommunikation/2026-11-12_TEMPO_FUER_KOLLEGE.md` (Entwurfsskript `daten/hlzf_entwurf.py`, Stapel von 10).
