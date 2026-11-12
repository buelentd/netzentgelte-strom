# Auftrag 5: Modul 3 (HT/ST/NT-Zeiten) für die offenen Netzbetreiber

Liste: `ergebnis/modul3_offen.csv` (MaStR-Nr. zuerst, mit Ausschnitt aus dem Preisblatt-Text). Davon sind rund 430 mit Uhrzeiten im Text, bei denen der Maschinenleser die Zuordnung zu HT/ST/NT nicht eindeutig fand.
Genaue Anleitung: `ergebnis/modul3_ANLEITUNG_KOLLEGE.md`. Bearbeitet sind bereits die Zeilen in `ergebnis/modul3_manuell.csv`; diese nicht noch einmal anfassen.

Regeln (wie bei den Hochlastzeitfenstern):
1. Jede Zeit am Dokument prüfen (Text und Bild). Die Zeit steht oft über oder unter dem Tarifnamen, weil die Zelle mittig ausgerichtet ist.
2. HT, ST und NT zusammen müssen genau 24 Stunden ergeben und dürfen sich nicht überlappen. ST darf `Restzeit` heißen, wenn das Dokument "alle übrigen Zeiten" sagt.
3. Quartale aus dem Dokument: Ja/Nein-Tabelle oder Satz. Zeiten, die je Quartal verschieden sind: je Quartalsgruppe eine Angabe `Q1+Q4: …; Q2+Q3: …`.
4. Gilt eine Zeit nur werktags oder an bestimmten Wochentagen: nicht eintragen, in `hinweis` vermerken.
5. Preise nur eintragen, wenn sie eindeutig zum Tarif gehören (ct/kWh, netto). Sonst leer.
6. Unklar heißt leer lassen und im `hinweis` begründen. Nichts raten.

Ausgabe: Zeilen im Format von `ergebnis/modul3_manuell.csv` (gleiche Spalten), `hinweis` beginnt mit `gelesen_kollege:`.
