# Offene Punkte nach dem Arbeitstag 12.11.2026

Zahlen aus den Dateien, Stand nach der letzten Übernahme (Commit auf `main`).

## 1. Hochlastzeitfenster: 199 von 831 offen (632 fertig)
| Status | Anzahl | Wer | Aktion |
|---|---:|---|---|
| Kein Dokument gefunden | 88 | Kollege + Nutzer | suchen (Auftrag 7 `suchen`, 132 Fälle inkl. Teile von unten) |
| Dokument da, nicht lesbar | 80 | Kollege | am Dokument ablesen (Auftrag 7 `ablesen`) |
| Raster-Grafik | 8 | Kollege | Markierung am Bild lesen |
| Falsches Jahr | 6 | Kollege | neues Dokument suchen |
| Gelesen, nicht bestätigt (Maschine 6, Kollege 5) | 11 | Claude/Kollege | gegenprüfen, Beleg nachliefern |
| "keine im Dokument" | 4 | Kollege | Stelle belegen |
| Zurückgehalten (unplausibel) | 2 | Nutzer | Dokumente Gemünden, Fröndenberg-Wickede, Töging im Browser holen (Töging und Gemünden/Fröndenberg liegen nicht vor) |
**Aus der letzten Lieferung des Kollegen nicht übernommen (14 + 6):** Selb, Heikendorf, Waldbüttelbrunn, werkkraft, Bielefelder (Zeiten nicht im PDF-Text); Bad Hersfeld, Angermünde, Halberstadt, Springe, BIGGE (Datei fehlt im Repo); Senftenberg, Herten, Fürstenfeldbruck (Bild); Cottbus (4 von 8). 43 Zeilen ohne Zeiten ("nur MS", "separat veröffentlicht"): Dokument muss gesucht werden. Details: `lauf/hlzf_lieferung_zurueck.csv`.

## 2. Modul 3 (§ 14a): 541 von 831 ohne Zeiten, 50 von 231 gelesenen ohne alle drei Preise
- 426 mit Uhrzeiten im Preisblatt, aber Zuordnung zu HT/ST/NT nicht eindeutig: **Kollege liest** (Auftrag 5, `modul3_offen_kollege.csv`).
- Gut 110 ohne Uhrzeit im Preisblatt: Dokument suchen oder "nicht ausgewiesen" belegen.
- Preise HT/ST/NT: 181 von 231 vollständig; Rest nachlesen.
- Modul 3 für 2027: noch nicht erfasst.

## 3. Preise 2027
- **571 Netzbetreiber ohne Preisblatt** (rund 67 % der Einwohner): **Nutzer im Browser**, Liste `ergebnis/browser_preise_2027_571.csv`, von oben (Westnetz, Berlin, EWE, MITNETZ, E.DIS …). Auftrag 8.
- 62 "teilweise gelesen", 4 "prüfen", 50 nur Quelle: **Claude** klärt, sobald die Blätter da sind.
- 21 Werte mit über 40 % Abweichung zum Vorjahr: Belegprüfung am Dokument, **Claude**.
- 92 manuell zu prüfende Fälle (403/robots/nicht erreichbar) aus dem Crawler: `BLOCKIERT_MANUELL_PRUEFEN.csv` in der Kommunikation, **Nutzer**.
- Ungeordnete Uploads in `dl_up/sonst/` (beim Kollegen): zuordnen.

## 4. Entscheidungen, die bei dir liegen
| Entscheidung | Wirkung |
|---|---|
| Zeitstempel = Ende der Messperiode (Rostock, Aalen, ODR, Düsseldorf): 15 Minuten nach vorn schieben? | Hochlastzeitfenster-Zeitreihe |
| Repo öffentlich oder nur Partner | REST-API, Daten |
| Hosting und Schlüsselkonzept der REST-API | Angebot der API |
| Rechte an Marktdaten (Day-Ahead, Regelenergie) | Datenpaket |

## 5. Conplot
- Importformat für 2026 steht (`data_quellen/netzentgelte_2026/`, mit deren Skript getestet). **Noch offen:** Conplot übernimmt den Ordner und führt den Import aus.
- Nicht im Importer: Modul 3, Preise 2027, Konzessionsabgabe je PLZ. Dafür braucht Conplot einen eigenen Importschritt (Dateien liegen in `ergebnis/conplot/`).
- Fehler in der **bisherigen** App-Datei: Hochlastzeitfenster-Quellen zeigen auf andere Netzbetreiber (Berlin, Avacon, EWE, Bayernwerk, SH Netz, Stuttgart Netze, Syna, MVV, Hamburg), dazu Zeiten wie "09:00-08:77". Conplot sollte die Datei ersetzen. Nachtfenster (19:45-02:00) werden in `_fenster` abgeschnitten.
- Zeitumstellung: Fenster sind Ortszeit, die Preisreihe von Conplot läuft in MEZ.

## 6. Eigene Aufgaben (Claude)
- Lieferungen des Kollegen prüfen: `PYTHONPATH=. python daten/hlzf_lieferung_uebernehmen.py`, danach `bash daten/hlzf_kette.sh`, Tests, Export. Montag und Donnerstag.
- Leser ausbauen für die 80 "nicht lesbar"-Layouts und die Quartals-/Ja-Nein-Tabellen bei Modul 3 (kein Ersatz für das Ablesen, nur Beschleunigung).
- **Test:** ein Test ist bei langsamem Lauf (über 60 s) zweimal rot gewesen und bei Wiederholung grün. Ursache nicht geklärt; ich pushe künftig nur bei grünem Lauf.
- Mein Crawler `vnb/hlzf_crawl.py`: Lauf auf der Restliste hing, Ursache offen. Der Kollege führt ihn seit heute.
- Messentgelt bei Leistungsmessung und § 14a Modul 2/3 im Rechner sind nicht gebaut.

## 7. Nicht unser Teil (damit es klar ist)
Day-Ahead, Regelenergie, PV (PVGIS), NACE, Förderdaten, Brandschutz: liegen bei Conplot.
