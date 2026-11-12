# Offene Punkte für den Kollegen (Stand 12.11.2026, nach der Übernahme deiner Lieferung)

Danke für die große Lieferung: **632 von 831** Hochlastzeitfenster sind fertig, 37 neue Zeilen und 45 aktualisierte Versionen habe ich übernommen (alle Zeiten im PDF-Text wiedergefunden, 0 verloren). Das hier ist deine Liste für die nächsten Tage. Reihenfolge von oben nach unten.

## 1. Nachbessern (erste Priorität, kurz)
| Netzbetreiber | Problem | Was ich brauche |
|---|---|---|
| Selb-Marktredwitz | 8 von 8 Zeiten stehen nicht im PDF-Text (zum zweiten Mal) | Seite und Zelle je Zeit, oder Zeile neu |
| Heikendorf, Waldbüttelbrunn | alle Zeiten nicht im Text | Beleg (Seite/Zelle) |
| werkkraft | 5 von 5 nicht im Text (du schreibst "formatkorrigiert") | Beleg |
| Bielefelder Netz | 3 von 3 nicht im Text | Beleg, Jahr im Dokument klären |
| Cottbus | 4 von 8 nicht im Text | die 4 belegen |
| Senftenberg, Herten, Fürstenfeldbruck | Datei ist ein Bild | Seite/Zelle im `bemerkung`, "nur im Bild" ausdrücklich |
| Bad Hersfeld, Angermünde, Halberstadt, Springe, BIGGE | Quelldatei nicht im Repo | Datei ablegen (Halberstadt: Adresse der Webseite) |
Liste mit Gründen: `lauf/hlzf_lieferung_zurueck.csv`.

## 2. Hochlastzeitfenster: 199 offen
| Status | Anzahl | Aktion |
|---|---:|---|
| Kein Dokument gefunden | 88 | suchen (Auftrag 7, `suchen`; Suchlinks in `ergebnis/kollege_hlzf_253.csv`) |
| Dokument da, nicht lesbar | 80 | am Dokument ablesen (Auftrag 7, `ablesen`) |
| Raster-Grafik | 8 | markierte Viertelstunden am Bild lesen |
| Falsches Jahr | 6 | neues Dokument (2026 oder 2027) suchen |
| Gelesen, nicht bestätigt | 11 | Beleg nachliefern |
| "keine im Dokument" | 4 | Stelle im Dokument belegen |
| Unplausibel zurückgehalten | 2 | Gemünden, Fröndenberg-Wickede, Töging: der Nutzer holt die Dokumente im Browser |
**Aus deinen 43 Zeilen ohne Zeiten** ("nur MS", "separat veröffentlicht"): Das eigene Hochlastzeitfenster-Dokument fehlt noch. Bitte suchen, wo die Seite "separat veröffentlicht" sagt, und ablegen. Zählt als `suchen`.

## 3. Modul 3 (§ 14a)
426 Netzbetreiber mit Uhrzeiten im Preisblatt, bei denen die Zeit nicht eindeutig zu HT/ST/NT gehört: `ergebnis/modul3_offen_kollege.csv`, Anleitung `modul3_ANLEITUNG_KOLLEGE.md`, Prüfung `daten/modul3_manuell_pruefen.py`. Bitte erst die HLZF-Nachbesserung (1), dann die 80 `ablesen`, dann Modul 3.

## 4. Ordnung
- Die ungeordneten Uploads in `dl_up/sonst/` bitte zuordnen: Dateiname `SNB…_hlzf_<Jahr>.pdf` bzw. `SNB…_preis_<Jahr>.pdf`, nach `eingang/2027_vorlaeufig/` oder `eingang/pdfs_neu/`.
- Der Crawler `vnb/hlzf_crawl.py` läuft bei dir. Meine Version hing auf der Restliste; falls du eine Ursache findest, bitte melden.

## 5. Regeln, die gelten
- Beide Jahre gelten (2026 oder 2027, was zuerst gefunden wird). Kein Dokument deshalb aussortieren, nur 2025 und älter.
- Jede Zeit am Dokument zeigen können (Seite/Zelle). Fehlt der Text, ausdrücklich "nur im Bild".
- Mittelspannung nicht unter MS/NS. Fehlende Ebene leer, nicht `keins`.
- Nichts raten, nichts umgehen (403, Cloudflare, robots.txt), das holt der Nutzer im Browser.
- Zahlen in Meldungen nur aus `lauf/hlzf_zusammen.csv` und den Export-Dateien.

## 6. So lieferst du
Stapel von 10 bis 20 Netzbetreibern, vorher `daten/hlzf_lieferung_pruefen.py` grün, dann Push und eine kurze Meldung in `eingang/kommunikation/` (gelesen / nicht gefunden / blockiert / unklar mit Grund). Ich übernehme mit einem Befehl und melde dir die Zahl zurück.

Gesamtplan mit Fristen: `ergebnis/PLAYBOOK_2027.md`. Alle Punkte des Tages: `ergebnis/OFFENE_PUNKTE_2026-11-12.md`.
