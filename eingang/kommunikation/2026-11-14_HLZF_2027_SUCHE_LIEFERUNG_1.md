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
