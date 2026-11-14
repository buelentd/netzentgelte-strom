## Nachtrag: HLZF-2027-Suche Block 1+2 - Lieferung 1 (22 Zeilen)

Neu in ergebnis/hlzf/hlzf_2027_gelesen.csv geliefert (22 Zeilen, jahr=2027, nr-Spalte fuer 400er-Liste leer, Stromnetz Berlin mit nr=1):
- SNB979269087643 Stromnetz Berlin GmbH
- SNB971311555230 EAM Netz GmbH
- SNB973875583315 N-ERGIE Netz GmbH
- SNB929881052512 Westfalen Weser Netz GmbH
- SNB970821959712 TEN Thüringer Energienetze GmbH ＆ Co. KG
- SNB921899277833 NRM Netzdienste Rhein-Main GmbH
- SNB968914838013 SachsenNetze HS.HD GmbH
- SNB976379598847 energis-Netzgesellschaft mbH
- SNB923953358557 EWR Netze GmbH (Lichtenstein-Unterhausen)
- SNB983425156814 TraveNetz GmbH
- SNB971087047229 Stadtwerke Karlsruhe Netzservice GmbH
- SNB950584553167 Stadtwerke Wiesbaden Netz GmbH
- SNB950262883869 SWE Netz GmbH (Erfurt)
- SNB912743424114 Energie- und Wasserversorgung Hamm GmbH
- SNB936172924014 Energie Waldeck-Frankenberg GmbH
- SNB950006175489 SWTE Netz GmbH ＆ Co. KG
- SNB922220582657 Stadtwerke Flensburg GmbH
- SNB990887002092 Thüga Energienetze GmbH
- SNB939624707241 Neubrandenburger Stadtwerke GmbH
- SNB929027950139 Netzgesellschaft Potsdam GmbH
- SNB977443469322 LokalWerke GmbH
- SNB911144461377 NGN Netzgesellschaft Niederrhein mbH

Bereits im Arbeitsstand vorhanden und daher NICHT erneut geliefert: SNB981060961299 Dortmunder Netz, SNB961471621746 Pfalzwerke Netz, SNB980808485264 SachsenNetze GmbH, SNB916123648602 Netze Duisburg, SNB935482852901 Staedtische Werke Netz+Service (Werte deckungsgleich mit eigener Recherche).

Besonderheiten:
- SNB968914838013 SachsenNetze HS.HD: 2027-PDF vom NB-Server (200, application/pdf), bildbasiert ohne Text -> Browser-Liste/Augenschein.
- SNB922220582657 Flensburg: MS-Zeitstempel-Notation (Uhrzeit=Intervallende), NS mit N.N. gekennzeichnet, Interpretation unklar -> Nutzerpruefung.
- SNB977443469322 LokalWerke: Werte hinter gemeinsamer Herbst/Winter-Zeile, Zuordnung H+W mit Vorbehalt.
- SNB923953358557 EWR Netze GmbH (Lichtenstein-Unterhausen, ewr-netze.eu) ist NICHT identisch mit EWR Netz GmbH (SNB969068596941, ewr-netz.de) - getrennte Firmen, Dublettenpruefung beachten.
- Quellen-ZIP hlzf_quellen_etappe_7.zip kann nicht auf den Branch (github_app nimmt nur Text-Dateien), liegt lokal unter /home/user/artifacts/hlzf_quellen_etappe_7.zip.
- Offen (Positional-Parses, sobald Bash wieder verfuegbar): wesernetz Bremen (AES-verschluesselt), ENERVIE Vernetzt, EWR Netz GmbH Uebersicht, Mainzer Netze, SWP Pforzheim, SWS Solingen; ausserdem swa Netze 2027, FairNetz (Proxy blockiert), NHF, Stadtwerke Herne.
- Potsdam: korrekte URL lautet .../unsere_sparten_1/... (die in der 400er-Liste stehende URL enthaelt einen Tippfehler spartan_1).
## Nachtrag: HLZF-2027-Suche - Lieferung 2 (4 Zeilen)

Neu geliefert:
- SNB935723521351 Stadtwerke Weinheim GmbH
- SNB925999725461 Stadtwerke Neuwied GmbH
- SNB959523885956 Mainzer Netze GmbH
- SNB948816192529 GeraNetz GmbH

Besonderheiten:
- SNB959523885956 Mainzer Netze: HS/UHM/MS-Winterwerte gesichert; NS/UMN-Zuordnung im Extrakt nicht eindeutig -> Felder leer, Pruefung offen.
- SNB982030394239 Stadtwerke Lingen: 2027-PDF (netz.stadtwerke-lingen.de/...hlzf_2027.pdf) vom NB-Server geladen, ohne Textlayer -> Browser-Liste/Augenschein.
- SNB991882909515 FairNetz: automatisierter Zugriff auf fairnetzgmbh.de blockiert (kein Umgehen) -> Browser-Liste.
- SNB920157746937 GEW Wilhelmshaven: automatisierter Zugriff blockiert -> Browser-Liste (oder curl, sobald Bash wieder verfuegbar).
- Zurueckgestellt fuer Positional-Parse (Bash gerade nicht verfuegbar): NHF (Tabelle 5-Spalten), ENERVIE Vernetzt (5 Segmente x 7 Ebenen), BEW-Netze Bocholt/stadtwerker (3 Ebenen x 4 Jahreszeiten), Ahrtal 2027, wesernetz Bremen (AES), EWR Netz GmbH, SWP Pforzheim, SWS Solingen, Mainzer NS/UMN.
- Kein 2027-Fund per Websuche: e-regio Netz, Stadtwerke Ludwigsburg-Kornwestheim, Stadtwerke Ostmuensterland, SWT Trier, StWB Brandenburg, Stadtwerke Herne, swa Netze (2027 noch nicht gefunden; Suchlinks folgen).
## Nachtrag: HLZF-2027-Suche - Lieferung 3 (3 Zeilen)

Neu geliefert:
- SNB913992545742 E-Werk Netze GmbH ＆ Co. KG (volle Werte)
- SNB922607376381 Stadtwerke Bochum Netz GmbH (2027-PDF gefunden, Ebenen-Zuordnung der Zellen im Textextrakt nicht eindeutig -> Werte nicht uebernommen, Browser-Liste)
- SNB978108787379 NHL Netzgesellschaft Heilbronner Land GmbH ＆ Co. KG (2027-PDF gefunden, Spaltenzuordnung Winter Jan-Feb/Dez nicht eindeutig -> Felder leer, Nutzerpruefung)

Hinweise:
- WSW Wuppertal (WSW-Netz-S-105-Hochlastfenster_fuer_2027.pdf), e-netze Allgaeu (ENA_Hochlastzeitfenster_2027.pdf) und Stadtwerke Leipzig (files.l.de ...HLZF...2027.pdf) stehen NICHT auf der 400er-Liste, daher keine Zeilen. Leipzig-PDF blockiert beim Proxy-Zugriff.
- SNB-Konflikt: Die 400er-Liste weist SNB962618092306 den Stadtwerken Schwaebisch Gmuend zu. Im hlzf_2027_gelesen.csv laeuft SNB962618092306 unter SWM Infrastruktur GmbH (Zeile aus Preisblatt-Crawler, Felder leer). Bitte Zuordnung klaeren. Die Zeile bleibt unveraendert.
## Nachtrag: HLZF-2027-Suche - Lieferung 4 (3 Zeilen)

Neu geliefert (jeweils 2027-PDF vom NB-Server gefunden; Textextrakt ohne eindeutige Zellzuordnung -> Felder leer, Werte in bemerkung gesichert, Browser-Liste/Augenschein empfohlen):
- SNB998819299022 NHF Netzgesellschaft Heilbronn-Franken mbH (Tabelle-1-Layout wie NHL)
- SNB929168402344 SWP Stadtwerke Pforzheim GmbH ＆ Co. KG
- SNB917625393281 Stadtwerke Passau GmbH (Uhrzeit=Endzeitstempel)

Nicht gefunden/404 bzw. nicht lesbar ueber Proxy: Stadtwerke Hof (Erratum-URL 404), Stadtwerke Herne (erratumene 2027-URL 404), SWK Kaiserslautern (Persistent-Ordner-Erratum blockiert), Stadtwerke Luenen (Erratum liefert Cookie-HTML-Seite), Stadtwerke Hilden (erratumene URL liefert Cookie-Consent-Seite).
## Nachtrag: HLZF-2027-Suche - Lieferung 5 (4 Zeilen)

Neu geliefert:
- SNB993059842564 Stadtwerk am See GmbH ＆ Co. KG (volle Werte)
- SNB918576265276 stadtwerker GmbH (BEW-Netze Bocholt): 2027-PDF gefunden, nur ein Zeitensatz je Jahreszeit im Extrakt, Ebenen-Zuordnung unklar -> Felder leer, Browser-Liste
- SNB921319639913 ENERVIE Vernetzt GmbH: 2027-PDF gefunden (5 Segmente x 7 Ebenen), Extrakt nicht zuordenbar -> Felder leer, Browser-Liste
- SNB969068596941 EWR Netz GmbH: Uebersicht 2027 gefunden, Extrakt nicht zuordenbar -> Felder leer, Browser-Liste

Nicht gefunden (404/blockiert): SWO Netz (erratene URL 404), Stadtwerke Herne (erratene 2027-URL 404, Websuche ohne Herne-Fund), GEW Wilhelmshaven (Zugriff blockiert -> Browser-Liste), wesernetz Bremen/Bremerhaven (liefern Cookie-Consent-Seite statt PDF -> Browser-Liste).

## Nachtrag: Lieferung 6 (2026-11-14)

- SNB915638224585 SWS Netze GmbH (Stralsund): 2027-HLZF-PDF vom NB-Server vollstaendig gelesen und geliefert (NS, MS/NS, MS in Bemerkung; Uhrzeit=Intervallende; nur Werktage).
- SNB969362778135 SWS Netze Solingen GmbH: 2027-PDF (zeitfenster-netznutzung-2027.pdf) gefunden; Textextrakt ohne eindeutige Zellen-/Ebenen-Zuordnung -> Felder leer, gesicherte Zeiten in Bemerkung, Browser-Liste. 2026er Vergleichs-PDF nicht mehr abrufbar (404).
- SNB961745390019 Stadtwerke Frankenthal: kein 2027er HLZF-Dokument; Preisblatt 2027 geprueft (kein Paragraph-19-Abschnitt) -> negativ dokumentiert.
- SNB953453232156 Stadtwerke Sindelfingen: kein 2027er HLZF-Dokument; Preisblatt 2027 geprueft (kein Paragraph-19-Abschnitt) -> negativ dokumentiert.
- Konsolidierung: 16 bereits frueher dokumentierte Negativ-/Blockiert-Faelle der 400er-Liste als Zeilen mit leeren Feldern aufgenommen (wesernetz Bremen/Bremerhaven Cookie-Consent, FairNetz, SWO 404, Herne 404, GEW Wilhelmshaven blockiert, e-regio/Ludwigsburg/Ostmuensterland/SWT Trier/StWB/SVO ohne 2027-Fund, SWK Kaiserslautern/Luenen nicht abrufbar, Hilden Cookie, Hof 404).
- Bestand hlzf_2027_gelesen.csv danach: 205 + 20 = 225 Zeilen.

## Nachtrag: HLZF-2027-Suche - Lieferung 7 (15 Zeilen, 2026-11-14)

Lieferung 7 (alle jahr=2027, nr leer):
- swa Netze GmbH: volle Werte aus Preisblatt 2027 (Seite 14). NS H 17:15-18:30, W 16:30-19:30; MS/NS H 17:15-18:45, W 16:45-19:15; MS/HS/HS-MS in bemerkung.
- Energieversorgung Filstal: NS H+W 16:30-19:30, MS/NS W 16:30-19:30; MS W 08:15-14:15, H 09:45-13:15.
- Stadtwerke Waiblingen: NS W 12:00-13:45 + 17:30-19:45, MS/NS W 17:30-19:45; MS W 09:30-13:45 + 17:30-19:15.
- Stadtwerke Neustadt a.d. Weinstr.: Umsp MS/NS W 17:00-19:00, NS H 11:30-13:00, MS W 17:00-19:00 (Zuordnung nach Textextrakt-Reihenfolge).
- Netzgesellschaft Frankfurt (Oder): NS W 10:00-13:00, MS/NS W 09:45-13:00; MS W 08:15-13:00 + 16:30-19:00; Schwellen 20/30, 100 kW, 500 EUR.
- Stadtwerke Wolfenbuettel: NS W 17:00-19:00, MS/NS W 17:00-19:00; MS W 09:30-09:45 + 11:30-12:00 + 17:00-19:00 (HTML-Tabelle).
- Heider Energie Woerth: NS W 16:30-19:30, MS/NS W 16:30-19:30; MS W 07:00-09:30 + 16:30-19:30 (HTML-Tabelle).
- KORREKTUR Stadtwerke Ostmuensterland: 2027-HLZF-Dokument doch gefunden (Download-Link so.de), Zellen nicht eindeutig zuordenbar -> Felder leer, Zeiten in bemerkung, Browser-Liste (ersetzt frueheren Eintrag "kein Dokument").
- Nicht auswertbar: Stadtwerke Lingen (2027-PDF nur Titelzeile im Textlayer), Stadtwerke Duelmen (Uhrzeiten nicht im Textlayer), Stadtwerke Gronau (Zellen nicht eindeutig zugeordnet) -> Browser-Liste.
- Kein 2027-Fund: Vereinigte Stadtwerke Netz, Stadtwerke Rastatt, Soest, SWL Verteilungsnetzgesellschaft (Ludwigshafen), Stadtwerke Bruel -> Browser-Liste.

Hinweis: Offen-Definition korrigiert - es zaehlen nur Zeilen mit jahr=2027. Von 400 Eintraegen fehlten vor Lieferung 7 noch 281 mit 2027-Zeile; Lieferung 7 liefert 15 neue (Bestand danach 240 Zeilen).
## Nachtrag: HLZF-2027-Suche - Lieferung 8 (5 Zeilen, 2026-11-14)

- Stadtwerke Lemgo: volle Werte (MS W 08:15-09:00 + 09:45-13:15; NS nur Fruehling 16:15-16:30); Umsp MS/NS W 17:00-19:0x im Textextrakt abgeschnitten -> msns-Feld leer, Browser-Liste.
- Stadtwerke Dreieich: 2027-PDF gefunden (Druckfehler "Genehmigungszeitraum 2026"), Ebenen-/Saison-Zuordnung nicht eindeutig -> Felder leer, Browser-Liste.
- Kein 2027-Fund: Stadtwerke Homburg (Netzentgelte-Seite ohne HLZF, Cookie-Consent), Stadtwerke Amberg (2026er-Muster-URL 404), Stadtwerke Nuertingen (Downloadliste ohne HLZF) -> Browser-Liste.
- Hinweis: PDF auf stadtwerke-service.de (sites/6, Zeitfenster 2027, mit aus HS/in MS/aus MS/in NS) nennt keinen Netzbetreiber, daher keiner SNB zugeordnet.
- Bestand hlzf_2027_gelesen.csv danach: 241 + 5 = 246 Zeilen.

## Nachtrag: HLZF-2027-Suche - Lieferung 9 (5 Zeilen, 2026-11-14)

- Stadtwerke Pirmasens: 2027-PDF vollstaendig lesbar; NS W 11:00-13:00 + 17:00-19:00, MS/NS W 11:30-13:00 + 17:00-18:45, MS in bemerkung; F/S/H entfaellt.
- Maintal-Werke: 2027-PDF vollstaendig lesbar (URL enthaelt Tippfehler "hochlastzeifenster"); NS/MS/MS-NS-Werte geliefert.
- Stadtwerke Itzehoe: 2027-PDF vollstaendig lesbar; NS H 10:00-11:00 + 17:00-19:30, W 10:45-12:00 + 17:30-18:45; MS/NS nur H; MS in bemerkung (Winter 08:30-14:00, Herbst 08:00-11:30).
- Freitaler Stadtwerke: 2027-PDF vorhanden, Textextrakt ohne eindeutige Jahreszeiten-Zuordnung -> Felder leer, Zeiten in bemerkung, Browser-Liste.
- Überlandwerk Erding: 2027-PDF auf stadtwerke-erding.de (dort laut Kontaktdatenblatt auch Netzbetreiber U.Erding) vollstaendig lesbar; NS und MS/NS je H/W 16:45-19:15, MS in bemerkung.
- Bestand hlzf_2027_gelesen.csv danach: 246 + 5 = 251 Zeilen.

## Nachtrag: HLZF-2027-Suche - Lieferung 10 (5 Zeilen, 2026-11-14)

- Stadtwerke Pirna Energie: 2027-PDF vollstaendig lesbar; MS/NS nur Sommer 10:15-13:15, NS nur Winter 16:15-17:30, MS ohne Zeitfenster.
- Stadtwerke Backnang: 2027-PDF (HLZF-Backnang-2027-alle.pdf) vollstaendig lesbar; Titel enthaelt Druckfehler "2025" (Referenzzeitraum/Feiertage 2027). NS H 09:45-12:45 + 13:00-13:15, W 08:45-13:45 + 16:45-18:00; MS/NS W 16:30-19:30; MS W 16:15-19:15 in bemerkung.
- Stadtwerke Greven: 2027-Uebersichtsblatt gefunden, Ebenen-Zuordnung im Textextrakt nicht eindeutig -> Felder leer, gesicherte Zeiten in bemerkung, Browser-Liste.
- Stadtwerke Wedel: Cookie-Consent, erratene 2027er URL-Varianten ohne Treffer -> Browser-Liste.
- SWE Netz Ettlingen: HLZF-2027-Link auf der Netzzugang-Seite vorhanden, PDF-URL nicht ermittelbar -> Browser-Liste.

## Nachtrag: HLZF-2027-Suche - Lieferung 11 (4 Zeilen, 2026-11-14)

- Stadtwerke Schwabach: 2027-Bekanntmachung (PDF vom 02.11.2026) vollstaendig lesbar; NS W 16:45-19:30, H 17:00-17:30; MS/NS W 16:45-19:30, H 17:00-17:15; MS W 08:00-14:15 + 17:00-17:45 in bemerkung.
- Netzwerke Saarlouis: erratene 2027er URL 403 -> Browser-Liste.
- Stadtwerke Tuttlingen: Cookie-Consent, kein 2027-Fund -> Browser-Liste.
- Stadtwerke Balingen: 2027er PDF nicht auffindbar (404 auf erratene Varianten) -> Browser-Liste.

## Nachtrag: HLZF-2027-Suche - Lieferung 12 (6 Zeilen, 2026-11-14)

- UEZW Woerth/I.-Altheim Netz AG: 2027-HLZF-PDF vollstaendig lesbar; NS nur W 18:00-20:15; Umspg MS/NS H 08:00-08:45, W 08:30-12:00; MS in bemerkung.
- Stauferwerk GmbH: Individuelle-Netzentgelte-2027-PDF lesbar; NS H 17:15-18:45, W 11:45-12:15 + 16:45-20:00; Umsp NS H 17:00-18:15, W 17:00-20:00; MS nur W in bemerkung.
- Stadtwerke Merseburg: 2027-HLZF lesbar; NS/MS-NS je H 16:45-19:00, W 11:15-12:15 + 16:00-19:15 (Bloecke identisch, Zuordnung mit Vorbehalt); MS in bemerkung.
- Stadtwerke Deggendorf: 2027-PDF vorhanden, Spaltenzuordnung nicht eindeutig -> Felder leer, Zeiten in bemerkung, Browser-Liste.
- TEN eG: kein 2027er HLZF-Dokument; Preisblatt 2027 nur Modul-3-HT/NT -> Browser-Liste.
- SEW Stromversorgungs GmbH (Erding): HLZF-Liste auf sewerding.de nur bis 2026 -> Browser-Liste.

## Nachtrag: HLZF-2027-Suche - Lieferung 13 (6 Zeilen, 2026-11-14)

- Stadtwerke EVB Huntetal Netz: 2027-PDF vom NB-Server vollstaendig lesbar; NS/MS-NS je H 17:45-18:45, W 17:15-19:30 bzw. 17:15-19:15; MS in bemerkung.
- Stadtwerke Geesthacht: 2027-PDF nach 2026er URL-Muster erraten und vollstaendig lesbar; NS/MS-NS nur W; MS in bemerkung.
- Stadtwerke Radolfzell: 2027-PDF lesbar; NS nur F 12:00-13:15; Winter-Zeiten (4 Fenster) nicht eindeutig MS/MS-NS zuordenbar -> msns-Felder leer, Browser-Liste; MS-Herbst in bemerkung.
- Kein 2027-Fund (erratene URLs 404, Websuche negativ): Stadtwerke Kempen, Netzgesellschaft Bitterfeld-Wolfen, Stadtwerke Freudenstadt -> Browser-Liste.

## Nachtrag: HLZF-2027-Suche - Lieferung 14 (3 Zeilen, 2026-11-14)

- Stadtwerke Weissenfels Energienetze: 2027-PDF (hochlastzeitfenster_swe_2027_final.pdf) vom NB-Server lesbar; NS/MS-NS je F 13:00-14:00, S 10:00-11:15 + 15:00-16:00, W 11:00-12:45 + 17:00-18:45, H keins; MS in bemerkung; Ebenen-Zuordnung nach Layoutreihenfolge mit Vorbehalt.
- Stadtwerke Rinteln: HLZF-2027-PDF auf Netzzugang-Seite gelistet, URL nicht ermittelbar (erratene Varianten 404) -> Browser-Liste.
- Stadtwerke Annaberg-Buchholz (swa-b.de): 2027-PDF vorhanden, automatisierter Zugriff blockiert -> Browser-Liste.

## Nachtrag: HLZF-2027-Suche - Lieferung 15 (4 Zeilen, 2026-11-14)

- Stadtwerke Schoenebeck: 2027-PDF vom NB-Server vollstaendig lesbar; NS nur W 11:45-15:15; MS in bemerkung; MS/NS nicht ausgewiesen.
- Kein 2027-Fund per Websuche (teilweise Cookie-Consent): Stadtwerke Wertheim, Stadtwerke Andernach Energie, Stadtwerke Werl -> Browser-Liste.

## Nachtrag: HLZF-2027-Suche - Lieferung 16 (9 Zeilen, 2026-11-14)

- Stadtwerke Buehl: 2027-PDF vollstaendig lesbar; NS nur W 07:45-14:45, MS/NS W 07:15-14:45, MS H+W 07:15-14:45 in bemerkung.
- Stadtwerke Strausberg: 2027-PDF lesbar; NS/MS-NS je W 16:30-19:00, MS W 08:15-13:45 + 15:45-19:00 in bemerkung.
- Stadtwerke Schifferstadt: 2027-Datenblatt lesbar; NS nur S 13:30-15:00, MS/NS W 17:00-19:15.
- Stadtwerke Northeim: 2027-PDF lesbar (mit Viertelstundenraster); NS/MS-NS-Werte geliefert, MS in bemerkung; MS/NS-Zuordnung mit Vorbehalt.
- Stromnetz Kulmbach: 2027-PDF vorhanden, nur drei Zeitfenster 10:45-12:00 im Extrakt, Saison-Zuordnung unklar -> Browser-Liste.
- Netzzugangs-/Download-Seite listet HLZF 2027, PDF-URL nicht ermittelbar: Stadtwerke Einbeck, Stadtwerke Neuburg -> Browser-Liste.
- Kein 2027-Fund per Websuche: Bautzen, Meissen -> Browser-Liste.
- Schwedt: Primaerverdacht swaue.de-HLZF gehoert zu Stadtwerken Aue (nicht Schwedt), keine Zuordnung vorgenommen -> Pruefung laeuft.

## Nachtrag: HLZF-2027-Suche - Lieferung 17 (11 Zeilen, 2026-11-14)

- Energieversorgung Suedbaar: 2027-PDF (esb-energie.de) vollstaendig lesbar; NS/MS-NS nur W, MS F/S in bemerkung.
- Stadtwerke Schuettorf (SWSE): Uebersichtsblatt lesbar, Saison-Zuordnung unklar -> Felder leer, Zeiten in bemerkung, Browser-Liste.
- Energie Calw: netz.plus-Uebersichtsblatt 2027 (Zuordnung plausibel, Vorbehalt), Saison-Zuordnung unklar -> Browser-Liste.
- Herzo Werke: HLZF-2027-URL gelistet, Abruf 404 -> Browser-Liste.
- Bad Kissingen: HLZF 2027 auf Netznutzungs-Seite gelistet, URL nicht ermittelbar -> Browser-Liste.
- Kein 2027-Fund per Websuche: Schwedt, Hann. Muenden, Schneverdingen-Neuenkirchen, Zirndorf, Altenburg, Inn-Salzach -> Browser-Liste.
- Hinweis Schwedt: swaue.de-2027-HLZF vermutlich Stadtwerke Aue zuzuordnen (Aue bereits geliefert), nicht Schwedt.

## Nachtrag: HLZF-2027-Suche - Lieferung 18 (5 Zeilen, 2026-11-14)

- Stadtwerke Elmshorn: 2027-PDF vollstaendig lesbar; NS/MS-NS nur W, MS W 11:30-13:30 + 17:15-19:00 in bemerkung.
- Stadtwerke Forchheim: 2027-PDF lesbar; NS W 16:45-19:45, Umsp MS/NS W 08:15-10:00; MS nur Sommer 09:00-17:00 (Spaltenfolge mit Vorbehalt) in bemerkung.
- Seite listet HLZF 2027, URL nicht ermittelbar: Eckernfoerder Netzgesellschaft, Eilenburger Stadtwerke -> Browser-Liste.
- Kein 2027-Fund: Stadtwerke Goch -> Browser-Liste.

## Nachtrag: HLZF-2027-Suche - Lieferung 19 (5 Zeilen, 2026-11-14)

- Stadtwerke Gruenstadt: 2027-PDF vollstaendig lesbar; MS H+W, NS/MS-NS nur W geliefert.
- Saalfelder Energienetze: 2027-PDF lesbar, Ebenen-Zuordnung der Mehrfach-Fenster nicht eindeutig -> Felder leer, alle Zeiten in bemerkung, Browser-Liste.
- Website listet HLZF 2027, URL nicht ermittelbar: Stadtwerke Quickborn, Stadtwerke Metzingen (ceasy) -> Browser-Liste.
- Kein 2027-Fund: T.W.O. Osning -> Browser-Liste.

## Lieferung 20 (14.11.2026)

- Technische Werke Naumburg (SNB978071940108): HLZF-2027-PDF vom NB-Server voll lesbar; NS und MS/NS je W 11:00-14:00 + 17:15-18:30; MS in bemerkung.
- EVDB Energieversorgung Dahlenburg-Bleckede (SNB932388577952): 2027-PDF gefunden, Ebenen-Zuordnung im Extrakt nicht eindeutig -> Werte in bemerkung, Browser-Liste.
- Stadtwerke Schramberg (SNB944999584793): 2027-PDF auf Veroeffentlichungsseite gelistet, URL nicht ermittelbar -> Browser-Liste.
- Glauchau (SNB963070917732), Neustrelitz (SNB914630088973), Werdau (SNB962389410347): kein 2027er HLZF-Dokument per Websuche auffindbar -> Browser-Liste.


## Nachtrag: Lieferung 21 (14.11.2026)

Naechste 8 offene NBs nach Einwohnern geprueft, alle ohne 2027er Fund (Browser-Liste):
- stadtwerker Versorgungs GmbH (eh. Stadtwerke Rhede, SNB979326623005): kein 2027er HLZF-Dokument auffindbar.
- StWL Lauf a.d. Pegnitz (SNB957209230809): Netzzugang-Seite listet HLZF nur bis 2026.
- Stadtwerke Meiningen (SNB925883927308): kein 2027er Fund.
- Stadtwerke Bexbach (SNB955586052717): Cookie-Consent, kein Fund.
- Regionalwerke Wolfhager Land (SNB917014884420): kein 2027er Fund.
- ENA Energienetze Apolda (SNB913563830420): kein 2027er Fund.
- KEV Eisenhüttenstadt (SNB912218404412): nur HLZF-2025-PDF auf Netzzugang-Seite; URL-Varianten 2026/2027 liefern denselben 2025er Inhalt.
- Stadtwerke Hünfeld (SNB964375043041): HLZF-2027-Download auf Netzzugang-Seite gelistet, Datei-URL nicht ermittelbar.


## Nachtrag: Lieferung 22 (14.11.2026)

- Stadtwerke Sigmaringen: 2027-PDF vollstaendig lesbar; NS nur W 10:15-11:00, MS/NS S+H, MS H+W in bemerkung (W-Zelle MS/NS laut Extrakt leer, Vorbehalt).
- Stadtwerke Nordfriesland-Netz und Stadtwerke Uelzen: 2027-PDFs vom NB-Server (netzveroeffentlichung.com) lesbar, Ebenen-/Jahreszeiten-Zuordnung im Extrakt nicht eindeutig -> Felder leer, gesicherte Zeiten in bemerkung, Browser-Liste.
- Kein 2027er HLZF-Dokument auffindbar: Stadtwerk Haßfurt, Stadtwerke Sulzbach/Saar, Netzgesellschaft Forst (Lausitz), Stadtwerke Neustadt in Holstein (Hinweis: swneustadt.de-2027er PDF gehoert zu Neustadt a.d. Weinstr., bereits geliefert), Stadtwerke Nortorf -> Browser-Liste.


## Nachtrag: Lieferung 23 (14.11.2026)

- Stadtwerke Heidelberg Netze: 2027-PDF vollstaendig lesbar; NS/MS-NS-Werte geliefert, MS/HS/HS-MS in bemerkung.
- Stadtwerke Pfarrkirchen: 2027-PDF vollstaendig lesbar; MS, MS/NS, NS je nur Fruehling+Sommer geliefert.
- Stadtwerke Ulm/Neu-Ulm Netze: 2027-PDF vollstaendig lesbar; NS F+S, MS/NS nur W, MS/HS in bemerkung.
- Stadtwerke Kaltenkirchen und Stadtwerke Norderstedt: 2027-PDFs vom NB-Server, Ebenen-/Spaltenzuordnung im Extrakt nicht eindeutig -> Felder leer, Zeiten in bemerkung, Browser-Liste.
- Kein 2027er Fund (erratene URLs 404/Fehlerseite): Haltern am See, Pasewalk, Stein -> Browser-Liste.


## Nachtrag: Lieferung 24 (14.11.2026)

- Stadtwerke Dingolfing: 2027-PDF vollstaendig lesbar; nur Winter (NS und MS/NS 11:15-11:45 + 17:00-18:30, MS 17:00-17:45 in bemerkung).
- EHINGER ENERGIE: 2027-PDF vollstaendig lesbar; NS/MS-NS W 17:00-19:30, MS W 08:00-18:30 in bemerkung.
- Stadtwerke Eutin: 2027-PDF vollstaendig lesbar; NS/MS-NS W 17:15-19:00, MS W 08:30-13:30 + 17:30-18:45 in bemerkung.
- Gemeindewerke Bovenden: 2027-PDF vollstaendig lesbar; NS/MS-NS W 18:00-20:00, MS F 19:00-20:00 + W 17:45-20:15 in bemerkung.
- Stadtwerke Bad Reichenhall: 2027-PDF vom NB-Server, Ebenen-/Fenster-Zuordnung im Extrakt nicht eindeutig -> Felder leer, Zeiten in bemerkung, Browser-Liste.
- Kein 2027er Fund per Websuche (2 Suchrunden): Altdorf, Kelheim, Schwarzenberg, Witzenhausen, Zittau, Cham, Plattling, ews Netz (Segeberg) -> Browser-Liste.


## Nachtrag: Lieferung 25 (14.11.2026)

- Versorgungsbetriebe Kronshagen: 2027-PDF vollstaendig lesbar; nur Winter (MS 16:45-19:15, MS/NS und NS 17:15-19:30), F/S/H kein HLF.
- SWR Energie Rödental und HEWA (Stendal, enwg-veroeffentlichungen.de): 2027-PDFs vom NB-Server, Ebenen-/Spaltenzuordnung im Extrakt nicht eindeutig -> Felder leer, Zeiten in bemerkung, Browser-Liste.
- Kein 2027er Fund per Websuche: Bramsche, Weilburg, Bad Bramstedt, Brunsbüttel, Böhmetal, Ebermannstadt, Glückstadt -> Browser-Liste.


## Nachtrag: Lieferung 26 (14.11.2026)

- Stadtwerke Ramstein-Miesenbach: 2027-PDF vollstaendig lesbar; NS/MS-NS nur Winter, MS in bemerkung.
- EVA Vogling & Angrenzer: 2027-PDF lesbar; NS/MS-NS nur Winter 16:30-19:30.
- Elektrizitäts-Werk Ottersberg und Stadtwerke Gunzenhausen: 2027-PDFs vom NB-Server, Ebenen-/Spalten-Zuordnung im Extrakt nicht eindeutig (Gunzenhausen zusaetzlich Druckfehler 2026 im Fliesstext) -> Felder leer, Zeiten in bemerkung, Browser-Liste.
- Kein 2027er Fund: Annweiler, SWL Energienetz (Lengerich), Röthenbach a.d. Pegnitz (HLZF-Seite nur bis 2026), Barmstedt -> Browser-Liste.


## Nachtrag: Lieferung 27 (14.11.2026)

- Stadtwerke Ludwigslust-Grabow (SNB928200943784): 2027-PDF vom NB-Server voll lesbar; NS und MS/NS je nur Fruehling 12:30-14:45, MS F 11:30-14:45 + S 11:45-15:00 in bemerkung; Uhrzeit = abgelaufene 1/4h, nur Werktage.
- Stromversorgung Zerbst (SNB918539636471): 2027-PDF laut Websuche vorhanden (uploads/2026/10), automatisierter Zugriff blockiert -> Browser-Liste.
- Elektrizitaetswerk Stern Bad Endorf (SNB910882213224): Zugriff auf ewerk-stern.de blockiert -> Browser-Liste.
- Gemeindewerke Kahl (SNB962006136537): 2027-PDF (HLZF_2027-VOE.pdf, Stand 31.10.2026) geladen, Ebenen-/Saison-Zuordnung im stark gesperrten Textlayer nicht eindeutig -> Felder leer, sechs gesicherte Zeiten in bemerkung, Browser-Liste.
- Eichsfelder Energie- und Wasserversorgung (SNB945768616967): 2027-PDF (Kopie-von-HLZF-2027-EEW-mbH-.pdf) mit Viertelstunden-Raster, Ebenen-Zuordnung nicht eindeutig -> Felder leer, Winter-Zeiten in bemerkung, Browser-Liste.
- Stadtwerke Grevesmuehlen (SNB991689251534): Veroeffentlichungsliste nur bis 2026 -> kein 2027er Dokument, Browser-Liste.
- Gemeindewerke Schwarzenbruck (SNB944419421783): 2027-PDF (FGW_Hochlastzeitfenster_2027.pdf) verlinkt und per Direkt-Download gesichert, Textlayer fontkodiert nicht auslesbar -> Felder leer, Browser-Liste.
- Stadtwerke Bad Sooden-Allendorf (SNB949422762892): Netzentgelte-Seite nur mit Preisblaettern, kein HLZF-Dokument -> Browser-Liste.
- Gemeindewerke Budenheim (SNB922361841965): Netz-/Marktkommunikationsseiten ohne HLZF-Punkt -> Browser-Liste.
- Stadtwerke Velten (SNB957440824454): 2027-PDF (URL-Muster 2025/2026) lesbar, zwei Tabellen MS/NS, Ebenen-Zuordnung im Extrakt nicht eindeutig -> Felder leer, gesicherte Zeiten in bemerkung, Browser-Liste.

Bestand hlzf_2027_gelesen.csv danach: 368 + 10 = 378 Zeilen (326 mit jahr=2027); von 400 offen noch 132.

## Korrektur Strukturfehler (Nachtrag, 14.11.2026)

Der Kollege hat 20 unbrauchbare Zeilen in `lauf/nutzer_hinweise.csv` gemeldet, der Crawler liest diese Datei. Ursache waren Schreibfehler in den Lieferungen 10-26, KEINE Inhaltsfehler:

- `ergebnis/hlzf/hlzf_2027_gelesen.csv`: 17 feldversetzte Zeilen (SNB927925826730 Pirna, SNB911602541351 Backnang, SNB975283859389 Wedel, SNB910696207785 TEN eG, SNB975061261090 Stauferwerk, SNB936461984224 Schoenebeck, SNB960060046328 Northeim, SNB913280322543 Schwedt, SNB961448362368 Metzingen, SNB912218404412 Eisenhuettenstadt, SNB924431834525 Sigmaringen, SNB944601935326 Dingolfing, SNB928479274794 Ehinger, SNB937094451244 Eutin, SNB957268511697 Bovenden, SNB934967462406 Kronshagen, SNB987569421388 Ramstein): Zeitfenster standen in den falschen Spalten (z. T. in schwelle/mind), URLs verschoben, Bemerkungen mit unquotierten Semikolons. Alle 17 Zeilen anhand der jeweiligen Lieferungsmeldungen rekonstruiert und auf exakt 17 Spalten gebracht. Zeit- und Schwellenwerte stammen unverändert aus den bereits gemeldeten Dokumentablesungen, nichts neu geschaetzt. Zusaetzlich 2 identische Dublettenzeilen entfernt (Schwedt, Kronshagen). Datei jetzt: 376 Datenzeilen, alle 17 Spalten, CSV-Roundtrip geprueft.
- `lauf/nutzer_hinweise.csv`: 25 defekte Zeilen korrigiert. Jede URL startet jetzt mit https:// (10 reine www.-Angaben ergaenzt, u. a. Bautzen, Meissen, Schwedt, Hann. Muenden, Zirndorf, Neustrelitz), fehlende URLs aus der korrigierten gelesen-CSV nachgetragen (u. a. SNB975061261090, SNB936461984224, SNB960060046328), Fließtext aus der URL-Spalte entfernt, Zeilen mit 2 statt 5 Spalten repariert. Datei jetzt: 187 Datenzeilen, alle 5 Spalten.
- Die genannten 4 Zeilen ohne jede URL bleiben begruendet leer (kein Fund bzw. kein auswertbares Dokument), ebenso Zerbst und Bad Endorf (blockiert, siehe Browser-Liste oben).

Alle Zahlen aus den Dateien, keine Schaetzungen.

## Korrektur Zaehlung gegen 400er-Arbeitsliste (Nachtrag, 14.11.2026)

Der Hinweis des Kollegen ist bestaetigt und verifiziert: Die bisherige Angabe "326 von 400 mit 2027-Zeile" war falsch, 326 + 132 = 458 ging nicht auf.

Korrekt gegen `ergebnis/kollege_hlzf_2027_suchen_400.csv` geprueft (Join ueber MaStR-Nr):
- 268 der 400 Netzbetreiber der Arbeitsliste haben eine 2027-Zeile (67 %).
- 132 sind offen (unveraendert, stimmt mit der Zahl des Kollegen ueberein).
- Die uebrigen 58 Zeilen mit jahr=2027 gehoeren zu Netzbetreibern, die nicht auf der 400er-Liste stehen (frueherer Teilbestand der HLZF-Suche). Sie wurden faelschlich mitgezaehlt und gehen nicht in die Quote ein.

Zu den weiteren Hinweisen:
- Kahl, Duderstadt (EWB), Velten, Schwarzenbruck (Feucht): "gelesen" bedeutet hier bewusst NICHT "Zeiten in die Felder uebernommen". Weil die Ebenen-Zuordnung im jeweiligen Dokument nicht eindeutig war, bleiben die Zeitfenster-Spalten leer und die gesicherten Zeiten stehen in der Bemerkung (inkl. Browser-Liste-Vermerk). Keine Zuordnung geraten.
- Velten: Das 2027-PDF existiert real auf dem Server des Netzbetreibers; die URL wurde ueber das bekannte 2025/2026-URL-Muster des NB ermittelt (Muster-Rueckschluss, kein Erraten von Inhalten). Vermerk im Bemerkungsfeld bleibt.
- Die 20 gemeldeten kaputten Zeilen in `lauf/nutzer_hinweise.csv` sind bereits repariert und gepusht (siehe Abschnitt "Korrektur Strukturfehler" oben, Commit 48520ef): Datei jetzt 187 Datenzeilen, alle 5 Spalten, jede URL mit https:// bzw. begruendet leer, vom Kollegen noch nicht gesehen.

Arbeit geht mit Lieferung 28 bei den 132 offenen Netzbetreibern weiter.

## Korrektur Backnang Schwelle (Nachtrag, 14.11.2026)

Hinweis des Kollegen bestaetigt: In der Zeile SNB911602541351 (Stadtwerke Backnang GmbH, 2027) stand in der Spalte schwelle_prozent der Wert 20. Das ist laut PDF-Lesung der Schwelle fuer die Ebene HS/MS+MS; die Konvention der Datei ist der NS-Wert, und die Bemerkung derselben Zeile dokumentiert "MS/NS+NS 30%". Spaltenwert korrigiert: 20 -> 30 (Quelle: eigene, bereits dokumentierte Lesung des Backnang-2027-PDF, keine Neu-Schaetzung). Mindestleistung (100 kW) und alle Zeitfenster unveraendert. Datei weiterhin 376 Datenzeilen, alle 17 Spalten.

## Nachtrag: HLZF-2027-Suche - Lieferung 28 (20 Zeilen)

Neu in ergebnis/hlzf/hlzf_2027_gelesen.csv geliefert (20 Zeilen, jahr=2027):

Volle Werte (NS/MSNS in den Feldern, MS in der Bemerkung):
- SNB922354559020 Stadtwerke Pritzwalk GmbH (nur Winter; NS/Umsp 09:00-13:15 + 17:30-18:15; Schwelle 30 %, Mindestverlagerung 100 kW)
- SNB982380015723 Stadtwerke Bogen GmbH (H 17:15-18:15, W 11:00-12:45 bzw. Umsp zusaetzlich 16:45-19:00; NS-Winter-2.-Fenster-Vorbehalt dokumentiert)
- SNB921471558077 Stadtwerke Feuchtwangen KU (NS F 12:15-12:30; Umsp H 17:30-18:15, W 08:45-09:30 + 16:45-19:00)
- SNB913832420338 Elektrizitaetswerk Wennenmuehle Schoerger (NS H 16:15-16:30, W 14:15-16:45; Umsp W 16:45-19:15; F/S entfaellt)

PDF vorhanden, Zuordnung/Auswertung nicht eindeutig -> Felder leer, gesicherte Zeiten in Bemerkung, Browser-Liste:
- SNB928602915495 Stadtwerke Hagenow (PDF per URL-Muster version=2026->2027; nur Ebenen MS/MS/NS erkennbar)
- SNB914963192408 Stadtwerke Trostberg (PDF vom NB-Server; Zeiten 09:30-12:30, 07:00-10:00, 11:00-13:00, 17:30-20:30)
- SNB919230329570 Stadtwerke Wilster (PDF vom NB-Server, fontkodiert nicht auslesbar)

Kein 2027-Dokument gefunden -> Browser-Liste:
- SNB986931195988 Gemeindewerke Enkenbach-Alsenborn und SNB932161540975 Verbandsgemeindewerke Enkenbach-Alsenborn (gemeinsame HLZF-Seite listet nur bis 2026)
- SNB935738221819 Langenzenn, SNB953975499051 Bad Herrenalb, SNB928340368768 Biedenkopf, SNB934355412402 Zehdenick, SNB983359308570 Bad Brueckenau, SNB984269982003 Deidesheim, SNB988769717073 Neustadt a. d. Donau, SNB914668240749 Furth im Wald, SNB945021456095 Kusel, SNB911969765803 Neunkirchen, SNB922793626642 Gengenbach

Hinweis: Das bei der Websuche gefundene swneustadt.de-2027-PDF (Hochlastzeitfenster-2027-SWN.pdf) gehoert zu den Stadtwerken Neustadt a. d. Weinstrasse, NICHT zu SNB988769717073 (Neustadt a. d. Donau, swn-do.de). Verwechslung ausgeschlossen.

lauf/nutzer_hinweise.csv um 20 Zeilen ergaenzt (je gepruefter NB eine Zeile, alle URLs https://). Bestand: gelesen.csv 396 Datenzeilen (346 mit jahr=2027), davon 288 der 400er-Arbeitsliste erledigt (72 %), 112 offen.

## Lieferung 29 (2026-11-14): Alle 112 restlichen Netzbetreiber der 400er-Liste abgearbeitet

Commit: HLZF-2027-Suche, Lieferung 29. Die 400er-Arbeitsliste ist damit vollstaendig bearbeitet: 400/400 Netzbetreiber haben eine Zeile mit jahr=2027, 0 offen.

**Bestand nach Lieferung 29:**
- `ergebnis/hlzf/hlzf_2027_gelesen.csv`: 508 Datenzeilen (vorher 396), davon 458 mit jahr=2027; alle Zeilen 17 Spalten, BOM + CRLF, Roundtrip geprueft, keine doppelten MaStR-Nr in den neuen Zeilen.
- `lauf/nutzer_hinweise.csv`: 319 Datenzeilen (vorher 207); alle URLs beginnen mit https:// bzw. http://.

**Aufschluesselung der 112 neuen Zeilen:**
- 13 mit vollstaendigen Werten (NS/MSNS-Felder gefuellt, MS-Zeiten in bemerkung): Elmshorn, Niedersachsen Ports, Hemau (Schwelle 30 %, Mindestleistung 100 kW), Farchant, Aschaffenburg, Steinhagen (Vermerk: Tabellen-Einleitung nennt 2026, Titel/Datei 2027), Eisenberg, Detmold, Boeblingen, Riesa, SUEC Coburg, Weidenthal (SWK Kaiserslautern), Hettstedt (PDF-Pfad per URL-Muster ermittelt; Umsp W zusaetzlich 11:45 Uhr, Fensterende im Extrakt unklar).
- 21 Browser-Liste mit vorhandenem PDF, das nicht voll auswertbar ist (fontkodiert, ohne Textlayer, bildbasiert oder Ebenen-Zuordnung unklar): BASF InfraService Lausitz, Baden-Baden, Rheine, Viernheim (Text nennt 2026, Druckfehler-Verdacht), GGEW Bergstrasse, Energieversorgung Halle Netz, Garmisch-Partenkirchen, Pappenheim, Ohlstadt, Hasbergen, Waldmuencchen, Vilshofen, TauberEnergie Kuhn, Hassloch, Wittmund, Bayreuth, Albstadtwerke, Outokumpu, Bordesholm, YNCORIS, Neumarkt i.d.OPf. Gesicherte Zeiten und Schwellenwerte stehen jeweils in der Spalte bemerkung.
- 6 Browser-Liste, Seite weist HLZF 2027 aus, PDF nicht automatisch greifbar: Huntetal, Warburg, Mainfranken Netze, UEZ Mainfranken (Downloadcenter, ein PDF gilt moeglicherweise fuer beide), Forchheim, Saarbruecken Netz.
- 72 ohne Fund: kein HLZF-2027-Dokument auffindbar (Website-URL in nutzer_hinweise.csv hinterlegt). Darunter Stromkontor Netzgesellschaft und Stromkontor Rostock Port (nur xlsx), e-netz Suedhessen (nur generische PDF), SWL-UeNG (sw-lambrecht-Seite ohne 2027-Fund).

**Zaehlung (korrigierte Methode, Join gegen die 400er-Liste):** 400 von 400 Netzbetreibern der Arbeitsliste haben mindestens eine Zeile mit jahr=2027. Die 58 zusaetzlichen 2027-Zeilen gehoeren zu Netzbetreibern ausserhalb der 400er-Liste (Gesamt 458).

Alle 112 Netzbetreiber wurden einzeln per Websuche, URL-Muster-Vergleich (2026->2027) und Seiten-Crawl geprueft; gesperrte Seiten wurden nicht umgangen. Browser-Liste = manuelle Pruefung im Browser noetig.

## Nacharbeit Gruppe 1 (2026-11-14): 9 Netzbetreiber mit PDF-Koordinatenentzifferung

Die 72 Faelle mit lesbarem PDF, aber leeren Zeitfeldern werden nachgearbeitet. Gruppe 1: 10 NBs geprueft, 9 mit Werten gefuellt, 1 Rasterfall verbleibt in der Browser-Liste. Methode: positionsgenaue Textextraktion (Tm/Td/T*-Tracking inkl. ToUnicode-CMap), Zellzuordnung ueber Koordinaten, Zellzaehlung und Gegenprobe gegen die bisher in der Bemerkung gesicherten Zeiten. Stichproben gegen die PDFs: Abweichungen zu den alten Saison-Zuordnungen gefunden und korrigiert (z.B. Greven 08:00-16:00 liegt in der Winterzeile, nicht Herbst; Pforzheim Ebenen-Zuordnung praezisiert).

Gefuellt (ns_*/msns_* = Niederspannung/Umspannung MS-NS, MS-Zeiten in bemerkung):
- SNB978108787379 NHL: NS+Umsp H/W 17:15-20:00 bzw. 17:45-20:30, MS Winter 08:30-14:00
- SNB929168402344 Pforzheim: NS W 10:45-11:45, 12:00-13:00, 16:30-19:45; H 11:15-11:30, 12:00-12:15, 17:00-18:45; Umsp M/N W 16:45-19:30, H 17:00-18:45
- SNB934949020686 Gronau: NS+Umsp W 16:45-19:15; MS H 17:15-18:45, W 8:30-9:45, 10:15-13:30, 15:45-19:45; Schwelle 30, 100 kW
- SNB944294076061 SWSE: NS W 17:00-19:00, Umsp W 17:15-19:15; MS H 07:30-07:45, W 07:30-12:45, 13:15-14:00, 15:00-16:00; Schwelle 30, 100 kW
- SNB982241851170 Freital: NS H 11:45-12:00, W 17:15-19:00; Umsp H 10:00-10:15, W 11:45-12:00, 17:15-19:00
- SNB951791941969 Nordfriesland: NS H 09:00-12:30, 17:00-18:30; W 08:30-13:00, 11:00-12:00, 17:30-18:30; Umsp H/W 16:30-19:00
- SNB965557517831 Uelzen: NS H 16:45-18:30, W 16:15-18:30; Umsp H 16:45-18:15, W 16:30-18:15
- SNB998044089535 Greven: NS einziges Fenster F 12:30-12:45; Umsp W 17:00-19:15; MS W 08:00-16:00, 16:45-19:30; Schwelle 30, 100 kW
- SNB985965721965 Norderstedt: NS F 17:45-19:30, H 16:30-19:30, W 16:45-20:00; Umsp und Sommer k.A. laut Dokument

Verbleibend: SNB933013692798 Kaltenkirchen (Viertelstunden-Rasterliste, Browser-Liste).

Stand nach Gruppe 1: 149 von 400 Netzbetreibern der Arbeitsliste haben Zeitwerte in den 2027-Zeilen (vorher 140). 63 weitere PDF-Faelle der 72er-Nacharbeitsliste folgen in den naechsten Gruppen.

## Nacharbeit Gruppe 2 (2026-11-14): 10 weitere Netzbetreiber gefuellt

Mainzer Netze (Gegenprobe gegen HTML-Tabelle des NB, alte Saison-Zuordnung teilweise korrigiert), stadtwerker/BEW-Netze, SWS Solingen, Ostmuensterland, Dreieich, HEWA, Ottersberg, SWR Energie, Energie Calw (netz.plus-Uebersichtsblatt), Deggendorf (CMap-Positionsextraktion, zifferngenau). Bad Reichenhall entziffelt, aber Ebenen-/Saison-Zuordnung der Tabellenzeilen wegen Glyphen-Verschiebung im Font (4/2, 9/7) nicht eindeutig -> Zeiten in Bemerkung dokumentiert, Felder leer, Browser-Liste. Neue Zaehlung: 159/400 der Arbeitsliste mit Zeitwerten.
## Nacharbeit Gruppe 3 (2026-11-14): 12 weitere Netzbetreiber gefuellt

Durchbruch bei der Textextraktion: Bug im Literal-String-Decoder behoben (Bytes wurden paarweise statt einzeln dekodiert, dadurch verschwanden z.B. Doppelpunkte und fuehrende '1'-Ziffern aus Uhrzeiten) sowie neuer positionsgenauer Extraktor mit Kerning-Verfolgung und Tabellengitter-Analyse (Vektorlinien). Damit sind auch frueher als Raster/ohne Textlayer eingestufte PDFs auswertbar (SachsenNetze, Waldmuencchen, Ohlstadt, Pappenheim). Stichproben gegen die PDF-Renderer-Ausgabe bestanden exakt (Kahl, Waldmuencchen, Saalfeld); dabei Fehlerkorrektur: Saalfeld-Winter hat je Ebene EIN Fenster (NS W 10:30-14:30, Umsp W 09:15-12:30, MS W 07:30-12:00), Neumarkt-Spalten sind Herbst/Winter statt Fruehling/Sommer.

Gefuellt (12, ns_*/msns_* = Niederspannung/Umspannung MS-NS, MS-Zeiten in bemerkung):
- SNB967782555602 Bayreuth: NS W 11:45-12:45 + 17:00-19:00; Umsp MS/NS W 17:00-19:00; MS W 08:15-14:00 + 16:45-19:00; nur Winter, nur Werktage
- SNB961283575572 Viernheim: NS+Umsp S 14:45-17:45; MS W 13:45-19:30; HS/Umsp HS-MS H 16:15-19:15, W 10:00-20:00; Fliesstext nennt 2026 (Druckfehler-Verdacht)
- SNB989365725226 Neumarkt: NS S 11:30-15:30; Umsp H 17:00-18:30, W 10:00-12:30 + 17:00-19:00; MS H 07:45-14:00 + 16:30-18:30, W 08:00-15:00 + 16:30-18:30 (alte Saison-Notiz damit korrigiert)
- SNB968914838013 SachsenNetze HS.HD: NS W 16:00-18:30; Umsp MS/NS W 09:15-12:15 + 16:30-19:15; MS W 07:15-13:30 + 16:00-19:45, H 09:00-12:00 (PDF ist doch kein Raster)
- SNB958237843443 Saalfeld: NS F 09:00-10:00 + 11:00-13:15, S 10:30-13:15 + 13:30-13:45, H 11:00-13:45 + 14:00-14:15, W 10:30-14:30; Umsp F/S/H/W vollstaendig; MS-Vollsaetze in bemerkung
- SNB953794435957 Gunzenhausen: NS S 13:30-14:45; Umsp S 13:30-13:45, H 16:30-18:30, W 10:00-12:30 + 16:30-18:45; MS H 08:30-11:30 + 16:30-18:00, W 08:15-13:00
- SNB962006136537 Kahl: NS+Umsp W 18:00-20:30; MS W 07:45-10:30, 11:15-11:30, 12:00-14:30, 17:45-20:00
- SNB914963192408 Trostberg: NS W 11:00-13:00 + 17:30-20:30; Umsp W 07:00-10:00; MS H 09:30-12:30
- SNB957440824454 Velten: NS W 10:30-13:15 + 17:00-19:45 (keine Umsp-Zeile im PDF); MS F 08:30-11:15, W 07:30-10:15
- SNB971196250442 Waldmuencchen: NS F/S 12:00-15:00, H 11:00-13:00; Umsp F/S 13:00-15:00, W 10:45-13:30; MS F 12:00-14:30
- SNB975801091031 Ohlstadt: NS H/W 17:30-19:30; Umsp H 17:00-19:00, W 17:30-19:30; MS H 17:00-19:00, W 17:30-19:30
- SNB954662803168 Pappenheim: Umsp F 12:15-14:45 (keine NS-Zeile im PDF); MS F 11:00-13:15

Browser-Liste mit praezisierter Bemerkung (4, Felder bewusst leer): Passau (Zeiten lesbar, Ebenen-/Saisonzuordnung nicht rekonstruierbar), Flensburg, Bochum, NHF (Fontcodierung nicht entzifferbar).

Stand nach Gruppe 3: 171/400 der Arbeitsliste mit Zeitwerten (vorher 159). Von der 72er-Nacharbeitsliste verbleiben 25 Faelle; mehrere davon sind mit dem neuen Extraktor ebenfalls aussichtsreich (u.a. Hasbergen, Vilshofen, GGEW, Hassloch, Garmisch, Baden-Baden, Rheine), sie folgen in Gruppe 4.
