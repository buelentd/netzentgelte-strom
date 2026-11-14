# LIEFERUNG HLZF ETAPPE 8 - 2026-11-14

7 Zeilen aus vom Kunden im Browser geladenen PDFs (Nutzeruploads, OCR-Lesung):
- Werte-Korrekturen (ersetzen fruehere Statuszeilen): Steinfurt 2026, Leitungspartner 2026, Wunsiedel 2026, Perlesreut 2026
- Neue Jahre: Pullach 2027 (2026 bleibt gesperrt/Referer), Guestrow 2027 (2026 bleibt offen), Radevormwald 2026 (2027 war bereits geliefert)

Quelldateien: 7 PDFs als hlzf_quellen_etappe_8.zip (Download-Karte), Dateinamen = quelle_url. Bitte unter eingang/ ablegen.
Werte- und Regelwerk: werte_verifiziert.json (89 Eintraege), merge_werte.py je SNB+Jahr, regeln.py = OK.
Hinweis: Pullach-2026-Eintrag in werte_verifiziert.json (fruehere Lesung) wurde NICHT geliefert, da Dokument nicht erneut verifizierbar (Referer-Sperre). Klärung mit Kunde laufen.

## Nachtrag Etappe 8b (gleicher Tag): Raster-PDFs per Content-Stream-Analyse dekodiert

5 weitere Zeilen (Original-Downloads vom NB-Server, kein OCR mehr noetig):
- Meerane 2026, Gemeindewerke Gundelfingen 2026 (MS/NS/Umspannung), Stadtwerke Reichenbach/Vogtland 2026 (Umspannung 66 kV), Elektrizitaetswerk Simbach GmbH 2026 (fuellt leere 2026-Zeile), Stadtwerke Marburg 2026 (nur MS)
- Die im Nutzerupload unlesbaren Zellschattierungen wurden direkt aus den Original-PDF-Content-Streams gelesen (blaue Viertelstunden = Hochlastzeit); URLs von Reichenbach und Marburg per HEAD verifiziert.
- werte_verifiziert.json jetzt 93 Eintraege; regeln.py alles = OK; alle Zeilen ueber merge_werte.py gemergt.
- Offen bleibt: Marburg 2027 (GrundNetz MS-NS ohne lesbare Zeitliste).

## Nachtrag 8c: Pullach 2026 und Stadtwerk Tauberfranken 2026 (2026-11-14)

1. Stromnetz Pullach GmbH (SNB903808877785, Nr. 752), Jahr 2026: Der Kunde hat das wegen Referer-Sperre im Browser geladene Original-PDF per Upload bereitgestellt; OCR-Lesung geprueft. NS nur Winter 17:00-20:00; MS/NS Herbst 09:00-11:30 und 18:00-19:00, Winter 08:45-13:30 und 17:00-19:45; MS in Bemerkung (Herbst 09:00-12:00, Winter 08:30-13:30 und 17:15-18:15); F/S ohne Fenstereintrag = kein HLZF (R8-Marker). Quelle: stromnetz-pullach-hochlastzeitfenster-2026.pdf; Kunde legt das Original selbst unter eingang/ ab (Uploads sind Stubs). Ersetzt die "gesperrt"-Statuszeile.
2. Stadtwerk Tauberfranken GmbH (SNB936176430474, Nr. 376), Jahr 2026: Der Kunde hat die Zuordnung des Uploads 2026_NSP_Kasten.pdf als Tauberfranken bestaetigt. NS (NSP-Kasten) nur Winter 10:45-11:00, 12:00-12:45, 14:00-14:15 (Stand 26.01.2026); NS F/S/H nicht als Hochlastzeit markiert -> kein HLZF (R8-Marker); MSP/USP bleiben Lastgang-Diagramme ohne Zeitliste -> Felder leer (2026 und 2027 offen). Ersetzt die Diagramm-Negativzeile.
Pipeline: werte_verifiziert.json (94 Eintraege), regeln.py alles OK, merge_werte.py fuer beide SNBs 2026, Arbeitsstand 1776 Zeilen, hlzf_lieferung_2026-11-14.csv um 2 Zeilen erweitert.

## Nachtrag 8d: Rothenburg o.d.T. 2027 (2026-11-14)

Stadtwerke Rothenburg o.d.T. GmbH (SNB979202870318, Nr. 634), Jahr 2027: Die 2027-Tabelle steht auf derselben HTML-Seite wie die bereits verifizierte 2026-Tabelle; Spaltenzuordnung per exaktem Abgleich mit den verifizierten 2026-Werten gesichert. NS Winter 12:00-12:15 und 16:30-18:15, Herbst 12:15-12:30 und 16:45-18:15; MS/NS Winter 16:30-18:30, Herbst 16:45-18:15; MS (Bemerkung) Winter 08:15-08:30, 09:00-11:30, 12:30-14:00, Herbst 10:00-11:30; Fruehling/Sommer je explizit "keine" (R8-Beleg). Pipeline: werte_verifiziert.json ergaenzt, regeln.py OK, 10 Zeilen gemergt, Arbeitsstand 1786 Zeilen.

Zudem: Pruefliste der 16 Diagramm-/Raster-Faelle (17 Zeilen) unter eingang/kommunikation/2026-11-14_PRUEFLISTE_DIAGRAMM_RASTER.md fuer den Blockdurchblick der Kollegen abgelegt.
