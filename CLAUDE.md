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
- RLM NS: ns_lp_unter_2500h_eur_kw_jahr; ns_ap_unter_2500h_ct_kwh; ns_lp_ab_2500h_eur_kw_jahr;
  ns_ap_ab_2500h_ct_kwh
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
5. Plausibilität, sonst pruefen: NS LP ab 2.500 h 40–500 €/kW/a (Dokumentprüfung 05.11.2026: echte Werte bis 463, z. B. Eisleben, Barmstedt); LP unter < LP ab; AP unter > AP ab;
   SLP-AP 3–15 ct/kWh; Grundpreis 0–200 €/a; Netzbetreibername im PDF.

## Bekannte Sonderfälle aus dem Pilot

- Tagesleistungspreise (€/kW/Tag) und Tagesgrundpreise (€/Tag): × 365 (enercity, NRM, Hamburg)
- Spalten im Textauszug vertauscht: Reihenfolge über die Kopfzeile (Mittelrhein, WEMAG)
- Links per JavaScript (SachsenNetze `evd-link`, Hamburg filehub.admiralcloud.com) → DOM lesen
- Mehrere Netzgebiete pro Betreiber: je Gebiet eine Zeile (wesernetz, SachsenNetze)
- SLP-Preise teils in separatem Preisblatt (SachsenNetze: "Standardlastprofil-Kunden")
- Umbenennungen: Netrion → MVV Netze, Netze Mittelbaden → E-Werk Netze
- Datei "Aktuell" kann veraltet sein (Bochum: 2024) → Jahr im PDF prüfen
- PDF ohne Netzbetreibernamen (storyblok) → pruefen; liegt es auf der eigenen Website des Netzbetreibers (laut MaStR, nicht bei geteilter Website), gilt es als zugeordnet (Hinweis „Name nicht im Dokument, Preisblatt von der eigenen Website“)
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

## Regel: HTML immer mitdenken (Festlegung Nutzer, 04.11.2026)

Bei jeder Suche im Netz gelten HTML-Seiten genauso wie PDF und Excel: Preise können als Tabelle in einer Webseite, in einem Portal (EnWG-Tool, Netzveröffentlichung) oder auf einer sichtbaren Sitemap-Seite stehen. Das gilt für Preisblätter, Hochlastzeitfenster, Sitemaps und alles, was wir sonst suchen. Nie nur auf Dateiendungen (.pdf, .xlsx) oder XML-Sitemaps verlassen.


## Regel: Erwartete Ebenen und fehlende Werte (Festlegung Nutzer, 04.11.2026)

Es zählen nicht nur die Dokumente, sondern auch die fehlenden Werte. Für jeden Netzbetreiber und jede Ebene (MS, MS/NS, NS, HS/MS, SLP) wird festgehalten, warum ein Wert fehlt: `ergebnis/ebenen_erwartung.csv` (Skript `daten/ebenen_erwartung.py`, nach jedem Lauf neu erzeugen).

- **gelesen**: alle vier Werte vorhanden.
- **im_dokument_nicht_gelesen**: im Dokumenttext steht eine Zeile mit dem Ebenennamen und mindestens drei Zahlen, der Leser hat keinen Wert. Das ist eine Leser-Lücke und muss behoben werden.
- **nicht_ausgewiesen**: Dokument vorhanden und gelesen, aber keine solche Zeile. Nur dann darf die Ebene leer bleiben, und das Ergebnis sagt es so ("nicht ausgewiesen"), es ist kein Fehler.
- **kein_dokument**: Dokument fehlt. Die Veröffentlichung ist gesetzlich vorgeschrieben, das Dokument existiert also; es ist unsere Lücke und wird gesucht (PDF, Excel, HTML, Portale).
- Es gilt: **Niederspannung und SLP hat jeder Netzbetreiber**; fehlen sie, ist es nie "nicht ausgewiesen", sondern ein Lese- oder Suchfehler.
- **Mittelspannung und MS/NS** haben nicht alle Stadtwerke. Eine Ebene gilt erst als "nicht ausgewiesen", wenn das gelesene Dokument sie nicht nennt. HS/MS nur bei großen Netzbetreibern (Dokument nennt Hochspannung).
- Ziel sind alle 831 Netzbetreiber mit allen Ebenen, die ihr Dokument ausweist. Sonderfälle (Industrie- und Arealnetze) bleiben in der Liste und werden als Sonderfall markiert.


## Regel: Suchlinks für den Browser (Festlegung Nutzer, 06.11.2026)

Wenn dem Nutzer Dokumente zum Holen im Browser aufgelistet werden, gibt es zu jedem Netzbetreiber Google-Suchlinks mit mehreren Suchbegriffen und `site:` **ohne www.** (also `site:eks.ch`, nicht `site:www.eks.ch`). Erzeugt von `daten/browser_liste.py`, Ergebnis `ergebnis/BROWSER_DOWNLOADS_33.md`.


## Regel: MaStR-Nummer ist der Schlüssel (Festlegung Nutzer, wiederholt, 09.11.2026)

In jeder Liste, Tabelle und jedem Ergebnis (2026, 2027, Gegenprobe, Aufträge, Browser-Listen, Zuordnungen) steht als Erstes die MaStR-Nummer (`mastr_nr`, SNB…). Die laufende Nummer `nr` ist nur Hilfsnummer und ersetzt sie nie. Neue Dateien ohne `mastr_nr` werden nicht abgegeben.


## Festlegung: Umlagen, Steuern, Konzessionsabgabe 2026 (Nutzer, 09.11.2026)
Die Werte stehen in `ergebnis/umlagen_steuern_2026.csv` (Offshore 0,941; KWKG 0,446; besondere Netznutzung 1,559; AbLaV 0; EEG 0; Stromsteuer 2,05, produzierendes Gewerbe netto 0,05 nach Erstattung; Konzessionsabgabe Höchstsätze 1,32/1,59/1,99/2,39, Schwachlast 0,61, Sondervertragskunden 0,11; USt 19 %). Gesetzt vom Nutzer. Am Original geprüft am 09.11.2026: Offshore, KWKG, besondere Netznutzung (netztransparenz.de), Stromsteuer (§ 3 und § 9b StromStG, Entlastung nur Produzierendes Gewerbe und Land-/Forstwirtschaft, nur über 250 €/Jahr, auf Antrag), Konzessionsabgabe (§ 1, § 2 KAV). AbLaV und EEG (0 ct) am 10.11.2026 auf netztransparenz.de geprüft (Seiten führen Umlagen nur bis 2022). Einbau in die API später.


## Festlegung: Ordner eingang/fehlende (Nutzer, 09.11.2026)
Dort liegen die PDFs der blockierten Netzbetreiber, zum Großteil 2026 und 2027 gemischt. Je Datei zuerst das Jahr im Dokument bestimmen: 2026 in die 2026-Tabelle, 2027 nach `eingang/2027_vorlaeufig/`, unklares Jahr in die Restliste. Details in `eingang/fehlende/LIES_MICH.md`.


## Regel: Erst im Git nachsehen, was vereinbart ist (Festlegung Nutzer, 11.11.2026)

Bevor eine Liste, Anleitung oder Zahl geliefert wird, wird im Git nachgesehen, wie es besprochen und schon gebaut ist: `CLAUDE.md`, `START_HIER.md`, `ergebnis/STAND_*.md`, `eingang/kommunikation/`, `git log`. Nichts aus dem Gedächtnis, keine zweite Liste neben einer vorhandenen.

- **Listen fehlender Dokumente** (Preisblatt, Hochlastzeitfenster) sind die **Arbeitsliste**: `daten/arbeitsliste.py` erzeugt `ergebnis/arbeitsliste.csv` und je Bearbeiter `ergebnis/kollege_preise.csv`, `ergebnis/kollege_hochlastzeitfenster.csv` (MaStR-Nr. zuerst, Aktion, Suche `site:` ohne www, Dateiname); Anleitung `ergebnis/arbeitsliste_ANLEITUNG.md`. Diese Dateien liefern, nicht neu bauen. Sie entstehen neu mit der Kette (`daten/hlzf_kette.sh`).
- Nennt der Nutzer eine Zahl (z. B. „101 nicht auffindbare“), wird sie im Git einer Datei zugeordnet (z. B. 101 Zeilen in `kollege_hochlastzeitfenster.csv`). Passt sie nirgends, wird das gesagt, nicht eine andere Liste untergeschoben.
- Die Kommunikation mit dem Kollegen läuft über `eingang/kommunikation/` (Branch `vibe/…` für seine Lieferungen); Antworten und Prüfergebnisse dort ablegen, alle 15 Minuten nachsehen (Cron der Sitzung).
