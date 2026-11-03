# Stand Netzentgelte Strom 2026 (31.10.2026, 19:15 Uhr)

## Ergebnis

**566 von 831 Netzbetreibern sind nutzbar** (mindestens ein Teil der Preise geprüft und plausibel).

| | Anzahl |
|---|---:|
| Vollständig: Standardlastprofil und registrierende Leistungsmessung | 375 |
| Nur registrierende Leistungsmessung | 117 |
| Nur Standardlastprofil | 74 |
| **Nutzbar zusammen** | **566** |
| Preisblatt vorhanden, Werte aber auffällig oder unvollständig | 19 |
| Kein Preisblatt gefunden | 184 |
| Website blockiert automatische Abrufe | 38 |
| robots.txt verbietet den Abruf | 23 |
| Keine Website | 1 |

Spannen (nur geprüfte Werte):

- Standardlastprofil, Arbeitspreis Niederspannung: 3,17 bis 14,98 Cent pro Kilowattstunde, Median 7,28 (449 Netzbetreiber)
- Registrierende Leistungsmessung Niederspannung bei 4.000 Benutzungsstunden: 2,80 bis 14,46 Cent pro Kilowattstunde, Median 6,34 (492 Netzbetreiber)

Preisstand der vollständigen: unklar 215, endgültig 132, vorläufig 28.

Dateien:

- `ergebnis/netzentgelte_2026.csv`: alle 831, Spalten erklärt in `LEGENDE.md`
- `ergebnis/gefunden.csv`: die nutzbaren, mit Quelle je Preisart
- `ergebnis/nicht_gefunden.csv`: die übrigen, mit Grund
- `ergebnis/zusammenfassung.md`: Zahlen je Status und Spannen

## Verlauf heute

| Schritt | Nutzbar |
|---|---:|
| Morgens (Lauf 18) | 467 |
| Hochgeladene Preisblätter (Westnetz, Bayernwerk, E.DIS, Schleswig-Holstein Netz, Syna, Stuttgart, Avacon) und Verbesserungen beim Auslesen | 491 |
| Brave-Suche, erster Suchbegriff (Lauf 30) | 504 |
| Korrektur „vermiedene Netzentgelte“ und Suchbegriff mit Jahr (Lauf 32) | 509 |
| Auslesen verbessert (Nordhausen, Borken, Schwäbisch Hall, ÜZ Mainfranken, e.wa riss, Ratingen und andere), neu ausgelesen (Lauf 33) | 517 |
| Bekannte Preisblätter direkt neu geladen (Lauf 34), 22 weitere vollständig | 522 |
| Unklare Umspannung macht Niederspannung nicht mehr unbrauchbar (Lauf 35) | 526 |
| Grenze „bis zu / mehr als 2.500“ und über mehrere Kopfzeilen verteilte Grenzen (Lauf 36), 18 weitere vollständig | 527 |
| Preisblatt ohne Namen von der eigenen Website gilt als zugeordnet (Lauf 37) | 566 |

## Was die Brave-Suche gebracht hat

- Suchbegriff jetzt: `<Name ohne Rechtsform> netzentgelte strom 2026 pdf`, nur PDFs von der eigenen Website.
- Lauf 30: 141 Netzbetreiber mit Treffern, 432 PDFs, daraus 13 neu nutzbar.
- Lauf 32: 96 Netzbetreiber mit Treffern, 278 PDFs, daraus 5 neu nutzbar.
- Der Großteil der Treffer sind **ältere Preisblätter** (2025 und früher), auch mit „2026“ im Suchbegriff:
  151 von 278 PDFs in Lauf 32. Dazu kommen Stromtarife für Endkunden, Hausanschluss- und
  Messstellenpreisblätter und tote Links.
- Brave-Guthaben: etwa 4,98 von 5,00 US-Dollar verbraucht. Der Abrechnungszeitraum endet am 01.11.2026.
  9 Netzbetreiber ohne Preisblatt wurden wegen der Höchstzahl von 185 Abfragen nicht mehr gesucht.

## Offene Punkte, nach Nutzen geordnet

1. **Weitere Lücken beim Auslesen.** 210 Netzbetreiber haben ein Preisblatt, bei dem ein Teil fehlt oder
   auffällig ist (Liste: `ergebnis/nicht_gefunden.csv`, Status `pruefen`). Arbeit an den Textauszügen, danach
   `AUSLESEN=true` (Minuten, ohne Internet). Jede Änderung gegen alle Textauszüge abgleichen (keine Verluste).
2. **Ramstein:** Drei Netzbetreiber mit derselben Website (Ramstein, Bruchmühlbach-Miesau, Weilerbach); die Regel
   „Zuordnung unklar“ hat Ramstein den Standardlastprofil-Teil genommen. Künftig verliert ein Netzbetreiber beim
   Neu-Laden oder Neu-Auslesen keinen nutzbaren Teil mehr.
3. **Netzgesellschaft mit eigener Adresse.** Beispiel Aschaffenburg: Im Marktstammdatenregister steht
   `www.stwab.de`, die Preisblätter liegen auf `www.netze-stwab.de`. Vorschlag: Als eigene Website gilt auch
   eine Adresse, die den Kern der bekannten Adresse enthält (mindestens 5 Zeichen). Für Aschaffenburg liegen
   die Links vor:
   - https://www.netze-stwab.de/Stromnetz/Netzzugang-Entgelte/AVG-Preisblatt-2026-Netznutzung-mit-Leistungsmessung.pdf
   - https://www.netze-stwab.de/Stromnetz/Netzzugang-Entgelte.html
4. **184 ohne Preisblatt.** Die Suche liefert hier meist alte Jahre. Weiter nur von Hand: Link in
   `lauf/hinweis_urls.csv` eintragen oder PDF in `lauf/preisblaetter/` ablegen und in `lauf/preisblaetter.csv`
   zuordnen (Beispiele dort).
5. **38 blockiert und 23 robots.txt:** nur von Hand (PDF herunterladen und ablegen wie in Punkt 4).
6. **Preisblätter 2027.** Ist für ein Netzbetreiber kein Blatt 2026 auffindbar, wird jetzt das Blatt 2027 mit
   Hinweis genommen. Für eine eigene Tabelle 2027 braucht es noch einen eigenen Ergebnisordner je Jahr
   (sonst vermischen sich die Fortschrittsdateien) und den Ausschluss der Pilotwerte 2026.

## Bedienung (Kurzfassung, Einzelheiten in README.md)

Ein Lauf startet bei jeder gepushten Änderung an `lauf/anstoss.env`. Wichtige Einstellungen:

| Einstellung | Wirkung |
|---|---|
| `WIEDERHOLEN=kein_preisblatt` | welche Status erneut bearbeitet werden |
| `NUR_SUCHTREFFER=true` | nur Brave-Treffer und Hinweis-Links prüfen, Websites nicht durchsuchen (etwa 20 Minuten) |
| `AUSLESEN=true` | nur die schon geladenen Preisblätter neu auslesen, ohne Internet (Minuten) |
| `SUCHE_MAX=185` | Höchstzahl Brave-Abfragen je Lauf (Kosten: 5 US-Dollar je 1.000) |
| `NEU_PRUEFEN=` | Nummern, die unabhängig vom Status neu bearbeitet werden; nach Gebrauch leeren |

Ein Ergebnis wird in den Modi `NUR_SUCHTREFFER` und `AUSLESEN` nur übernommen, wenn es besser ist als das
bisherige. Der Fortschritt im Repository hat Vorrang vor dem Zwischenspeicher des Laufs.

## Bekannte Fehler von heute (behoben)

- Ein älterer Zwischenspeicher hat den gespeicherten Fortschritt überschrieben (Lauf 29): Ergebnisse der Läufe
  25 und 28 gingen verloren und wurden zusammengeführt.
- Die Liste „schon gesucht“ hat einen Lauf mit neuem Suchbegriff komplett übersprungen (Lauf 31). Entfernt.
- Eine Anmerkung zu vermiedenen Netzentgelten im Kopf hat echte Preisblätter verworfen (Butzbach, OVAG).
- Suchtreffer fremder Netzbetreiber wurden geprüft (REDINET). Jetzt nur eigene Website.

## Nachtrag 01.11.2026: conplot.de

Ziel: Die Netzentgelte fließen in den Rechner „Was ein Batteriespeicher in Ihrem Betrieb spart“ auf
https://www.conplot.de/webanwendung.html (geführte Abschätzung, Schritt 2 Szenario und Ergebnis).

- **Datensatz für conplot:** `ergebnis/conplot/netzbetreiber_2026.json`, `plz_2026.json`, Beschreibung und
  Rechenweg in `ergebnis/conplot/FORMAT.md`. Erzeugen mit `python run.py export`.
- **Hochlastzeitfenster 2026:** `ergebnis/hochlastzeitfenster_2026.csv` (112 nutzbare Netzbetreiber mit
  Niederspannung), gelesen mit `vnb/hlzf.py` aus vorhandenen Textauszügen (`python run.py hlzf --texte …`).
- **Testseite** (Nachbau der geführten Abschätzung mit unseren Daten): https://claude.ai/artifact/J8UnVGkS6kvUFdF2WFZMiL
  Quelltext `conplot_testseite/vorlage.html`, bauen mit `python conplot_testseite/bauen.py`, dann mit dieser URL
  als Artifact aktualisieren. Postleitzahl-Vorschläge nur für Postleitzahlen mit geprüften Preisen.
- **Befund bei conplot:** Ein pauschaler Leistungspreis von 12,5 € je kW und Monat (150 € je kW und Jahr)
  überschätzt die Ersparnis durch Spitzenkappung bei Kunden mit wenig Benutzungsstunden um ein Mehrfaches
  (Beispiel Meerane: 3.771 statt 15.000 € pro Jahr). Tarifwechsel bei 2.500 h und echte Hochlastzeitfenster
  fehlen; der Speicher lädt im Modell teils innerhalb der Hochlastzeitfenster nach; Preispfad startet 2025.

Nächste Schritte:
1. Lauf für die Hochlastzeitfenster der übrigen rund 450 nutzbaren Netzbetreiber: pro Netzbetreiber eine
   Brave-Suche `site:<Website> hochlastzeitfenster 2026`, nur Treffer prüfen (noch einzubauen).
2. Preise für die fehlenden Netzbetreiber (Suchmuster mit `site:` und Netzentgelt-Seiten aus den Treffern).
3. Abstimmung mit conplot: Leistungspreis-Feld durch den Datensatz ersetzen, Basisjahr 2026, Strompreis ohne
   Netzentgelt, Nachladen nur außerhalb der Hochlastzeitfenster.

## Nächster Ausbau der Testseite (beschlossen 02.11.2026)

Ergebnis als Balkendiagramm mit 5 Säulen (Euro pro Jahr, plus oder minus) und Summe:
1. Spitze senken (fertig) 2. Atypische Netznutzung (fertig) 3. Eigenverbrauch Solar (mit Anlage: kWp und
Ausrichtung; ohne: Dachfläche, etwa 6–7 m² je kWp) 4. Börsenhandel 5. Regelenergie.
Regeln: erst Spitze senken, dann Solar, dann Handel/Regelenergie mit Restkapazität; nie im
Hochlastzeitfenster nachladen; höchstens 1,5 Ladungen pro Tag (conplot: 10–90 %, 2 h, Wirkungsgrad 0,92).
Daten: Lastprofile in daten/lastprofile/; fehlen: Börsenpreise 2025 stündlich (Energy-Charts, später
ENTSO-E) und Solarertrag je Region (PVGIS), beide über einen GitHub-Lauf holen; Einspeisevergütung;
Speicher- und Solarpreise (Anbieter). Mit Sonnet arbeiten, kurz antworten.

## Stand der Testseite (02.11.2026, abends)

Aktuelle Adresse: https://claude.ai/artifact/AuKrxs6bAcwhuacUp7LTDA (Version 8). Quelltext
`conplot_testseite/vorlage.html`, bauen mit `python conplot_testseite/bauen.py`. Die ältere Adresse im Nachtrag
oben (J8UnVGkS6kvUFdF2WFZMiL) ist überholt.

### Fertig und belegt
| Posten | Wert | Quelle |
|---|---|---|
| Netzentgelte, Hochlastzeitfenster | je Netzbetreiber, 2026 | eigene Erfassung (566 von 831 nutzbar, 112 mit Hochlastzeitfenstern) |
| Börsenpreise stündlich | Mittel 11,2 ct/kWh (1.11.2025 bis 31.10.2026) | ENTSO-E, mit Energy-Charts verglichen |
| Solarertrag je Bundesland | 12 Monate mal 24 Stunden je kWp | PVGIS |
| Regelenergie (Frequenzhaltung) | 148.800 € je MW und Jahr, Mittel von 365 Tagen; Winter 58.000 bis 86.000, Sommer über 200.000 | regelleistung.net, `daten/fcr_roh.json` |
| Umlagen 2026 | Kraft-Wärme-Kopplung 0,446, Offshore 0,941, besondere Netznutzung 1,559, Konzessionsabgabe 0,11 ct/kWh | EHA, Strom-Report, Cleanthinking (BDEW), Vattenfall |
| Stromsteuer | 0,05 ct/kWh nach Entlastung (nur produzierendes Gewerbe: Bäckerei mit Backstube, Handwerk, Produktion), sonst 2,05; Voreinstellung nach Branche, Summe der Abgaben 3,11 bzw. 5,11 ct | Bundesregierung, Vattenfall, b2b energy |
| Einspeisevergütung | gestaffelt 7,70 / 6,66 / 5,44 ct (bis 10 / 40 / 100 kW), Teileinspeisung, Inbetriebnahme ab 1.8.2026; über 100 kW näherungsweise 5,44 | Bundesnetzagentur |

### Richtwerte ohne gute Quelle (auf der Seite so gekennzeichnet)
- Aufschlag des Stromanbieters 2,5 ct/kWh (Haushalte belegt 3,5 bis 4, Gewerbe 1 bis 3 ohne Quelle).
- Speicherpreis: bis 100 kWh 450 €/kWh, danach sinkend auf 350 €/kWh bei 500 kWh. Die Staffel ist geschätzt;
  belegt sind Gewerbe 100 kWh 410 bis 450 und Heimspeicher 500 bis 800 installiert.
- Solaranlage 1.100 €/kWp netto (Spanne 800 bis 1.300 für 30 bis 100 kWp), Betrieb 2 % der Investition im Jahr.
- Spitzenlast: aus Branchenprofil geschätzt (größte Unsicherheit), nur mit Netzrechnung genau.
- Ladeverluste bei der Spitzenkappung: Annahme täglicher Kappung (zu optimistisch).
- Verfügbarkeit Regelenergie 50 %, Vermarkteranteil 20 %.

### Neu heute
- Regelenergie aus 365 Tagen statt zwei Stichproben; Abgaben und Einspeisevergütung belegt statt Platzhalter.
- Speicherpreis nach Größe gestaffelt; Solaranlage (neu, aus Dachfläche oder kWp) mit Kosten und Barwert über 20 Jahre,
  zusammen mit dem Speicher dargestellt.
- Beispiel Bäckerei Biberach (150.000 kWh, dynamischer Tarif, 75 kWh): Summe der Säulen etwa 2.750 € im Jahr,
  Barwert des Speichers negativ (etwa −6.300 € mit gestaffeltem Preis). Mit neuer Anlage (400 m², 62 kWp) trägt
  die Anlage selbst (Barwert etwa +94.000 € über 20 Jahre), der Speicher bleibt negativ.

### Was noch fehlt
1. **Netzentgelte 2027:** Die Preisblätter 2027 mussten bis 15.10.2026 erscheinen. Entscheidung offen, ob die
   Datenbasis auf 2027 umgestellt wird (großer Lauf über alle Netzbetreiber). Der Bundeszuschuss sinkt 2027 bis 2029
   auf 5,525 Mrd. € (Kabinettsbeschluss, noch kein Gesetz), Netzentgelte dürften steigen.
2. **Hochlastzeitfenster** für die übrigen etwa 450 nutzbaren Netzbetreiber (Brave-Lauf, rund 2,25 USD, braucht Ok).
3. **Preise der fehlenden 265 Netzbetreiber.**
4. **Belegte Gewerbe-Speicherpreise** (Angebote, nicht nur Ratgeber); Gewerbe-Aufschlag des Stromanbieters aus
   echten Rechnungen.
5. **Spitzenlast als Spanne** aus den Lastprofilen (Untergrenze Profil, Obergrenze Branche); Lastprofil-Upload.
6. **Förderung:** bundesweit nur Kredit (KfW 270, in Baden-Württemberg zusätzlich L-Bank); Zuschüsse regional,
   für Gewerbe aktuell keine in Baden-Württemberg. Steuerwirkung (Abschreibung, § 7g EStG) nicht eingerechnet.
7. **Strompreisentwicklung:** Börse zuletzt 14 bis 17 ct/kWh (Sept./Okt. 2026), Jahresmittel 11,2; Rechnung nutzt
   das Jahresmittel, keine Preispfade über 12 Jahre.
8. **Stromsteuer-Entlastung** gilt nur für die Produktionsmenge; Mischbetriebe müssen den Wert anpassen
   (Hinweis am Feld, kein Eingabefeld für den Anteil).
9. **Google Solar API** live einbinden (Schlüssel nie im Browser, Ergebnisse nicht speichern) und Gespräch mit
   conplot: Herkunft von `demand_charge_kw_month`, Datensatz ersetzen, Basisjahr, Nachladen nur außerhalb der
   Hochlastzeitfenster, Strompreis ohne Netzentgelt.
10. Aufräumen: `regelenergie()` in `daten/holen.py` und `daten/regelenergie.json` (ENTSO-E-Versuch, ungültig) entfernen;
    ENTSO-E gegen Energy-Charts: 991 Viertelstunden mit mehr als 0,5 ct Abweichung nicht untersucht.
11. Annahmen im Sonnenstrom-Teil: Einspeisung über 100 kWp läuft über Direktvermarktung (Marktprämie), hier nur näherungsweise.

### Nachtrag 02.11.2026 (Vergleich mit conplot, Biberach 150.000 kWh, 111 kW, 220 kWh)
conplot: Investition 200.926 € (913 €/kWh), Kappung 111 auf 50 kW, Netzentgelt-Ersparnis 3.639 €/J (Balken Netzentgelt
etwa 6.600 €, Betriebskosten etwa −3.000 €, Trading etwa +200 €), Ergebnis 2.936 €/J, keine Amortisation.
Umgesetzt danach: (1) beste Zielspitze je Speichergröße statt fest 20 % (Biberach 220 kWh: 45 kW, conplot 50 kW);
(2) Betriebskosten Speicher 1,5 % der Investition; (3) Bäckerei-Lastprofil, geschätzt, Form aus einem conplot-Beispiel abgelesen (5 kW Grundlast, 4:30–7:30 Uhr
95 kW, 2–4:30 und 7:30–11:30 Uhr 19 kW).
Ergebnis unserer Seite danach (220 kWh, dynamisch): Spitze senken +3.346, Verschieben +3.867, Regelenergie +1.619,
Betriebskosten −1.386, Summe +7.445 €/J, Barwert −29.981 €.
Offen aus dem Vergleich: conplot-Balken Netzentgelt 6.600 € lässt vermuten, dass dort ein pauschaler Leistungspreis
(etwa 108 €/kW) gilt, nicht e.wa riss mit 31,80/176 €/kW (unbestätigt, bei conplot erfragen); 913 €/kWh Investition
erklären lassen; Hochlastzeitfenster e.wa riss Winter: conplot-Grafik etwa 8:00–12:45 und 16:00–18:45, unsere Auslesung
12:00–13:30 und 16:15–19:15, gegen das Original prüfen (PDF aus dieser Umgebung nicht abrufbar); Handel/Verschieben
bei uns (3.867) viel höher als bei conplot (200), Ursache offen (Optimierer, Regelleistung bei conplot abgewählt).

### Morgen weiter (Stand 02.11.2026, spätabends)
1. Kapazitätsabbau 2,5 % je Jahr und Entsorgung 75 €/kWh in den Barwert einbauen (Werte von conplot, nicht belegt).
   Rechenbeispiel Biberach 220 kWh: Barwert −29.981 € heute, −37.490 € mit Abbau, −45.690 € mit Entsorgung.
   Zyklen: 6.000 Zyklen bei 1,5 pro Tag halten etwa 11 Jahre (daher die 12 Jahre).
2. Handelswege FCR, aFRR, Day-Ahead je MW vergleichen, nicht addieren, mit Erklärung auf der Seite. Day-Ahead aus unseren
   Preisen: etwa 79.000 €/MW und Jahr brutto (Obergrenze), conplot 91.000. aFRR: echte Preise von regelleistung.net für
   365 Tage holen (Lauf, braucht Ok); conplot 146.000 vermutlich zu hoch (Markt sinkt, nur Modellrechnungen gefunden).
3. Fragen an conplot (siehe `ergebnis/conplot/VERGLEICH.md`); Hochlastzeitfenster e.wa riss gegen das Preisblatt prüfen.
4. Preisblätter mit auffälligem Datum prüfen (Nr. 13 TEN, 137 ENA Apolda, 562 Wittenberg).
5. Danach: Entscheidung Netzentgelte 2027, Hochlastzeitfenster für weitere Netzbetreiber (Brave-Lauf, Ok nötig).

### Nachtrag 03.11.2026
- Barwert mit Kapazitätsabbau (2,5 %/Jahr) und Entsorgung (75 €/kWh), Werte von conplot, nicht belegt (Biberach 220 kWh: −45.688 €).
- aFRR gemessen (`daten/afrr_roh.json`, 365 Tage, Einheit €/MW und Stunde je 4-Stunden-Block): Grenzpreis Aufwärts 133.115 + Abwärts
  154.343 = 287.458 €/MW und Jahr; Durchschnittsgebot 204.373. Monatlich stark schwankend (April 533.000, Oktober 196.000,
  November 88.000 hochgerechnet). Meine frühere Aussage, conplots aFRR-Wert (146.000) sei „vermutlich zu hoch“, war falsch:
  gemessen liegt aFRR im Jahresmittel darüber, aber der Trend ist fallend.
- Testseite: Block „Drei Handelswege für dieselbe Batterieleistung (nicht addieren)“: FCR 148.800, aFRR 204.000, Day-Ahead 79.176 €/MW und Jahr.
- conplot-Schnittstelle „Site Intelligence“ (POST /api/v1/site-intelligence/analyze) kombiniert MaStR, VNB-Datenbank und Förderdaten;
  VNB-Prozessdatenbank = „Netzentgelt-Strukturen und Anschlussfristen pro Netzbetreiber“; Funktion get_vnb_process(process_key, storage_kw).
  Mögliche Quelle der VNB-Daten: vnb-monitoring.org (Karte mit 793 VNB: Smart-Meter-Quote, Anzahl Zähler, Netzentgelte 2026,
  Unterbrechungsdauer 2024, Anschlussdauer 2024), noch nicht bestätigt; die Seite ist aus dieser Umgebung nicht abrufbar.

### Netztransparenz (03.11.2026)
- Zugang funktioniert (Client_ID als Secret `NETZ_TRANSPARENZ_ID`, Client_Secret als `NETZ_TRANSPARENZ`). Skript `daten/netztransparenz.py`
  (Modi pruefen, holen), Workflow `.github/workflows/netztransparenz.yml`, Auslöser `lauf/netztransparenz.env`. Die Schnittstelle liefert
  keine Umlagesätze, nur Marktdaten.
- Jahresmarktwerte funktionieren: `Jahresmarktpraemie/2025` ergibt JW 8,932, Wind an Land 7,441, Wind auf See 8,059, **Solar 4,508 ct/kWh**.
  Monatsmarktwerte: `marktpraemie` erwartet Monat/Jahr als getrennte Zahlen (Fehlermeldung: monthFrom 1 bis 12), Reihenfolge noch zu klären.
- `NegativePreise/1`: 94 % der Stunden „Ja“, unplausibel (die Bedeutung des Produkts ist unklar); nicht verwenden. Aus unseren Börsenpreisen:
  409 Stunden (4,7 %) unter 0, im Mittel −1,99 ct/kWh.
- Aktivierte aFRR (`daten/ntp_afrr_aktiviert.csv`, Viertelstunden, MW): Mittel positiv 60,5 MW, negativ 72,0 MW bei zugeteilter Leistung
  von im Mittel 2.031 / 1.852 MW: Auslastung etwa 3,0 % / 3,9 %. Die Energiepreise (Arbeitspreis) fehlen, daher noch kein Erlös daraus.
- Testseite (03.11.2026): Einspeisung über 100 kWp als Direktvermarktung: anzulegender Wert 5,84 ct minus Gebühr (eigene Annahme 0,4 ct, nicht belegt);
  Marktwert Solar 2025 4,508 ct/kWh als Hinweis. Beispiel Biberach, Dach 400 m² (62 kWp): Eigenverbrauch mit dem neuen Backstubenprofil
  nur 33.378 kWh (vorher mit G5 57.466), Barwert der Anlage +42.387 € (vorher +93.960 €): Das Ergebnis der Anlage hängt stark vom Tagesprofil ab.
