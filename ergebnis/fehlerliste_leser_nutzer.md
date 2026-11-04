# Fehlerliste zu fill_neu.js, parse_v3.js, dler.sh, verify.js, verify3.js

Stand 04.11.2026. Zeilennummern beziehen sich auf die hochgeladenen Dateien.

## parse_v3.js (wichtigster Punkt)
1. Zuordnung der Ebenen nach LP ab 2.500 h (aufsteigend sortiert, Reihenfolge HS/MS, MS, MS/NS, NS) mit Monotonie von LP und AP (Zeilen 157-179, 248-253).
   Das ist fachlich falsch: Die MS-LP kann höher sein als die NS-LP (Beispiel Schönau: MS 264,69, MS/NS 291,66, NS 242,13).
   Richtig: Zuordnung über den Ebenennamen in derselben Zeile.
2. Die Plausibilitätsprüfung (Zeilen 294-299) prüft die LP-Reihenfolge. Bei 109 von 217 Datensätzen mit MS, MS/NS und NS ist sie verletzt, die ct/kWh-Reihenfolge bei 4.000 h aber nur bei 25.
   Richtig: ct/kWh bei 4.000 h = AP + LP x 100 / 4000, Reihenfolge MS <= MS/NS <= NS (mit kleiner Toleranz).

## fill_neu.js
3. Zeilen 89-91: Feld `r.confidence` gibt es nicht, der Datensatz heißt `conf`. Der Grund "Werte prüfen" wird nie geschrieben (159 von 201 Zeilen mit "teilweise" betroffen).
4. Zeilen 77-80: Die Hochlastzeitfenster der NS werden auf MS/NS kopiert. 100 von 110 Zeilen mit beiden Ebenen sind in allen vier Jahreszeiten gleich (bei unserer Lesung 30 von 159). Nur eintragen, was im Dokument für MS/NS steht.
5. Zeile 85 wird von Zeile 99 überschrieben (HLZF-Notiz geht verloren).
6. Zeilen 61-65: ct/kWh bei 1.500 h muss den Tarif "unter 2.500 h" nutzen (AP und LP unter), nicht den Tarif "ab".
7. Zeile 87: stand_datum fest "2026"; preisstand wird nie befüllt.
8. Zeile 38: Zeilen ohne Ebenen werden übersprungen (kein Eintrag in der Restliste).
9. Absolute Pfade fest eingetragen.

## dler.sh
10. Vorgetäuschter Browser-User-Agent, keine robots.txt-Prüfung, keine Begrenzung pro Domain (max. 1 Anfrage/s), Timeout 60 s statt 30 s. Widerspricht den Projektregeln.
11. Jina-Weg (r.jina.ai): URLs gehen an einen Dritten und umgehen Sperren. Nicht übernehmen.

## verify.js / verify3.js
12. "Wert kommt irgendwo im Text vor" ist zu schwach (Zufallstreffer). Besser: alle vier Werte in derselben Zeile neben dem Ebenennamen.
