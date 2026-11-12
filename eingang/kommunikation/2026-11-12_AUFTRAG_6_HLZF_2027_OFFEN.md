# Auftrag 6: 91 offene HLZF-2027-Dokumente ablesen

Liste: `eingang/kommunikation/AUFTRAG_6_hlzf_2027_offen.csv` (MaStR-Nr. zuerst, Dateiname, Grund, warum der Maschinenleser sie nicht las). Die Dokumente liegen in `eingang/2027_vorlaeufig/` (`SNB…_hlzf_2027.pdf`).

Was lesen: § 19 Abs. 2 StromNEV (Hochlastzeitfenster), je Ebene NS und MS/NS, je Jahreszeit (Frühling, Sommer, Herbst, Winter). Nicht Modul 3.

Regeln (wie Rückmeldung Etappe 1/2):
1. Text und Bild vergleichen, bei jeder Zeile.
2. Spaltenreihenfolge pro Dokument aus der Kopfzeile, nicht annehmen.
3. Jede Ebene hat ihren eigenen Block; nur NS und MS/NS übernehmen.
4. Alle Fenster einer Zelle eintragen.
5. `keins` nur bei "entfällt" oder "-" im Dokument; eine leere Zelle heißt "nicht gelesen".
6. Raster mit markierten Viertelstunden (Grund in der Liste): Markierung am Bild ablesen, Zeiten als von–bis.
7. Mehrere Netzgebiete in einem Dokument: je Gebiet eine Zeile, Gebiet im `bemerkung`.
8. Unklar: Zelle leer lassen, im `bemerkung` begründen.
9. Jede Zeile rückwärts prüfen (jede Zeit in deiner Zeile am Dokument zeigen, jede Zeit im Dokument bei NS/MS/NS in deiner Zeile).

Ausgabe: `ergebnis/hlzf/hlzf_2027_offen_gelesen.csv` auf deinem Branch, Spalten wie `lauf/hlzf_kollege_verifiziert.csv` (mastr_nr zuerst, hlzf_ns_… , hlzf_msns_…, hlzf_schwelle_prozent, hlzf_mindestleistung_kw, hlzf_quelle_url, hlzf_status = `gelesen_aus_2027`) plus Spalte `bemerkung`. Danach kurze Meldung in `eingang/kommunikation/`: Anzahl gelesen, Anzahl unklar mit Grund.
