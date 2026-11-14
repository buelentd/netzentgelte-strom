# Etappe 9: Grosse Netzbetreiber (2026-11-14)

Rangfolge nach Netzgroesse/Einwohnern (Sammelauftrag-Regel), Start der 146 offen_websuche-Faelle.

## Geliefert

1. **Netze BW GmbH (SNB948311994307, Nr. 3), 2026**: HLZF-Tabelle steht in den "Regelungen fuer die Nutzung des Stromverteilnetzes 2026" (Version 1.1, Stand 12.12.2025, Kap. 4.1.2, Seite 9/19). Content-Stream-Analyse des Original-Downloads: NS und MS/NS nur Winter 17:00-20:45; MS nur Winter 07:00-14:00 und 16:45-19:45; HS Winter 07:15-13:15 und 15:15-19:15, Herbst 07:30-17:30; HS/MS Winter 07:00-13:30 und 15:00-18:30, Herbst 15:30-17:30. Fruehling/Sommer in allen Ebenen explizit "entfaellt" (R8-Beleg). 10 Zeilen gemergt, Status verifiziert.
2. **badenovaNETZE GmbH (SNB965774651691, Nr. 62), 2026**: Original-PDF (STAND 07.04.2026, Storyblok-CDN der badenova-Website) per Content-Stream-Analyse zellgenau dekodiert (5 Seiten je Netzebene; Spaltenzuordnung per Tm/Td-Positionen). NS nur Winter 13:00-13:45 und 17:30-19:30; MS/NS nur Winter 17:30-19:30; MS Herbst 10:45-13:30, Winter 07:45-13:45 und 17:15-19:15; HS und HS/MS in Bemerkung. 18 Zeilen gemergt, Status verifiziert_mit_vorbehalt.
   - **Pruefpunkt**: HS Winter ist im Dokument inkonsistent gedruckt: "von 10:30 bis 10:15" und "von 11:00 bis 10:45" (bis < von; Spalten Von/Bis zellgenau verifiziert, Fonts WinAnsi literal). Werte wie gedruckt uebernommen, zur Klaerung ggfs. beim NB anfragen. Zudem ist das dritte HS/MS-Winter-Fenster erneut als "HLZF 2" statt "HLZF 3" bezeichnet (Dokument-Typo).

## Blockiert / Browser-Liste

- **Westnetz GmbH (SNB921897286493, Nr. 29)**: HLZF-URL bekannt (zeitfenster-fuer-atypische-netznutzung-2026.pdf), aber Cloudflare managed challenge auf robots.txt und PDF -> Sperre wird nicht umgangen. Bitte im Browser laden und unter eingang/ ablegen.
- **SWKiel Netz GmbH (SNB973742186519, Nr. 42)**: HLZF-PDFs vorhanden auf swkiel-netz.de, liegen aber unter /fileadmin/user_upload_swk_netz/... - robots.txt erlaubt /fileadmin/user_upload/ nicht aber user_upload_swk_netz (Disallow /fileadmin/ greift) -> nicht geladen. URLs: /fileadmin/user_upload_swk_netz/dokumente/strom/marktpartner/individuelle_netzentgelte_strom/_Hochlastzeitfenster2026_fertig.pdf und Hochlastzeitfenster2027.pdf. Bitte im Browser laden und unter eingang/ ablegen.

## Nebenbefund

- Auf cdn.swk.de liegt das HLZF-2026-PDF der NGN Netzgesellschaft Niederrhein (nicht SWKiel). NGN ist im Netzentgelt-2027-Strang relevant, dort dokumentiert: HS Fruehling 10:15?-10:30... (nur grob gesichtet, nicht uebernommen).

Pipeline: werte_verifiziert.json 96 Eintraege, regeln.py OK, Arbeitsstand 1811 Zeilen, hlzf_lieferung_2026-11-14.csv um 2 Zeilen erweitert.
