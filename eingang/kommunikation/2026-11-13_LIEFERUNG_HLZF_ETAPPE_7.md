# HLZF-Etappe 7 - Lieferung Crawler-Funde (67er-Liste), 2026-11-13

## Umfang
- 41 Zeilen an \'ergebnis/hlzf/hlzf_auftrag7_gelesen.csv\' angehaengt (inkl. Status-/Negativ-Zeilen), zusaetzlich separat als \'ergebnis/hlzf/hlzf_lieferung_2026-11-13b.csv\'.
- **Korrektur in lugar:** Die bisherige Leer-Zeile SNB971770548286 (VersorgungsBetriebe Elbe, 2026, TXT/Preisblatt ohne Zeiten) wurde **in-place ersetzt** durch eine Werte-Zeile: echtes HLZF-PDF via _hash-URL gefunden (NS W 10:45-12:30 + 17:00-19:30; MS W 06:45-11:30 + 12:30-13:30, S 06:15-14:00 + 15:30-18:00, H 06:00-13:30; MS/NS alle entfaellt). Datei: SNB971770548286_hlzf2026.pdf.

## Werte-Zeilen (25)
Simbach 2027, Bad Aibling 2027, MEGA Monheim 2026, Dettelbach 2027 (CID-Font per Content-Stream-Parse), Selb 2027 (nur MS), Wolmirstedt 2026, Straubing 2026, Heiligenhaus 2026, Linzgau 2027, Miller 2027, Neuendettelsau 2027 (Vorbehalt: Zuordnung per Block-Kontinuitaet), AVU Netz 2027 (HTML), Lindau 2026+2027 (HTML), Malchow 2026+2027 (HTML), Rothenburg 2026 (HTML; 2027-Tabelle auf der Seite folgt), Hellenstein 2026+2027 (HTML), Bad Harzburg/Harzenergie 2026 (HTML), GGV Gross-Gerau 2027 + Georgensgmuend 2027 (identische Tabellen; Ueberschrift 2027, URL/Title 2025), Wendelsteinbahn 2026+2027.

## Status-/Negativ-Zeilen (16)
- GETEC net/Quartier/grid solutions 2026: xlsx listet 173 individuelle Kostenstellen-Fenster, kein netzweit einheitliches HLZF je Ebene -> Felder leer.
- Browser-Liste: Meerane 2026, Ansbach 2027, Reichenbach 2026 (Lastgang ohne explizite Fenster); Hockenheim 2027, NEW Netz 2027, Marburg 2027 (Raster ohne Textmarken); Tauberfranken 2027, QuartiersNetz 2027 (Diagramme); Langen 2027 (kein separates HLZF-Dokument, Preisblatt verweist nur auf "veroeffentlichte Hochlastzeiten").
- Negativ: Torgau 2026 (nur 2023-2025), Baiersdorf 2026 (nur 2022-2024), Wadgassen 2027 (nur 2024), WiDe Flex 2026 ("auf Anfrage").

## Quelldateien (PDF-Transport)
Originale (22 Dateien: 14 PDFs + 8 HTML-Snapshot-Dateien) laufen wie gehabt als ZIP-Download-Karte, da Binary-Push ueber den Connector PDFs verfaelscht (UTF-8-Inflation, bereits getestet). Bitte unter \'eingang/**\' mit exakt den quelle_url-Dateinamen ablegen (die 8 HTML-Dateien enden auf .html, NICHT als .pdf umbenennen; pdftotext kann sie lesen). Hinweis: Hellenstein/Lindau/Malchow/AVU/Bad Harzburg/GGV/Georgensgmuend sind HTML-Tabellen.

## Hinweise
- GGV/Georgensgmuend: Tabellenueberschrift im Inhalt lautet "Hochlastzeitfenster 2027"; URL und Title-Tag nennen 2025 - inhaltlich 2027 massgeblich, in Bemerkung dokumentiert.
- Heiligenhaus: PDF liegt auf dem Server unter /gas/, Dokumenttitel nennt aber Hochlastzeitfenster (Strom); Server-Lesung gegengeprueft.
- Rothenburg: 2027-Tabelle auf derselben Seite vorhanden, Auswertung folgt in der naechsten Etappe.
- Offen geblieben: Wunsiedel-Werte (Quelle unklar), Parchim-2027-Nachweis, Rest der bulk_todo ab Zeile 66.
