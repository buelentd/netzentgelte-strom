# Stand und Neuerungen für den Kollegen (12.11.2026, in einem Rutsch)

Bitte zuerst `git pull origin main`. Dein Crawler ist derselbe wie meiner (`vnb/hlzf_crawl.py`), aber **nur der Stand von heute Abend hat alle Neuerungen unten**.

## 1. Stand
- Hochlastzeitfenster in der Tabelle: **566 von 831**.
- Noch offen: **257** (Liste mit MaStR-Nr. zuerst: `2026-11-12_OFFEN_HLZF_MASTR.csv`, mit Website, RLM-Indikator, Crawl-Status und zwei Suchlinks je Netzbetreiber). Dazu 15 Industrie-/Werksnetze (Sonderfall, nicht für KMU) und 4 belegte Befunde "geprüft, nicht gefunden" (`lauf/hlzf_geprueft_nicht_gefunden.csv`).
- In der Liste stehen **54 Netzbetreiber mit Crawl-Status `gefunden_2026`**: Der Crawler hat das Dokument, es ist aber noch nicht gelesen und nicht in der Tabelle. Die Dateien liegen in `eingang/pdfs_neu/<MaStR-Nr.>_hlzf_*` und `eingang/2027_vorlaeufig/`. **Das sind deine ersten Aufgaben** (Auftrag 3, 44 davon in `…AUFTRAG_3_CRAWL_FUNDE_44.csv`).
- 126 sind noch nicht gecrawlt: lass den Crawler darauf laufen (Anleitung `…ANLEITUNG_KOLLEGE_CRAWLER.md`).

## 2. Neue Regeln (Festlegung Nutzer, stehen in `CLAUDE.md`)
1. **2027 zuerst, 2026 nur wenn 2027 fehlt.** Ein 2027-Fund zählt für 2026 und 2027 (Status `gelesen_aus_2027`). Nicht mehr diskutieren.
2. **Suche nur noch:** `<Name des Netzbetreibers> Hochlastzeitfenster 2027` und zweite Suche `<Name> Modul 3 zeitvariable Netzentgelte 2027 Preisblatt`. Nicht mehr `site:Domain` (Domains im MaStR sind oft falsch).
3. **Zwei Arten von Zeitfenstern, getrennt führen:** § 19 Abs. 2 (Hochlastzeitfenster, Spalten `hlzf_…`) und **Modul 3** (§ 14a, HT/ST/NT-Zeiten, steht oft im Preisblatt). Modul 3 kommt in `ergebnis/modul3_zeiten.csv` (MaStR-Nr. zuerst: HT-/ST-/NT-Zeiten, Quartale, drei Preise, Preisstand, Quelle). Bisher 25 Zeilen, 237 weitere Rohfunde in `ergebnis/modul3_rohfunde_2026.csv`. **Beim Lesen eines Preisblatts immer auch den Modul-3-Abschnitt mitnehmen.**
4. **Hochlasttarifstufe (HT/NT) ist kein § 19-Fenster.** Nie in die `hlzf_`-Spalten schreiben (EWR Remscheid war so ein Fehler).
5. **Nichts umgehen:** 403, Schutzseiten, robots.txt werden nicht umgangen. Gesperrtes (auch `robots_dokument_bekannt`) an den Nutzer melden, er holt es im Browser.
6. **Befund "geprüft, nicht gefunden"** gibt es nur, wenn die Seite vollständig durchgesehen wurde und die sichtbaren Dokumente notiert sind. Vorher gilt der Netzbetreiber als offen.

## 3. Was der Crawler jetzt zusätzlich kann (alles gelernt an Beispielen des Nutzers)
- liest **iframes** (GIPS-Portal, Emden), folgt Links auf **Portale** (`enwg-veroeffentlichungen.de`, `gipsprojekt.de`),
- erkennt **Dokumentlinks ohne `.pdf`** (`/downloads/ID`, `/download/`, `/dam/jcr:…?vid=…`, Linktext "(pdf, KB)"),
- liest **eingeklappte HTML-Bereiche** und Umfeldtext von Links, die nur "PDF"/"Download" heißen,
- lädt **Preisblätter und "Regelungen für die Nutzung des Stromverteilnetzes"** mit 2026/2027 im Namen und prüft den Inhalt (swa Netze, Netze BW, Emmendingen: Fenster stehen dort als Abschnitt),
- startet auch auf dem **Verzeichnis der schon bekannten Preisblatt-URL** (Mittelrhein: dort liegt die Seite mit allen Dokumenten),
- überspringt **Soft-404-Seiten** (erfundene Pfade liefern die Startseite mit 200),
- gibt per robots gesperrte Dokumente als **`robots_dokument_bekannt` mit Direktadresse** aus,
- **2027-Dokumente werden höher bewertet** als 2026,
- Zeitlimit je Netzbetreiber (5 Minuten).

## 4. Typische Muster, die der Nutzer gefunden hat
- Kleine Ortsnetze: Preisblatt hat **nur Modul 3**, die Fenster liegen woanders oder fehlen (Butzbach, Meckenheim, Leitlein, Pinzberg, Effeltrich, Vagen, Unterneukirchen, Peissker). Gemeinsame Vorlage (Pinzberg/Effeltrich/Mainbernheim).
- TYPO3-Seiten mit `robots.txt` auf `/*.pdf$` und `/fileadmin/Dateien/` (Niefern-Öschelbronn, Georgensgmünd): Dokumente nicht ladbar, Direktlink an den Nutzer.
- Falsche Website im MaStR: Korrekturen in `lauf/website_korrektur.csv` (nr;website;herkunft).
- Zwei Netzgebiete in einem Dokument (Gelsenwasser, MITNETZ): je Gebiet eine Zeile.

## 5. Abgabe
CSV mit `mastr_nr` zuerst, im Format der Etappen; für Modul 3 die Spalten aus `modul3_zeiten.csv`. Jeder Wert am Dokument geprüft (Text und Bild), Spalte nach Position, Zelle mit mehreren Zeilen = eine Jahreszeit.

## 6. Git
**Vor jedem `git pull` erst committen** (nicht stashen). Erzeugte Listen (`arbeitsliste.csv`, `lauf.log`) nicht von Hand bearbeiten und nie mit Konfliktmarkern (`<<<<<<<`) committen.
