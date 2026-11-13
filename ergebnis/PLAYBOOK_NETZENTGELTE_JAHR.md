# Playbook: Netzentgelte eines Jahres für alle Netzbetreiber (aus 2026 gelernt, für 2027 angewendet)

Stand 12.11.2026. Aufgeschrieben aus dem Git (`STAND_*.md`, `START_HIER.md`, `CLAUDE.md`, Commits), nicht aus dem Gedächtnis.

## Warum 2026 fast vollständig ist und 2027 noch nicht
2026 war ein Arbeitslauf von rund zwei Wochen mit mehreren Helfern. Die Quote stieg in Schritten (aus `STAND.md` vom 31.10.): morgens 467 nutzbar, nach hochgeladenen Preisblättern der Großen (Westnetz, Bayernwerk, E.DIS, SH Netz, Syna, Stuttgart, Avacon) 491, nach Suche mit Brave 504, nach Suchbegriff mit Jahr 509, am Ende 788 mit Status ok. Dazu kamen Nutzer-Uploads, das Nachziehen des Lesers (Spalten vertauscht, Tagespreise, Grenze ≤/<), die Stichprobenprüfung (2,5 % Fehler) und die Arbeitsliste für Kollege und Browser.
2027 steht am Tag 1 dieses Weges: Der Crawler lief über die HLZF-Fälle, Preise 2027 liegen als Dateien für 205 Netzbetreiber vor, die großen Netzbetreiber fehlen noch.

## Die Schritte (in dieser Reihenfolge, mit Werkzeug)
1. **Stammdaten:** MaStR-Liste mit Name, MaStR-Nr., Website (`vnb/mastr_*.py`, GitHub Actions `netzentgelte.yml`, weil die Cloud-Umgebung MaStR und Netzbetreiber-Seiten sperrt). Schlüssel ist die MaStR-Nr.
2. **Vorjahr als Landkarte:** Die Quelle-URL des Vorjahres zeigt, wo der Netzbetreiber seine Preisblätter ablegt. Für 2027: `lauf/url_kandidaten_2027.csv` leitet aus der 2026-Adresse (2026→2027, _26→_27) 460 Kandidaten und 517 Verzeichnisse ab. **Ungetestet**; die Adressen sind Vermutungen, die jemand mit Netzzugang öffnen muss.
3. **Crawler:** `vnb/hlzf_crawl.py` (Playwright, 1 Anfrage pro Sekunde je Domain, robots.txt, ehrlicher User-Agent, Seitenbewertung nach Stichwörtern, Dokument-Prüfung auf Jahr/Strom). Läuft beim Kollegen. Status: gefunden, nur_2027, blockiert, kein_treffer, nicht_erreichbar.
4. **Browserarbeit für Gesperrte:** Liste mit Suchlinks nach **Netzbetreiber-Name**, sortiert nach Einwohnern (`ergebnis/browser_preise_2027_571.csv`). Der Nutzer holt Dokumente, nichts wird umgangen.
5. **Dateien ablegen:** `eingang/2027_vorlaeufig/SNB…_preis_2027.pdf` (und `…_hlzf_2027.pdf`), Prüfung vorher mit `daten/dokument_pruefen.py`.
6. **Einlesen ohne KI-API:** `daten/netzentgelte_2027.py` (gleicher Leser wie 2026, `vnb/extract.py`). Plausibilität: NS LP ab 2.500 h 40–500, LP unter < LP ab, AP unter > AP ab, SLP-AP 3–15, Grundpreis 0–200. **Vorjahresvergleich:** Abweichung über 40 % wird zur Prüfung vorgemerkt.
7. **Lesefehler beheben statt wegwerfen:** Wenn im Dokument eine Zeile mit Ebenenname und drei Zahlen steht, aber kein Wert gelesen wurde (`ergebnis/ebenen_erwartung.csv`), ist das eine Leser-Lücke.
8. **Stichprobenprüfung** gegen das Original (200 Zeilen im 2026-Lauf, 2,5 % Fehler) und Kollege-Gegenprobe.
9. **Arbeitsliste:** `daten/arbeitsliste.py` erzeugt je Bearbeiter die Listen; Kollege, Nutzer im Browser, Claude haben getrennte Aufgaben (`ergebnis/ARBEITSTEILUNG.md`).
10. **Export:** `daten/conplot_export.py` (JSON, MaStR-Nr. zuerst), `partnerpaket.py`.

## Was der Kette für 2027 noch fehlt (ehrlich)
- Die **571 ohne Blatt** (rund 67 % der Einwohner, darunter Westnetz, Berlin, EWE, MITNETZ, E.DIS, Hamburg, Syna). Das ist die Browserarbeit aus Auftrag 8 und der Crawler mit den abgeleiteten Adressen.
- **62 teilweise und 4 zu prüfen:** Leserlücken oder Dokumente, in denen nicht alle Ebenen stehen.
- **Kein Stichprobenlauf** für 2027 bisher; die 21 Abweichungen über 40 % sind nicht geprüft.

## Kurzregeln, die sich bewährt haben
- Nichts raten: leer lassen, begründen. Text und Bild vergleichen. Jede Zeit rückwärts prüfen.
- Gefundene Datei heißt noch nicht gelesen. Zahlen aus der Datei zählen, nicht aus dem Gedächtnis.
- Bevor etwas überschrieben wird: Stand vorher und nachher vergleichen (verloren = 0).
- Tests vor dem Push; Stop-Hook verlangt Commit und Push.

## Hinweise des Nutzers und gelernte Fälle: immer sofort speichern (Festlegung Nutzer, 13.11.2026)

Alles, was der Nutzer oder der Kollege im Gespräch nennt (Adresse, Dokument, Netz-Host, Schreibweise, Sonderfall), wird **sofort** festgehalten und geht nicht im Chat unter:

1. **Adresse/Seite zu einem Netzbetreiber** → `lauf/nutzer_hinweise.csv` (mastr_nr; url; zweck; datum; von). Der Crawler (`vnb/hlzf_crawl.py`) nimmt sie als erste Startseiten. Ältere Sammlungen: `lauf/hinweis_urls.csv`, `lauf/hinweis_urls_2027.csv`.
2. **Dokument (PDF/XLSX/HTML)** → in `eingang/…` unter `<mastr_nr>_…` ablegen, einlesen, im Status vermerken.
3. **Gelernte Regel** (warum etwas nicht gefunden wurde) → hier ins Playbook und, wenn es das Verhalten ändert, in den Crawler/Leser einbauen.

Gelernte Fälle:
- **Witten (13.11.2026):** Preisblätter und Hochlastzeitfenster liegen auf einer anderen Subdomain (`netze.stadtwerke-witten.de`) als die MaStR-Website. Der Crawler verbrauchte seine 40 Seiten auf der Hauptseite. Folge: Startseite des Hosts der bekannten 2026-Quelle zuerst; Google findet über Titel und Namen schneller (Suchlinks nach Name).
- **Ludwigsfelde (13.11.2026):** Nutzer nennt `stadtwerke-ludwigsfelde.de/netze_infos/` → `lauf/nutzer_hinweise.csv`.
- **Butzbach (13.11.2026):** kein eigenes Hochlastzeitfenster-Dokument; Rechenwert nur als getrennter Fallback (`ergebnis/hlzf_fallback.csv`, Herkunft und Konfidenz), nie in den Primärdaten.
- **Werks-/Industrienetze (GETEC, Alzchem, BASF, Cassella, DB Energie, werkkraft …):** Sonderfall, keine Einzelwerte in den Hochlastzeitfenster-Spalten, Beleg im `bemerkung`.
- **Suchjahr:** 2027 zuerst, 2026 nur als Rückfall (Crawler seit 13.11.2026).
- **Namensfalle SWN (13.11.2026, Kollege):** `swneustadt.de` = Stadtwerke Neustadt an der Weinstraße, `swn-netze.de` = Stadtwerke Neustadt bei Coburg. Vor jeder Übernahme Impressum/Ort des Dokuments mit dem Netzbetreiber der MaStR-Nr. abgleichen.
- **Sperren (Nutzerregel):** Kein Referer-Trick und keine Umgehung von Cloudflare/403/robots.txt; gesperrte Dokumente gehen in die Browser-Liste für den Nutzer.
- **Vilsbiburg:** Links der Seite enthalten ein Leerzeichen statt Schrägstrich im Pfad; mit Schrägstrich lädt das PDF.
