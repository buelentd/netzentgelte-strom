# Nachlauf für den Kollegen (Stand 06.11.2026 abends)

Liste mit MaStR-Nummer: `ergebnis/kollege_nachlauf.csv` (eine Zeile je Dokument, Spalte `aufgabe` sagt, was zu tun ist; `suche_1/2` sind Google-Links mit `site:` ohne www).

## Dateinamen und Ablage
- Preisblatt: `<nr>_preis_<Originalname>.pdf`, Hochlastzeitfenster: `<nr>_hlzf_<Originalname>.pdf` (nr = unsere Nummer aus der Liste). Mehrere Dateien je Nummer sind erlaubt (z. B. SLP und RLM getrennt).
- Alle Dateien flach in einen Ordner, z. B. `eingang/lieferung2`. Nur Strom, nur 2026.
- Jede Datei vorher mit `daten/dokument_pruefen.py` prüfen (OK / PRUEFEN / FALSCH). FALSCH nicht ablegen. Bei PRUEFEN den Grund in `status_preise.txt` bzw. `status_hlzf.txt` notieren.
- Nichts schätzen, nichts abtippen außer bei Scans (siehe unten).

## Was zu tun ist

### A. Preisblätter (81 Zeilen)
1. **30× „Dokument ist vermutlich das falsche (keine Niederspannung ausgewiesen)":** richtiges Preisblatt Strom 2026 mit Leistungspreisen für Niederspannung (Jahresleistungspreis, unter und ab 2.500 h) suchen.
2. **26× „SLP-Preis steht nicht vollständig im Dokument":** separates Preisblatt „Netznutzung ohne Leistungsmessung / Standardlastprofil" suchen (Grund- und Arbeitspreis Niederspannung). Datei zusätzlich zum vorhandenen, nicht ersetzen.
3. **15× „Dokument bestätigt die Preise nicht":** richtiges, endgültiges Preisblatt 2026 liefern.
4. **5× „Dokument gehört einem anderen Netzbetreiber":** das eigene Preisblatt dieses Netzbetreibers suchen (Dokument darf nicht den Namen eines anderen tragen).
5. **4× „Dokument lückenhaft oder mehrdeutig":** im Original-PDF nachsehen, ob die genannte Stelle wirklich leer ist, und ein besseres Preisblatt liefern, falls es eins gibt. Konkrete Fälle: Fellbach (476, Arbeitspreis ab 2.500 h bei Umspannung leer), Greifswald (497, nur Tageswerte), GSW Kamen (265, nur SLP), Bad Herrenalb (395, „fiktives" Netzentgelt).
6. **4× Preisblatt Strom 2026 suchen und laden,** 2× Scan ohne Text (Preisblatt liefern oder Werte als Text abschreiben), 1× Preisblatt mit allen Ebenen.

### B. Hochlastzeitfenster (113 Zeilen)
1. **93× „Hochlastzeitfenster 2026 suchen und laden":** Wenn der Netzbetreiber **kein** separates 2026er-Dokument veröffentlicht hat, bitte in `status_hlzf.txt` als `nicht_veroeffentlicht` mit Begründung festhalten (Seite geprüft, Datum). Das gilt dann als Endbefund.
2. **11× „Dokument ist nicht für 2026":** Datei für 2026 suchen (nicht 2025, nicht 2027). Zeilen siehe Liste (z. B. 36, 457, 811 haben 2027).
3. **10× „Raster/Grafik":** Raster mit markierten Viertelstunden: bitte als Text abschreiben (Ebene, Jahreszeit, von-bis) in eine `<nr>_hlzf_abschrift.txt`.

### C. Von dir (Nutzer) bleibt: 29 Browser-Downloads (`ergebnis/BROWSER_DOWNLOADS_33.md`)

## Rückmeldung
- Nach jeder Runde commit und sync, dann Meldung an Claude. Ich lese ein und melde die neuen Zahlen.
- Für die 73 Netzbetreiber, bei denen „kein 2026er-Hochlastzeitfenster veröffentlicht" belegt ist: bitte die Nummern in einer Liste (`nr;grund;datum`) schicken, dann trage ich sie als Endbefund ein.
