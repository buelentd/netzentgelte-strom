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
