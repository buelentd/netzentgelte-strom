# Vergleich: Rechenweg Testseite und conplot (Stand 02.11.2026)

Fall: Bäckerei, Biberach an der Riß (88400, e.wa riss Netze), 150.000 kWh, Spitzenlast 111 kW, Speicher 220 kWh,
keine Solaranlage, Eigenfinanzierung. Die Angaben zu conplot stammen aus Bildschirmfotos der Web-App und den Angaben
des Nutzers. Was dort nicht sichtbar ist, steht als „unbekannt“. Die Testseite rechnet wie gebaut; die Unterschiede
sind hier festgehalten, nicht angeglichen.

## Eingaben und Daten
| Punkt | conplot | Testseite |
|---|---|---|
| Lastprofil | hergeleitet, angezeigt als „synthetisiert“ und „ereignisbasiert, aus 66 Werktagen“ (Datengüte 65 % vor, 80 % nach der Analyse); Grundlage nicht erkennbar, laut Hinweis werden Eingaben an einen KI-Dienstleister übermittelt; Bäckerei: Grundlast 4,6 kW, Spitze 98,6 kW | Bäckerei: geschätztes Tagesprofil Backstube, Form aus dem conplot-Beispiel abgelesen (nicht gemessen), skaliert auf Verbrauch und Spitzenlast; andere Branchen BDEW-Standardprofile |
| Spitzenlast | Eingabe | Eingabe, sonst aus Anlagen geschätzt |
| Netzbetreiber und Preise | unbekannt | 492 Netzbetreiber mit geprüften Preisblättern 2026 |
| Leistungspreis | pauschal (Angabe des Nutzers) | je Netzbetreiber, Gruppe unter oder ab 2.500 Benutzungsstunden |
| Strompreis und Abgaben | unbekannt | Börse 11,2 ct, Aufschlag 2,5 ct (Annahme), Abgaben 3,11 ct (belegt) |
| Preisjahr | Preispfad startet laut früherer Beobachtung 2025 | Basis 2026 |

## Rechenregeln
| Punkt | conplot | Testseite |
|---|---|---|
| Nutzbar, Dauer, Wirkungsgrad, Ladungen | 10 bis 90 %, 2 h, 0,92, 1,5 je Tag | gleich |
| Zielspitze | 111 auf 50 kW | beste Spitze je Speichergröße (45 kW) |
| Tarifwechsel nach Kappung | nicht erkennbar | ja, vorher und nachher getrennt |
| Nachladen | 44.636 kWh im Jahr, laut Text außerhalb der Hochlastzeitfenster | nur außerhalb der Hochlastzeitfenster |
| Atypische Netznutzung | nicht erfüllt | nicht erfüllt (Mindestverlagerung 100 kW laut Netzbetreiber) |
| Hochlastzeitfenster Winter | grafisch etwa 8:00 bis 12:45 und 16:00 bis 18:45 | 12:00 bis 13:30 und 16:15 bis 19:15 laut Preisblatt gelesen, noch gegen das Original zu prüfen |

## Erträge pro Jahr (220 kWh)
| Posten | conplot | Testseite (dynamischer Tarif) |
|---|---|---|
| Spitze senken | Netzentgelt etwa +6.600 | +3.346 (4.263 Netzentgelt minus 917 Ladeverluste) |
| Verschieben im eigenen Betrieb | nicht vorhanden | +3.867 (Obergrenze mit perfekter Voraussicht etwa 5.300) |
| Handel (Regelenergie und Arbitrage) | etwa +200 („Trading“), Rechenweg unbekannt | Festpreis: Börsenhandel +2.605 |
| Regelenergie | abgewählt | +1.619 (Spanne 1.214 bis 2.024) |
| Betriebskosten Speicher | etwa −3.000, vermutlich die Servicegebühr von conplot (3.000 € fix im Jahr plus 10 % vom Rest), keine Betriebskosten | −1.386 (eigene Annahme 1,5 % von 92.400, nicht belegt) |
| **Summe** | **2.936** (bis 3.171) | **+7.445** |

## Kosten und Ergebnis
| Punkt | conplot | Testseite |
|---|---|---|
| Investition | 200.926 € = 913 €/kWh | 92.400 € = 420 €/kWh (Staffel geschätzt) |
| Förderung | KfW 270 als Kredit wählbar | nur Hinweis |
| Amortisation | keine | 12,4 Jahre |
| Bewertung | 10 Jahre kumuliert 26.523 € | Barwert 12 Jahre bei 6 %: −29.981 € |

## Parameter von conplot (vom Nutzer eingefügt, Stand 02.11.2026)
| Bereich | Wert |
|---|---|
| Batterie, Wechselrichter, Installation | 430 €/kWh, 1.500 €, 800 € (bei 220 kWh ergibt das 96.900 €, angezeigt wurden 200.926 €) |
| Handelserlöse je MW und Jahr | Regelenergie (FCR) 106.000, aFRR 146.000, Day-Ahead 91.000; Gebühr Direktvermarkter 15 % |
| Betrieb | Lebensdauer 20 Jahre, 6.000 Zyklen, Kapazitätsabbau 2,5 % je Jahr, Entsorgung 75 €/kWh |
| conplot-Servicegebühr | 3.000 € je Jahr fix plus 10 % vom Restertrag |
| Atypische Netznutzung | pauschal 60 €/kW und Jahr, C-Rate 2,0 |
| Energy as a Service | Strompreis 20 ct/kWh, Schwelle Fonds-Rendite 8 % (10 Jahre) |

Folgen: Die Investition von 200.926 € folgt nicht aus diesen Parametern (Faktor etwa 2,1). Das Ergebnis „2.936 € Ihr Anteil“
ist vermutlich nach Abzug der Servicegebühr, also mit unserer Summe nicht gleichartig. Wir rechnen ohne Kapazitätsabbau und
ohne Entsorgungskosten und sind dadurch auf lange Sicht optimistischer.

## Offene Fragen an conplot
1. Woraus setzen sich 913 €/kWh Investition zusammen (die Parameter ergeben für 220 kWh nur 96.900 €)?
2. Welcher Leistungspreis wird verwendet, und wird der Tarifwechsel bei 2.500 Stunden berücksichtigt?
3. Wie wird „Trading“ gerechnet, und warum liegt es bei etwa 200 €? (Der Nutzer sagt: keine Quelle.)
4. Welche Hochlastzeitfenster werden für e.wa riss angesetzt, und woher?
5. Woher stammt das Lastprofil (Quelle der Bäckerei-Form)?

## Einordnung
Der größte Unterschied im Ergebnis ist die Investition (913 gegen 420 €/kWh). Beim Netzentgelt liegt conplot bei einem
pauschalen Leistungspreis fast doppelt so hoch wie der echte Preis von e.wa riss. Verschieben und Handel sind bei beiden
unsicher; unser Wert liegt nah an der Obergrenze.

## Nachtrag 03.11.2026
- aFRR gemessen (regelleistung.net, 365 Tage, beide Richtungen mit je 1 MW): Grenzpreis 287.458, Durchschnittsgebot 204.373 €/MW und Jahr;
  conplot-Wert 146.000 liegt darunter. Trend fallend (Oktober 196.000, November 88.000 hochgerechnet).
- Day-Ahead aus unseren Börsenpreisen: etwa 79.000 €/MW und Jahr (obere Grenze), conplot 91.000.
- conplot-Bausteine laut Angaben des Nutzers: „Site Intelligence“ (MaStR, VNB-Datenbank, Förderdaten) und VNB-Prozessdatenbank
  („Netzentgelt-Strukturen und Anschlussfristen pro Netzbetreiber“); die Datenbank enthält nach der Beschreibung nicht zwingend Preise.
- Zusätzliche Fragen: Welche Felder liefert die VNB-Datenbank, woher stammen sie (vnb-monitoring.org?), gelten die Netzentgelte dort für
  Haushalte oder für Gewerbe, und wie fließen Anschlussdauer und Anschlusskosten in die Wirtschaftlichkeit ein?
