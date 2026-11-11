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
