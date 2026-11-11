# Unabhängige Nachrechnung Speicher (B1): Spitze senken (Säule 1), Verbrauch verschieben (Säule 4), Barwert.
# Ablauf: NODE_PATH=$(npm root -g) node tests/audit/speicher_dump.js  (schreibt dump.json), dann python tests/audit/speicher_nachrechnung.py 25 50 100 ...
# Erwartung Metzingen 250.000 kWh, 100 kW, ohne Entlastung (Steuern 5,11 ct): 100 kWh -> Summe 12.394, Barwert 32.362, Preisgrenze 741 (tests/rechner_pruefung.js prüft das in pytest).
# Eingaben: Profil G0 und Börsenpreise aus der Seite (dump.json), Tarif aus ergebnis/netzentgelte_2026.csv, Parameter wie in der Seite eingestellt.
import json, csv, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
d = json.load(open(os.path.join(HERE, 'dump.json')))
I = d['inputs']; f = lambda k: float(I[k])
kwh, kw, tage = 250000.0, 100.0, int(I['tage'])
ETA, NUTZ, DAUER = 0.92, 0.8, 2.0
row = [r for r in csv.DictReader(open(os.path.join(ROOT, 'ergebnis', 'netzentgelte_2026.csv'), encoding='utf-8-sig'), delimiter=';') if r['mastr_nr'] == 'SNB961448362368'][0]
z = lambda k: float(row[k].replace(',', '.'))
T = (z('msns_lp_unter_2500h_eur_kw_jahr'), z('msns_ap_unter_2500h_ct_kwh'), z('msns_lp_ab_2500h_eur_kw_jahr'), z('msns_ap_ab_2500h_ct_kwh'))
grenze_le = row['grenze_2500h']
def tarif(k):
    h = kwh / k
    unter = (h <= 2500) if '≤' in grenze_le or grenze_le.strip() in ('le', '<=') else (h < 2500)
    lp, ap = (T[0], T[1]) if unter else (T[2], T[3])
    return lp, ap, lp * k + ap * kwh / 100
G = d['g0']; B = d['boerse']
# Lastprofil auf Jahresmenge: 261 Werktage, 52 Samstage, 52 Sonntage (Seite: 6 Betriebstage -> Samstag wie Samstagsprofil)
wd, sa, so = G['werktag'], G['samstag'], G['sonntag']
tot = 261 * sum(wd) + 52 * sum(sa) + 52 * sum(so); fk = kwh / tot
wd, sa, so = [x * fk for x in wd], [x * fk for x in sa], [x * fk for x in so]
lwMax = max(wd)
steuern = f('a-steuern'); strom = sum(B) / len(B) + f('a-aufschlag') + steuern
arbeitstage = 52 * tage
lp0, ap0, sum0 = tarif(kw)
zins, abbau, ent = f('a-zins') / 100, f('a-abbau') / 100, f('a-entsorg')
jahre = max(1, min(25, int(f('a-zyklen-ges') / (min(2, f('a-zyklen')) * 365))))
faktor = sum(max(0, 1 - abbau * (t - 1)) / (1 + zins) ** t for t in range(1, jahre + 1))
def s1(cap):
    U, P = NUTZ * cap, cap / DAUER
    spike = kw > lwMax; skala = 1 if spike else kw / lwMax
    eNat = lambda zz: sum(max(0, c * skala - zz) for c in wd)
    eSp = lambda zz: (1 * max(0, kw - zz)) if spike else 0
    best = (0, kw, 0, 0, sum0)
    zz = kw - 1
    while zz >= max(1, kw - P):
        if max(eNat(zz), eSp(zz)) > U * 1.001: break
        lp, ap, s = tarif(zz)
        kEff = (arbeitstage * min(U, eNat(zz)) + 12 * min(U, eSp(zz))) / arbeitstage
        verlust = arbeitstage * kEff * (1 / ETA - 1) * (strom + ap) / 100
        ers = sum0 - s
        if ers - verlust > best[0]: best = (ers - verlust, zz, kEff, verlust, ers)
        zz -= 1
    return best
def s4(cap, genutzt_kEff):
    U, P = NUTZ * cap, cap / DAUER
    frei = max(0, min(1, min(2, f('a-zyklen')) - (genutzt_kEff * arbeitstage / 365 / U)))
    lp, ap, _ = tarif(kw)  # Seite: ap der Zielspitze; unten korrigiert
    return U * frei, P
def verschiebung(Emax, P, abg):
    n = len(B) // 24; tot = 0.0
    for dgi in range(n):
        wdx = (5 + dgi) % 7
        ld = wd if wdx < 5 else (sa if wdx == 5 else so)
        # Seite wählt bei tage=6 für Sonntag das Sonntagsprofil
        pr = B[dgi * 24:(dgi + 1) * 24]
        teuer = sorted(range(24), key=lambda h: -pr[h]); billig = sorted(range(24), key=lambda h: pr[h])
        lad = [0.0] * 24; E = 0.0; w = 0.0
        for hi in teuer:
            dh = min(ld[hi], P, Emax - E)
            if dh <= 1e-9: continue
            need = dh / ETA
            for lo in billig:
                fr = P - lad[lo]
                if fr <= 0 or lo == hi: continue
                m = min(need, fr); marge = (pr[hi] + abg) * m * ETA - (pr[lo] + abg) * m
                if marge <= 0: break
                lad[lo] += m; w += marge; E += m * ETA; need -= m
                if need <= 1e-9: break
        tot += w / 100
    return tot
def preis(c): return 450 if c <= 100 else max(350, 450 - (c - 100) / 400 * 100)
def lauf(cap):
    ben, zielz, kEff, verlust, ers = s1(cap)
    lp, ap, _ = tarif(zielz)
    U, P = NUTZ * cap, cap / DAUER
    genutzt = kEff * arbeitstage / 365 / U
    frei = max(0, min(1, min(2, f('a-zyklen')) - genutzt))
    v4 = verschiebung(U * frei, P, ap + steuern) if frei > 0 else 0
    pj = preis(cap); opex = 0.015 * pj * cap
    summe = ben + v4 - opex; kosten = pj * cap
    entsorgbw = ent * cap / (1 + zins) ** jahre
    ann = sum(1 / (1 + zins) ** t for t in range(1, jahre + 1))
    bw = (summe + opex) * faktor - opex * ann - kosten - entsorgbw
    be = ((summe + opex) * faktor - entsorgbw) / (0.015 * ann + 1) / cap
    return dict(cap=cap, ziel=zielz, ersparnis=ers, verlust=verlust, s1=ben, s4=v4, opex=opex, summe=summe, kosten=kosten, barwert=bw, breakEven=be, entsorg=entsorgbw)
if __name__ == '__main__':
    print('lwMax', round(lwMax, 2), 'strom', round(strom, 3), 'jahre', jahre, 'faktor', round(faktor, 4), 'grenze', grenze_le, 'T', T)
    for c in [float(x) for x in sys.argv[1:]] or [100.0]:
        print({k: round(v, 1) for k, v in lauf(c).items()})
