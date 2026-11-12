# Anleitung: Modul 3 (HT/ST/NT) für die offenen Netzbetreiber lesen

Ziel: zu jedem Netzbetreiber in `ergebnis/modul3_offen_kollege.csv` die Zeiten für Hochtarif (HT), Standardtarif (ST) und Niedertarif (NT) ablesen. Das sind die § 14a-Zeiten (Modul 3), nicht die Hochlastzeitfenster nach § 19.

## 1. Vorbereiten
```bash
git pull origin main
```
Arbeitsliste: `ergebnis/modul3_offen_kollege.csv` (MaStR-Nr. zuerst, Name, Quelle, Textausschnitt). Schon erledigte stehen in `ergebnis/modul3_manuell.csv`; diese überspringen.

## 2. Einen Fall ansehen
Kompakte Ausschnitte der offenen Fälle, 12 auf einmal:
```bash
PYTHONPATH=. python daten/modul3_batch.py 0 12
```
(nächster Stapel: `12 24` usw.). Das Skript zeigt nur die Textzeilen um die Uhrzeiten. Das ist eine Hilfe, nicht die Quelle.

Danach **immer das Dokument selbst ansehen**: Die Adresse steht in `quelle_url` der Liste, die PDFs liegen auch unter `ergebnis/pdf/` und `eingang/pdfs_neu/`. Der Text ist oft verschoben, das Bild zeigt, welche Zeit in welche Zelle gehört.

## 3. Was ablesen
Je Netzbetreiber, in der Niederspannung ohne Leistungsmessung:
- **HT-, ST-, NT-Zeiten** (Uhrzeit von–bis, 24-Stunden-Schreibweise, `24:00` als Ende ist erlaubt).
- **Quartale**, in denen Modul 3 gilt (Ja/Nein-Tabelle oder Satz wie „nur in Q1 und Q4“). Gelten in verschiedenen Quartalen verschiedene Zeiten, je Gruppe eine Angabe.
- **Preise** für HT/ST/NT in ct/kWh netto, nur wenn eindeutig zugeordnet.

## 4. Die häufigsten Fehler (aus dem Maschinenleser gelernt)
1. **Zeiten über oder unter dem Tarifnamen.** Die Zelle ist mittig ausgerichtet; eine Zeit vor dem Namen kann zum Namen darunter gehören. Am Bild entscheiden.
2. **Mehrere Zeitfenster pro Tarif** (z. B. ST 06:00–17:00 und 21:00–24:00). Alle eintragen.
3. **Spaltenreihenfolge** steht in der Kopfzeile und ist je Dokument anders (NT-ST-HT oder ST-HT-NT). Nicht annehmen.
4. **Quartale aus dem Datum, nicht aus dem Jahr.** „Q1/2026 und Q4/2026“ heißt Q1 und Q4. „alle 4 Quartale“ heißt ganzjährig.
5. **Gilt nur werktags oder Mo–Fr:** nicht eintragen, im `hinweis` vermerken (die Zeitreihe braucht ganzjährig, jeden Tag).
6. **„Rest“, „alle übrigen Zeiten“, „übriger Zeitraum“** ist ST: als `Restzeit` eintragen.
7. **Ein Quartal ohne Tarifstufen** („keine Gültigkeit gesonderter Tarifstufen“, „0–24 Uhr“): in dem Quartal gilt nur ST, als `Q2+Q3: keins` bei HT/NT eintragen.
8. **Grundpreis und Arbeitspreis nicht verwechseln.** Bei „Modul 1 + 3“ steht der Grundpreis (€/a) vor dem Arbeitspreis (ct/kWh). Der Arbeitspreis liegt meist zwischen 0,5 und 25.

## 5. Eintragen
In `ergebnis/modul3_manuell.csv` (gleiche Spalten wie `modul3_zeiten.csv`, Trennzeichen `;`, Dezimalkomma). Eine Zeile je Netzbetreiber, **MaStR-Nr. zuerst**.

| Spalte | Beispiel |
|---|---|
| ht_zeiten | `17:00-19:00` oder `11:00-13:00, 17:00-19:00` |
| st_zeiten | `Restzeit` oder `06:00-17:00, 21:00-24:00` |
| nt_zeiten | `00:00-06:00` |
| quartale | `ganzjährig` oder `Q1+Q4` |
| ht/st/nt_ct_kwh | `9,44` / `7,13` / `1,43` (leer, wenn nicht eindeutig) |
| hinweis | beginnt mit `gelesen_kollege:` und nennt Besonderheiten |

Wechseln die Zeiten je Quartalsgruppe: `ht_zeiten` = `Q1+Q4: 16:30-20:00; Q2+Q3: keins`, ebenso ST und NT, `quartale` = `Q1+Q4; Q2+Q3`.

## 6. Prüfen, bevor du lieferst
```bash
PYTHONPATH=. python daten/modul3_manuell_pruefen.py
```
Das Skript meldet jede Zeile, bei der sich HT, ST und NT überlappen oder nicht genau 24 Stunden ergeben. **Dann erst committen.** Zusätzlich jede Zeile rückwärts prüfen: Zu jeder Zeit in deiner Zeile die Stelle im Dokument zeigen können, und zu jeder Zeit im Dokument die Stelle in deiner Zeile.

## 7. Liefern
```bash
git add ergebnis/modul3_manuell.csv && git commit -m "Modul 3: <n> Netzbetreiber gelesen" && git pull --rebase origin main && git push
```
Auf den Branch `vibe/…` wie bei den Hochlastzeitfenstern. Danach lege eine kurze Meldung in `eingang/kommunikation/` ab: Anzahl gelesen, Anzahl unklar (mit Grund).

## 8. Unklar
**Unklar heißt leer lassen und begründen.** Zeile mit leeren Zeiten und dem Grund im `hinweis`. Nichts raten. Fehlt das Dokument ganz (kein Preisblatt oder Modul 3 nicht aufgeführt), in `hinweis`: „Modul 3 im Dokument nicht ausgewiesen“.
