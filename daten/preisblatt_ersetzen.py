"""Ersetzt den gespeicherten Dokumenttext einzelner Netzbetreiber durch ein neues Preisblatt aus eingang/ (wenn dort schon ein schlechterer Text liegt).
Nur nach Prüfung von Hand (Jahr 2026, Netzbetreibername im Text, Preiszeile Niederspannung/Umspannung, kein Messstellenbetrieb): Liste unten.
Aufruf: PYTHONPATH=. python daten/preisblatt_ersetzen.py"""
import glob, os, sys
sys.path.insert(0, ".")
src = open("daten/eingang_verarbeiten.py", encoding="utf-8").read().split("def main(")[0]
exec(src)
ERSETZEN = ["pb_115_d.pdf", "pb_461_d.html", "pb_550.pdf", "pb_711_d.pdf", "pb_743_d.pdf", "pb_646_d.html"]    # geprüft 05.11.2026
n2m, unser = zuordnung()
for name in ERSETZEN:
    f = glob.glob(f"eingang/*/{name}")[0]
    z = ziel(f, n2m, unser)
    mastr, nr = z
    txt = f"ergebnis/texte_layout/{mastr}_{int(nr):04d}.txt"
    neu = "/tmp/preisblatt_neu.txt"
    if os.path.exists(neu):
        os.remove(neu)
    fehler = datei_text(f, neu)
    if fehler or not os.path.exists(neu) or os.path.getsize(neu) < 200:
        print(name, "übersprungen:", fehler or "kein Text (Scan?)"); continue
    os.replace(neu, txt)
    print("ersetzt:", name, "->", txt)
