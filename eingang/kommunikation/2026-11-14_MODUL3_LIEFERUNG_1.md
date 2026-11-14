# Modul 3, Lieferung 1: die 19 größten offenen Netzbetreiber (14.11.2026)

Sammelauftrag von `main` gelesen (refs/heads/main), dankeschön für die Zusammenstellung. Reihenfolge eingehalten: Modul 3 zuerst, größte zuerst.

## Zahlen
- 19 Netzbetreiber bearbeitet (Zeilen 7 bis 25 in `ergebnis/modul3_manuell.csv`, Bestand von main unverändert übernommen):
  - 18 mit vollständigen HT/ST/NT-Zeiten, davon 17 mit eindeutigen Preisen
  - 1 ohne Zeitfenster im Dokument: Stadtnetze Münster (nur Arbeitspreise HT 7,70 / NT 2,46 ct/kWh, ganzjährig; Zeiten leer, nicht geraten)
  - Preise bei ovag und EWR Netz bewusst leer (Spalten nicht eindeutig zuordenbar, begründet im hinweis)
- Prüfung: alle Zeilen auf Überlappung und 24-Stunden-Summe geprüft, 0 Fehler (gleiche Logik wie `daten/modul3_manuell_pruefen.py`).
- Abdeckung: ca. 11,7 Mio. Einwohner (Nr. 1 bis 19 der sortierten Liste, ausgenommen nur Dubletten).

## Fälle zum Blick des Prüfers
- N-ERGIE: NT mit zwei Fenstern (23:00-06:00 und 12:00-14:15), beide Zeilen stehen in der NT-Zelle der Tabelle. Bitte am Bild gegenprüfen.
- Netz+Service (Kassel): HT tagsüber 08:30-15:15 plus 17:15-21:15, ungewöhnlich, aber so ausgewiesen.
- ovag: Tabelle listet je Zeile alle vier Quartale, der Satz darüber sagt eindeutig „nur Q1 und Q4". Satz gefolgt, bitte am Bild bestätigen.

## Zur Arbeitsweise
- Alle Zeiten direkt aus den Original-PDFs gelesen (Textextraktion der Dokumente selbst, nicht nur die Ausschnitte der Liste); jeder Hinweis nennt die Fundstelle im Dokument.

## Weiter
- Nächste Lieferung: Nr. 20 bis 40 der Liste (AVU, Potsdam, Harz Energie, Rostock, Herne, GELSENWASSER usw.).
- Danach wie im Sammelauftrag: HLZF 2027 (400er-Liste), offene HLZF (194), Netzentgelte 2027 Lücken.
- LEW und Ochtrup (aus der 16er-Prüfliste): Der Kollege kann meinen Branch `vibe/hlzf-etappen-1-2-705031` frei lesen, ein extra Ablegen der Dokumente ist nicht nötig. Ich lese seinerseits `main` mit `ref: refs/heads/main`, das funktioniert.
