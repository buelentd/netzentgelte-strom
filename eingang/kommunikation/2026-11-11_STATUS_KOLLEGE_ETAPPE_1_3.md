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

## 2027-vorläufig — Crawl-Batches 360–540 verifiziert (Commits c6f0b20, 58599a4, 79ae623, 35f0368 + dieser)

Neu in `eingang/2027_vorlaeufig/`:
- SNB977253144464 Stadtwerke Bad Neustadt a.d. Saale — HLZF 2027
- SNB949369515353 Stadtwerke Burgdorf Netz GmbH — Preisblätter Strom 2027 (1–6)
- SNB922514070884 Stadtwerke Bliestal GmbH — HLZF 2027
- SNB927160517950 Stadtwerke Burg Energienetze GmbH — HLZF 2027
- SNB983029590205 Stadtwerke Güstrow GmbH — Preisblatt NNE Strom 2027
- SNB989253327099 Stadtwerke Haslach i.K. — HLZF 2027
- SNB925565312521 Stadtwerke Gaggenau — HLZF 2027
- SNB958416423039 Stadtwerke Emsdetten GmbH — HLZF 2027
- SNB945861817537 Stadtwerke Jena Netze GmbH — HLZF 2027
- SNB958680286002 Stadtwerke Hollfeld — HLZF 2027
- SNB918070278383 Stadtwerke Meerane GmbH — Preisblatt Strom 2027
- SNB989365725226 Stadtwerke Neumarkt i.d. OPf. — Netzentgelte Strom 2027
- SNB984863778941 Stadtwerke Mosbach GmbH — HLZF 2027
- SNB955718588763 Stadtwerke Neunburg vorm Wald — HLZF 2027

Verworfen: Bad Brückenau/Bad Pyrmont/Bad Salzuflen/Bad Wildbad/Bayreuth/Bamberg/Bernau/Eichstätt/Elmshorn/Emmerich/Hameln/Heidelberg/Heiligenhaus/Lippe-Weser/Mühlheim a.M./Meiningen (Gas oder Nicht-NNE), Crailsheim/Meiningen/Hollfeld-WVN/KEEP (WVN), Ilmenau (iMSB), Hockenheim (Delta-Gas), Döbeln (Jahr/Level unklar), Heiligenstadt (Konzessionsabgabe/Umlagen, kein NNE-Preisblatt), Husum (Gas-Preisblatt).

## 2027-vorläufig — Domain-Crawl komplett (769 Domain-Zeilen, Batches 0–769) — Abschluss Commit 69fa7f8 + dieser

Letzter Batch 750–769:
- SNB941650885558 VSE Verteilnetz GmbH — HLZF 2027 (alle SpE, Hochspannung/…)
- SNB946612539746 VBH Hoyerswerda — verworfen (Gas-Grundversorger 2025–2027)

Gesamtbilanz Domain-Crawl (eingang/2027_vorlaeufig/, zusätzlich zu 56ccddd + Nutzer-Uploads):
- 18 Preisblätter Strom 2027 vorläufig neu abgelegt (Magdeburg, Blomberg, BEW, C. Ensinger, Bauer Netz, DSDL, Dahner Felsenland, Hindelang, eG Karlstein, Unterwössen, Hauenstein, Weimar, Gochsheim, Zwiefalten, Gotha NETZ, KommEnergie, Merck, MVE eurokom, LokalWerke, Mainnetz, Borkum, Arnstadt, Burgdorf, Güstrow, Meerane, Neumarkt, SWO Holstein, Schwäbisch Gmünd, Vilshofen, Wismar, Weiden, ÜZ Mainfranken)
- 17 HLZF-2027 neu abgelegt (Düsseldorf, Pfalzwerke, Alliander, ODR, Mainbernheim, Rettenberg, Cottbus, Guben, ENGIE Radeberg, Rudolstadt, Gelsenwasser, Glattbach, EW Geiger, Bad Neustadt, Bliestal, Burg, Haslach, Gaggenau, Emsdetten, Jena, Hollfeld, Mosbach, Neunburg, Rosenheim, St. Ingbert, Wasserburg, Waren, Vlotho, Wernigerode, ÜWL Leinetal, ÜWR Rhön, VSE)
- Alle Dateien inhaltsgeprüft (2027 + Strom + Preisblatt/HLZF; verworfen: Gas, §14a-Modul 3, WVN, BKZ, Konzessionsabgabe, MSB, Grundversorger, 2025/2026er Blätter, fiktive Blätter, Scans ohne Text)
- Verbleibend ohne Dokument: Rest der 769 Domain-Zeilen (kein 2027-PDF erreichbar) sowie 403/robots-Fälle bleiben als blockiert dokumentiert.

## 2027-vorläufig — Crawler 27d (Seed-Pfade + Anchor-Scoring + Sitemap + HTML-Fallback), 99 valide Dokumente (Commit fac9bca)

Neu in `eingang/2027_vorlaeufig/` (Auszug, MaStR-Nr. zuerst): u. a. SNB911347846643 Stadtwerke Ingolstadt Netze, SNB911641710114 Regionetz, SNB913130054136 NGS Schwerin (HLZF), SNB913244202027 SW Bretten, SNB914306944756 WSW Netz, SNB916123648602 Netze Duisburg (HLZF), SNB918516394612 Bielefelder Netz, SNB922607376381 SW Bochum Netz, SNB924477581384 RheinNetz, SNB926644622999 Braunschweiger Netz, SNB913992545742 E-Werk Netze, SNB954187049256 SW Springe (HLZF), SNB950336540445 SW Husum Netz, SNB951760950909 KEEP (HLZF) — insgesamt 90 Preisblätter + 9 HLZF aus 2.366 Kandidaten-PDFs (2.115 verworfen: falsches Jahr, Gas, WVN, iMSB, Stromkennzeichnung etc.).

Gesamtbestand eingang/2027_vorlaeufig/: 133 Preisblaetter 2027 vorlaeufig + 43 HLZF-2027.

## 2027-vorläufig — Kollegen-Crawl (main) ausgewertet: 54 HLZF/Preisblatt-2027-Dokumente übernommen (Commit a1a333c)

Aus `eingang/pdfs_neu/` auf main alle 2027-relevanten PDFs inhaltsgeprüft (2027 + Strom + HLZF/Preisblatt) und für noch offene MaStR-Nr. unter den vorgeschriebenen Namen abgelegt, überwiegend HLZF 2027 (u. a. LEW Verteilnetz, EWE NETZ, WEMAG, Mainzer Netze, EWR Remscheid, Netz Leipzig, Stadtwerke Tübingen, Emden, DB Energie Bahnstrom, ESM Selb, MITNETZ, CPM Netz, Hanau Netz, …). XLSX-HLZF (z. B. GETEC) und 2025/2026er-Dokumente nicht übernommen.

Hinweis: Playwright/Chromium ist in meiner Sandbox nicht installiert — der Chromium-Crawler des Kollegen kann ich nicht selbst ausführen; ich arbeite mit ehrlichem UA + urllib weiter und werte seine Ergebnisse aus.

## 2027-vorläufig — Zwischenstand 12.11. (neuer Chromium-Crawler vnb/hlzf_crawl, main 94888e8)

- 13 HLZF-2027 aus dem Chromium-Crawl inhaltsgeprueft und abgelegt (Commit 593a3a6): u. a. Energienetze Berlin, MVV Netze, Bonn-Netz, EnergieSuedwest Netz, EMB Miltenberg, EV Alzenau, EV Ruesselsheim, BIGGE ENERGIE, E-Werk Goldbach-Hoesbach, EV Inselsberg, Freisinger Stadtwerke, Abita Otterberg, E-Werk Bruchmuehlbach.
- Crawler laeuft ueber 508 offene MaStR-Nr. (bisher ~29 bearbeitet: 16 kein_treffer, 6 gefunden_2026, 3 nicht_erreichbar, 2 blockiert, 1 nur_aelter).
- HTML-Tabellen-Funde: SNB953422913031 Gebrueder Eirich — Seite "Individuelle Netzentgelte" mit HLZF-Tabelle (28 Zeitfenster), Text nennt 2026 (2027 auf der Seite nicht gefunden) -> Kandidat fuer 2026-Fallback, 2027 offen.
- Manuelle Nachpruefung (Browser durch dich): 2026-11-12_BLOCKIERT_MANUELL_PRUEFEN.csv — 92 Faelle: 49 nicht_erreichbar, 40 blockiert (403), 2 robots_dokument_bekannt, 1 anfrage. Nichts wird umgangen; Direktadressen in der Spalte hinweis/dokument_url.

- SNB926699071292 Albwerk GmbH & Co. KG — Preisblatt Netzentgelte 2027 vorläufig (Nutzer-URL, robots ok, 200, inhaltsgeprueft: vorläufige Preise gültig ab 01.01.2027). Ebenfalls geliefert: Individuelle-Netentgelte-2026-N031.pdf (HLZF 2026, lokal in dl_up, 2027-HLZF fuer Albwerk nicht geliefert).

## 2027-vorläufig — Crawler-Stand 12.11. (vnb/hlzf_crawl, main 94888e8, Chromium headless)

Crawler-Lauf ueber 508 offene MaStR-Nr. nahezu abgeschlossen (503 bearbeitet): 218 kein_treffer, 111 nicht_erreichbar, 115 blockiert (403 — dokumentiert, nicht umgangen), 38 gefunden_2026, 5 nur_2027, 9 nur_aelter, 2 robots_dokument_bekannt, 2 zeitlimit, 1 anfrage, 1 keine_website, 1 robots. 285 PDFs geladen.

Daraus inhaltsgeprueft und abgelegt: 13 HLZF-2027 (Commit 593a3a6) + 26 weitere Dokumente (Commit 0532875: 18 Preisblaetter 2027 + 8 HLZF-2027, u. a. SW Bad Duerkheim, SW Elbtal, Netz+Service, Queichtal Offenbach, Reussenkoege, SW Lambrecht, SW Bad Hersfeld, SV Angermuende, SVH Haar, SW Bad Pyrmont; Preisblaetter u. a. TWL, TWS, Warendorf, Pfaffenhofen, LeineNetz, Herrenberg …) + Albwerk Preisblatt 2027 (Nutzer-URL, 01dd277).

Gesamtbestand eingang/2027_vorlaeufig/: siehe Dateiliste auf dem Branch.
Blockiert-Liste fuer manuelle Pruefung: eingang/kommunikation/2026-11-12_BLOCKIERT_40_TABELLE.md (40 Faelle) bzw. ..._MANUELL_PRUEFEN.csv (92 Faelle inkl. nicht_erreichbar/robots/anfrage).

- SNB918620072652 ASCANETZ GmbH — HLZF 2027 (HLFZ-asc27.pdf) + Preisblatt NNE Strom 2027 vorläufig (Nutzer-URLs, robots ok, inhaltsgeprueft).

- SNB973356062049 Bad Honnef AG — Preisblatt Stromnetzentgelte 2027 vorläufig (Nutzer-Upload, inhaltsgeprueft: gültig ab 01.01.2027, Stand 15.10.2026). Ebenfalls geliefert: Hochlastzeiten-BHAG-2026.pdf (HLZF 2026, lokal in dl_up/bhag, 2027-HLZF nicht geliefert).

- SNB990362338043 Avacon Netz GmbH — HLZF 2027 (regionale Methode, §19 Abs. 2 StromNEV) + Preisblätter Strom 01.01.2027 vorläufig (Nutzer-Uploads, inhaltsgeprueft; automatisierter Abruf war 403-blockiert).

- SNB940352624434 Bayernwerk Netz GmbH — HLZF 2027 + Preisblatt Netzentgelte 2027 vorläufig (Nutzer-Uploads, inhaltsgeprueft; automatisierter Abruf war 403-blockiert).

- SNB940133714842 Creos Deutschland GmbH — HLZF 2027 + Preisblätter NNE Strom „ab 01.01.2027 vorläufig“ (Nutzer-Uploads, inhaltsgeprueft; Dateiname nennt 2026, Inhalt bestaetigt 2027). Automatisierter Abruf war 403-blockiert.

- SNB973074326355 ELE Verteilnetz GmbH (EVNG) — HLZF 2027 (§19, Jahr 2027 im Text; Betreiber aus Upload-Stapel, da das HLZF-PDF selbst keinen Namen nennt) + voraussichtliche Netzentgelte Strom ab 01.01.2027 (Nutzer-Uploads, inhaltsgeprueft; automatisierter Abruf war 403-blockiert).
- Vorige Uploads nicht im 2027-Scope abgelegt: Dessauer Stromversorgung HLZF-2026 (lokal dl_up/sonst) und Netznutzungsentgelte Gas 2027 (Gas — verworfen).

- SNB985099151188 Elektrizitätswerk des Kantons Schaffhausen AG (EKS) — Netz Nutzung DE 2027 (Nutzer-Upload, inhaltsgeprueft: EKS Schaffhausen, Netznutzungsentgelte Strom, 2027). Automatisierter Abruf war 403-blockiert.

- SNB914735995145 Energiegenossenschaft für Wittmund eG — Preisblatt Strom 2027 vorläufig (Nutzer-Upload)
- SNB932516649124 EWR Rheine GmbH — Preisblatt Strom 2027 vorläufig (Nutzer-Upload)
- SNB994111700501 Energienetze Bayern (Germering) — HLZF 2027 §19 (Nutzer-Upload)
- Offen: hlzf_2027.pdf aus dem Wittmund/Rheine-Stapel nennt keinen Betreibernamen im Text — lokal dl_up/sonst/hlzf_2027_ungeordnet.pdf, Zuordnung bitte durch Nutzer bestaetigen.

- SNB991797615686 Energieversorgung Lohr-Karlstadt und Umgebung GmbH & Co. KG (EVK) — HLZF 2027 §19 + Preisblatt Strom 2027 vorläufig, Stand 15.10.2026 (Nutzer-Uploads, inhaltsgeprueft; automatisierter Abruf war 403-blockiert).

- SNB967982606159 Erlanger Stadtwerke AG (ESTW) — Preisblatt Netznutzungsentgelte Strom, gültig ab 01.01.2027, Stand Oktober 2026, vorläufig (Nutzer-Upload, inhaltsgeprueft). HT/NT-Schwachlastzeiten (Modul 3) liegen auf der Website und im Preisblatt — gehören in ergebnis/modul3_zeiten.csv, nicht in die HLZF-Spalten. Automatisierter Abruf war 403-blockiert.

- SNB940297211072 EZV Energie- und Service GmbH & Co. KG Untermain — NNE-Preisblatt ab 01.01.2027 vorläufig + HLZF 2027 §19 (Nutzer-Uploads, inhaltsgeprueft). Zweites HLZF-PDF (andere md5) lokal dl_up/sonst.
- SNB923953358557 EWR Netze GmbH (Lichtenstein-Unterhausen) — Netzentgelte ab 01.01.2027 vorläufig, Stand 13.10.2026 (Nutzer-Upload; Betreiber aus Text "EWR Netze GmbH").
- Langenpreising-Uploads (2026) lokal dl_up/sonst, nicht im 2027-Scope.

## HLZF 2027 gelesen (Kollege) — erste 7 Zeilen in ergebnis/hlzf/hlzf_2027_gelesen.csv

Gelesen aus den 2027-Dokumenten in eingang/2027_vorlaeufig/ (Text+Bild, Bild entscheidet): SNB911696239035 ESM Selb-Marktredwitz (nur MS), SNB913130054136 NGS Schwerin, SNB911521002599 EnergieSuedwest Netz Landau, SNB913576376151 EV Alzenau, SNB915186313908 EV Guben, SNB914879260819 SW Wernigerode, SNB910474681448 SW Stassfurt (nur MS, 1/4-h-Raster). jahr=2027, vorlaeufig in bemerkung. Neustrelitz (SNB914630088973) entpuppte sich als 2026-Dokument -> nicht in 2027 uebernommen. Weitere 84 offene Dokumente folgen.

- SNB947727983103 Gemeindewerke Frammersbach — Netzentgelte Strom 2027 vorlaeufig + HLZF 2027 (Nutzer-Uploads)
- SNB990971435621 Freiberger Stromversorgung GmbH — vorlaeufiges Preisblatt NNE Strom 2027 (Stand 15.10.2026) + HLZF 2027 (Nutzer-Uploads)
- SNB991410365127 Gemeindewerke Ebersdorf — Preisblatt NNE Strom 2027 vorlaeufig (15.10.2026) + HLZF 2027 (Nutzer-Uploads)

- SNB926937565941 Gemeindewerke Garmisch-Partenkirchen KU — Preisblatt Netzentgelte Strom 2027 vorlaeufig, Stand 15.10.2026 (Nutzer-Upload, inhaltsgeprueft).
- Aus demselben Upload-Stapel ohne Betreibernamen im Text (nicht zugeordnet, lokal dl_up/sonst): 2x Preisblatt 2027 vorlaeufig (OjzUSMbT, aMmLmXxU), 1x HLZF 2027 (vy6yJTHy), 2x HLZF 2026 (9uGAiPSI, zwXq30kI = Pleinfeld 2026). Zuordnung bitte durch Nutzer.
