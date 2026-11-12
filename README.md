# Netzentgelte Strom 2026: SLP und RLM aller Verteilnetzbetreiber

Repository: `buelentd/netzentgelte-strom`. Alle Befehle werden im Wurzelverzeichnis ausgeführt.

Erfasst für alle Stromverteilnetzbetreiber in Deutschland die Netzentgelte 2026, netto:
SLP Niederspannung (Arbeits- und Grundpreis) sowie RLM im Jahresleistungspreissystem
(Niederspannung und Umspannung MS/NS, unter und ab 2.500 h). Dazu Netzgebiet (Bundesland,
Region, Netztyp), PLZ-Zuordnung und ct/kWh bei typischen Benutzungsstunden. Datenbasis für
den Netzentgelt-Rechner (`vnb/rechner.py`). Ohne KI-API. Aufgabe in `CLAUDE.md`, Spalten in `LEGENDE.md`.

## Lauf über GitHub Actions (empfohlen)

Die Cloud-Umgebung von Claude Code sperrt Netzbetreiber-Websites und MaStR. Darum läuft das
Ganze über GitHub Actions: Actions → „Netzentgelte Strom“ → Run workflow.

1. Erster Start mit `limit` 10: lädt die MaStR-Liste (Marktakteure, Netze, Solareinheiten für die
   Netzgebiete), bearbeitet 10 Netzbetreiber und committet `ergebnis/*.csv` und `zusammenfassung.md`.
   Danach prüfen: Anzahl in `ergebnis/netzbetreiber.csv` (ca. 850), `ergebnis/mastr_rollen.txt`,
   Stichprobe gegen die Pilotwerte.
2. Danach mit leerem `limit` starten. Ein Lauf darf bis zu 350 Minuten dauern. Der Fortschritt
   wird gesichert (Cache, Artifact und `fortschritt.jsonl` im Repo), ein erneuter Start macht weiter.
3. `wiederholen` (z. B. `blockiert`) bearbeitet Fälle erneut, `liste_neu` lädt die MaStR-Liste neu.

PDFs liegen nur im Artifact, nicht im Repo. Der Workflow muss auf dem Standard-Branch liegen,
damit GitHub ihn manuell startbar anzeigt.


### Von Hand heruntergeladene Preisblätter

Manche Websites sperren automatische Abrufe (Bot-Schutz). Solche Preisblätter können im Browser
heruntergeladen und unter `lauf/preisblaetter/` abgelegt werden. `lauf/preisblaetter.csv` ordnet sie der
Original-Adresse zu (Spalten `url;datei;netzbetreiber;herkunft`). Der Crawler nimmt dann die Datei statt des
Downloads und liest sie mit demselben Parser aus; die Original-Adresse bleibt die Quelle im Ergebnis.

### Nur neu auslesen (ohne Internet)

`AUSLESEN=true` in `lauf/anstoss.env` (bzw. `python run.py lauf --offline`) liest nur die Dokumente neu aus,
die frühere Läufe schon heruntergeladen haben (Zwischenspeicher `ergebnis/cache`, zwischen den Läufen im
GitHub-Cache). Kein Browser, keine Website, keine Suche: nach einer Verbesserung am Auslesen dauert das Minuten
statt Stunden. Netzbetreiber ohne Dokument im Zwischenspeicher behalten ihr bisheriges Ergebnis. Welche
Netzbetreiber neu ausgelesen werden, steuern wie sonst `WIEDERHOLEN` und `NEU_PRUEFEN`.

### Preisblätter über eine Such-Schnittstelle finden

Der große Lauf ruft direkt vor dem Auslesen den Schritt `python run.py suche` auf. Er fragt für jeden Netzbetreiber
ohne Preisblatt (nur Status `kein_preisblatt`, nicht `blockiert`) die Such-Schnittstelle von
Brave Search ab, mit dem Suchbegriff `<Name ohne Rechtsform> netzentgelte strom 2026 pdf` (wie bei einer Suche von Hand; das Jahr
prüft das Auslesen).
Alle Dokument-Links von der eigenen Website des Netzbetreibers (bis zu 20) kommen vorübergehend in `lauf/suche_treffer.csv`; Links mit Gas,
Wasser, Wärme, Grundversorgung oder Ersatzversorgung im Namen werden verworfen. Derselbe Lauf prüft die Treffer
wie Hinweis-Adressen (robots.txt, Drosselung, Jahres-, Sparten-, Namens- und Plausibilitätsprüfung).

Die Trefferdatei wird nicht ins Repository übernommen, weil die Nutzungsbedingungen von Brave das dauerhafte
Speichern von Suchergebnissen beschränken. Dauerhaft vermerkt wird nur, welcher Netzbetreiber schon gesucht
wurde (`lauf/suche_erledigt.csv`, nur zur Information). Jeder Lauf sucht neu; die Kosten begrenzt `SUCHE_MAX`.

Einrichtung: den Brave-Schlüssel als Repository-Secret `SUCHE_SCHLUESSEL` eintragen (Settings, Secrets and
variables, Actions, Repository secrets). Ohne den Schlüssel wird der Schritt übersprungen. Höchstens 1.000
Abfragen je Lauf, einstellbar mit `SUCHE_MAX` in `lauf/anstoss.env`. Eine Änderung an
`lauf/suche_anstoss.env` startet den Workflow „Such-Schlüssel testen“ (drei Probeabfragen, nichts wird gespeichert).

### Hinweis-URLs

`lauf/hinweis_urls.csv` (Spalten `website;url;herkunft`) enthält zusätzliche Startpunkte je Netzbetreiber,
z. B. eine Unterseite "Netzentgelte" oder den direkten Link auf ein Preisblatt. Der Crawler prüft verlinkte
Dokumente sofort und besucht Unterseiten direkt nach der Startseite; reine Startseiten werden übergangen.
Für Hinweis-URLs gelten dieselben Regeln (robots.txt, Drosselung, Jahres-, Sparten- und Plausibilitätsprüfung).

### Lauf ohne Formular starten

Der Workflow startet auch, wenn eine Änderung an `lauf/anstoss.env` auf `main` gepusht wird. Die Datei
enthält dieselben Einstellungen wie das Formular (`JAHR`, `LIMIT`, `WORKER`, `WIEDERHOLEN`, `LISTE_NEU`,
`DIAGNOSE`); `ANSTOSS` hochzählen, um mit gleichen Einstellungen erneut zu starten. Läuft bereits ein Lauf,
wartet der neue, bis er fertig ist. Beim Commit der Ergebnisse gewinnt bei Konflikten der neuere Lauf.

## Setup

```
pip install -r requirements.txt
playwright install chromium
```

`pdftotext` (poppler-utils) wird genutzt, falls vorhanden, sonst pdfplumber.
Netzwerk: freier Zugriff auf `www.marktstammdatenregister.de`, `download.marktstammdatenregister.de`
und die Websites der Netzbetreiber (bzw. deren CDNs) ist nötig.

## Lauf

```
python run.py alles --worker 4
```

entspricht nacheinander:

| Schritt | Was passiert |
|---|---|
| `python run.py liste` | MaStR-Bulk-Download (open-mastr: Marktakteure, Netze, Solareinheiten), Filter auf Verteilnetzbetreiber Strom ohne geschlossene Verteilnetze, Netzgebiet, Abgleich mit `pilot_50_vnb_2026.csv` → `ergebnis/netzbetreiber.csv`, `ergebnis/plz_netzbetreiber.csv` |
| `python run.py lauf` | Pilot übernehmen (Quelle neu auslesen für MS/NS und SLP, sonst SLP-Blatt suchen; bei vorläufig nach endgültigem Preisblatt suchen), alle anderen crawlen und auslesen |
| `python run.py bericht` | `netzentgelte_2026.csv`, `restliste.csv`, `gefunden.csv`, `nicht_gefunden.csv`, `zusammenfassung.md` aus dem Fortschritt neu schreiben |

Der Lauf ist fortsetzbar: Jeder fertige Netzbetreiber wird sofort in `ergebnis/fortschritt.jsonl`
gespeichert, alle 10 Einträge werden die CSVs aktualisiert. Ein neuer Aufruf überspringt Erledigte.

Nützliche Optionen:

- `--wiederholen blockiert,kein_preisblatt`: diese Status erneut bearbeiten
- `--nur "Stadtwerke Bochum"`, `--limit 20`: Teilmengen (z. B. zum Testen)
- `--csv export.csv`: MaStR-Export der Weboberfläche statt open-mastr verwenden
- `--ohne-gebiete`: keine Solareinheiten laden (schneller; Bundesland/Region dann aus dem Sitz)
- `--rolle-regex "..."`: Marktrolle für den MaStR-Filter vorgeben. Der Standardfilter
  (Rolle enthält "Netzbetreiber", ohne Gas/Übertragung/geschlossene Verteilernetze, Marktfunktion
  Stromnetzbetreiber) ist gegen echte Katalogwerte noch ungeprüft. `ergebnis/mastr_rollen.txt`
  listet alle Rollen mit Anzahl. Weicht das Ergebnis stark von ca. 850 ab, bricht `liste` mit Hinweis ab.

## Ergebnis

Alle Spalten und Dateien sind in `LEGENDE.md` beschrieben. Kurz:

- `ergebnis/netzentgelte_2026.csv`: Stammdaten, SLP, RLM NS und MS/NS, ct/kWh bei 1.500/2.500/
  4.000/6.000 h, Preisstand, Quelle
- `ergebnis/restliste.csv`: alle Zeilen mit Status ungleich ok, mit Grund und geprüften Kandidaten
- `ergebnis/nicht_gefunden.csv`: nur die Fälle, in denen Preisblatt, SLP- oder RLM-Werte nicht gefunden wurden (Spalte `fehlt`), zur separaten Nachbearbeitung
- `ergebnis/gefunden.csv`: alle Fälle mit gefundenem und gelesenem Preisblatt, je Teil (RLM NS, RLM MS/NS, SLP) mit Zustand ok, auffällig oder fehlt
- `ergebnis/zusammenfassung.md`: Anzahl je Status, Spannen SLP-AP und NS ct/kWh bei 4.000 h, Restfälle
- `ergebnis/plz_netzbetreiber.csv`: PLZ → Netzbetreiber für den Rechner
- `ergebnis/pdf/`: verwendete Preisblätter, `ergebnis/cache/`: alle geladenen Dokumente (nicht im Git)

`ok` heißt: RLM und SLP gelesen, plausibel, Name passt. Fehlt einer der beiden Teile oder ist er
auffällig, ist der Status `pruefen`. Die vorhandenen Werte stehen trotzdem in der Zeile, die
ct/kWh-Spalten aber nur bei unauffälligem RLM.

## Rechner (`vnb/rechner.py`)

```python
from vnb.rechner import Tarif, berechnen, lastprofil_lesen, berechnen_aus_profil, kappung
tarif = Tarif.aus_zeile(zeile_aus_netzentgelte_csv)
berechnen(tarif, 40_000)                              # SLP
berechnen(tarif, 300_000, 150)                        # RLM NS, mit Spitzenleistung
berechnen(tarif, 300_000, branche="baeckerei")        # RLM, Benutzungsstunden als Annahme
berechnen(tarif, 300_000, 150, ebene="MS/NS")
berechnen_aus_profil(tarif, lastprofil_lesen("lastgang.csv"))
kappung(tarif, 300_000, 150, 20)                      # Spitze um 20 kW senken, ggf. Tarifwechsel
```

Ergebnis: Netzentgelt €/Jahr, ct/kWh, Leistungs- und Arbeitsanteil, Tarif mit Begründung,
Annahmen, Hinweise, Ersparnis je kW, Tarifwechsel durch Spitzenkappung. Beim Lastprofil kommen
Kennzahlen dazu: Jahresverbrauch, Spitze mit Zeitpunkt, Benutzungsstunden, Hochrechnung, Lücken,
Ausreißer. Lässt sich die Einheit (kW oder kWh je Intervall) nicht sicher erkennen, wirft
`lastprofil_lesen` `RueckfrageNoetig` mit Frage und Optionen für das UI.

## Vorgehen im Detail

**Suche (vnb/crawl.py):** Chromium über Playwright. Startseite, dann Links nach Relevanz
(Netzentgelte, Netznutzung, Preisblatt, Marktpartner, Veröffentlichungen, Netzzugang. Gas,
Wärme, Wasser und Einspeisung ohne "Strom" ausgeschlossen), max. 40 Seiten, Tiefe 3, dazu die
Sitemap aus robots.txt. Links werden nach dem Rendern aus dem DOM gelesen, auch Attribute wie
`link`/`data-href` (z. B. Angular `evd-link`) und Download-URLs im HTML (z. B. admiralcloud).
Dokumente (PDF, xlsx, xls) werden nach Jahr, Endgültigkeit und Schlagworten gereiht. Abzüge gibt
es für § 14a, § 19, fiktiv, 2027, Messstellenbetrieb usw. Die Suche endet, sobald ein plausibles,
endgültiges 2026-Preisblatt gefunden ist.

**MaStR (vnb/mastr_download.py, vnb/mastr_xml.py):** Aus dem Gesamtexport auf
download.marktstammdatenregister.de werden nur die benötigten Dateien geladen (Katalogwerte,
Marktakteure, Rollen, Netze, Netzanschlusspunkte, Solareinheiten). Geladen wird per HTTP-Range
in 8-MB-Stücken mit Wiederholungen, weil der Server lange Verbindungen oft abbricht. Jedes Stück
wird sofort gespeichert, ein Neustart setzt fort (im Workflow über den Cache). Die XML-Dateien
werden gestreamt gelesen, ohne open-mastr-Datenbank. Die scheitert an Listenfeldern der
aktuellen MaStR-Version. Ein vollständiger Export bis 14 Tage alt wird wiederverwendet.

**Netzgebiet (vnb/gebiete.py):** Solareinheiten → Netzanschlusspunkt → Netzbetreiber; daraus
Bundesland, Region, Netztyp und PLZ-Zuordnung (Regeln in LEGENDE.md).

**Auslesen SLP:** Abschnitt „ohne Leistungsmessung“/„Standardlastprofil“. Arbeits- und
Grundpreis werden über die Einheit hinter der Zahl, das Wort davor oder die Kopfzeile zugeordnet.
Wärmepumpe, Speicherheizung, § 14a, HT/NT und unterbrechbare Verbrauchseinrichtungen werden übersprungen.
Mehrere verschiedene Werte (z. B. gestaffelte Grundpreise) → pruefen. Steht SLP in einem eigenen
Preisblatt, sucht der Crawler weiter und führt beide Quellen zusammen.

**Auslesen RLM (vnb/extract.py):** `pdftotext -layout`, Fallback pdfplumber. Excel wird in denselben
spaltentreuen Text übersetzt. Gelesen werden nur Abschnitte des Jahresleistungspreissystems, nicht
Monatsleistungspreis, ohne Leistungsmessung, § 14a usw. Die Zahlen der Zeilen Niederspannung und
Umspannung MS/NS werden über die Kopfzeile zugeordnet: Einheiten €/kW/a bzw. ct/kWh und Grenzen
< 2.500 / ≥ 2.500. Damit werden vertauschte Spalten richtig gelesen. Unterstützt sind auch getrennte
Tabellen je Benutzungsdauer, Zeilen je Benutzungsdauer und umbrochene Labels. €/kW/Tag wird
× 365 gerechnet, €/kWh × 100. Ohne bestimmbare Kopfzeile wird nichts zugeordnet.

**Prüfung (vnb/bewerten.py):** Jahr 2026 im Dokument, gültig ab nicht ein anderes Jahr, nicht
fiktiv, kein Preisblatt für vermiedene Netzentgelte (§ 18 StromNEV, Referenzpreisblatt, vNE). NS LP über
2.500 zwischen 40 und 260, LP unter < LP über, AP unter > AP über, AP unter mindestens 1 ct/kWh.
Netzbetreibername (oder Domain) im Text. Bei mehreren Netzbetreibern mit derselben Website
(z. B. wesernetz Bremen/Bremerhaven, SachsenNetze/HS.HD) muss das Gebiet passen.

**Rücksicht:** robots.txt je Host (Protego; nach RFC 9309: 4xx = keine Einschränkung, 5xx = nicht
erreichbar; jede Sperre wird im Log mit der greifenden Disallow-Regel protokolliert), max. 1 Anfrage pro
Sekunde je Host über alle Worker,
Timeout 30 s, Bilder/Schriften/Medien werden nicht geladen. User-Agent nennt
`intersignum-netzentgelte` mit Kontakt-URL.

**Pilot:** Die 50 geprüften Werte haben Vorrang. Die Quelle wird neu ausgelesen, um MS/NS zu
ergänzen (nur wenn die NS-Werte exakt übereinstimmen). Bei vorläufig/unklar wird nach einem
endgültigen Preisblatt gesucht und dieses bei Status ok übernommen.

## Bekannte Grenzen

- Fehlende Websites werden nicht per Suchmaschine ermittelt: Deren robots.txt sperrt automatisierte
  Suchanfragen. Fallback ist die Domain der MaStR-E-Mail-Adresse (im Hinweis vermerkt).
- Downloads, die erst ein Klick per JavaScript ohne URL im DOM auslöst, werden nicht gefunden.
- Gescannte PDFs ohne Textebene → `kein_preisblatt` mit Grund "Scan?".

## Preisdaten für Solaranlagen und Speicher (`daten/preise_anlagen.json`)

Quellen und Regeln für die Preise, die in die Wirtschaftlichkeitsrechnung (Testseite in `abschaetzung_testseite/`) eingehen sollen.
Die Datei ist noch nicht an die Rechnung angeschlossen und wird vorher freigegeben.

**Regeln:** Alle Preise netto. Liegt eine Spanne mit Minimum und Maximum vor, gilt die Mitte; liegt ein Median vor, gilt der Median.
Nie Werte verschiedener Definitionen mischen (Gerät oder installiert, Heim oder Gewerbe). Jeder Wert nennt seine Quelle; was nicht
belegt ist, steht als "Annahme" da.

| Quelle | Was | Art, Lizenz |
|---|---|---|
| Green Contracting – Energiepreise, https://contracting.green/feeds/pv-preise.xml | Modul, Hybrid-Wechselrichter, Heimspeicher (nur Gerät, nutzbare kWh), wöchentlich | Markterhebung von Shop-Angeboten (3 bis 8 Angebote), 0 % Umsatzsteuer, **CC BY 4.0: Quellenangabe "Green Contracting – Energiepreise" mit Link** |
| Logic Energy, https://www.logicenergy.de/neuigkeiten/stromspeicher-100-kwh-preis-2026 | Gewerbespeicher ab 100 kWh: 410 bis 450 €/kWh installiert; kleine Gewerbespeicher rund 500 und mehr | Anbieterseite |
| Logic Energy, https://www.logicenergy.de/neuigkeiten/pv-investition-2026 | 30 bis 100 kWp: 800 bis 1.300 €/kWp (zitiert Fraunhofer ISE) | Anbieterseite, sekundär |
| energiefluss24, https://www.energiefluss24.de/photovoltaik/fuer-gewerbe | 50 kWp: 950 bis 1.200 €/kWp | Ratgeber |
| elektronik-zeit.de, https://elektronik-zeit.de/photovoltaik-leitfaden-2026/gewerbe-photovoltaik/ | 100 kWp: 950 bis 1.300 €/kWp; Betrieb 1,5 / 2,0 / 2,5 % je Größe | Ratgeber |
| leospardo, https://leospardo.de/ratgeber/photovoltaik-gewerbe-wirtschaftlichkeit/ | 100 kWp: 800 bis 1.050; ab 250 kWp: 700 bis 900 €/kWp | Ratgeber |
| solar.red, https://solar.red/batteriespeicher-gewerbe/ | Gewerbespeicher 30 bis 100 kWh: 400 bis 500; 100 bis 250 kWh: 410 bis 450 €/kWh | Anbieterseite |
| photovoltaik.sh, https://www.photovoltaik.sh/news/gewerbespeicher-in-deutschland-2026-starkes-wachstum-sinkende-kosten-und-blick-auf-die-eeg-novelle-2027/ | 450 €/kWh unter 100 kWh (Primärquelle unbekannt); Schwelle 135 kW (VDE-AR-N 4110); EEG-Novelle 2027 geplant | Installationsbetrieb, Zahlen in sich widersprüchlich |

**Grenzen:** Die Hardwarepreise sind Einzelhandelspreise für Hausanlagen; für Gewerbegrößen (Stringwechselrichter, Staffelpreise) fehlen
Daten. Für Gewerbespeicher unter 100 kWh fehlt die Obergrenze (Satz bei Logic Energy abgeschnitten). Betriebskosten (1,5 %) sind eine
eigene Annahme, Kapazitätsabbau (2,5 % je Jahr) und Entsorgung (75 €/kWh) stammen von conplot und sind ungeprüft. Wirtschaftliche Auslegung
von Gewerbespeichern braucht echte Lastgänge und installierte Systempreise (Aussage von Green Contracting).

## Tests

```
python -m pytest -q tests
```

Synthetische Preisblätter decken die Layout-Varianten ab (`tests/fixtures.py`). Der Crawler wird
gegen eine lokale Test-Website geprüft: robots.txt-Sperre, JavaScript-Link, vorläufig/2027/Gas als
Fallen und die Drosselung.


## Nebenkosten für Solaranlagen und Speicher

Gerüst, Zählerschrank, Netzanschluss, Fundament, Brandschutz u. a.: `daten/nebenkosten_anlagen.md` (Stand 03.11.2026, mit Quellen und Güte; offene Posten sind als „offen“ gekennzeichnet, nicht geschätzt). Noch nicht in der Rechnung.

## REST-API (v1)

```bash
pip install -r requirements.txt
uvicorn api.main:app --port 8000      # Doku: http://localhost:8000/docs
```
Endpunkte unter `/api/v1`: `health`, `netzbetreiber` (Suche per Name oder PLZ), `netzbetreiber/{mastr_nr}`, `netzentgelte/{mastr_nr}`, `plz/{plz}` (Netzbetreiber + Konzessionsabgabe),
`hlzf/{mastr_nr}`, `hlzf/{mastr_nr}/zeitreihe` (Viertelstunden-Vektor), `modul3/{mastr_nr}`, `umlagen`, `POST berechnung/netzentgelt`.
Schlüssel ist die MaStR-Nr. Zugriffsschutz optional: `NETZENTGELTE_API_KEY` setzen, dann Header `X-API-Key`. Daten aus `ergebnis/conplot/` (neu erzeugen mit `python daten/conplot_export.py`).
