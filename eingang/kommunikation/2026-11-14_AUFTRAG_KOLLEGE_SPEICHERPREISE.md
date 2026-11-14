# Auftrag an den Kollegen: Speicherpreise am Original prüfen (14.11.2026)

Ziel: belegte Preise für Gewerbespeicher (€/kWh) für den Rechner. Der Scraper hat 412 Funde aus 42 Domains geliefert, alle **ungeprüft**:
`ergebnis/speicherpreise_funde.csv` (Spalten erklärt in `ergebnis/speicherpreise_LEGENDE.md`).

## Aufgabe
1. Pro **Domain** höchstens zwei Funde auswählen (die mit dem klarsten Kontext), nicht alle 412. Die Domains `batteriespeicher-report.de`, `reduco.ai`, `echtsolar.de` zählen zusammen wie jede andere, nicht 100 Mal.
2. Die **Original-Seite öffnen** (Link in `url`) und die Angabe im Text lesen. Prüfen:
   - Preis oder Spanne stimmt mit dem Fund überein?
   - **netto oder brutto** (inkl. oder zzgl. MwSt.)?
   - **Umfang**: nur Hardware oder schlüsselfertig (Wechselrichter, EMS, Montage, Inbetriebnahme)?
   - **Größe** in kWh, für die der Preis gilt?
   - **Stand/Datum** der Seite? Ältere als 18 Monate verwerfen.
   - Ist es ein **Angebot/Listenpreis**, eine **Marktübersicht**, eine **Studie** oder ein **Ratgeber**? Seiten, die sich als KI-generiert kennzeichnen, nicht verwenden.
3. Ergebnis in `status` und `pruefnotiz` der CSV eintragen: **geprüft**, **verworfen** (mit Grund) oder **offen**. Bei „geprüft“ zusätzlich netto/brutto, Umfang, kWh und Datum korrigieren, falls der Scraper `unklar` hatte.
4. Zusätzlich 3 bis 5 **neue Quellen** suchen, die der Scraper nicht hat (Studien: Fraunhofer ISE, BSW, EUPD, Bundesnetzagentur; Angebote; Fachmagazine; PDF-Angebote). Als neue Zeilen mit `status = geprüft` und Link nachtragen.

## Regeln
- Nichts schätzen. Was im Original nicht steht, bleibt `unklar`.
- Preisangaben nur mit Seite und Datum. Keine Zahl ohne Link.
- Hardware und schlüsselfertig nie in einem Topf. Netto und brutto nie mischen.
- Robots.txt und Nutzungsbedingungen der Seiten beachten, Seiten von Hand öffnen, nicht massenhaft abrufen.

## Abgabe
Die geänderte `ergebnis/speicherpreise_funde.csv` auf den Branch `vibe/speicherpreise` legen und in `eingang/kommunikation/` eine kurze Notiz mit Zahlen: geprüft, verworfen, offen, neue Quellen. Ich übernehme sie in den Rechner.

## Hintergrund
Quellen widersprechen sich (410–450 LogicEnergy, 450–800 Ratgeber, 650–750 eine Seite, 173–434 Hardware im Shop). Der Rechner zeigt später eine Spanne aus **geprüften** Werten mit Quelle und Datum, nicht aus dem Mittel aller Funde.
