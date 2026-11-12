"""Datensatz für conplot.de aus der aktuellen Tabelle (MaStR-Nr. ist der Schlüssel): Netzentgelte 2026 (RLM, SLP), Hochlastzeitfenster,
Modul-3-Zeiten, Netzentgelte 2027 (vorläufig, soweit gelesen) und PLZ-Zuordnung. Beschreibung: ergebnis/conplot/FORMAT.md
Aufruf: PYTHONPATH=. python daten/conplot_export.py"""
import csv, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FERTIG = ("gelesen_nutzer", "gelesen_unser", "gelesen_kollege_verifiziert", "gelesen_aus_2027")
JZ = ("fruehling", "sommer", "herbst", "winter")


def lesen(pfad):
    return list(csv.DictReader(open(ROOT / pfad, encoding="utf-8-sig"), delimiter=";"))


def zahl(v):
    v = (v or "").strip()
    return float(v.replace(".", "").replace(",", ".")) if v else None


def rlm(z, p):
    w = {"lp_unter_eur_kw_jahr": zahl(z.get(f"{p}_lp_unter_2500h_eur_kw_jahr")), "ap_unter_ct_kwh": zahl(z.get(f"{p}_ap_unter_2500h_ct_kwh")),
         "lp_ab_eur_kw_jahr": zahl(z.get(f"{p}_lp_ab_2500h_eur_kw_jahr")), "ap_ab_ct_kwh": zahl(z.get(f"{p}_ap_ab_2500h_ct_kwh"))}
    return w if all(v is not None for v in w.values()) else None


def preise(z, ok_wert="ok"):
    ok = z.get("status") == ok_wert
    ns, msns, ms = (rlm(z, "ns") if ok else None), (rlm(z, "msns") if ok else None), (rlm(z, "ms") if ok else None)
    slp = {"ap_ct_kwh": zahl(z.get("slp_ap_ct_kwh")), "gp_eur_jahr": zahl(z.get("slp_grundpreis_eur_jahr"))} if ok and z.get("slp_ap_ct_kwh") else None
    return {"rlm": {"ns": ns, "msns": msns, "ms": ms} if (ns or msns or ms) else None, "slp": slp}


def hlzf_ebene(z, eb, schwelle, mind):
    fenster = {}
    for j in JZ:
        v = (z.get(f"hlzf_{eb}_{j}") or "").strip()
        if v:
            fenster[j] = [] if v == "keins" else [x.strip() for x in v.split(",")]
    if not fenster:
        return None
    laut = bool(schwelle)
    return {"zeitfenster": fenster, "schwelle_prozent": int(float(schwelle)) if laut else 30,
            "herkunft_schwelle": "laut Netzbetreiber" if laut else "Standard (fachlich zu bestätigen)",
            "mindestverlagerung_kw": int(float(mind)) if mind else None}


def main():
    T = lesen("ergebnis/netzentgelte_2026.csv")
    T27 = {z["mastr_nr"]: z for z in lesen("ergebnis/netzentgelte_2027_vorlaeufig.csv")}
    M3 = {}
    for r in lesen("ergebnis/modul3_zeiten.csv"):
        M3.setdefault(r["mastr_nr"], []).append({
            "jahr": int(r["jahr"]), "hochtarif": {"zeiten": r["ht_zeiten"], "ct_kwh": zahl(r["ht_ct_kwh"])},
            "standardtarif": {"zeiten": r["st_zeiten"], "ct_kwh": zahl(r["st_ct_kwh"])},
            "niedertarif": {"zeiten": r["nt_zeiten"], "ct_kwh": zahl(r["nt_ct_kwh"])},
            "quartale": r["quartale"] or None, "preisstand": r["preisstand"], "quelle": r["quelle_url"], "hinweis": r["hinweis"]})
    out = []
    for z in T:
        p = preise(z)
        ns_h = hlzf_ebene(z, "ns", z.get("hlzf_schwelle_prozent"), z.get("hlzf_mindestleistung_kw")) if z.get("hlzf_status") in FERTIG else None
        ms_h = hlzf_ebene(z, "msns", z.get("hlzf_schwelle_prozent"), z.get("hlzf_mindestleistung_kw")) if z.get("hlzf_status") in FERTIG else None
        hl = {"status": z["hlzf_status"], "quelle": z.get("hlzf_quelle_url") or None, "ns": ns_h, "msns": ms_h} if (ns_h or ms_h) else None
        z27 = T27.get(z["mastr_nr"])
        p27 = preise(z27, "gelesen") if z27 else None
        p27 = p27 if p27 and (p27["rlm"] or p27["slp"]) else None
        fehlt = [t for t, v in (("rlm_ns", p["rlm"] and p["rlm"]["ns"]), ("slp", p["slp"]), ("hlzf", hl)) if not v]
        out.append({"mastr_nr": z["mastr_nr"], "nr": int(z["nr"]), "netzbetreiber": z["netzbetreiber"], "website": z["website"],
                    "bundesland": z.get("bundesland") or None, "jahr": 2026, "preisstand": z["preisstand"] or None, "stand_datum": z["stand_datum"] or None,
                    "grenze": "<=2500" if "≤ 2.500" in z["hinweis"] else "<2500", "rlm": p["rlm"], "slp": p["slp"], "hlzf": hl,
                    "modul3": M3.get(z["mastr_nr"]), "preise_2027_vorlaeufig": p27,
                    "quelle_url": z["quelle_url"] or None, "status": z["status"], "fehlt": fehlt})
    plz = {}
    for r in lesen("ergebnis/plz_netzbetreiber.csv"):
        plz.setdefault(r["plz"], [])
        if all(e["mastr_nr"] != r["mastr_nr"] for e in plz[r["plz"]]):
            plz[r["plz"]].append({"mastr_nr": r["mastr_nr"], "anteil_prozent": zahl(r["anteil_prozent"])})
    ziel = ROOT / "ergebnis" / "conplot"
    ziel.mkdir(exist_ok=True)
    (ziel / "netzbetreiber_2026.json").write_text(json.dumps({"schluessel": "mastr_nr", "jahr": 2026, "einheiten": {"lp": "EUR je kW und Jahr (Jahresleistungspreis, netto)", "ap": "Cent je kWh (netto)", "gp": "EUR je Jahr (netto)"}, "netzbetreiber": out}, ensure_ascii=False, indent=1), encoding="utf-8")
    (ziel / "plz_2026.json").write_text(json.dumps(plz, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print({"netzbetreiber": len(out), "rlm_ns": sum(1 for e in out if e["rlm"] and e["rlm"]["ns"]), "slp": sum(1 for e in out if e["slp"]),
           "hlzf": sum(1 for e in out if e["hlzf"]), "modul3": sum(1 for e in out if e["modul3"]), "preise_2027": sum(1 for e in out if e["preise_2027_vorlaeufig"]), "plz": len(plz)})


main()


def umlagen_export():
    import csv
    zeilen = list(csv.DictReader(open("ergebnis/umlagen_steuern_2026.csv", encoding="utf-8-sig"), delimiter=";"))
    out = [{"position": z["position"], "wert": float(z["wert"].replace(",", ".")), "einheit": z["einheit"],
            "jahr": z["jahr"], "quelle": z["quelle_fundstelle"], "status": z["status"]} for z in zeilen]
    Path("ergebnis/conplot/umlagen_steuern_2026.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return len(out)


if __name__ == "__main__":
    print("umlagen:", umlagen_export())
