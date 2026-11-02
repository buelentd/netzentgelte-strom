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
