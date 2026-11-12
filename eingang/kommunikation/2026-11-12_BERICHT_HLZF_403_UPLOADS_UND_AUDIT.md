# Bericht: 403-Uploads gelesen + Fehler-Audit (12.11.2026, abends)

Branch `vibe/hlzf-etappen-1-2-705031`, Commits `530d9e1` (Audit/2026-vorang), `3be4525` (+59 Uploads).

## 1. Neue Uploads (403/gesperrte Seiten) gelesen: +59 Zeilen in `ergebnis/hlzf/hlzf_2027_gelesen.csv` (jetzt 164 Zeilen)

Regel angewendet: **2026-Dokument hat Vorrang, 2027 nur wenn kein 2026 existiert** (jahr = Dokumentjahr; 2025 und aelter unbrauchbar). Wo Dateiname und Inhalt auseinanderfallen, zaehlt der Inhalt (z. B. Schwedt, Neustrelitz, Steinhagen, Kronshagen, Balingen, Eilenburg tragen 2027 im Namen, Inhalt 2026 -> jahr=2026; Ensinger-Datei traegt 2026-10-30, Inhalt 2027 -> jahr=2027).

Jede Zeile mit Seiten-/Zellen-Beleg in `bemerkung`; MS/HS-Werte nur in `bemerkung`, nie unter msns; Zeiten ausserhalb 05:00-23:59 (Leinetal NS W 00:00-00:30, BASF MS/NS H 03:00-07:30) stehen nur in `bemerkung`, Feld leer (Pruefskript).

Beispiele (alle in der CSV): Leinetal, LEW, KBG Homberg, Schwedt, EMB Miltenberg, BASF (Werksnetz), Neustrelitz, Steinhagen, Energienetze Berlin, ASCANETZ, Elbtal, ENGIE Radeberg, Loebau, Wasserburg, Greiz, Alliander Heinsberg, Cottbus, Ruesselsheim, Duesseldorf, Kronshagen, Netz+Service, UWR Rhoen, Abita Otterberg, Creos, EZV Untermain, Emden, Haiger, Weilerbach, Jena (Raster dekodiert), Frammersbach, Netze BW (S.8), Leipzig, Burgdorf, Keep Eisenberg, Schleswig, Ensinger, Osterholz, Lambrecht, Pfalzwerke, Balingen, Wendelstein, Kirchzarten, Greding, Glattbach, BHAG, Inselsberg, Eilenburg, Plauen, EW Geiger, Stromnetz Berlin, SachsenNetze, Ahrtal-Werke, Bad Pyrmont, Mosbach, MVV, Fuerstenfeldbruck (bild-only, am Bild gelesen), Rosenheim, Freiberg, Lohr-Karlstadt.

## 2. Fehler-Audit danach: alle behoben

- Pruefskript `daten/hlzf_lieferung_pruefen.py`: **hlzf_2027_gelesen.csv 164 Zeilen, 0 Fehler; hlzf_auftrag7_gelesen.csv 105 Zeilen, 0 Fehler**.
- Format: beide Dateien UTF-8-sig mit einfachem BOM, alle Zeilen 17 Felder (werkkraft 18->17 und Halberstadtwerke 16->17 gefixt).
- Jede Zeile hat Beleg in `bemerkung`; `jahr` nur 2026/2027.
- Regel 2026-vorangig: frueher 61 Zeilen von 2027 auf 2026 umgestellt. Verbleibende jahr=2027 trotz 2026-Datei sind inhaltlich begruendet und in `bemerkung` vermerkt: Bielefelder Netz (2026-Dateiname enthaelt 2027-Raster), Hauenstein (2027-Zeile = Preisblatt, HLZF 2026 in auftrag7-Datei), Ensinger (2026-Dateiname enthaelt 2027-Inhalt).

## 3. Offen fuer dich

- 132 "suchen"-Faelle aus Auftrag 7 (Browser/Web).
- Noch nicht zugeordnete Uploads in `dl_up/sonst/` (u. a. EZV/Hochlastzeitfenster 2027, Hochlastzeitfenster 2027 (2), Langenpreising, Gas-Preisblatt) - bitte MaStR-Nr. zuordnen.
- Auftrag 8 (Preisblaetter 2027 fuer 571 ohne Blatt) bleibt Browser-Arbeit.
