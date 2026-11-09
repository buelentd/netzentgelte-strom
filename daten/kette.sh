#!/bin/bash
# Kette nach Änderungen an Preisen: Entscheidungen anwenden, Tabelle, Ebenen, Bestätigung, Prüfmarke, Arbeitsliste.
export PYTHONPATH=.
python daten/preise_entscheidungen.py
for i in 1 2; do python run.py bericht >/dev/null 2>&1; python daten/ebenen_erwartung.py >/dev/null 2>&1; python daten/hsms_grund.py >/dev/null 2>&1; python run.py bericht >/dev/null 2>&1; python daten/preise_bestaetigung.py | tail -2; python daten/geprueft_setzen.py; done
python daten/beleg_leser.py alle >/dev/null 2>&1; python run.py bericht >/dev/null 2>&1; python daten/ebenen_erwartung.py >/dev/null 2>&1; python daten/arbeitsliste.py | tail -3
