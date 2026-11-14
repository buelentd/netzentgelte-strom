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
