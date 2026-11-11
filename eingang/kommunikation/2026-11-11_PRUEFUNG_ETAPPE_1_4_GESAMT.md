# Gesamtprüfung Etappe 1–4 (11.11.2026): Fehlerliste und Lehre

Stand geprüft: Branch `vibe/hlzf-etappen-1-2-705031`, Commit 08f9251. Alle Zeilen mit 2026-Werten, die ich am Dokument prüfen konnte (48 von 53), am Bild bzw. Text gegen das Original. Nicht geprüft: 2027-Zeilen, die 5 Zeilen ohne passendes PDF (Nüdlingen, Werraenergie, enercity Netz, enercity GridPartner, VersorgungsBetriebe Elbe).

Ergebnis: 31 richtig, 12 falsch oder unvollständig, 5 mit Bemerkungsmangel. Das ist zu viel für eine Übernahme. Nichts davon geht in die Tabelle, bevor die Fehler unten korrigiert und von uns erneut geprüft sind.

## A. Falsch (Wert muss geändert werden). MaStR-Nr. zuerst

| MaStR-Nr. | Netzbetreiber | Fehler | Richtig laut Dokument |
|---|---|---|---|
| SNB975659838086 | Stade | 16:00-19:00 steht im Bild in Spalte **Herbst**, du hast Sommer | NS und MS/NS: Sommer `keins`, Herbst `16:00-19:00` |
| SNB999405828558 | ENRO Ludwigsfelde | Eine Zelle mit drei Zeilen auf zwei Jahreszeiten verteilt | MS/NS Frühling `keins`; Sommer `08:15-08:30, 09:00-10:00, 13:45-14:00` |
| SNB946612539746 | Hoyerswerda | Zellen mit zwei Zeilen auf zwei Jahreszeiten verteilt | NS: Frühling `11:15-12:45`, Herbst `keins`, Winter `11:15-12:00, 17:00-18:45`. MS/NS: Herbst `17:00-18:15`, Winter `10:30-12:30, 16:15-19:00` |
| SNB971503120734 | Meerbusch | MS/NS 12:30-14:30 in Frühling, steht aber in Spalte Sommer | MS/NS Frühling `keins`, Sommer `12:30-14:30` |
| SNB922689183730 | Süll Luckau-Lübbenau | MS/NS Frühling 17:00-20:00 ist das 2. Winter-Fenster | MS/NS Frühling `keins`; Winter `11:00-12:00, 17:00-20:00` |
| SNB957862279702 | LSW Netz | Aus dem 0/1-Raster gelesen statt aus dem Text darüber; MS/NS "ohne Fenster" | NS Sommer `11:15-12:30`. MS/NS Sommer `19:45-21:30`, Winter `17:45-18:45`. 2027 ebenfalls neu prüfen |
| SNB950336540445 | Husum | NS Sommer fehlt | NS Sommer `13:15-13:45` ergänzen |
| SNB965281540327 | Limburg/EVL | NS Winter fehlt ein Fenster | NS Winter `08:45-09:15, 12:30-14:15, 16:00-19:00` |
| SNB948068461008 | Emmendingen | NS und MS/NS vermischt, MS/NS Herbst fehlt | NS Winter `11:30-13:30, 17:15-19:30`. MS/NS Herbst `17:00-18:15`, Winter `17:15-19:30` |
| SNB924747450655 | EWR Remscheid | Seite 5 ist die **Modul-3-Tarifzeit** (§ 14a), kein § 19 Hochlastzeitfenster; Quartale statt Jahreszeiten | Zeile entfernen, echtes HLZF-Dokument suchen |
| SNB961497906636 | Gelsenwasser | Nur das Netzgebiet Unna Südwest/Westmünsterland erfasst | Zweite Zeile Stolzenau/Rehburg-Loccum: NS Frühling `12:00-15:00`, Sommer `12:15-13:30`; MS/NS Frühling `13:15-14:45` |
| SNB939724292715 | Rostock | NS Winter: Fenster `12:15-12:15` weggelassen | Wie im Dokument eintragen, Bemerkung: Zeitstempel kennzeichnen das Ende |

## B. Richtig, aber Bemerkung fehlt oder falsches Format
- SNB927892816017 Schweiger: Einzelzeiten `18:30` und `12:30` sind kein `hh:mm-hh:mm`. Im Raster eine Viertelstunde ablesen und so eintragen, sonst leer lassen mit Begründung.
- SNB973742186519 Kiel: Dokument nennt Uhrzeit **und** Viertelstunden-Intervall (Ende-Stempel). Du hast die Intervall-Spalten genommen. In `bemerkung` angeben, welche Spalte.
- SNB963821222269 Oberkirch: Im Dokument steht Referenzzeitraum **2016 bis 2017**, Überschrift 2026. In `bemerkung` vermerken, dass das Dokument vermutlich nicht aktualisiert wurde.
- SNB963795614626 Bad Windsheim: MS/NS Frühling und Sommer leer, im Dokument leere Zellen: `keins`.
- Bigge, Kiel, Rostock, Emmerich u. a.: Zeitstempel gelten als Ende des Intervalls. Immer in `bemerkung` vermerken.

## C. Richtig (am Bild geprüft)
Aalen, Borna, Schonstett, Walldorf, Zeil (nach Korrektur), Verden, Wolkersdorf, Cottbus, inetz, Nordhausen, ovag, Borken, Emmerich, Gaggenau, Bad Kreuznach, Greifswald, Lehrte, Peine, Springe, Zweibrücken, thyssenkrupp, Veolia, Bad Vilbel, Bad Nauheim, Jena, Bigge, Tegernsee, Wittenberg, badenova, Mosbach, Limburg MS/NS.

## Was du daraus lernst (4 Muster erklären fast alle Fehler)
1. **Zelle mit mehreren Zeilen gehört zu EINER Jahreszeit.** ENRO, Hoyerswerda, Süll: Die zweite und dritte Zeile einer Zelle stehen untereinander in derselben Spalte. Erst Spalte bestimmen (x-Position unter dem Kopf), dann alle Zeilen in dieser Spalte sammeln.
2. **Spalte nach Position, nicht nach Reihenfolge.** Stade, Meerbusch: Leere Spalten (Frühling, Sommer) verschieben die Reihenfolge im Textauszug. Dann steht ein Wert plötzlich vorne.
3. **Zwei Zeilen im Bild: erst fragen, ob es dasselbe Dokument zu einer anderen Ebene gibt.** Gelsenwasser (zwei Netzgebiete), LSW (zwei PDFs für NS und MS/NS), Emmendingen (Zeilen unter und über dem Ebenennamen).
4. **Prüfe die Art des Dokuments.** EWR: Tarifzeiten Modul 3 sind kein HLZF. Das Wort "Hochlastzeitfenster" allein genügt nicht, Überschrift mit § 19 Abs. 2 StromNEV und Jahreszeiten Winter bis Herbst muss stimmen.
5. **Text vor Raster.** Steht im Dokument ein Text mit Uhrzeiten und ein Raster, gilt der Text (LSW). Das Raster nur zur Kontrolle.
6. **Rückwärtsprüfung vor dem Abgeben.** Für jede Zeit im Dokument bei NS und MS/NS die Stelle in deiner Zeile finden. Fehlt eine, ist die Zeile falsch (Limburg, Husum, Rostock).

## Auftrag
Bitte alle Zeilen in A korrigieren, B in `bemerkung` nachziehen, danach Etappe 5 liefern. Statusmeldung künftig mit MaStR-Nr. zuerst und einer Zeile je Netzbetreiber, damit wir ohne Hin und Her prüfen können. Nach Korrektur prüfen wir A und eine Stichprobe von C erneut.
