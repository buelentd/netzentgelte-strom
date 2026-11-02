# Vergleich: Rechenweg Testseite und conplot (Stand 02.11.2026)

Fall: Bäckerei, Biberach an der Riß (88400, e.wa riss Netze), 150.000 kWh, Spitzenlast 111 kW, Speicher 220 kWh,
keine Solaranlage, Eigenfinanzierung. Die Angaben zu conplot stammen aus Bildschirmfotos der Web-App und den Angaben
des Nutzers. Was dort nicht sichtbar ist, steht als „unbekannt“. Die Testseite rechnet wie gebaut; die Unterschiede
sind hier festgehalten, nicht angeglichen.

## Eingaben und Daten
| Punkt | conplot | Testseite |
|---|---|---|
| Lastprofil | synthetisch aus Branche und Jahreshöchstlast (Datengüte 65 bis 80 %); Bäckerei: Grundlast 4,6 kW, Spitze 98,6 kW | Bäckerei: geschätztes Tagesprofil Backstube, Form aus dem conplot-Beispiel abgelesen (nicht gemessen), skaliert auf Verbrauch und Spitzenlast; andere Branchen BDEW-Standardprofile |
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
| Betriebskosten Speicher | etwa −3.000 (1,5 % von 200.926) | −1.386 (1,5 % von 92.400) |
| **Summe** | **2.936** (bis 3.171) | **+7.445** |

## Kosten und Ergebnis
| Punkt | conplot | Testseite |
|---|---|---|
| Investition | 200.926 € = 913 €/kWh | 92.400 € = 420 €/kWh (Staffel geschätzt) |
| Förderung | KfW 270 als Kredit wählbar | nur Hinweis |
| Amortisation | keine | 12,4 Jahre |
| Bewertung | 10 Jahre kumuliert 26.523 € | Barwert 12 Jahre bei 6 %: −29.981 € |

## Offene Fragen an conplot
1. Woraus setzen sich 913 €/kWh Investition zusammen?
2. Welcher Leistungspreis wird verwendet, und wird der Tarifwechsel bei 2.500 Stunden berücksichtigt?
3. Wie wird „Trading“ gerechnet, und warum liegt es bei etwa 200 €? (Der Nutzer sagt: keine Quelle.)
4. Welche Hochlastzeitfenster werden für e.wa riss angesetzt, und woher?
5. Woher stammt das Lastprofil (Quelle der Bäckerei-Form)?

## Einordnung
Der größte Unterschied im Ergebnis ist die Investition (913 gegen 420 €/kWh). Beim Netzentgelt liegt conplot bei einem
pauschalen Leistungspreis fast doppelt so hoch wie der echte Preis von e.wa riss. Verschieben und Handel sind bei beiden
unsicher; unser Wert liegt nah an der Obergrenze.
