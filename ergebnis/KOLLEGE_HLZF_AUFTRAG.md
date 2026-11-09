# Auftrag Hochlastzeitfenster 2026 (Stand 09.11.2026)

Liste: `hlzf_auftrag_kollege.csv` (MaStR-Nummer in der ersten Spalte, kein Wert von uns, du liest blind).

## Was zu liefern ist
Je Netzbetreiber die **Hochlastzeitfenster 2026** nach § 19 Abs. 2 Satz 1 StromNEV: Ebene (NS, MS/NS, ggf. MS, HS/MS), Jahreszeit (Frühling, Sommer, Herbst, Winter), Uhrzeit von/bis. Steht für eine Jahreszeit kein Fenster im Dokument, schreib „keins". Steht im Dokument „keine Hochlastzeitfenster", schreib das in `bemerkung`.

## Spalten der Lieferung
`mastr_nr; nr; netzbetreiber; jahr; ebene; jahreszeit; uhrzeit_von; uhrzeit_bis; quelle (Adresse des Originals); fundstelle (Seite und Zeile); dokument_datei; bemerkung`. Eine Zeile je Zeitfenster.

## Regeln (aus den Fehlern der letzten Lieferungen)
1. **Nur 2026.** Andere Jahre interessieren uns nicht. Gibt es kein 2026-Dokument, schreib „kein 2026-Dokument gefunden" in `bemerkung` und liefere nichts anderes.
2. **Original des Netzbetreibers.** Die Adresse muss auf der Website **dieses** Netzbetreibers liegen. In der Liste stehen Adressen anderer Betreiber (zum Beispiel Elbtal, Herborn, Lingen, Neustadt a.d. Aisch). Die ignorieren und neu suchen. Netzbetreibername im Dokument oder eigene Website.
3. **Spalten am Layout lesen,** nicht raten. Bei Tabellen mit Spalten Frühling bis Winter die Position prüfen. Wenn die Zuordnung unklar ist (zum Beispiel nur eine Zelle je Ebene), leer lassen und in `bemerkung` begründen.
4. **Uhrzeiten, nicht Preise.** Bei 237 standen Preiszahlen als Uhrzeiten. Jedes Fenster muss im Dokument stehen.
5. **Datei ablegen** als `<mastr_nr>_hlzf_<Originalname>.pdf` und mitliefern (ZIP).
6. **Regeln fürs Beschaffen:** höchstens 1 Anfrage pro Sekunde je Domain, robots.txt beachten, ehrlicher Kennzeichner, Zertifikatsprüfung an, keine Umgehung von Cloudflare oder anderen Sperren (dann „gesperrt" eintragen). Keine nicht dokumentierten Schnittstellen Dritter.
7. **Nichts schätzen.** Unsicher heißt leer lassen.
