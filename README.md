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
| `python run.py bericht` | `netzentgelte_2026.csv`, `restliste.csv`, `zusammenfassung.md` aus dem Fortschritt neu schreiben |

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
fiktiv. NS LP über 2.500 zwischen 40 und 260, LP unter < LP über, AP unter > AP über.
Netzbetreibername (oder Domain) im Text. Bei mehreren Netzbetreibern mit derselben Website
(z. B. wesernetz Bremen/Bremerhaven, SachsenNetze/HS.HD) muss das Gebiet passen.

**Rücksicht:** robots.txt je Host (Protego), max. 1 Anfrage pro Sekunde je Host über alle Worker,
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

## Tests

```
python -m pytest -q tests
```

Synthetische Preisblätter decken die Layout-Varianten ab (`tests/fixtures.py`). Der Crawler wird
gegen eine lokale Test-Website geprüft: robots.txt-Sperre, JavaScript-Link, vorläufig/2027/Gas als
Fallen und die Drosselung.
