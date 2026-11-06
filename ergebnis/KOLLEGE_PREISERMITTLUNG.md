# Aufgabe Preisermittlung: Strom ab 100.000 kWh, dynamischer Tarif, Smart Meter (Stand 06.11.2026)

Ziel: Die drei Zahlen finden, an denen unsere Wirtschaftlichkeitsrechnung (Speicher, PV, dynamischer Tarif) hängt und die wir heute nur als Annahme haben. Alles belegen (URL, Datum, Datei). Nichts schätzen. Ergebnisse in `ergebnis/preisermittlung_vorlage.csv` (Spalten dort).

## A. Dynamische Gewerbetarife: Aufschlag und Grundpreis
Welche Anbieter ein dynamisches Gewerbeprodukt haben (Beispiele zum Prüfen, nicht abschließend: Rabot Energy `rabot.business`, Tibber, 1Komma5°, Octopus, Ostrom, Stadtwerke mit „Börsenstrom“-Tarif). Je Produkt vom Anbieter (Preisblatt oder Produktseite, kein Vergleichsportal):
- Aufschlag auf den Börsenpreis in ct/kWh (netto) und Grundpreis in €/Monat netto.
- Ob Netzentgelt, Steuern, Umlagen, Konzessionsabgabe im Preis enthalten sind oder separat.
- Mindestlaufzeit, Kündigungsfrist, ab welchem Jahresverbrauch (Gewerbe, RLM?) das Produkt angeboten wird, welche Messung nötig ist (Smart Meter / RLM).
- Wichtig: Bei Rabot zeigte die Gewerbe-Vergleichsliste 38,30 ct/kWh für einen „dynamischen“ Tarif. Bitte klären, aus welchem Börsenpreis und Aufschlag sich das zusammensetzt.

## B. Festpreis-Angebote ab 100.000 kWh (Verhandlungspreise)
Es gibt keine veröffentlichten Preise. Einzige echte Quelle: Angebote einholen. Für drei Beispielbetriebe jeweils bei 3 bis 5 Lieferanten (Stadtwerk vor Ort, ein überregionaler Anbieter, ein Energiemakler) anfragen:
- Bäckerei, 150.000 kWh/Jahr, 45 kW Spitze, PLZ 10245 (Berlin)
- Supermarkt, 450.000 kWh/Jahr, 150 kW Spitze, PLZ 10245
- Handwerk, 200.000 kWh/Jahr, 80 kW Spitze, PLZ 10245
Festgehalten wird je Angebot: Laufzeit, Arbeitspreis ct/kWh netto, Grundpreis, ob Netzentgelt enthalten (nur „Energie“ oder „All-in“), Preisstand-Datum. Angefragte Betriebe nur als Beispiele nennen, keine Kundendaten.
Falls Anfragen nicht möglich sind: Ersatz sind der Terminmarktpreis (Jahres-Base und -Peak für 2027, Quelle EEX oder Energy-Charts) und die amtlichen Durchschnittspreise je Verbrauchsband (Bundesnetzagentur Monitoringbericht, BDEW Strompreisanalyse, Eurostat). Dann ausdrücklich als Durchschnitt, nicht als Angebot kennzeichnen.

## C. Smart Meter: Kosten und Nutzen
- Messstellenbetrieb je Jahr: konventioneller Zähler (RLM-Zähler) gegen intelligentes Messsystem, netto, aus den Preisblättern der Netzbetreiber (bei den 100 größten reicht).
- Ob der Netzbetreiber zeitvariable Netzentgelte (Modul 3 nach § 14a) für Gewerbe anbietet und mit welchen Stufen (Preisblatt).
- Ab wann ein Smart Meter für Gewerbe Pflicht ist (Verbrauch, Erzeugung) laut Messstellenbetriebsgesetz: nur Stand und Quelle nennen.

## Regeln
- Nur Anbieter- und Netzbetreiberseiten oder Angebote, kein Vergleichsportal als Beleg.
- Netto, 2026, mit Datum. Mehrere Zeilen je Anbieter sind erlaubt.
- Formulare im Browser nur nutzen, wenn eine Anfrage nötig ist, und nur mit Firmenangaben, nicht mit Kundendaten.
- Rückmeldung wie bisher: Commit, Sync, „synched“.
