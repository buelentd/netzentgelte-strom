# Gesamtbild Netzentgelte Strom 2026 (05.11.2026, 831 Netzbetreiber)

## Preise je Ebene (Quelle: `ergebnis/ebenen_erwartung.csv`)
| Ebene | gelesen (4 Werte) | nicht ausgewiesen | im Dokument, nicht gelesen | kein Dokument / fehlt |
|---|---|---|---|---|
| SLP (AP + Grundpreis) | 707 (85 %) | n. a. | n. a. | 124 (93 fehlt, 31 kein Dokument) |
| Niederspannung | 735 (88 %) | 54 | 13 | 29 |
| Umspannung MS/NS | 669 (80 %) | 106 | 27 | 29 |
| Mittelspannung | 649 (78 %) | 135 | 17 | 30 |
| Umspannung HS/MS | 121 | 670 | 8 | 32 |
| Hochspannung (HS direkt) | nicht erfasst | | | |

- Regel: Niederspannung und SLP hat jeder Netzbetreiber. Die 54 „nicht ausgewiesen“ bei NS sind deshalb Lese- oder Suchfehler und werden bearbeitet (kein Endzustand).
- HS/MS-Status: 121 gelesen, 512 nicht ausgewiesen, 128 Hochspannung nur im Text genannt, 30 nur Hochspannung, 32 kein Dokument, 4 im Dokument nicht gelesen, 4 null ausgewiesen.
- Hochspannung direkt (HöS/HS) ist im Datenmodell nicht vorgesehen (nur HS/MS). 48 Dokumente enthalten eine reine Hochspannungszeile mit Zahlen. Das betrifft vor allem große Netzbetreiber und spielt für Gewerbekunden kaum eine Rolle; falls gewünscht, als eigene Ebene ergänzen.
- Bestätigung am Dokument: 2.011 Preisblöcke bestätigt (rund 90 %), 62 unbestätigt (31 Netzbetreiber, richtiges Preisblatt nötig), 101 ohne Text (Scans).

## Hochlastzeitfenster (Quelle: `lauf/hlzf_zusammen.csv`)
- Mit Werten: 543 von 831 (65 %): 358 unser Leser, 185 Liste des Nutzers. Davon NS-Fenster 508, MS/NS-Fenster 461, Erheblichkeitsschwelle 97.
- Nicht gelesen: 136 Dokumente liegen vor, Tabellenform fehlt (Claude); 97 kein Dokument/Adresse (Kollege); 19 ungeprüft; 11 Prüfung offen; 11 nicht 2026; 8 Raster; 6 keine im Dokument.
- HLZF für HS/MS und Hochspannung werden nicht gespeichert (Datenmodell kennt NS und MS/NS).

## Rechner-Tauglichkeit
- SLP + NS-Preise + NS-HLZF vollständig: 465 Netzbetreiber (56 %).
- Status ok 326, prüfen 468, blockiert 23, robots 10, kein_preisblatt 3, keine_website 1.

## Wer was
- Kollege: 49 Preisblatt-Nacharbeitsfälle, 69 Preisfälle, 116 HLZF-Fälle.
- Claude: 75 Preis-Fälle, 172 HLZF-Fälle (136 neue Dokumente, 19 ungeprüft, Raster), 54 fehlende NS und 93 fehlende SLP prüfen.
- Nutzer: 33 blockierte Dokumente im Browser, 4 gesperrte HLZF-Fälle, 14 offene Schlüssel.
