# Modul 3 (§ 14a): so bekommst du die 425 offenen Netzbetreiber hin

Liste: **`ergebnis/modul3_offen_kollege_sortiert.csv`** (425 Netzbetreiber mit Uhrzeiten im Preisblatt, MaStR-Nr. zuerst, nach Einwohnern sortiert, die großen zuerst). Schon gelesen sind 231 (`ergebnis/modul3_zeiten.csv`); die 6 von Hand gelesenen stehen in `ergebnis/modul3_manuell.csv` und bleiben.
Modul 3 ist **nicht** das Hochlastzeitfenster nach § 19. Beides getrennt halten.

## 1. Was Modul 3 ist (damit du weißt, wonach du suchst)
Im Preisblatt steht ein Abschnitt "Modul 3" / "zeitvariable Netzentgelte" für steuerbare Verbrauchseinrichtungen (Wärmepumpe, Wallbox, Speicher) ohne Leistungsmessung. Er gibt **drei Tarifstufen**: Hochtarif (HT, auch Hochlasttarifstufe), Standardtarif (ST) und Niedertarif (NT, Niedriglast). Jede Stufe hat **Uhrzeiten** und einen **Arbeitspreis in ct/kWh**. Oft gilt das nur in bestimmten **Quartalen** (meist Q1 und Q4). Die Uhrzeiten decken zusammen **24 Stunden** ab: HT + NT sind genannt, ST ist "alle restlichen Zeiten".

## 2. Arbeitsablauf je Netzbetreiber (3 bis 5 Minuten)
1. **Ausschnitt ansehen:** `PYTHONPATH=. python daten/modul3_batch.py 0 12` zeigt 12 Ausschnitte. Der Ausschnitt ist die Hilfe, **nicht die Quelle**.
2. **Dokument öffnen** (Adresse in `quelle_url` der Liste, PDFs auch in `ergebnis/pdf/` und `eingang/pdfs_neu/`) und die Seite mit "Modul 3" ansehen, **am Bild**. In der Niederspannung **ohne Leistungsmessung** lesen, nicht den RLM-Teil.
3. **HT, ST, NT einzeln ablesen:** Uhrzeiten, Quartale, Preis (ct/kWh, netto).
4. **Prüfen:** HT + ST + NT = 24 Stunden, nichts überlappt. Quartale aus dem Dokument.
5. **Eintragen** in `ergebnis/modul3_manuell.csv`, `PYTHONPATH=. python daten/modul3_manuell_pruefen.py`, erst bei grün weiter.
6. Alle 10 bis 20 Netzbetreiber **pushen** und eine Meldung in `eingang/kommunikation/`.

## 3. Die Tabellenformen, die vorkommen (mit Lösung)
**A. Zeile je Tarif mit Zeit und Preis** (einfach): `Hochtarif 17:00-21:00 Uhr 15,14 ct/kWh`. Direkt eintragen.
**B. Zeit steht über oder unter dem Tarifnamen** (Bad Kissingen, Bebra, Huntetal, Bietigheim-Bissingen, Blomberg): Die Zelle ist mittig ausgerichtet, die Zeit steht eine Zeile versetzt. Beispiel Kissingen: `06:00-17:00 / Standardtarif 7,13 21:00-00:00 / Hochtarif 9,44 17:00-21:00 / Niedrigtarif 1,43 00:00-06:00` bedeutet ST 06:00-17:00 und 21:00-24:00, HT 17:00-21:00, NT 00:00-06:00. **Am Bild entscheiden**, nicht am Text.
**C. Spalten mit Kopfzeile** (Wadgassen, Elmshorn, Leinetal): Kopf `Fenster NT | Fenster ST | Fenster HT` (Reihenfolge je Dokument verschieden), darunter die Zeiten in der jeweiligen Spalte. **Reihenfolge aus der Kopfzeile lesen**, nicht annehmen.
**D. Quartalstabelle** (Leinetal, Neumarkt, Selb): Zeilen `Quartal 1 … Quartal 4`, je Quartal eigene Zeiten. Gleiche Zeiten in Q1 und Q4: `Q1+Q4`. Quartale mit "0-24 Uhr", "keine Gültigkeit" oder "-": dort gilt nur ST, bei HT/NT `keins`.
**E. Ja/Nein-Tabelle** (Bad Kissingen, Stockach, Rothenburg, Mössingen): Zeiten stehen einmal, eine Tabelle sagt je Quartal `Ja` oder `Nein`. Die `Ja`-Quartale sind die Gültigkeit. Auch waagerecht: `Ja Nein Nein Ja` über vier Datumsspalten = Q1 und Q4.
**F. Hochtarif in mehreren Fenstern** (Mittelhessen, Haimhausen): `HT-Zeiten: 17:00-20:00 und 22:00-23:00`. **Alle** Fenster eintragen.
**G. Nur Wochentage** ("werktags", "Mo-Fr"): **nicht eintragen**, in `hinweis` vermerken (die Zeitreihe braucht jeden Tag).

## 4. Eintragen (Spalten in `modul3_manuell.csv`)
| Spalte | Beispiel |
|---|---|
| mastr_nr (zuerst), netzbetreiber, jahr | `SNB911031559460`, Stadtwerke Bad Kissingen, `2026` |
| ht_zeiten | `17:00-21:00` oder `11:00-13:00, 17:00-19:00` |
| st_zeiten | `06:00-17:00, 21:00-24:00` oder `Restzeit` ("alle übrigen Zeiten") |
| nt_zeiten | `00:00-06:00` |
| quartale | `ganzjährig` oder `Q1+Q4` |
| ht_ct_kwh / st_ct_kwh / nt_ct_kwh | `9,44` / `7,13` / `1,43` (Dezimalkomma, netto, leer wenn nicht eindeutig) |
| quelle_url, preisstand, hinweis | `hinweis` beginnt mit `gelesen_kollege:` |
Wechseln die Zeiten je Quartalsgruppe: `ht_zeiten` = `Q1+Q4: 16:30-20:00; Q2+Q3: keins`, ebenso ST und NT, `quartale` = `Q1+Q4; Q2+Q3`.

## 5. Preise: Falle Grundpreis
Bei "Modul 1 + 3" steht zuerst der **Grundpreis** (€/a, z. B. 72,00), dann die Arbeitspreise (ct/kWh, z. B. 13,07 | 2,91 | 8,71). Nur die ct/kWh eintragen. Netto und Brutto stehen oft nebeneinander: die **Nettozahl**. Plausibel ist NT < ST < HT, alle zwischen 0,3 und 25 ct/kWh.

## 6. Unklar, werktags, nicht gefunden
- **Unklar:** Zeile mit leeren Zeiten und Begründung im `hinweis`. Nichts raten.
- **Modul 3 steht nicht im Preisblatt:** `hinweis` = "Modul 3 im Dokument nicht ausgewiesen", ggf. mit Hinweis, wo (Seite). Gibt es ein eigenes Modul-3-Dokument ("Regelungen", "Zeitvariable Netzentgelte"), suchen.
- **Nur im Bild:** ausdrücklich "nur im Bild, Seite X, Zeile Y".
- **Nach 3 Minuten ohne Ergebnis:** weiter, später zurück.

## 7. Reihenfolge
1. Die ersten 100 der sortierten Liste (die großen Netzbetreiber, rund 80 % der Einwohner).
2. Danach der Rest.
3. Gleiche Layouts hintereinander (z. B. alle Ja/Nein-Tabellen), das geht in zwei Minuten pro Fall.

## 8. Qualität
- Jede Zeit am Dokument zeigen können (Seite/Zelle). Jede Zeile rückwärts prüfen.
- Prüfskript grün vor jedem Push. Es meldet Überlappungen und Summen ungleich 24 Stunden.
- Zahlen in Meldungen nur aus Dateien.
- Ich (Claude) ziehe Stichproben und nehme geprüfte Zeilen nach `main`. Maschinell habe ich 200 gelesen; die Zuordnung "Zeit über dem Namen" lasse ich bewusst bei dir, weil sie das Bild braucht.

## 9. Was schon gelöst ist (nicht noch einmal lesen)
Die 231 in `ergebnis/modul3_zeiten.csv` (davon 200 maschinell, 25 früher geprüft, 6 von Hand). Bei 181 stehen auch alle drei Preise.

Gesamtplan: `ergebnis/PLAYBOOK_2027.md`. Offene Punkte: `ergebnis/OFFENE_PUNKTE_2026-11-12.md`. Ältere Anleitung (Kurzfassung): `ergebnis/modul3_ANLEITUNG_KOLLEGE.md`.
