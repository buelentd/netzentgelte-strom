# Stichprobe „nicht vorhanden“ (Lieferung Kollege Etappe 1–4), 11.11.2026

Grundlage: 145 Netzbetreiber ohne 2026-Werte in der Lieferung (Branch `vibe/hlzf-etappen-1-2-705031`, Commit `7c5d84c`). Gezogen: 14 zufällig (Startwert 11), ohne die mit HTTP 403/404 oder „nur 2027“ in der Bemerkung. Geprüft auf der eigenen Website des Netzbetreibers: Startseite, Links zu Netzentgelte, Veröffentlichungen, Netzzugang und Ähnlichem bis Tiefe 2, höchstens 40 Seiten, robots.txt beachtet, 1 Anfrage je Sekunde. Gelesene Dokumente: `pdftotext -layout`, Bild bei Scan.

## Ergebnis: 14 geprüft

| MaStR-Nr. | Netzbetreiber | Befund | Adresse des Dokuments |
|---|---|---|---|
| SNB972264483465 | Überlandwerk Eppler | **2026-Dokument vorhanden und lesbar, Kollege hatte nichts.** NS: Herbst `17:45-19:30`, Winter `17:00-20:00`; MS/NS: Herbst `17:45-19:30`, Winter `17:15-20:00`; Frühling/Sommer nicht genannt (nicht eingetragen, „keins“ nur wenn das Dokument es sagt). Ebene MS: Winter `15:30-19:15`. | https://www.ueberlandwerk.de/files/ueberlandwerk/source/2025_10_25_Anhang_1_IV_HLZF_2026_Eppler.pdf (Pfad ohne `/strom/stromnetz/`, der relative Link der Seite führt in die Irre) |
| SNB912063565672 | Stadtwerke Fröndenberg Wickede | **Zwei 2026-Dokumente, Kollege kannte nur Mittelspannung.** Niederspannung 2026 liegt separat: Frühling `-`, Sommer `-`, Herbst `17:45-18:30`, Winter `15:00-19:30`. MS/NS nicht ausgewiesen. | https://sfw-ruhr.de/wp-content/uploads/2025/10/Hochlastzeitfenster-Niederspannung-2026.pdf |
| SNB962736090291 | Gemeindewerke Großkrotzenburg | **2026-Dokument vorhanden und lesbar**, aber ohne Trennung nach Ebenen: Frühling/Sommer/Herbst `-`, Winter `12:15-13:45, 17:45-19:45`. Kollege hat nichts eingetragen, weil die Ebene fehlt. Entscheidung offen, ob das für NS und MS/NS gilt. | https://www.gemeindewerke-grosskrotzenburg.de/de/Netze/Stromnetz/Hochlastzeitfenster-fuer-2026.pdf |
| SNB929383206369 | Elektrizitätswerk Simbach | 2026-Dokument vorhanden, Raster mit markierten Viertelstunden, im Text keine Markierung. Nur per Bild lesbar (Kollege hatte das schon so gemeldet). | https://www.e-werk-simbach.de/veroeffentlichungen?file=files/e-werk-simbach/formulare/Ver%C3%B6ffentlichungen/Hochlastzeitfenster/2026%20Hochlastzeitfenster.pdf&cid=2390 |
| SNB983029590205 | Stadtwerke Güstrow | Kollege richtig: Die als „2026“ verlinkte Datei (28.10.2026, Bild) ist laut Kopf **„Hochlastzeitfenster 2027“**. Ein 2026-Dokument habe ich nicht gesehen. | |
| SNB925861098273 | Stadtwerke Uslar | bestätigt: nur ≤ 2025 auf der Seite | |
| SNB919654931526 | Stadtwerke Blankenburg | bestätigt: nur ≤ 2024 | |
| SNB984607096621 | Harz Energie Netz | bestätigt: nur ≤ 2025 | |
| SNB916328839515 | Elektrizitätswerk Dießen | bestätigt: nur 2025 | |
| SNB971007500575 | Stadtwerke Witten | nichts gefunden (18 Seiten) | |
| SNB975680234468 | Stadtwerke Witten Mittelspannung | nichts gefunden (6 Seiten) | |
| SNB947270211210 | SWN Stadtwerke Neustadt | nichts gefunden (34 Seiten) | |
| SNB985701689504 | Stadtwerke Fürstenfeldbruck | nichts gefunden (20 Seiten) | |
| SNB984338214660 | Gemeinde-Elektrizitäts- und Wasserwerk | nichts gefunden (1 Seite, Website kaum erreichbar) | |

**Zusammenfassung:** 3 von 14 haben ein lesbares 2026-Dokument, das fehlt (Eppler, Fröndenberg-Wickede NS, Großkrotzenburg), 1 weiteres liegt als Bild vor (Simbach), 5 sind bestätigt (4 nur ältere Jahre, 1 Datei ist 2027), 5 ohne Fund ohne dass ich ein Dokument ausschließen kann.

**Folgerung:** „kein Dokument gefunden“ ist nicht verlässlich. Bei etwa jedem vierten bis fünften Netzbetreiber der Stichprobe gibt es ein 2026-Dokument. Schätzung für alle 145 nicht möglich (14 sind zu wenig), aber die Liste braucht eine zweite Suche. Nichts davon ist in `lauf/hlzf_kollege_verifiziert.csv` oder in der Tabelle eingetragen.

## Prüfung der gelieferten Werte am Dokumenttext (zum selben Termin)

55 Zeilen mit 2026-Werten gegen die Originale der ZIP-Dateien: bei 40 stehen alle Uhrzeiten im Dokumenttext. 15 nicht (Scan, Bild oder kein Text): Elektrizitätsgenossenschaft, EW Schweiger, Cottbus (EVC), Peine, Stade, Zweibrücken (teils), Borna (teils), VSE, Werraenergie, enercity Netz und GridPartner, Tegernsee, Wittenberg, VersorgungsBetriebe Elbe, Verden. Das prüft nur, ob die Zeiten im Dokument stehen, nicht, ob Jahreszeit und Ebene stimmen. Stade zeigt, dass das allein nicht reicht.

## Nachtrag: Suche über alle übrigen 143 Netzbetreiber ohne 2026-Werte

Gleicher Crawler (nur lesend, robots.txt, 1 Anfrage/s, höchstens 40 Seiten). Ergebnis je Netzbetreiber: `2026-11-11_SUCHE_145_ERGEBNIS.csv` (MaStR-Nr. zuerst). Klassen: 2026-Kandidat 30, nur ältere Jahre 22, nur 2027 2, nichts gefunden 54, Seite nicht abrufbar 35 (davon viele HTTP 403: Westnetz, Syna, E.DIS, NordNetz, Olching, Weilheim, Putzbrunn und andere). Nichts davon ist in Tabelle oder Overlay eingetragen. „Kandidat“ heißt: Link oder Text nennt 2026 und das Dokument enthält 2026; Jahr, Ebene und Jahreszeit sind noch nicht gelesen.
