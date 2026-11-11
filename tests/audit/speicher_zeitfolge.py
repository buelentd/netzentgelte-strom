# Prüft, wie optimistisch "Verbrauch verschieben" ist: Die Seite sortiert teure und billige Stunden eines Tages ohne Reihenfolge.
# Vergleich mit Linearprogramm je Tag mit Ladezustand (zyklisch: Ende = Anfang; und strikt: Start 0, Ende >= 0).
import sys; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy.optimize import linprog
import speicher_nachrechnung as N
def lp_tag(pr, ld, U, P, Emax, abg, zyklisch):
    # Variablen: c[0..23] (Netzbezug zum Laden), d[0..23] (Entladen für eigene Last), s[0..23] Ladezustand nach Stunde h
    n = 24; nv = 3 * n
    cost = np.zeros(nv)
    for h in range(n):
        cost[h] = (pr[h] + abg)           # Laden kostet
        cost[n + h] = -(pr[h] + abg)      # Entladen spart
    Aeq, beq = [], []
    for h in range(n):
        row = np.zeros(nv); row[2 * n + h] = 1; row[h] = -N.ETA; row[n + h] = 1
        if h > 0: row[2 * n + h - 1] = -1
        Aeq.append(row); beq.append(0)
    if zyklisch:
        # Anfangszustand = Zustand nach Stunde 23: ersetze Gleichung h=0 durch s0_prev = s23
        row = np.zeros(nv); row[2 * n + 0] = 1; row[0] = -N.ETA; row[n + 0] = 1; row[2 * n + 23] = -1
        Aeq[0] = row
    A, b = [], []
    row = np.zeros(nv); row[n:2 * n] = 1; A.append(row); b.append(Emax)     # höchstens Emax entladen
    bounds = [(0, P)] * n + [(0, min(P, ld[h])) for h in range(n)] + [(0, U)] * n
    r = linprog(cost, A_ub=np.array(A), b_ub=b, A_eq=np.array(Aeq), b_eq=beq, bounds=bounds, method='highs')
    return -r.fun / 100
def lauf(cap, ziel_kw=50.0):
    ben, zielz, kEff, verlust, ers = N.s1(cap)
    lp, ap, _ = N.tarif(zielz); U, P = N.NUTZ * cap, cap / N.DAUER
    frei = max(0, min(1, min(2, N.f('a-zyklen')) - kEff * N.arbeitstage / 365 / U))
    Emax = U * frei; abg = ap + N.steuern
    seite = N.verschiebung(Emax, P, abg)
    res = {'seite': seite, 'zyk': 0.0, 'strikt': 0.0}
    for dgi in range(len(N.B) // 24):
        wdx = (5 + dgi) % 7
        ld = N.wd if wdx < 5 else (N.sa if wdx == 5 else N.so)
        pr = N.B[dgi * 24:(dgi + 1) * 24]
        res['zyk'] += lp_tag(pr, ld, U, P, Emax, abg, True)
        res['strikt'] += lp_tag(pr, ld, U, P, Emax, abg, False)
    return res
if __name__ == '__main__':
    for c in [float(x) for x in sys.argv[1:]] or [100.0]:
        r = lauf(c); print(c, {k: round(v) for k, v in r.items()}, 'Seite/zyklisch', round(r['seite'] / r['zyk'], 3), 'Seite/strikt', round(r['seite'] / r['strikt'], 3))
