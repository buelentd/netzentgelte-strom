# Anleitung: Hochlastzeitfenster-PDFs lesen, auch wenn die Schrift nicht lesbar erscheint

Anlass: Das PDF der Stadtwerke Ilmenau (HLZF_2026.pdf) hieß bei dir „Schrift nicht lesbar". Bei uns war es lesbar. Das PDF enthält einen normalen Textlayer (eingebettete Schrift mit Unicode-Zuordnung). Mit diesen Schritten kommst du auch dann an die Werte, wenn dein Werkzeug den Text nicht anzeigt.

## 1. Datei holen
- PDF direkt herunterladen (kein Abbild der Webseite). Vorher `robots.txt` der Seite ansehen. Ist der Pfad gesperrt, nicht umgehen, in `bemerkung` „gesperrt" eintragen.
- Höchstens 1 Anfrage pro Sekunde je Domain, ehrlicher Kennzeichner.

## 2. Text maschinell auslesen
```
pdftotext -layout datei.pdf text.txt
```
`-layout` ist wichtig: Es behält die Spalten bei. Ohne diese Option stehen die Uhrzeiten durcheinander.
Läuft `pdftotext` bei dir nicht, siehe 2b. Ist `text.txt` leer oder voller Zeichensalat (Kästchen, Fragezeichen), ist der Text nicht auslesbar (Scan oder Schrift ohne Zuordnung). Dann Schritt 3.

## 2b. Wenn pdftotext bei dir nicht läuft
Dann brauchst du es nicht, es geht auch ohne. Zwei Wege:
- **Nur Bild (immer möglich):** Das PDF in einem PDF-Programm oder im Browser öffnen, bei Bedarf als Bild speichern oder einen Bildschirmausschnitt machen und die Zeiten ablesen. Das reicht für alle Dokumente. Bei jedem Wert die Spalte (Jahreszeit) und die Zeile (Netzebene) im Bild mitlesen.
- **Mit Python, ohne Poppler:** `pip install pymupdf` und dann
```
import fitz
d = fitz.open("datei.pdf")
for w in d[0].get_text("words"):   # (x0, y0, x1, y1, Wort, ...)
    print(round(w[0]), round(w[1]), w[4])
d[0].get_pixmap(dpi=110).save("seite.png")
```
Die Ausgabe nennt jedes Wort mit Position. Zeiten, die unter einem Jahreszeit-Kopf stehen (gleiche x-Position), gehören zu dieser Jahreszeit. Das ersetzt `pdftotext -layout` und das Bild.

## 3. Als Bild lesen (Kontrolle oder wenn der Text fehlt)
```
pdftoppm -r 110 -png datei.pdf seite
```
Das Bild ansehen und die Zeiten ablesen. Bei jedem PDF **beides vergleichen**: Text und Bild müssen übereinstimmen. Stimmen sie nicht überein, gilt das Bild.

## 4. Spalten zuordnen, nicht raten
Typisches Muster A (Ilmenau): Zeilen je Netzebene (MS, MS/NS, NS), Spalten je Jahreszeit mit „von" und „bis". Mehrere Fenster stehen **untereinander** in derselben Zelle, auf Folgezeilen ohne Beschriftung. Die Zeit gehört zu der Jahreszeit-Spalte, unter der sie steht. Positionen der Spaltenköpfe in `text.txt` mit der Position der Zeiten vergleichen (oder im Bild nachsehen).
Typisches Muster B (Forst): Eine Zeile je **Viertelstunde** („06:30 - 06:45 Uhr"), die Netzebene steht nur einmal in der Mitte des Blocks. Blockgrenzen sind im Bild sichtbar (Farbwechsel). **Nicht** nach dem Text der Ebene zuordnen: Die Zeilen oberhalb des Ebenen-Namens gehören auch zu diesem Block. Aneinanderstoßende Viertelstunden zu einem Fenster zusammenfassen (06:30-06:45, 06:45-07:00 ... wird 06:30-08:30).

## 5. Ergebnis eintragen
Je Netzbetreiber und Netzebene eine Zeile, je Jahreszeit eine Zelle:
- Spalten: `mastr_nr` zuerst, dann NS und MS/NS je Frühling, Sommer, Herbst, Winter.
- Format: `hh:mm-hh:mm`, mehrere Fenster getrennt durch Komma und Leerzeichen, zum Beispiel `09:45-12:45, 14:00-14:15, 16:30-19:00`.
- Steht in einer Jahreszeit nichts: `keins`. Nichts schätzen. Ist die Zuordnung unklar, Zelle leer lassen und in `bemerkung` begründen.
- Zusätzlich, falls im Dokument genannt: **Schwelle in Prozent** (zum Beispiel 30 %), **Mindestverlagerung in kW** (zum Beispiel 100 kW), Gültigkeit (Werktage, Brückentage, Zeit zwischen Weihnachten und Neujahr). Steht nichts im Dokument, leer lassen.
- Quelle: die genaue Adresse des PDFs.

## 6. Prüfen vor dem Abgeben
- Sind es Uhrzeiten und keine Preise oder Zähler?
- Passen die Netzebenen (NS, MS/NS, MS) zu den Zeilen im Bild?
- Hat das Dokument das Jahr 2026? Steht 2027 oder älteres darin, nicht eintragen, sondern in `bemerkung` das Jahr nennen.
- Liegt das Dokument auf der Website dieses Netzbetreibers (nicht eines anderen)?

## 7. Abgabe
Wie im Auftrag: CSV (mastr_nr zuerst) und ZIP mit den Originalen an den Nutzer, in Etappen.

## Beispiele aus dem Bestand (beide am PDF und am Bild geprüft)
- Stadtwerke Ilmenau (SNB964659661008): NS Winter `10:45-12:00`; MS/NS Herbst `17:00-18:45`, Winter `09:45-12:45, 14:00-14:15, 16:30-19:00`; Schwelle 30 %, Mindestverlagerung 100 kW.
- Netzgesellschaft Forst (SNB922055731633): nur Winter. NS `07:30-10:00, 17:30-17:45, 18:15-18:30`; MS/NS `06:45-08:00, 16:45-20:00`. Schwelle und Mindestleistung stehen nicht im Dokument.
