# Recherche für den Rechner (Stand 06.11.2026)

Ziel: Die Annahmen im Rechner (Strompreis, dynamischer Tarif, Speicher, PV, Smart Meter) mit belegten Zahlen unterlegen. Jede Zahl trägt einen Belegstatus:

- **Original geprüft**: Ich habe die Primärquelle selbst abgerufen und gelesen.
- **Sekundär**: Aus einer Such- oder Ratgeberseite, Original nicht gelesen.
- **Von anderem Leser**: Aus den Teilen A, B, C des anderen Lesers, von mir nicht am Original geprüft.
- **Offen**: Nicht gefunden.

Nichts davon ist in die Daten oder in den Rechner übernommen. Zum Durchgehen gemeinsam: Abschnitt 9.

## 1. Terminmarkt Strom (Original geprüft)

Energy-Charts, Strom-Futures Base, Handelstag 05.11.2026, Deutschland, €/MWh (Diagrammdaten ausgelesen):

| 2027 | 2028 | 2029 | 2030 | 2031 | 2032 | 2033 | 2034 | 2035 | 2036 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 148,18 | 105,80 | 91,63 | 85,23 | 79,51 | 74,00 | 74,25 | 74,50 | 74,75 | 75,00 |

- 2027 = 14,82 ct/kWh. Mittel 2027 bis 2036 = 88,3 €/MWh = **8,8 ct/kWh**.
- Unser Börsenmittel der letzten 365 Tage: 11,2 ct. Letzte 30 Tage: 17,1 ct. Letzte 7 Tage: 23,0 ct.
- Der hohe Wert 2027 hängt laut BDEW am Preisanstieg infolge des Iran-Kriegs.
- Folge für den Rechner: Die Barwerte (Speicher 12 Jahre, PV 20 Jahre) rechnen heute mit einem festen Strompreis. Bei dauerhaft 14,8 ct würden PV und Speicher überschätzt, die Kurve zeigt langfristig etwa 7,5 ct.

## 2. Strompreis für Gewerbe und Industrie

- **BDEW Strompreisanalyse Oktober 2026 (Original geprüft):** Kleine und mittlere Industrie, einfacher Durchschnitt aus 5 Abnahmefällen von 160.000 kWh bis 20 Mio. kWh im Jahr, Mittelspannung, Lieferverträge ab dem nächsten Halbjahr: **17,9 ct/kWh** (2026 bisher), davon Beschaffung, Netzentgelt und Vertrieb 15,5 ct und Steuern, Abgaben, Umlagen 2,5 ct (inklusive reduzierter Stromsteuer). Quelle der Industriewerte: VEA. Mittelgroße Industrie (20 bis 70 Mio. kWh): 14,6 ct.
  - Das ist ein Durchschnitt über Mittelspannungskunden und enthält das Netzentgelt. Für unsere Niederspannungs-Beispielbetriebe (150.000 bis 450.000 kWh) ist es nur eine grobe Orientierung.
- **BDEW Haushalte Oktober 2026 (Original geprüft):** 37,3 ct/kWh, davon Beschaffung und Vertrieb 15,4 ct, Netzentgelte 9,2 ct, Steuern, Abgaben und Umlagen 12,6 ct.
- **Gewerbe-Vergleichsliste, Berlin 10245, 100.000 kWh (aus Screenshot und PDF des Nutzers):** netto 23,86 ct (günstigster) bis 38,30 ct (teuerster, dynamisch). Vollpreise inklusive Netz und Abgaben. Ohne Netzentgelt von etwa 7,5 ct bleiben etwa 16,4 ct bis 30,8 ct. Mitte der Liste etwa 20 ct.
- **Von anderem Leser (Teil B):** Terminmarkt 14,82 ct plus Aufschlag, Spanne netto ohne Netz 20 bis 22 ct. Seine Angabe „mit Netz 27 bis 30 ct brutto“ ist netto gemeint (brutto wären es 33 bis 35 ct).
- **Offen:** Echte Verhandlungspreise für Festpreisverträge ab 100.000 kWh. Dafür gibt es keine öffentliche Quelle. Anfrage-Entwürfe liegen beim anderen Leser.

## 3. Dynamische Tarife, Aufschlag

| Anbieter | Aufschlag / Gebühr | Beleg |
|---|---|---|
| Rabot | Servicegebühr entweder 20 % Ersparnisanteil oder 1,5 ct netto je kWh; Grundpreis enthält Netz, Messung und 4,99 € Servicegebühr | Ausschnitt der Recherche (FAQ). Original von mir nicht geprüft, Adresse unklar |
| Tibber | 2,15 ct/kWh „weitere Beschaffungskosten“ plus 5,99 € im Monat inkl. MwSt. | Von anderem Leser. Tibber-AGB (Original geprüft) nennen Spotmarktpreis, weitere Beschaffungskosten, Tibber-Gebühr, die Zahl 2,15 steht dort nicht. Netto oder brutto bleibt offen |
| 1Komma5° Dynamic Pulse | Börsenpreis ohne Aufschlag; Gebühr für die Software, dazu Grundpreis | Von anderem Leser |
| Octopus, Ostrom | kein fester Aufschlag veröffentlicht | Von anderem Leser |
| Stadtwerke Kiel StromDynamik | Arbeitspreis ohne Börse 17,41 ct, 15,75 € im Monat, 12 Monate, nur mit Smart Meter | Von anderem Leser |

- Die meisten sind Haushaltsprodukte. Ob es sie ab 100.000 kWh oder mit Leistungsmessung gibt, ist offen.
- Rabots 38,30 ct in der Vergleichsliste sind ein Vollpreis (Börse plus etwa 15 ct für Netz, Steuern, Umlagen, Service), keine Marge. Mit 23 ct Börse (letzte 7 Tage) kommt man auf diese Größenordnung.
- Unser Modell nimmt 2,5 ct Aufschlag. Das liegt oberhalb der belegten 1,5 bis 2,15 ct.

## 4. Smart Meter

- **§ 30 MsbG, Preisobergrenzen für intelligente Messsysteme, ab 01.01.2025 (Original geprüft, gesetze-im-internet.de):** Die Ausstattung ist wirtschaftlich vertretbar, wenn das jährliche Entgelt insgesamt brutto nicht mehr als diese Werte beträgt:

| Jahresverbrauch (oder Anlage) | Obergrenze brutto im Jahr | davon Netzbetreiber, Rest Anschlussnutzer |
|---|---:|---:|
| über 6.000 bis 10.000 kWh | 120 € | 80 € / 40 € |
| über 10.000 bis 20.000 kWh (oder § 14a, oder Anlage über 7 bis 15 kW) | 130 € | 80 € / 50 € |
| über 20.000 bis 50.000 kWh (oder Anlage über 15 bis 25 kW) | 190 € | 80 € / 110 € |
| über 50.000 bis 100.000 kWh (oder Anlage über 25 bis 100 kW) | 220 € | 80 € / 140 € |
| über 100.000 kWh (oder Anlage über 100 kW) | „angemessenes jährliches Entgelt“, keine feste Obergrenze | Netzbetreiber höchstens 80 €, Rest Anschlussnutzer |

  - Zusätzlich bis 50 € brutto je Anschlussnehmer und Netzbetreiber für eine Steuerungseinrichtung am Netzanschlusspunkt.
  - Absatz 6: Eine Festlegung der Bundesnetzagentur nach § 33 ersetzt diese Werte. Ob eine gilt, habe ich nicht geprüft.
- **Preisblätter (Sekundär, Suchergebnis):** Zwei Netzbetreiber-Preisblätter nennen für über 100.000 kWh 139 € netto (Stand 2024) und 369,74 € netto bzw. 440 € brutto (Stand 2026). Das zeigt: Bei RLM ist der Preis netzbetreiberabhängig und kann deutlich über den 220 € der Stufe darunter liegen.
- **Bundesnetzagentur (aus dem Quellenausschnitt der Recherche):** Anlagen über 7 kW Pflichteinbau, 1 bis 7 kW Entscheidung des Messstellenbetreibers, seit 2025 Einbau auf Kundenwunsch möglich.
- **Von anderem Leser (Teil C):** Eintarifzähler Median 11,40 € im Jahr (254 Netzbetreiber), iMSys-Bandpreise Median 344 € im Jahr (23 Netzbetreiber), Mehrkosten etwa 30 bis 338 €. Zeitvariable Netzentgelte (Modul 3) bieten 426 von 443 Netzbetreibern. Datengrundlage unklar.
- Bei RLM (über 100.000 kWh) ist das intelligente Messsystem ohnehin vorgesehen. Die Kosten sind dann keine Entscheidung, sondern Fixkosten.

## 5. Speicher (Sekundär)

- Gewerbespeicher 2026: 30 bis 100 kWh etwa 400 bis 500 €/kWh, 100 bis 250 kWh etwa 410 bis 450 €/kWh (Anbieter, Stand April 2026). Kleine Gewerbespeicher laut Leitfaden 500 bis 700 €/kWh, Großspeicher im MW-Bereich etwa 200 €/kWh. Hardware ohne Montage 142 bis 434 €/kWh netto (Händlerliste, Stand 09.10.2026).
- Fraunhofer ISE (Präsentation 2023): 450 bis 800 €/kWh.
- Förderung: Baden-Württemberg bis 30 %, höchstens 200 €/kWh für Gewerbe und Kommunen (10 bis 500 kWh); NRW progres.nrw läuft bis Ende 2026. Nicht von mir geprüft.
- Unser Richtwert: 450 €/kWh bis 100 kWh, danach sinkend auf 350 €/kWh bei 500 kWh. Das liegt im Rahmen der Anbieterangaben. Die Quellen sind überwiegend Händler- und Herstellerblogs.
- **Netzentgelt für den Speicher (Sekundär):** Batteriespeicher, die bis zum 4. August 2029 in Betrieb gehen, sind 20 Jahre vom Netzentgelt auf den Strombezug befreit (§ 118 Abs. 6 EnWG); die Bundesnetzagentur hat das laut Fieldfisher am 27.05.2026 bestätigt. Eine Stellungnahme nennt dagegen den 31.12.2028, das passt nicht zusammen. Baukostenzuschüsse sind nach einer Deloitte-Präsentation nicht befreit. **Offen:** Ob das auch für die Spitzenkappung am Leistungspreis gilt (der Speicher bezieht für den Betrieb selbst, nicht nur zur Einspeisung).

## 6. Photovoltaik (Sekundär)

- Gewerbe-Aufdach 30 bis 100 kWp: 800 bis 1.300 €/kWp netto, schlüsselfertig, ohne Speicher. 30 kWp etwa 1.200, 100 kWp etwa 1.050 €/kWp. Durchschnitt über alle Segmente etwa 1.015 €/kWp (Fraunhofer ISE, Frühjahr 2026, laut Sekundärquelle).
- Unser Richtwert: 1.100 €/kWp pauschal. Passt in die Spanne, eine Staffelung nach Größe wäre genauer.

## 7. Stromsteuer (Sekundär, widersprüchlich)

- Seit 01.01.2026 zahlen produzierendes Gewerbe sowie Land- und Forstwirtschaft dauerhaft nur den EU-Mindestsatz von 0,05 ct/kWh, alle anderen 2,05 ct/kWh. Vattenfall nennt produktiv tätige Handwerksbetriebe wie Bäckereien ausdrücklich als Teil des produzierenden Gewerbes; im Einzelfall muss das geprüft werden.
- Antrag: Quellen widersprechen sich (automatisch laut Forvis Mazars, auf Antrag laut anderen; Mindestverbrauch 12.500 kWh und Selbstbehalt 250 € in einer KMU-Unterlage).
- Folge für den Rechner: Der Steuer- und Umlagenanteil unseres Strompreises (3,11 ct oder je Branche vorgeschlagen) hängt an der Branche. Eine Bäckerei würde etwa 2 ct weniger zahlen als ein Supermarkt. Nicht gegengeprüft.

## 8. Weiter offen

- Echte Festpreisangebote ab 100.000 kWh (Anfrage-Entwürfe liegen beim anderen Leser).
- Tibber netto oder brutto, Rabot-Originalstelle.
- Ob eine Bundesnetzagentur-Festlegung die Preisobergrenzen des MsbG ersetzt.
- Ob die Netzentgeltbefreiung der Speicher auch den Leistungspreis bei der Spitzenkappung betrifft.
- Gewerbe-Versionen der dynamischen Tarife (Mindestverbrauch, Leistungsmessung).

## 9. Vorschläge für den Rechner, gemeinsam zu entscheiden

1. **Börsenniveau:** Schalter mit Terminmarkt 2027 (14,8 ct), Terminkurve 2027 bis 2036 (8,8 ct), Jahresmittel (11,2 ct), Mittel 30 Tage (17,1 ct). Frage: Voreinstellung für die Barwerte die Terminkurve?
2. **Aufschlag dynamisch:** bleibt überschreibbar, Voreinstellung 2,5 ct oder auf 2,0 ct senken (Belege 1,5 bis 2,15 ct)?
3. **Stromsteuer je Branche:** Bäckerei und Handwerk als produzierendes Gewerbe mit 0,05 ct, Hinweis auf die Prüfung im Einzelfall?
4. **Smart Meter:** Zeile mit den Kosten nach Verbrauchsgruppe aus § 30 MsbG (netto etwa Brutto durch 1,19), bei über 100.000 kWh als „Preis laut Preisblatt des Netzbetreibers, höchstens 80 € für den Netzbetreiber“.
5. **PV-Preis:** Staffel nach Größe (1.200 €/kWp bei 30 kWp, 1.050 bei 100 kWp)?
6. **Speicher:** Hinweis auf die Netzentgeltbefreiung bis 2029 und auf mögliche Förderung (Baden-Württemberg bis 30 %, höchstens 200 €/kWh).
7. **Vergleichswert:** Hinweistext zum Gewerbe-Strompreis (Orientierung 16 bis 20 ct ohne Netz, Quellen genannt).
