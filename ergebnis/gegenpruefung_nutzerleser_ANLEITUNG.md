# Gegenprüfung: so sind die Werte entstanden (04.11.2026)

Text-Quelle für alle Werte: die 665 `pdftotext -layout`-Texte (`ergebnis/texte_layout/`, Name = MaStR-Nr_unsere-Nr), also derselbe Text, den auch der Leser des Nutzers bekommt. Schlüssel ist die MaStR-Nummer.

## Was anders gemacht wurde
1. **Zeilenanker statt Wert-irgendwo-im-Text.** Ein Wert gilt nur als bestätigt, wenn alle vier Werte ab 2.500 h in einer Zeile mit dem passenden Ebenennamen stehen (Quelle "Leser, Zeilenanker bestätigt").
2. **Je Wert ein eigener Parser** für Lücken (Quellen "RLM-Parser" und "SLP-Parser"): suchen die Zeile mit dem Ebenennamen und lesen dahinter bzw. in den nächsten Zeilen die vier Preise. Regeln: bei netto/brutto die Nettowerte; Tageswerte (€/kW/Tag) x 365; Ausschluss von Kommunalrabatt, Speicherheizung/Wärmepumpe, §14a/Modul, Messstellenbetrieb, Beispiel- und Vergleichstabellen (Jahresverbrauch von ... kWh); "Umsp." = Umspannung; Zeile nur "Umspannung" = MS/NS; "Umspannung HS/MS" und "zur Mittelspannung" sind HS/MS.
3. **Tausenderpunkt** ("2.500 h") wird nie als Zahl gelesen; Datumsangaben und kV-Angaben (0,4 kV) werden entfernt.
4. **Nicht übernommen** wurden Dokumente, deren Zuordnung zum Betreiber nicht belegt ist (Hasbergen, Meißen, EVU Langenpreising).

## Reihenfolge der Ebenen im Dokument
Mittelspannung (MS) -> Umspannung MS/NS -> Niederspannung (NS); Umspannung HS/MS steht davor. Die Kosten bei 4.000 h (AP + LP*100/4000) müssen MS <= MS/NS <= NS erfüllen, die LP selbst nicht.

## Spalten der Datei
`wert_nutzerleser` und `ergebnis` bitte ausfüllen: gleich / abweichend / nichts. Bei Abweichung bitte die Zeile aus dem Text nennen.
Format der Werte: LP<2.500h / AP<2.500h / LP>=2.500h / AP>=2.500h (€/kW/a und ct/kWh); SLP als Grundpreis (€/a) / Arbeitspreis (ct/kWh).
