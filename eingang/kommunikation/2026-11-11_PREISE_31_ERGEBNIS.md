# Preise: die 31 mit Werten aus der Liste vom 04.11.2026 (Claude, 11.11.2026)

Liste mit MaStR-Nr. zuerst: `2026-11-11_PREISE_31_PRUEFUNG.csv`. Nichts ist in Tabelle oder Overlay eingetragen, kein Status geändert.

**Am Preisblatt bestätigt (Werte der Liste = Dokument, keine Abweichung):** SachsenNetze 39 (NS), Netze Magdeburg 40 (NS, MS/NS, SLP), Alzchem 57 (MS/NS, SLP), enercity GridPartner 138 (NS, MS), EWA Altenburg 144 (NS, MS/NS, MS), InfraServ Wiesbaden 281 (MS/NS, MS), Deidesheim 445 (NS, MS/NS, MS), SWL 776 (MS), Veolia 803 (NS, MS/NS), VersorgungsBetriebe Elbe 809 (NS, MS).

**Im Dokument gefunden, vom Leser nicht gelesen (SLP):**
- SNB809 VersorgungsBetriebe Elbe (SNB971770548286): Haushalts- und Gewerbekunden Grundpreis 66,00 €/a, Arbeitspreis 7,50 ct/kWh.
- SNB445 Stadtwerke Deidesheim (SNB984269982003): Arbeitspreis Niederspannung 8,71 ct/kWh; Grundpreis im Dokument nicht ausgewiesen.
- SNB803 Veolia Industriepark (SNB933760214908): SLP-Zeile „Kleinkunden (NSP)“ mit „---“, also nicht ausgewiesen (Industriepark).
- SNB40 Netze Magdeburg: Dokument nennt Mittelspannung 14-mal, der Leser meldet keine Mittelspannung: Leser-Lücke prüfen.
- Kein SLP im geladenen Dokument (separates Blatt nötig oder keins): enercity GridPartner, EWA Altenburg, InfraServ Wiesbaden, SWL.

**Preisblatt nicht gefunden (16):** Die Websites dieser Netzbetreiber liefern dem Crawler keine Netzentgelt-Preisblätter (JavaScript, nur Startseite oder andere Dokumente): BASF, CPM, EW Kanton, Haßloch, Niefern-Öschelbronn, GSW Kamen, InfraLeuna, InfraServ Gendorf, Outokumpu, Baden-Baden, Goch, Wunsiedel, thyssenkrupp, Westenthanner, Zwickau (nur „fiktive Netzentgelte“), Covestro (HTTP 503). Browser nötig (Arbeitsliste Kollege).

## Nachtrag: Energienetze Mittelrhein (SNB980055629275, nr 26) fertig (Claude, 11.11.2026)
Preisblatt 3 (Stand 17.12.2025, eigene Website): SLP Grundpreis 80,30 €/Jahr, Arbeitspreis 6,39 ct/kWh netto, eingetragen (`daten/preise_entscheidungen.py`). Preisblatt 1 bestätigt die vier RLM-Ebenen (HS/MS, MS, MS/NS, NS) zeilenweise, Belege in `lauf/beleg_manuell.csv`. Status jetzt ok (773). Preisblatt 4 (individuelle Entgelte nach § 19 Abs. 5) enthält nur Marktlokationen mit Anzeigen, keine Preise, nicht abgelegt. Vorläufige 2027er Blätter (PB 1, PB 3, Hochlastzeitfenster) in `eingang/2027_vorlaeufig/`.
**Abweichung Hochlastzeitfenster 2026:** Das Dokument (Winter, Frühling/Sommer/Herbst „keine“) nennt NS und MS/NS jeweils `17:00-19:30`, MS `07:45-13:00, 17:30-19:15`, HS/MS `07:45-09:45`. Die Tabelle (gelesen_nutzer) hat NS `16:45-19:45` und MS/NS `17:00-19:45`. Nicht geändert, Entscheidung beim Nutzer.
