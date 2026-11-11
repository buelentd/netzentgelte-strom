# Statusmeldung Etappen 1–3 (2026-11-11)

## Korrektur nach Rückmeldung Etappe 1/2 (bildgeprüft gegen die Original-PDFs)

- **Aalen (SNB982726407335), 2026:** NS Winter `11:15-12:15, 17:00-18:45`, NS Herbst `17:45-18:00`; MS/NS Winter `17:00-18:45`, Herbst `17:45-18:00`; Frühling/Sommer `keins`. Kopfzeile im Dokument ist Winter-Frühling-Sommer-Herbst. Hinweis: `14:00-15:30` steht laut Bild in der Zeile **Mittelspannung**, nicht MS/NS.
- **Borna (SNB946013720880), 2026:** MS/NS Herbst ergänzt: `17:00-20:00` (Winter `10:00-13:00, 17:00-20:00`, NS Winter `10:30-13:30` unverändert).
- **Schonstett (SNB950882682972), 2026:** NS Winter `09:00-11:45, 17:30-19:30`; MS/NS Winter nur `17:00-19:15`.
- **Walldorf (SNB946790148600), 2026:** MS/NS `10:30-11:45` von Frühling nach **Herbst** verschoben.
- **Zeil a. Main (SNB935626894156), 2026:** `13:00-13:15` (Frühling) und `12:45-13:00` (Sommer) gehören laut Bild zum Block **Umspg. MS/NS** und sind dort jetzt eingetragen.

## Etappe 3 (50 Netzbetreiber)

- `hlzf_etappe3.csv`: 55 Zeilen (50×2026, 5×2027), davon **5 Netzbetreiber mit 2026-Werten**: Limburg/EVL, VBH Hoyerswerda, Emmendingen, VersorgungsBetriebe Elbe, Bad Nauheim. 2027-Zeilen (vorläufig): VBH Hoyerswerda, Ochtrup, Eberbach, Stockach, Leine-Solling.
- `hlzf_etappe3_originale.zip`: 12 Originaldokumente.
- 45 Netzbetreiber ohne 2026-Werte, jeweils mit Begründung in `bemerkung` (403: Olching, Weilheim, Westnetz, Syna; 404: Traunstein, Stockach-2026; nur ältere Jahre: Uslar, Spremberg, Oberwössen, Gemünden; Scan/garbled: Wittenberg, Verden; nicht gefunden: u. a. Güstrow, Waldkirchen, Windsbach, RheinNetz, Schleswig, MITNETZ, E.DIS und die 27 Gruppe-G-Betreiber).

## Stand gesamt

150/201 Netzbetreiber bearbeitet (Etappen 1–3). 46 mit 2026-Werten. Offene Fälle siehe `offene_urls_etappe1_2.csv` plus Etappe-3-Bemerkungen. Nächste: Etappe 4 (50× Gruppe G).

## Regeln ab jetzt

Text und Bild werden bei jeder Zeile gegeneinander geprüft (Bild gilt), Spaltenreihenfolge je Dokument aus der Kopfzeile, jede Ebene getrennt, alle Fenster einer Zelle, `keins` nur bei „entfällt“/„-“, Rückwärtsprüfung, unklar = leer + Bemerkung.

## Nachcheck "nicht lesbar" (2026-11-11, spaeter)

Per Bild (150 dpi) jetzt erfolgreich gelesen und eingetragen:
- **Verden (SNB962996832648), 2026:** NS und MS/NS identisch: Herbst `17:00-17:30`, Winter `12:00-12:45, 17:00-18:45`.
- **Wittenberg (SNB932107297727), 2026:** NS Herbst `17:00-19:00`, Winter `11:30-12:00, 16:15-19:30`; Dokument hat nur MS- und NS-Zeilen (MS/NS leer); Mindest-Lastverlagerung 100 kW.
- **Stade (SNB975659838086), 2026:** NS Sommer `16:00-19:00`, Winter `11:00-13:45, 16:30-19:00`; MS/NS Sommer `16:00-19:00`, Winter `11:15-11:30, 12:00-14:30, 16:30-19:00`.
- **Tegernsee (SNB928258126528), 2026:** NS Winter `09:45-10:30, 17:00-19:45`; MS/NS Herbst `18:00-19:00`, Winter `09:45-10:30, 17:00-19:45`. **2027 (vorläufig):** NS Winter `17:00-19:45`; MS/NS Herbst/Winter `17:00-19:45`.

Weiterhin HTTP 403 (kein Bypass, erneut geprueft): Olching, Weilheim, Westnetz, Syna.

## Etappe 4 (2026-11-11)

- `hlzf_etappe4.csv`: 52 Zeilen (50×2026, 2×2027), `hlzf_etappe4_originale.zip`: 3 Originale.
- **Mit 2026-Werten: 1** — Stadtwerke Jena Netze (NS Herbst `17:45-19:15`, Winter `11:00-13:30, 17:30-20:00`; MS/NS Herbst `17:30-19:15`, Winter `11:30-12:45, 17:15-20:00`). 2027 vorläufig als eigene Zeile (NS H `17:45-19:15`, W `11:30-13:00, 17:30-20:00`; MS/NS W `11:30-12:30, 17:30-20:00`).
- **2027 vorläufig:** KBG Homberg (NS W `11:30-13:00, 13:30-15:00, 16:00-18:30`; MS/NS H `17:00-19:30`, W `10:30-12:30, 17:15-19:15`); 2026 nicht veröffentlicht.
- GWS Schönkirchen: 2026-Link vorhanden, liefert aber nur HTML (Hash nicht auflösbar).
- Übrige 47: kein HLZF-2026-Dokument gefunden, Felder leer + Bemerkung mit Website.

Stand gesamt: 200/201 bearbeitet, 51 mit 2026-Werten.

## GIPSProjekt-Abgleich (2026-11-11, nach Kundenliste)

- **Stadtwerke Oberkirch (SNB963821222269), 2026 jetzt mit Werten:** NS F `12:30-14:30`, H `17:30-20:00`, W `11:30-14:00, 16:30-19:45`, S keins (NSP-PDF direkt auf stadtwerke-oberkirch.de). MS/NS leer: nur MSP-Dokument (MS), USP 404.
- GIPS-Mandantenkürzel sind nicht erratbar (nicht aus Domain ableitbar); Traunstein, Norderney, HarzEnergie, Eberbach 2026 darüber nicht gefunden.

## LEW Verteilnetz (SNB911705062982) nachgereicht (2026-11-11)

- **2026:** NS Herbst `17:15-18:15`, Winter `17:00-19:15`; MS/NS Herbst `17:15-18:15`, Winter `17:15-19:00`; F/S keins (Seite 1 bildbasiert, per Bild gelesen).
- **2027 vorläufig:** NS und MS/NS je Herbst/Winter `17:00-19:00`, F/S keins.
- Lesson learned: Betreiberseiten direkt crawlen (Media-Pfade), nicht nur Websuche.

## SWKiel Netz (SNB973742186519) via Nutzer-Upload (2026-11-11)

- **2026:** NS Fruehling `18:45-19:30`, Winter `18:30-20:00`; MS/NS Herbst/Winter `08:00-08:15`; S keins. Zeiten = Ende des 1/4-h-Intervalls. Dokument als Datei bereitgestellt, da robots.txt /fileadmin/ sperrt (kein Bypass).
- SHNG 2027 (Schleswig-Holstein Netz GmbH) ist nicht Teil der 201 Netzbetreiber; Werte nur im Chat reported (NS/MSNS F `17:45-18:15`, H `17:15-19:00`; Schwelle 30%, 100 kW).

## Korrektur Stade (2026-11-11, nach Pruefergebnis)

- **SNB975659838086 (Stadtwerke Stade), 2026:** `16:00-19:00` steht bildbasiert (300 dpi) in der Spalte **Herbst**, nicht Sommer — korrigiert fuer NS und MS/NS: Herbst `16:00-19:00`, Sommer `keins`. Winter `11:00-13:45, 16:30-19:00` (NS) bzw. `11:15-11:30, 12:00-14:30, 16:30-19:00` (MS/NS) bleibt.
- Zusaetzlich: Zeilen mit nur einer besetzten Jahreszeit (ausser Winter) werden kuenftig an der Spaltenposition im Bild gegengeprueft; Statusmeldung nennt kuenftig MaStR-Nr. zuerst.

## Korrektur nach Gesamtpruefung (2026-11-11, MaStR-Nr. zuerst, eine Zeile je Fall)

- SNB975659838086 Stade: NS/MSNS Sommer `keins`, Herbst `16:00-19:00` (Spalte bildbasiert geprueft).
- SNB999405828558 ENRO: MS/NS Fruehling `keins`, Sommer `08:15-08:30, 09:00-10:00, 13:45-14:00` (eine Zelle, drei Zeilen).
- SNB946612539746 Hoyerswerda: NS H `keins`, W `11:15-12:00, 17:00-18:45`; MS/NS H `17:00-18:15`, W `10:30-12:30, 16:15-19:00`.
- SNB971503120734 Meerbusch: MS/NS F `keins`, S `12:30-14:30`.
- SNB922689183730 Suell: MS/NS F `keins`, W `11:00-12:00, 17:00-20:00`.
- SNB957862279702 LSW: Text vor Raster; NS S `11:15-12:30`; MS/NS S `19:45-21:30`, W `17:45-18:45`.
- SNB950336540445 Husum: NS S `13:15-13:45` ergaenzt.
- SNB965281540327 Limburg: NS W `08:45-09:15, 12:30-14:15, 16:00-19:00`.
- SNB948068461008 Emmendingen: NS W `11:30-13:30, 17:15-19:30`; MS/NS H `17:00-18:15`, W `17:15-19:30`.
- SNB924747450655 EWR Remscheid: Werte entfernt (Modul-3-Tarifzeit Paragraph 14a, kein Paragraph-19-HLZF).
- SNB961497906636 Gelsenwasser: zweite Zeile Netzgebiet Stolzenau/Rehburg-Loccum ergaenzt (NS F `12:00-15:00`, S `12:15-13:30`; MS/NS F `13:15-14:45`).
- SNB939724292715 Rostock: NS W `12:15-12:15, 17:15-20:00`; Bemerkung Intervallende.
- Bemerkungen nachgetragen: SNB927892816017 (Einzelzeiten nicht hh:mm-hh:mm -> leer), SNB973742186519 (Uhrzeit-Spalte = Intervallende), SNB963821222269 (Ref.-Zeitraum 2016/17), SNB963795614626 (leere Zellen -> keins).
- **Etappe 5 geliefert:** SNB914508596067 WiDe Flex Bau + Service GmbH — kein HLZF-2026 auf wideflex.de gefunden.

Stand: 201/201 bearbeitet.

## Crawl der 77 "kein Dokument" (2026-11-11)

- **SNB965107360993 Stadtwerke Geldern Netz, 2026 gefunden:** NS Winter `13:00-14:15, 17:45-18:45`; MS/NS Herbst `17:15-19:00`, Winter `17:15-19:30` (Rest keins).
- EVR Rottenburg (SNB935932937127, nicht im 201er-Auftrag): HLZF-2026 gefunden — NS H `17:00-18:00`, W `11:30-12:30, 17:15-20:30`; MS/NS W `16:45-20:30` (nur im Chat/Status, keine CSV-Zeile da nicht im Auftrag).
- Uebrige Crawls: viele Domains per 403/SSL/Timeout nicht erreichbar (westnetz, e-dis-netz, syna, panketal-netz, nordnetz, eks.ch u.a.); Bliestal-Link fuehrte zu Fremd-Domain (biosphaeren-stadtwerke.de) -> nicht verwendet; Fellbach nur 2025-PDF.

## Preisblatt-Nachzug + Schorndorf HLZF (2026-11-11)

- SNB935144085258 Stadtwerke Schorndorf: HLZF 2026 gefunden (nur Winter: NS `09:45-12:15`; MS/NS `09:45-10:00, 10:45-13:30, 17:30-18:45`) + endgueltiges Netzentgelte-Preisblatt 2026 unter eingang/NEUE PREISBLAETTER.
- Von den 8 fehlenden Preisblaettern auffindbar: nur Schorndorf. Nicht auffindbar: Oberhausen (ob-netz.de 403), Putzbrunn (403), PVU (nur 2023/2024), Hammelburg (blockiert), Merck/FLUXUM (kein Preisblatt), Heinzelmann (Netzbetrieb zum 01.01.2026 an E-Werk Netze uebergangen), Egloffstein (Storyblok-PDF gehoert anderem Betreiber).

## 2027-vorläufig — Domain-Crawl Batches 0–90, verifiziert und abgelegt (Commit 569ded8)

10 neue Dateien in `eingang/2027_vorlaeufig/`, alle inhaltsgeprüft (Text: 2027 + Strom + Preisblatt/HLZF; Negativ: Erdgas, §14a-Modul 3, §24c, falsches Jahr):

- SNB933459598975 Netze Magdeburg GmbH — Preisblatt 2027 vorläufig
- SNB910395619643 Blomberg Netz GmbH & Co. KG — Preisblatt 2027 vorläufig
- SNB944057190867 BEW Netze GmbH — Preisblatt 2027 vorläufig
- SNB956411704207 C. Ensinger GmbH & Co. KG — Preisblatt 2027 vorläufig
- SNB963282434775 Bauer Netz GmbH & Co. KG — Preisblatt 2027 vorläufig
- SNB974556654430 Donau-Stadtwerke Dillingen-Lauingen — Preisblatt 2027 vorläufig
- SNB933956506145 Netzgesellschaft Düsseldorf mbH — HLZF 2027 (§19 Abs. 2 StromNEV)
- SNB961471621746 Pfalzwerke Netz AG — HLZF 2027 (110 kV)
- SNB931070025696 Alliander Netz Heinsberg GmbH — HLZF 2027
- SNB935556509052 Netze ODR GmbH — HLZF/Individuelle Netznutzung 2027 (per Bild geprüft, Jahr 2027 bestätigt)

Verworfen: RheinNetz (war §24c-/typisierte-Abnahmefälle-Doc, kein Preisblatt), SWM/e.wa riss/Albstadtwerke/STWAB/Netze Duisburg (Erdgas), e-netz Südhessen (Niederdrucknetz-Gemeinden), SachsenNetze (Gas-Grundversorger), naturenergie netze (nur Messstellenbetrieb), E-Werk Netze Mittelbaden (2026), Weiler Wärme (Grundversorger), EHINGER ENERGIE + LKW Kitzingen (Scans ohne Text).

Hinweis: Für SNB933956506145, SNB961471621746, SNB931070025696 liegt nur das HLZF-2027 vor — das Preisblatt 2027 fehlt noch. Düsseldorf-HLZF liegt auf CDN a.storyblok.com (robots.txt dort 403, PDF selbst 200 mit ehrlichem UA).

## 2027-vorläufig — Domain-Crawl Batches 90–150, verifiziert und abgelegt (Commit e578153)

8 neue Dateien in `eingang/2027_vorlaeufig/`:

- SNB918689434309 Elektrizitätswerk Dahner Felsenland — Preisblatt 2027 vorläufig
- SNB925558752303 Elektrizitätswerk Hindelang eG — Preisblatt 2027 vorläufig
- SNB945322307522 Elektrizitätsgenossenschaft Karlstein — Preisblatt 2027 vorläufig
- SNB917593691679 Elektrizitätswerk Unterwössen Dölle — Preisblatt Netzentgelte 2027 vorläufig
- SNB997465895442 Energie- und Bäderbetrieb Hauenstein — Preisblatt NNE 2027 vorläufig
- SNB980126228475 Elektrizitätswerk Mainbernheim GmbH — HLZF 2027 (§19 Abs. 2 StromNEV)
- SNB986403410816 Elektrizitäts-Genossenschaft Rettenberg eG — HLZF 2027
- SNB931431136771 Elektroenergieversorgung Cottbus GmbH — HLZF 2027 (per Bild geprüft, Jahr 2027 bestätigt; NS/MS/NS-Umspannung-Tabelle)

Verworfen: EWA Altenburg (Wiederverkäufernachweis), EWF (Gas-Preisblatt), Cottbus-Preisblatt fehlt noch (nur HLZF gefunden).

## 2027-vorläufig — Crawl-Batches 150–210 verifiziert (Commits 3ff7265 + dieser)

Neu in `eingang/2027_vorlaeufig/`:
- SNB963792700889 ENWG Energienetze Weimar GmbH — Preisblatt 2027 vorläufig
- SNB989583209836 EVU der Gemeinde Gochsheim — Preisblatt Netznutzung 2027
- SNB915186313908 Energieversorgung Guben GmbH — HLZF 2027
- SNB921629791202 ENGIE Deutschland GmbH (Radeberg) — HLZF 2027
- SNB953495670831 EnR Energienetze Rudolstadt GmbH — HLZF 2027
- SNB961497906636 GELSENWASSER Energienetze GmbH — HLZF 2027 (Netzgebiet Stolzenau/Rehburg-Loccum)
- SNB968325295962 Gemeinde Glattbach — HLZF 2027
- SNB977966674678 EW Geiger GmbH — HLZF 2027

Verworfen: EVF/Freiberger/EVR Rottenburg/EVI Inselsberg/FairNetz (Gas), EVU Späth (2026), Gemeindewerke Ebersdorf (2025), EVB Netze (WVN-Nachweis), ewag kamenz (Netzstrukturdaten-Übersicht, kein Preisblatt).

## 2027-vorläufig — Crawl-Batches 210–360 verifiziert (Commits 5dbf429, da5dcc0 + dieser)

Neu in `eingang/2027_vorlaeufig/`:
- SNB933529129573 Getreidemühle Zwiefalten eG — Preisblatt 2027 vorläufig
- SNB961316124487 Gothaer Stadtwerke NETZ GmbH — Preisblatt Netzzugang Strom 2027 vorläufig
- SNB986580518855 KommEnergie GmbH — Preisblatt 2027 vorläufig
- SNB933391394338 Merck Site Management GmbH — Preisblatt Netznutzung 2027 (2026 war "kein Preisblatt")
- SNB943170046990 MVE eurokom — Preisblatt 2025–2027 (enthält 2027)
- SNB977443469322 LokalWerke GmbH — Preisblatt NNE Strom 2027 vorläufig
- SNB983526428810 Mainnetz GmbH — Preisblatt Strom NNE 2027 vorläufig
- SNB931610892481 Nordseeheilbad Borkum GmbH — Preisblatt Strom 2027 vorläufig
- SNB985993443181 Stadtwerke Arnstadt Netz GmbH — Preisblatt 2027
- SNB957591716776 Stadtwerke Aue-Bad Schlema GmbH — HLZF 2027

Verworfen u.a.: Grefrath (Gas), Kirkel (2026er Blatt), KEEP/STW Has/Nordhausen (WVN), KEW/Mainfranken/SW am See/SW Achim/SachsenNetze HS.HD/Saalfelder (Gas), LiKra Sonneberg (Baukostenzuschuss), Netzges. Eisenberg (MSB/AN, kein Strom), Netzges. Ahlen (2026er Blatt), Ebersdorf (2025).
