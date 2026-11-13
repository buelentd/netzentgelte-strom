# Status Lesen HLZF 2027-vorlaeufig (12.11.2026, abendlicher Stand)

## Geliefert auf Branch vibe/hlzf-etappen-1-2-705031
`ergebnis/hlzf/hlzf_2027_gelesen.csv`: jetzt **68 Zeilen** (vorher 20). Pruefskript: 68 Zeilen, 0 Fehler.

### Diesen Stand neu dazu (Commits 624b02b, 965ecae, 2dffa78, 57e8d13)
Jede Zeile mit Seiten-/Zellenbezug in bemerkung (Seite, Tabelle, Ebene, Saison):

| MaStR-Nr. | Netzbetreiber | Inhalt |
| --- | --- | --- |
| SNB941650885558 | VSE Verteilnetz | nur HS + HS/MS im Dokument (Winter-Zeiten in bemerkung), NS/MS-NS nicht ausgewiesen |
| SNB941042755957 | Bruchsal | NS + MS/NS nur Winter; F/S/H-Zellen leer (kein Strich) |
| SNB942173666990 | EV Beckum | NS = MS/NS: H 11:45-12:30, W 17:00-19:30; Schwelle 30%, 100 kW |
| SNB935556509052 | Netze ODR | Bild-only-Tabelle gelesen: NS W 11:00-14:00, MS/NS W 16:30-19:30, F/S/H Strich |
| SNB942804093577 | Queichtal Offenbach | MS/NS S 4 Fenster, H 2 Fenster, W 10:15-11:00; NS nur W |
| SNB946612539746 | VB Hoyerswerda | NS + MS/NS nur Winter, F/S/H Strich |
| SNB951051725711 | EWE NETZ | NS + MS/NS nur W 17:00-19:15, sonst "keine" |
| SNB942182027607 | DB Energie (Bahnstrom) | nur HS + MS; F/S/H "keine HLZF" -> keins; NS/MS-NS nicht ausgewiesen |
| SNB942257679137 | Stadtwerke Achim | NS W 17:15-19:30, MS/NS W 17:30-19:30, F/S/H entfällt |
| SNB953011641437 | Reußenköge | nur MS ausgewiesen, NS/MS-NS leer |
| SNB957591716776 | SW Aue-Bad Schlema | NS W 16:15-18:45, MS/NS W 16:15-18:30, F/S/H entfällt |
| SNB958416423039 | SW Emsdetten | NS W 17:15-19:15, MS/NS W 17:15-19:00, F/S/H Strich |
| SNB957549782006 | SW Finsterwalde | nur Winter; Schwelle 30%, 100 kW |
| SNB965998184692 | EW Goldbach-Hösbach | MS/NS H+W, NS nur W |
| SNB953495670831 | EnR Rudolstadt | nur Winter für NS + MS/NS |
| SNB954187049256 | SW Springe | NS + MSP/NSP nur W 17:00-20:00 |
| SNB959523885956 | Mainzer Netze | nur Winter-Zeiträume, NS + UMN je W 16:45-19:45 |
| SNB961497906636 | GELSENWASSER | 2 Zeilen (Stolzenau/Rehburg-Loccum, Unna Südwest/Westmünsterland) |

### Aussortiert (falsches Jahr im Dokument trotz 2027-Dateiname)
- SNB936940951426 ÜWR Rhön: Dokument nennt "Jahr 2025"
- SNB950006175489 SWTE Netz: Titel "Hochlastzeitfenster 2026"
- SNB942111583372 SW Lünen: 2026-Dokument

### Noch nicht gelesen (Grund bekannt)
- Raster/Diagramme: SNB936176430474 Tauberfranken, SNB938413573104 QuartiersNetz, SNB918516395612 Bielefelder, SNB961471621746 Pfalzwerke, SNB964262506406 Radevormwald, SNB945861817537
- Weiter im Lesen: Ratingen, Hollfeld, Herten, CPM Netz, Neunburg v.W. (H/W-Spalten), swa Netze (15 S.), SW Bad Rodach (9 S. Preisblatt)

## Update (spaeterer Stand)
Commits bis f8b3432: +29 weitere Zeilen gelesen (u.a. Aue, Emsdetten, Finsterwalde, Goldbach, Rudolstadt, Springe, Mainz, Gelsenwasser 2 Gebiete, swa Netze, Ratingen, Herten, Neunburg, CPM, Hollfeld unleserlich, Oerlinghausen, Bad Hersfeld, Heikendorf, Waren, Doebeln, Bad Neustadt, Freising, Mittelrhein, Mainbernheim, Angermuende, Waldbuettelbrunn, SVH Haar, Dortmunder Netz, Lingen unleserlich, Rettenberg, Bruchmuehlbach, BIGGE, Vlotho, Ditzingen, Haslach, Elm-Lappwald/Hanau unleserlich).
6 beanstandete Zeilen mit Seite-Zelle-Beleg nachgeliefert (Antwort: 2026-11-12_ANTWORT_AUF_RUECKMELDUNG_1630.md).

## Offen gesamt
91 Dokumente in lauf/hlzf_2027_offen.csv; 48 jetzt gelesen -> Rest ca. 43 (davon etliche Raster/Diagramme).

- SNB917593691679 (EW Unterwössen): Datei im Repo ist nginx-500-Fehlerseite, kein Dokument -> manuell holen.
- Defekt/leer: Uslar (404), Weilheim (JS-Gate), Simbach (Raster 2026), Spremberg (Bild-only), EV Schmid (Preisblatt ohne Paragraph 19), Alzchem/Bad Harzburg/Hengersberg (nur aeltere Jahre im Repo).
- Korrektur nach Regel: SWTE, Waging a. See, SW Luenen, Teterow (2026-Dokumente) gelesen und eingetragen (jahr=2026); UWR Roen (2025) bleibt unbrauchbar.
- Stand: hlzf_2027_gelesen.csv 69 Zeilen, hlzf_auftrag7_gelesen.csv 30 Zeilen, beide 0 Fehler.
- Auftrag 7 (ablesen): 51 Zeilen in hlzf_auftrag7_gelesen.csv, 0 Fehler (Stand Commit 080a67e). Rest der ablesen-Liste teils Raster/defekte Dateien/only-old-years.
- Aus den 170 Preisblaettern 2027: 37 mit HLZF-Abschnitt geprueft, 22 gelesen + 14 ohne Paragraph-19-Tabelle dokumentiert, 1 (SVS) bereits separat gelesen. hlzf_2027_gelesen.csv jetzt 105 Zeilen, 0 Fehler (Commit folgt).
- Pruefen (5 Faelle): Stockach = Gegenbeleg (HLZF vorhanden, Zeile uebernommen); Unterneukirchen = bestaetigt (Preisblatt 2027 ohne HLZF, S.1-2); Eschwege, Straubing, Klingenberg = kein Dokument im Repo -> bleiben offen/suchen.

- `ba0c591` (+5): KEW 2026, Oldenburg i.H. 2027, Luebbecke 2027, Hauenstein 2026, BEW 2027; Name SNB969708579983 = Stadtwerke Wallduern korrigiert. 76 Zeilen, 0 Fehler.
- `90a640a` (+5): Radevormwald 2027 gelesen; Bielefelder Netz 2027 als 0/1-Raster dekodiert (NS W 13:00-14:00, 17:15-19:30; MS/NS W 17:15-19:45); Tauberfranken (Diagramm), QuartiersNetz (nur HS/MS 09:15-19:00), Hanau (nur Modul 3) dokumentiert. 81 Zeilen, 0 Fehler.
- `1319f1f` (+19 dokumentiert): 10x Preisblatt 2027 ohne §19 (Unterwoessen, Uslar, Tirschenreuth, Roethenbach, Baiersdorf, enercity, Hameln, Fugger, GETEC x2), Perlesreut 2026 bild-only, Gundelfingen 2026 Raster, 8x Preisblatt 2026 ohne HLZF-Zeiten (Landshut, Alzchem, Weilheim, Olching, Fellbach, Elbe, Diessen). 100 Zeilen, 0 Fehler.
- `NEXT` (+5): Harz Energie 2026 (NS/MSNS je W 16:30-19:30 aus HTML), Senftenberg 2026 xlsx (NS/MSNS W 08:45-13:15, 18:00-20:00; MS/NS-Fruehling "19:00 Uhr" unklar), RheinNetz 2027, Dinkelsbuehl 2026 (nur Modul 3), Leine-Solling 2026 (kein HLZF). 105 Zeilen, 0 Fehler.
- Nur <=2025-Dokumente im Repo (keine Zeile moeglich, unbrauchbar): Bad Harzburg, Torgau, Wildeck, Bad Wildbad, Muenchberg, Neu-Isenburg, Heilsbronn, Gebr. Miller (2020), Schierling (2024), Rohrdorf (Leitfaden 2011), Schoenkirchen (2025), Oberwoessen (2022), Neuendettelsau (2022), GETEC net (Werksnetz-xlsx je Kostenstelle, <=2025, Sonderfall). enercity GridPartner: xls nur HT-Zeiten ohne Jahr. Windsbach: hlzf.pdf ist eine 404-Fehlerseite.
- Audit nach Regel "2026 hat Vorrang, 2027 nur wenn kein 2026": 61 Zeilen (beide CSVs) von 2027- auf 2026-Dokumente umgestellt, Werte neu gelesen (Text+Bild), Belege aktualisiert. Verbleibende jahr=2027 trotz 2026-Datei: Bielefelder Netz (Datei mit 2026-10-29 im Namen enthaelt Raster-Inhalt 2027) und Hauenstein (2027-Zeile = Preisblatt-Dokumentation; HLZF 2026 in auftrag7-Datei). Formatfix: werkkraft (18->17 Felder), Halberstadtwerke (16->17, quelle_art ergaenzt). Beides 105 Zeilen, 0 Fehler.
- Finaler Stand 12.11. abends (`ce5640e`): Branch sauber und gepusht. hlzf_2027_gelesen.csv 164 Zeilen / 0 Fehler, hlzf_auftrag7_gelesen.csv 105 Zeilen / 0 Fehler. Abgleich mit `kollege_hlzf_offen_199.csv` (main): 51 Ueberschneidungen, alles Dokumentations-/Bestaetigungsfaelle (keine §19-Zeiten bzw. nur Doku-Zeilen) - liegt beim Reviewer. Mein Teil HLZF ist damit fertig.

## 199er-Liste: dokumentbasierte Fälle abgearbeitet (Batch 14)
- Von 64 Doku-Fällen der Liste waren 50 bereits geliefert (in hlzf_2027_gelesen.csv / hlzf_auftrag7_gelesen.csv).
- +2 neue Zeilen (166 gesamt, 0 Fehler): GETEC net GmbH (Werksnetz-Sonderfall, HLZF 2026 pro Kostenstelle, Info!B12=2026), enercity GridPartner (nur HT-Tarifstufe 2026/2027, kein §19 -> leer).
- Nur ≤2025 bzw. unbrauchbar (dokumentiert, keine Zeile): Neu-Isenburg (2024/2025), Torgau (2023-2025), Bad Wildbad (2024/2025), Münchberg (2023-2025, alle "kein HLZF"), Heilsbronn (2021/2022/2024), Schönkirchen (2025), Bad Harzburg (2021-2023), Oberwössen (2022), Neuendettelsau (2022), Gebr. Miller (2020), Wildeck (2018-2023).
- Defekt: Windsbach-Datei ist eine gespeicherte 404-Seite. Rohrdorf-Datei ist nur der BNetzA-Leitfaden 2011, kein HLZF-Dokument.
- Restliche 127 "suchen" = Browser/Suche (Nutzer/Kollege).
