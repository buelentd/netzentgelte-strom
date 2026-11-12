# Anleitung: Hochlastzeitfenster für die 253 offenen Netzbetreiber (Auftrag 7)

Ziel: für jeden Netzbetreiber in `ergebnis/kollege_hlzf_253.csv` die Hochlastzeitfenster nach § 19 Abs. 2 StromNEV ablesen (Ebenen NS und MS/NS, je Jahreszeit). **Nicht** Modul 3 (§ 14a), das ist ein eigener Auftrag.

**Jahr:** 2026 oder 2027, beides ist gut. Fehlt 2026, nimm 2027 (und umgekehrt). Was zuerst gefunden wird, reicht. Ein 2027-Dokument zählt für 2026 und 2027.

## 1. Vorbereiten
```bash
git pull origin main
```
Liste: `ergebnis/kollege_hlzf_253.csv`, MaStR-Nr. zuerst, sortiert nach Aktion:

| Aktion | Anzahl | Bedeutung |
|---|---:|---|
| ablesen | 116 | Datei liegt im Repo (Spalte `dateien_im_repo`), unser Leser konnte sie nicht lesen. |
| prüfen | 5 | Das Dokument sagt "keine Hochlastzeitfenster". Bestätigen oder Gegenbeleg. |
| suchen | 132 | Noch kein Dokument. Suchen. |

Reihenfolge: erst `ablesen`, dann `prüfen`, dann `suchen`.

## 2. Aktion "ablesen"
1. Datei aus `dateien_im_repo` öffnen (Text und Bild).
2. In der Kopfzeile nachsehen, **welche Spalte welche Jahreszeit ist**. Die Reihenfolge ist je Dokument anders (Winter zuerst, Frühling zuerst …).
3. Zu jedem Ebenennamen den eigenen Block lesen. Die Zeiten über oder unter dem Ebenennamen gehören nur dann zum Block, wenn das Bild es zeigt.
4. **Alle** Fenster einer Zelle eintragen (zweite und dritte Zeile nicht vergessen).
5. Eintrag in die Ausgabedatei (siehe 5).

## 3. Aktion "prüfen"
Im Dokument die Stelle suchen, die sagt, es gebe keine Hochlastzeitfenster. Stelle in `bemerkung` nennen (Seite, Satz) und `quelle_url` füllen. Findest du dennoch Fenster (z. B. auf einer anderen Seite), trag sie ein.

## 4. Aktion "suchen"
1. Suchlinks aus der Liste öffnen (`suche_hlzf_2027`, `suche_hlzf_variante`). Sie suchen nach dem **Namen** des Netzbetreibers, nicht nach der Domain, weil die Domain im Marktstammdatenregister oft falsch ist.
2. Dann die Website selbst: Startseite, Netzentgelte, Netznutzung, Veröffentlichungen, Preisblätter, Netzzugang. Auch **HTML-Seiten**, nicht nur PDF und Excel. Portale: GIPS, enwg-veroeffentlichungen.de. Das Dokument kann "Regelungen zur Netznutzung" oder "Hochlast-/Niederlastzeiten" heißen und kann im Preisblatt stehen.
3. Gefunden: Datei als `SNB…_hlzf_<Jahr>.pdf` in `eingang/2027_vorlaeufig/` (2027) oder `eingang/pdfs_neu/` (2026) ablegen und ablesen wie in 2.
4. Nach vollständiger Suche nichts gefunden: Zeile mit leeren Zeiten und `bemerkung = nicht_gefunden: <geprüfte Adressen>`.
5. Gesperrt (403, robots.txt, Cloudflare): **nicht umgehen**. Zeile mit `bemerkung = blockiert: <Adresse>`, das holt der Nutzer im Browser.

## 5. Ausgabe
Datei `ergebnis/hlzf/hlzf_auftrag7_gelesen.csv`, Spalten (`;` getrennt, **mastr_nr zuerst**):

`mastr_nr;nr;netzbetreiber;jahr;ns_fruehling;ns_sommer;ns_herbst;ns_winter;msns_fruehling;msns_sommer;msns_herbst;msns_winter;schwelle_prozent;mindestleistung_kw;quelle_url;quelle_art;bemerkung`

- Zeiten: `17:00-19:30` oder bei mehreren `09:00-11:45, 17:30-19:30`.
- `keins` **nur**, wenn das Dokument für diese Jahreszeit "entfällt", "-" oder "keine" zeigt.
- Eine Ebene steht **nicht** im Dokument: Felder dieser Ebene **leer** lassen (nicht `keins`) und in `bemerkung` schreiben "MS/NS nicht ausgewiesen" (oder NS).
- **Mittelspannung (MS) ist nicht MS/NS.** MS-Zeilen nicht unter msns eintragen. Nur "Umspannung MS/NS" gehört nach `msns`.
- `jahr`: das Jahr aus dem Dokument. `quelle_art`: `PDF`, `HTML`, `Excel`.
- Schwelle (z. B. 30 %) und Mindestleistung (z. B. 100 kW), wenn im Dokument genannt, sonst leer.
- Mehrere Netzgebiete in einem Dokument: je Gebiet eine Zeile, Gebiet in `bemerkung`.

## 6. Die häufigsten Fehler
1. Spaltenreihenfolge angenommen statt aus der Kopfzeile gelesen.
2. Nur die erste Zeile einer Zelle eingetragen.
3. Zeit über dem Ebenennamen dem falschen Block zugeordnet.
4. `keins` für "nicht gelesen" benutzt. Leer heißt nicht gelesen, `keins` heißt "Dokument sagt entfällt".
5. MS-Zeilen unter MS/NS eingetragen (Selb-Marktredwitz).
6. Eine Jahreszeit mit anderem Text ("Winter 2026/27") nicht als Winter gelesen.

## 7. Prüfen, bevor du lieferst
```bash
PYTHONPATH=. python daten/hlzf_lieferung_pruefen.py ergebnis/hlzf/hlzf_auftrag7_gelesen.csv
```
Das Skript meldet falsche Formate, unplausible Zeiten (außerhalb 5:00–23:59, länger als 11 Stunden), unbekannte MaStR-Nr. und leere Zeilen ohne Bemerkung. Dann jede Zeile **rückwärts** prüfen: zu jeder Zeit in deiner Zeile die Stelle im Dokument zeigen können, und zu jeder Zeit im Dokument bei NS oder MS/NS die Stelle in deiner Zeile.

## 8. Liefern
```bash
git add ergebnis/hlzf/hlzf_auftrag7_gelesen.csv eingang/ && git commit -m "HLZF Auftrag 7: <n> gelesen, <m> nicht gefunden" && git pull --rebase origin main && git push
```
Stapelweise liefern (z. B. je 20 Netzbetreiber), nicht am Ende alles auf einmal. Danach eine kurze Meldung in `eingang/kommunikation/`: gelesen, nicht gefunden, blockiert, unklar (mit Grund). Claude prüft Stichproben am Dokumenttext und nimmt die Zeilen nach `main`.

## 9. Unklar
**Unklar heißt leer lassen und im `bemerkung` begründen.** Nichts raten.
