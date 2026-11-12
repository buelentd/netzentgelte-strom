# Crawler für den Kollegen: Hochlastzeitfenster, Modul 3, Preisblatt 2027 finden

Statt Seiten von Hand zu suchen, benutzt du den Crawler im Repo (`main`). Er öffnet die Website des Netzbetreibers in einem echten Chromium (JavaScript, iframes, Portale wie GIPS), findet die Dokumente und prüft sie am **Inhalt**. Er hat bei den bisherigen schwierigen Fällen die Dokumente gefunden, wo die Suche scheiterte.

## 1. Einrichten (einmal)
```
git pull origin main
pip install -r requirements.txt
```
Chromium muss vorhanden sein (Playwright). Läuft hinter einem Proxy, wird `HTTPS_PROXY` automatisch genutzt.

## 2. Starten
Für eine Liste von Netzbetreibern (Datei mit Spalte `mastr_nr`, zum Beispiel die Teilliste aus deinem Auftrag):
```
python -m vnb.hlzf_crawl --liste meine_liste.csv --ausgabe lauf/hlzf_crawl_kollege.csv --parallel 4
```
Für einzelne: `python -m vnb.hlzf_crawl --nur SNB941183960449 SNB942173666990`

Die Website nimmt er aus `ergebnis/netzentgelte_2026.csv` (bzw. `lauf/website_korrektur.csv`, falls dort eine korrigierte Adresse steht).

## 3. Was herauskommt
- Dokumente nach `eingang/pdfs_neu/<MaStR-Nr.>_hlzf_<Name>`, Webseiten-Tabellen als Text nach `ergebnis/hlzf_crawl_texte/`.
- Ergebnisdatei (`--ausgabe`), MaStR-Nr. zuerst, Spalte `status`:
  - `gefunden_2026` / `nur_2027`: Dokument mit Fenstern gefunden. **Lesen und nach den bekannten Regeln eintragen** (Text und Bild vergleichen, Spalte nach Position, Zelle mit mehreren Zeilen gehört zu EINER Jahreszeit).
  - `nur_aelter`: nur alte Jahre, 2026/2027 fehlt.
  - `robots_dokument_bekannt`: Das Dokument ist per robots.txt für Crawler gesperrt. In der Spalte `hinweis` steht die Direktadresse. **Nicht laden**, an den Nutzer melden (er öffnet es im Browser).
  - `blockiert`: Seite sperrt mit 403: an den Nutzer melden, **nicht umgehen**.
  - `kein_treffer`: nichts gefunden. Melde die Adresse der Website an den Nutzer, er sucht im Browser (Name des Netzbetreibers + "Hochlastzeitfenster 2027").
  - `anfrage`, `nicht_erreichbar`: melden.
- Die Spalte `hinweis` nennt auch "Tarifzeiten (HT/NT, Modul 3)": Dokumente mit Modul-3-Zeiten (zweite Art von Zeitfenstern, getrennt führen, steht oft im Preisblatt).

## 4. Regeln (gelten unverändert)
- robots.txt beachten, keine Sperren umgehen, 1 Anfrage pro Sekunde je Domain, ehrliche Crawler-Kennung (ist eingebaut).
- **2027 zuerst, 2026 nur wenn 2027 fehlt.** Ein 2027-Dokument zählt für 2026 und 2027.
- Nichts raten. Unklar = leer lassen und in `bemerkung` begründen.
- Abgabe: CSV mit `mastr_nr` zuerst, im Format der Etappen.

## 5. Wenn der Crawler etwas nicht findet
Schick dem Nutzer sofort die Adresse der Website und den Status. Findet der Nutzer das Dokument im Browser, bauen wir daraus eine neue Regel in den Crawler ein. So ist er in den letzten Tagen von 0 auf einen großen Teil der Fälle gekommen (iframe, Links ohne .pdf, Preisblatt mit Fenstern, Elternseite, "Regelungen für die Nutzung des Stromverteilnetzes").
