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

## Nachtrag 2: Einlesen der Funde und Kettenlauf (Claude, 11.11.2026)

Von den 15 Netzbetreibern mit lesbarem 2026-Dokument kam nur Städtische Betriebswerke Luckenwalde (SNB943531720705) durch den Leser samt Sicherungsprüfung (neu: gelesen_unser). Texte 2026 für Traunstein, Iserlohn und Heiligenhaus und Quedlinburg liegen in `ergebnis/hlzf_texte/`, der Leser liest Traunstein und Iserlohn, die Sicherungsprüfung lässt sie nicht durch (Zuordnung der Zeilen zu den Ebenen nicht gesichert). **Raster mit Viertelstunden, Markierung nicht im Text** (Bild nötig): Ansbach SNB937406641264, Meerane SNB918070278383, Reichenbach SNB959567240391, Hockenheim SNB967127819703, SWM Infrastruktur SNB969473762610, Landshut SNB928992067729, Marburg SNB972740218178. Noch zu lesen: EVE Netz SNB985172238775, Neuendettelsau SNB984571613121, Selb (NS und Umspannung) SNB911696239035, Quedlinburg SNB970223838288 (Tabelle mit Spalten je Ebene), Heiligenhaus SNB968694358282 (Tabelle je Ebene mit vier von/bis-Paaren), dazu Traunstein SNB940718804685 und Iserlohn SNB913730249284 mit Zuordnung prüfen.
Gegenprobe Kettenlauf (Tabelle vor/nach): neu 1, verloren 0, geändert 0, Preisspalten unverändert, verwertbar 648 von 831.

## Nachtrag 3: Von Hand am Dokumenttext gelesen und ins Overlay (Claude, 11.11.2026, Festlegung Nutzer: Werte rein, Annahmen dokumentieren)
Status `gelesen_kollege_verifiziert`, Bild nicht geprüft:
- Traunstein SNB940718804685 (2026-Dokument): NS Frühling `17:00-20:00`, Winter `17:00-20:00`; MS/NS Herbst `09:30-12:30`, Winter `07:00-11:00`.
- Iserlohn SNB913730249284: NS Winter `16:00-19:00`; MS/NS Frühling `07:30-11:30`, Herbst `07:45-12:00`, Winter `08:00-12:00`.
- Quedlinburg SNB970223838288: NS Winter `11:00-11:15, 11:45-12:00`; MS/NS Frühling `11:30-11:45, 13:00-13:30, 14:15-14:30, 15:15-15:45`. Spalten je Ebene nach Position im Textauszug.
- **Annahme Eppler SNB972264483465:** Frühling und Sommer im Dokument nicht genannt, als `keins` eingetragen (Festlegung Nutzer „Werte rein“). Schwelle 30 % und 100 kW laut Dokument.
- **Annahme Großkrotzenburg SNB962736090291:** Das Dokument unterscheidet nicht nach Ebenen, das Winterfenster `12:15-13:45, 17:45-19:45` gilt hier für NS und MS/NS.
- Mittelrhein SNB980055629275: Die alte Tabellenzeile (16:45-19:45, 17:00-19:45, Herbst 17:00-19:00) hatte die Quelladresse von E-Werk Sachsenwald, also eine vertauschte Zeile der Nutzerliste. Auf die Werte des Dokuments umgestellt. **Dasselbe Muster (gleiche Quelladresse bei zwei Netzbetreibern) gibt es bei weiteren Paaren, z. B. Hamburg/E-Werk Netze, e-netz Südhessen/ASCANETZ, Düsseldorf/Gundelfingen; Prüfung steht aus.**
- Heiligenhaus SNB968694358282: Tabelle im Text, aber die Zeile für NSP liegt in der Frühlingszeile und nicht in Winter: braucht das Bild.

## Nachtrag 4: Fehler in der Zuordnung der Nutzerliste behoben (Claude, 11.11.2026) — WICHTIG
**Befund:** `daten/hlzf_zusammenfuehren.py` ordnete die Zeilen der Nutzerliste (`ergebnis/FORMAT_NEU_netzentgelte_final_alle_3_ergaenzt.csv`) über die Spalte `nr` zu. Die Nutzerliste hat eine eigene, alphabetische Nummerierung (473 Zeilen, nr 1 = Abita, nr 26 = e-werk Sachsenwald), unsere Tabelle eine andere (nr 1 = Stromnetz Berlin, nr 26 = Energienetze Mittelrhein). Dadurch standen die Hochlastzeitfenster von rund 120 Netzbetreibern beim falschen Netzbetreiber. Erkannt an der Quelladresse: bei 182 von 185 Zeilen „gelesen_nutzer“ gehörte die Adresse einem anderen Netzbetreiber, bei 45 Paaren waren die Werte sogar identisch.
**Behebung:** Zuordnung über MaStR-Nr., sonst über den normalisierten Namen (172 Namen eindeutig, 13 MaStR-Nr., Rest 0). Danach passt bei 73 von 87 verbleibenden Nutzerzeilen die Adresse zur Website (vorher 3 von 185).
**Zweiter Befund:** Wo Nutzerliste und unser Leser beide das 2026-Dokument gelesen haben und verschieden lesen (96 Fälle, Liste `ergebnis/hlzf_konflikt_nutzerliste_leser.csv`), gilt jetzt unser Leser: Stichprobe am Dokumenttext: Abita (Dokument = unser Leser, Nutzerliste anders), Regionetz (Nutzerliste „01:06-03:00“ ist offenbar ein Datum). Regel „Nutzer gewinnt“ nur noch, wo unser Leser nichts oder nichts Sicheres gelesen hat.
**Folge:** verwertbare Hochlastzeitfenster 653 → 540 (die vorher falsch zugeordneten sind jetzt leer). Das Partnerpaket vom 10.11. enthält die falsch zugeordneten Fenster und muss ersetzt werden.
**Eigener Fehler:** Ich hatte beim Mittelrhein die Nutzerliste in der Zeile `nr 26` geändert; das war e-werk Sachsenwald. Wiederhergestellt, Mittelrhein steht jetzt über `daten/hlzf_handlesung.py`.
