# Rückmeldung zu Etappe 1 und 2 (Hochlastzeitfenster)

Wir haben deine Zeilen an den Originalen geprüft. Vieles stimmt (Mosbach 2026/2027, badenova 2027). Diese Zeilen sind falsch und müssen korrigiert werden. Etappe 1 und 2 sind erst nach der Korrektur freigegeben.

## Falsche Zeilen

**Aalen (SNB982726407335), 2026.** Dokument (Spalten dort: Winter, Frühling, Sommer, Herbst, also andere Reihenfolge als bei dir):
- MS/NS: Winter 14:00-15:30, 17:00-18:45; Herbst 17:45-18:00
- NS: Winter 11:15-12:15, 17:00-18:45; Herbst 17:45-18:00
- Frühling und Sommer: "entfällt"

Bei dir stehen: NS nur Winter 17:00-18:45 (es fehlen 11:15-12:15 und Herbst 17:45-18:00). MS/NS Sommer 11:15-12:15 (falsche Jahreszeit, der Wert gehört zu NS Winter) und MS/NS Winter ohne 14:00-15:30.

**Borna (SNB946013720880), MS/NS 2026.** Im Dokument: Herbst 17:00-20:00; Winter 10:00-13:00 und 17:00-20:00. Bei dir Herbst "keins". Die Herbst-Zeile steht im Dokument über der Winter-Zeile und wurde übersehen.

**Schonstett (SNB950882682972), 2026.** Dokument:
- MS: Herbst 10:15-11:45; Winter 8:30-12:15, 17:30-19:15
- MS/NS: Winter 17:00-19:15
- NS: Winter 9:00-11:45, 17:30-19:30

Bei dir: NS ohne 9:00-11:45, und 9:00-11:45 steht fälschlich bei MS/NS. Ursache: Die Zeile "Niederspannung" steht unter den Zeiten, die zu ihr gehören. Die Zeiten über dem Ebenennamen gehören zum Block darüber nur dann, wenn das Bild es zeigt.

**Walldorf (SNB946790148600), MS/NS Frühling.** Dein Wert 10:30-11:45 gehört ins Dokument zu Herbst, nicht zu Frühling.

**Zeil a. Main (SNB935626894156).** Die Zeiten 13:00-13:15 und 12:45-13:00 stehen im Text über der Zeile "Umspg. MS/NS". Nicht nach dem Text zuordnen, sondern am Bild entscheiden, zu welchem Zeilenblock sie gehören, und in `bemerkung` festhalten.

## Was du daraus lernen sollst

1. **Text und Bild vergleichen, bei jeder Zeile.** Alle Fehler oben passieren, wenn man nur dem Textauszug folgt. Bei Zellen mit mehreren Fenstern ist der Text mehrzeilig, und die Zeilen oberhalb oder unterhalb des Ebenennamens gehören oft zum selben Block.
2. **Spaltenreihenfolge pro Dokument aus der Kopfzeile ablesen.** Nicht Frühling-Sommer-Herbst-Winter annehmen (Aalen: Winter zuerst).
3. **Jede Ebene hat ihren eigenen Block.** Aalen hat Zeilen für HS/MS, MS, MS/NS, NS. Alle vier getrennt lesen und nur NS und MS/NS übernehmen.
4. **Eine Ebene mit mehreren Fenstern: alle eintragen.** Fehlende zweite oder dritte Zeile ist der häufigste Fehler (Aalen NS, Schonstett NS).
5. **Eine Jahreszeit mit "entfällt" oder "-" ist `keins`.** Eine leere Zelle bei dir heißt "nicht gelesen", das ist etwas anderes als `keins`. Bei Borna war "keins" falsch, weil die Zeile da war.
6. **Nach dem Eintragen jede Zeile rückwärts prüfen:** Für jedes Fenster in deiner Zeile im Dokument die Stelle zeigen können. Und für jede Zeit im Dokument bei NS oder MS/NS die Stelle in deiner Zeile.
7. **Unklar heißt: Zelle leer lassen und in `bemerkung` begründen.** Nicht raten.
