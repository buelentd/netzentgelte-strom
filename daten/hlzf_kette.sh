#!/bin/bash
# HLZF-Kette: Neu lesen, Handablesungen anwenden, zusammenführen, Tabelle, Ebenen, Arbeitsliste.
export PYTHONPATH=.
python daten/hlzf_neu_lesen.py | tail -1 | cut -c1-80
python daten/hlzf_handlesung.py
python daten/hlzf_zusammenfuehren.py | tail -1
python run.py bericht >/dev/null 2>&1; python daten/ebenen_erwartung.py >/dev/null 2>&1; python daten/hsms_grund.py >/dev/null 2>&1; python run.py bericht >/dev/null 2>&1
python daten/arbeitsliste.py | tail -3
