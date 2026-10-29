# Aufgabe: Netzentgelte Strom 2026 aller Verteilnetzbetreiber

Zweck: Datenbasis für eine Infoseite mit Netzentgelt-Rechner für Gewerbe aller Art (Bäckerei,
Supermarkt, Imbiss, Systemgastronomie, Handwerk, Büro usw.). Der Nutzer gibt Standort,
Jahresverbrauch und ggf. Spitzenleistung ein und sieht, was er beim zuständigen Netzbetreiber
zahlt, auch als ct/kWh.

Für alle Stromverteilnetzbetreiber in Deutschland (ca. 850) die Netzentgelte 2026 erfassen:

- SLP (ohne Leistungsmessung, bis 100.000 kWh/Jahr): Arbeitspreis und Grundpreis Niederspannung
- RLM (mit Leistungsmessung, ab 100.000 kWh/Jahr): Jahresleistungspreissystem, Niederspannung
  und Umspannung MS/NS, jeweils unter und ab 2.500 Benutzungsstunden

Ohne Rückfragen durchlaufen lassen. Unklare Fälle nicht raten, sondern in die Restliste.

## Ergebnis

`ergebnis/netzentgelte_2026.csv`, Trennzeichen `;`, Dezimalkomma, alle Preise netto. Eine Zeile
pro Netzbetreiber bzw. Netzgebiet. Einheit im Spaltennamen. Alle Spalten erklärt in `LEGENDE.md`
(bei Änderungen aktualisieren).

- Stammdaten: nr; netzbetreiber; mastr_nr; website; bundesland; region; netztyp; status
- SLP Niederspannung: slp_ap_ct_kwh; slp_grundpreis_eur_jahr
- RLM NS: ns_lp_unter_2500h_eur_kw_jahr; ns_ap_unter_2500h_ct_kwh; ns_lp_ueber_2500h_eur_kw_jahr;
  ns_ap_ueber_2500h_ct_kwh
- RLM MS/NS: msns_… analog
- Berechnet: ns_ct_kwh_bei_1500h; …_2500h; …_4000h; …_6000h = AP + LP × 100 / h mit dem Tarif der
  passenden Gruppe laut Preisblatt, nur wenn die RLM-Werte ok sind
- Abschluss: preisstand (endgültig/vorläufig/unklar); stand_datum; hinweis; quelle_url

bundesland/region: Netzgebiet, sonst Sitz laut MaStR (dann im hinweis vermerken).
status: ok | pruefen | kein_preisblatt | blockiert | robots | keine_website.
PDFs nach `ergebnis/pdf/`, Restfälle nach `ergebnis/restliste.csv`. Fortschritt laufend speichern,
bereits Erledigte überspringen.

## Vorgehen

1. Netzbetreiber-Liste aus dem MaStR (`open-mastr`, Marktrolle Netzbetreiber Strom, nur
   Verteilnetzbetreiber): Name, MaStR-Nr., Website. Fehlt die Website: ermitteln oder keine_website.
2. `pilot_50_vnb_2026.csv`: 50 geprüfte Netzbetreiber mit RLM-NS-Werten und Quelle. Übernehmen,
   SLP und MS/NS aus derselben Quelle ergänzen, bei vorläufigen nach dem endgültigen Blatt suchen.
3. Preisblatt finden mit Playwright: Startseite, dann Links wie Netzentgelte, Netznutzung,
   Preisblatt, Marktpartner, Veröffentlichungen, Netzzugang. Gas, Wärme, Wasser, Einspeisung
   ausschließen. 2026 bevorzugen, endgültig vor vorläufig. Nicht 2027, nicht fiktiv, nicht nur
   § 14a, nicht nur § 19. Auch xlsx.
4. Auslesen ohne KI-API (`pdftotext -layout` bzw. pdfplumber):
   - RLM: Jahresleistungspreis-Tabelle < 2.500 / ≥ 2.500, Zeilen NS und Umspannung MS/NS
   - SLP: Abschnitt ohne Leistungsmessung / Standardlastprofil, Niederspannung, Standard-AP und
     Grundpreis (nicht Wärmepumpe, Speicherheizung, § 14a Modul 2/3)
5. Plausibilität, sonst pruefen: NS LP ab 2.500 h 40–260 €/kW/a; LP unter < LP ab; AP unter > AP ab;
   SLP-AP 3–15 ct/kWh; Grundpreis 0–200 €/a; Netzbetreibername im PDF.

## Bekannte Sonderfälle aus dem Pilot

- Tagesleistungspreise (€/kW/Tag) und Tagesgrundpreise (€/Tag): × 365 (enercity, NRM, Hamburg)
- Spalten im Textauszug vertauscht: Reihenfolge über die Kopfzeile (Mittelrhein, WEMAG)
- Links per JavaScript (SachsenNetze `evd-link`, Hamburg filehub.admiralcloud.com) → DOM lesen
- Mehrere Netzgebiete pro Betreiber: je Gebiet eine Zeile (wesernetz, SachsenNetze)
- SLP-Preise teils in separatem Preisblatt (SachsenNetze: "Standardlastprofil-Kunden")
- Umbenennungen: Netrion → MVV Netze, Netze Mittelbaden → E-Werk Netze
- Datei "Aktuell" kann veraltet sein (Bochum: 2024) → Jahr im PDF prüfen
- PDF ohne Netzbetreibernamen (storyblok) → pruefen
- Grenze "≤ 2.500 / > 2.500" statt "< / ≥" → im hinweis vermerken

## Rechner (`vnb/rechner.py`)

Manuelle Eingabe (Netzbetreiber bzw. PLZ, kWh, optional kW; sonst Branchen-Benutzungsstunden als
Annahme) oder Lastprofil (CSV/xlsx, 15 min oder 1 h, kW oder kWh, Europe/Berlin mit
Zeitumstellung, Hochrechnung bei Teiljahr, Lücken/Ausreißer melden, unklare Einheit → Rückfrage).
Tarifwahl: < 100.000 kWh ohne Leistungsmessung → SLP, sonst RLM NS bzw. MS/NS nach
Benutzungsstunden. Ausgabe: €/Jahr, ct/kWh, Leistungs-/Arbeitsanteil, Tarif mit Begründung,
Ersparnis je kW, Hinweis auf Tarifwechsel durch Spitzenkappung.

## Regeln

- robots.txt beachten; gesperrte Pfade → status robots
- Langsam: max. 1 Anfrage pro Sekunde je Domain, max. 40 Seiten je Website, Timeout 30 s
- PDFs nur maschinell auslesen, nicht öffnen
- Nichts schätzen: lieber leer lassen und in die Restliste
- Zusammenfassung: Anzahl je Status, Spanne SLP-AP und NS ct/kWh bei 4.000 h, Restfälle

## Umsetzung

Repository `buelentd/netzentgelte-strom`, Code im Wurzelverzeichnis: `run.py` und `vnb/`, Bedienung in README.md, Spalten in LEGENDE.md.
Tests: `python -m pytest -q tests`. Lauf über GitHub Actions (`.github/workflows/netzentgelte.yml`),
weil die Claude-Code-Cloud-Umgebung Netzbetreiber-Websites und MaStR sperrt.
