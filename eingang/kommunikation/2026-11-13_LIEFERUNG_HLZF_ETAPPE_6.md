# Lieferung HLZF Etappe 6 (13.11.2026)

## Abgabe
19 Zeilen an **ergebnis/hlzf/hlzf_auftrag7_gelesen.csv** angehaengt (17 mit Werten, 2 Statuszeilen Pullach/Wunsiedel). Dieselben Zeilen liegen separat in **ergebnis/hlzf/hlzf_lieferung_2026-11-13.csv**.

## PDFs (wichtig)
Der Binary-Upload ueber die GitHub-App verfaelscht Dateien (getestet: Original 18.002 Bytes, im Repo angekommen 22.157 Bytes). Deshalb liegen von mir **keine PDFs im Repo**. Die Originale sind dem Nutzer als Download uebergeben:
- **hlzf_pdfs_lieferung.zip** (81 Originale, Dateinamen = quelle_url-Feld, MaStR-Nr. zuerst)
- SNB961816584323_hlzf2025/2026/2027.pdf einzeln (Mengen)
Bitte die benoetigten Dateien unter **eingang/** mit genau den Dateinamen aus quelle_url ablegen, dann findet hlzf_lieferung_uebernehmen.py sie ueber den basename. Original-URLs stehen je Zeile in bemerkung (Abruf mit ehrlichem Kennzeichner, robots beachten).

## Mitgelieferte Werte (2026 bzw. 2027)
- Wittenberge (730) 2026 | Neustadt a.d. Orla (587) 2026+2027 | Luckenwalde (742) 2026
- Vilsbiburg (697) 2026+2027, Vorbehalt: Dokumentkopf nennt "Stadtwerke XY" (BNetzA-Template)
- Eppler (797) 2026+2027, gegen serverseitige Textlesung doppelt geprueft
- Bliestal (424) 2027 (2026 ist schon drin, identisch) | Mengen (568) 2026+2027 | Nettetal (578) 2026+2027
- Iserlohn (531) nur 2027 (2026 = 404) | Ludwigsfelde (176) 2026 (Mehrfachfenster aus Mehrzeilen-Zellen, Raster 14,55pt exakt zugeordnet)
- Ditzingen (452): je Ebene separates PDF (NSP/MSP/MS-NS); Zeile referenziert das MS-NS-PDF; NS Winter 11:15-13:45 (2026) steht nur im NSP-PDF, daher ns-Zellen leer, Werte in bemerkung.

## Nicht geliefert, mit Grund
- **Pullach (752): gesperrt.** Download nur mit Referer-Header erreichbar; gemae der Regel (Sperren nicht umgehen) nicht geliefert -> Browser-Liste.
- **Wunsiedel (787):** GIPS nur 2024/2025, 2026/27 nur mit Session-ID. Falle dokumentiert: netz.sww.de = Stadtwerke WEINHEIM.

## Hinweis zur Pruefung
Einige PDFs haben CID-Schriften: pdftotext kann Zeichensalat liefern. Werte wurden per Positionsddekodierung und gegen serverseitige Textlesung geprueft; bei Rueckweisung bitte Bild-/Opener-Gegenprobe vor endgueltigem Verwerfen.

## Crawler-Funde
die 67 Funde (ergebnis/crawler_funde_hlzf_67.csv) und die vier gelesenen Faelle nehme ich als Naechstes ab.
