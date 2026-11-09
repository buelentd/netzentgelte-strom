# Testanleitung Rechner und Dateninfo (Stand 06.11.2026)

Seite: https://claude.ai/artifact/J8UnVGkS6kvUFdF2WFZMiL (privat, Freigabe über Share). Datenbasis: `ergebnis/netzentgelte_2026.csv`.

## 1. Was du eingeben sollst (6 Testfälle)

Reihenfolge der Felder: PLZ → Netzbetreiber anklicken → Jahresverbrauch → optional Spitzenlast → Anlagen-Text.

| # | Fall | PLZ | kWh/Jahr | kW | Erwartung |
|---|---|---|---|---|---|
| 1 | Imbiss | 10115 (Stromnetz Berlin) | 40.000 | leer | Tarif Standardlastprofil: Grundpreis 33,36 €, Arbeitspreis 7,46 ct, rund 3.017 € / Jahr, 7,54 ct/kWh. Hinweis „Spitzenkappung spart hier kein Netzentgelt". |
| 2 | Handwerk knapp unter der Grenze | 10115 | 95.000 | leer | Weiter Standardlastprofil: rund 7.120 € / Jahr, 7,50 ct/kWh. |
| 3 | Bäckerei Grenzfall | 10115 | 120.000 | leer | Über 100.000 kWh: Leistungsmessung (RLM). Ohne Spitzenlast rechnet die Seite mit einer Branchen-Annahme für die Benutzungsstunden. |
| 4 | Bäckerei Meerane | 08393 (Stadtwerke Meerane) | 150.000 | 45 | RLM Niederspannung, Speicher-Abschnitt: Zielspitze 35 statt 45 kW, Spitze senken 1.335 €. „Hochlastzeitfenster: Werte nicht vorhanden" (Meerane hat keine). |
| 5 | Supermarkt | 10115 | 450.000 | 150 | RLM (Leistungspreis 93,87 €/kW, 3,72 ct, rund 30.800 €/Jahr), Zielspitze 136 statt 150 kW, atypische Netznutzung „voraussichtlich erfüllt", Speicher lohnt sich bei diesen Angaben nicht (Barwert negativ, der alte Fehler ist behoben). |
| 6 | Netzbetreiber ohne geprüfte Werte | 29614 (Stadtwerke Soltau) | beliebig | beliebig | Meldung „Für diese Postleitzahl liegen noch keine geprüften Netzentgelte vor“ (Soltau hat nur SLP, keine Niederspannung mit Leistungsmessung). 14770 (Brandenburg an der Havel) hat jetzt Werte und wird normal gerechnet. |

Zusätzlich anschauen:
- Den Button **Bäckerei Friedrichshafen (mit Hochlastzeitfenstern)** oben auf der Seite. Dort wird die Prüfung der atypischen Netznutzung gezeigt.
- Im Feld Anlagen den Text `2 Etagenöfen je 36 kW, laufen morgens 4–7 Uhr; Kältemaschine 12 kW` eintragen: Die Seite liest daraus Anlagen und prüft sie gegen die Hochlastzeitfenster.
- Einen Test mit **dynamischem Tarif**: Stromtarif auf „dynamisch" stellen, die Speicherzahlen verändern sich (Verschiebung in billige Stunden).

Meldet mir pro Auffälligkeit: Netzbetreiber, PLZ, kWh, kW und was nicht stimmt. Ich suche es im Dokument.

## 2. Welche Daten die Seite zeigt und woher sie kommen

| Angezeigt | Quelle | Stand | Verlässlichkeit |
|---|---|---|---|
| Netzbetreiber je Postleitzahl (8.164 PLZ) | VNBdigital (Zuordnung PLZ zu Netzbetreiber, Anteile in %) | 2026 | Bei mehreren Netzbetreibern je PLZ wählt der Nutzer. Nur Betreiber mit geprüften Werten werden angeboten. |
| Grundpreis und Arbeitspreis SLP (Standardlastprofil) | Preisblatt 2026 des Netzbetreibers | 2026, vorläufig oder endgültig (im Ergebnis ausgewiesen) | Netto. Bei Status „ok" am Dokument bestätigt. |
| Leistungspreis und Arbeitspreis RLM (NS, MS/NS, MS, HS/MS), unter und ab 2.500 h | Preisblatt 2026 des Netzbetreibers | wie oben | Netto, €/kW/Jahr und ct/kWh. Grenze „≤ / >" statt „< / ≥" ist im Hinweis vermerkt. |
| Tarifwahl SLP gegen RLM | Regel: unter 100.000 kWh ohne Leistungsmessung SLP, sonst RLM nach Benutzungsstunden | – | Rechenlogik, 186 Tests |
| Netzentgelt €/Jahr und ct/kWh, Leistungs- und Arbeitsanteil | Berechnung aus den Preisblattwerten | – | Ohne Strom, Messstellenbetrieb, Konzessionsabgabe, Umlagen, Umsatzsteuer |
| Preisstand und Datenstand | Dokument (vorläufig oder endgültig) | pro Netzbetreiber | Bei „vorläufig" können sich Werte ändern |
| Typische Spitzenzeit nach Branche | BDEW-Standardlastprofil G5 (Bäckerei mit Backstube) und weitere | BDEW | Durchschnitt vieler Betriebe, nicht gemessen |
| Hochlastzeitfenster und Schwellen (atypische Netznutzung) | Veröffentlichung des Netzbetreibers 2026 (NS und MS/NS je Jahreszeit), Erheblichkeitsschwelle, Mindestverlagerung | 2026 | Für 541 Netzbetreiber vorhanden, sonst „Werte nicht vorhanden". Bei Mehrfachtabellen von Hand abgelesen. |
| Börsenpreis (Day-Ahead DE-LU, EPEX-Markt) | ENTSO-E und Energy-Charts, Stundenwerte aus Viertelstunden | bis 01.11.2026 | Belegt. Aktualisierung einmal am Tag, sobald das GitHub-Billing läuft. |
| Strompreis ohne Netzentgelt | Börsenmittel + Aufschlag Anbieter + Steuern und Umlagen | – | Aufschlag 2,5 ct ist eine Annahme, Steuern und Umlagen 3,11 ct sind 2026 belegt. Beides änderbar. |
| Solarertrag je Bundesland | PVGIS (EU-Kommission) | Typjahr | Belegt, regionale Mittelwerte |
| Dachfläche aus Adresse | Beispieldaten der Google Solar API (7 Adressen) | – | Nur Beispiele, bitte Gebäude prüfen |
| Einspeisevergütung | Bundesnetzagentur, Inbetriebnahme ab 08/2026, Teileinspeisung | 2026 | Über 100 kWp Direktvermarktung (Marktwert Solar 4,51 ct plus Prämie) |
| Regelenergie (aFRR, FCR): Leistungspreis je MW und Jahr | regelleistung.net, Mittel der letzten 365 Tage | bis 01.11.2026 | Belegt (aFRR 204.000, FCR 148.800 €/MW). Schwankt stark nach Monat. |
| Lastprofil für Solar- und Speicherrechnung | BDEW-Profil G5 für Bäckerei, andere Branchen: weitere BDEW-Profile; optional Testprofil | BDEW | Profil, nicht gemessen. Eigenes Lastprofil im Rechner (`vnb/rechner.py`) möglich. |
| Speicherpreis 450 €/kWh | Richtwert, ohne Quelle | – | Eigene Annahme. Angebot einholen. |
| Kapazitätsabbau 2,5 %, Entsorgung 75 €/kWh | von conplot übernommen | – | Nicht belegt |
| Wirkungsgrad 0,92, 2 Stunden Dauer, 1,5 Ladungen/Tag, 80 % nutzbar | wie conplot | – | Modellannahmen |
| Zinssatz 6 %, Barwert über 12 Jahre | Annahme | – | Änderbar |
| Datengüte-Balken | Berechnung aus den Angaben (sicher / geschätzt) | – | Zeigt, wie viel der Nutzer selbst eingibt |

## 3. Was die Seite nicht zeigt

- Hochspannung direkt (HS) ist nicht erfasst.
- Strompreise einzelner Anbieter und Tarife (nur Börse plus Annahmen).
- Messstellenbetrieb, Konzessionsabgabe, Umlagen und Umsatzsteuer bei den Netzentgelten.
- Netzbetreiber mit Status „prüfen" erscheinen nur, wenn die Werte für den gewählten Anschluss vollständig sind.

- PLZ 39326 bietet zwei Netzbetreiber an (Avacon 67 %, Wolmirstedt 33 %): bei „Stadtwerke Wolmirstedt“ gilt SLP 7,90 ct und 60 € Grundpreis (3.220 € bei 40.000 kWh), bei Avacon 6,04 ct und 80,30 € (2.496 €).
