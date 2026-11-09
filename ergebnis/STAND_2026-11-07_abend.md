# Stand Abend 07.11.2026 und Plan für morgen

## 1. Datenstand (`ergebnis/netzentgelte_2026.csv`, 831 Netzbetreiber)
- ok 596, pruefen 216, blockiert 13, robots 4, keine_website 1, kein_preisblatt 1.
- „ok“ ist streng: Mittelspannung, MS/NS, Niederspannung und SLP vorhanden und je Wert am Dokument mit Zeile und Beschriftung belegt (Beleg-Leser).
- 190 Tests laufen durch. Testseite (Artifact, Version 28) ist veröffentlicht, Hinweis „Werte in Prüfung“.

## 2. Heute erledigt
- Beleg-Leser (`daten/beleg_leser.py`): Zeilenbeleg je Wert, Netto/Brutto, Tagespreise, BDEW-Artikel-IDs, doppelte Werte als Konflikt.
- Gegenprobe am frischen Original (60 Netzbetreiber): 2 von 57 hatten versteckte Fehler (Mittelrhein 26, Hauenstein 142), korrigiert.
- Blinde Gegenprobe 200 (Kollege liest ohne unsere Werte): Ergebnis in `ergebnis/GEGENPROBE_200_ERGEBNIS.md`. 2.620 von 2.800 Feldern gleich. Fünf eigene Fehler gefunden und korrigiert: 421, 433, 675, 781, 805. 13 Abweichungen waren Fehler des Kollegen.
- Arbeitsanweisung an den Kollegen (`KOLLEGE_GEGENPROBE_200_auftrag.md`) mit den Regeln: nur Originale, kein Browser-Kennzeichner, Zertifikatsprüfung an, Jina nur als Lesehilfe.
- Netz ist offen (Umgebung „googlestitch“). Bayernwerk und ähnliche Seiten bleiben wegen Cloudflare unzugänglich, auch über Jina.

## 3. Fehlerquote (Orientierung)
Zwei unabhängige Stichproben ergeben rund 2,5 bis 3 % Netzbetreiber mit einem echten Fehler unter „ok“. Das ist eine Untergrenze. Typische Fehler: Brutto statt Netto, falsche Zeile (Ermäßigung, Modul 2, Nachtspeicher), Grundpreis und Arbeitspreis vertauscht.

## 4. Offen für morgen (Reihenfolge)
1. **9 Netzbetreiber, die nur ein Leser sah:** 33 Syna (gesperrt), 90 EGT (Spaltenzuordnung unklar), 140 Calw (MS nicht ausgewiesen), 393 Bad Dürkheim (SLP-Grundpreis), 499 Grevesmühlen, 564 Marburg, 656 Senftenberg, 700 Völklingen (Zonenpreissystem), 704 Waldkirchen (Bild-Scan). Am Original selbst prüfen.
2. **310 MEGA Monheim:** Quelladresse zeigt auf das 2027er vorläufige Blatt. Auf das 2026er Blatt ersetzen.
3. **Gegenprobe 200 weiter auswerten:** 8 Felder beide leer, Fälle mit „ungeprüft“ (6, 816, 578, 610, 722) am Original öffnen.
4. **Belegliste:** `lauf/beleg_offen.csv` (72 Netzbetreiber) und `lauf/beleg_verdacht.csv` (20): NRM 37, badenova 62, Mainsite 306, Schwerin 331, EWE 5, Bayernwerk 30, Syna 788, EWR 193, Waldkraiburg 705, Neumarkt 582, Trostberg 684 (SLP), 299/277/263 (SLP).
5. **Kleine Betreiber ohne Mittelspannung (ca. 660 „nicht ausgewiesen“):** Stichprobe von 30 gegen das Dokument.
6. **Hochspannung direkt** (Bayernwerk, Westnetz, EWE, TEN): Entscheidung nötig, ob als eigene Ebene geführt wird.

## 5. Entscheidungen, die beim Nutzer liegen
- Definition von „ok“: streng 596; „alle Ebenen, die das Dokument ausweist“ ungefähr 720.
- Hochspannung als eigene Ebene.
- Jina als Lesehilfe: bisher nur als Hinweis, kein Beleg.
- Alles Rechtliche, Geschäftliche, Außenwirkung.

## 6. 2027 (vorläufig), noch nicht gestartet, wartet auf Ja
- Eigener Datensatz `ergebnis/netzentgelte_2027.csv` im gleichen Format mit `preisstand` und `stand_datum`, gleiche Belegregeln.
- Delta-Tabelle 2026 nach 2027 (€/kW, ct/kWh, Beispielbetriebe), Jahresumschalter im Rechner mit Kennzeichnung „vorläufig“.
- Der Kollege sammelt nur die 2027-PDFs (`<nr>_preis_<Original>.pdf`) ohne Auswertung.
- Aktualisierung Mitte Dezember und im Januar.

## 7. Rechner und Testseite
- Auf 3 Stufen vereinfachen: Kern Netzentgelt, Spitzenkappung, Modell PV/Speicher/dynamisch (eingeklappt). Tooltips mit Quelle und Beleg je Zahl.
- Börsenniveau als vierte Option „Terminkurve“, Stromsteuer produzierendes Gewerbe (unbelegt, prüfen), Smart-Meter-Kosten, PV-Preisstaffel, Hinweis Speicher und Netzentgeltbefreiung.

## 8. Weitere offene Punkte
- 29 Browser-Downloads des Nutzers (`ergebnis/BROWSER_DOWNLOADS_33.md`), 14 offene Schlüssel (`schluessel_offen.csv`).
- GitHub Actions am 05.11. fehlgeschlagen, Ursache ungeprüft (tägliche Börsenpreise brauchen es).
- Kollege Runde 3: 18 Fälle, davon 7 „nicht veröffentlicht“ nicht gegengeprüft.
- Robots-Fälle 238/451 (Links), 352/644 (Startseite gesperrt).
- Strompreisliste für 100 Netzgebiete (`KOLLEGE_STROMPREISE.md`) und Preisermittlung (`KOLLEGE_PREISERMITTLUNG.md`): nicht übernommen, Quellen ungeprüft.
- Behauptungen des Kollegen zu § 14a und Rabot/Tibber/1Komma5° sind nicht am Original belegt.

## 9. Regeln, die gelten
- Nichts schätzen, leer lassen und in die Restliste.
- Geprüft heißt: Zeile und Beschriftung am Dokument.
- Dateien ohne Netzbetreibernamen nur, wenn die Quelle die eigene Website des Netzbetreibers ist.
- Kein Umgehen von robots.txt oder Bot-Schutz (Ausnahme: 5 vom Nutzer freigegebene Einzel-PDFs).
- Keine Zuschreibung von Arbeit an den Nutzer.
