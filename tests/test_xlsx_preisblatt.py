import openpyxl

from vnb.xlsx_preisblatt import preisblatt_lesen


def _datei(tmp_path, zeilen):
    wb = openpyxl.Workbook()
    ws = wb.active
    for z in zeilen:
        ws.append(z)
    p = tmp_path / "pb.xlsx"
    wb.save(p)
    return str(p)


def test_artikel_id_mit_einheit_in_nachbarzelle(tmp_path):
    z = []
    for ebene, (lp_u, ap_u, lp_o, ap_o) in {"7": (0.05, 0.07, 0.4, 0.02), "6": (0.04, 0.06, 0.3, 0.015)}.items():
        z += [[f"Artikel-ID [1-01-{ebene}-001]", "Leistungspreis", lp_u, "€/kW*Tag"], [f"Artikel-ID [1-01-{ebene}-002]", "Arbeitspreis", ap_u, "€/kWh"],
              [f"Artikel-ID [1-01-{ebene}-003]", "Leistungspreis", lp_o, "€/kW*Tag"], [f"Artikel-ID [1-01-{ebene}-004]", "Arbeitspreis", ap_o, "€/kWh"]]
    z += [["Artikel-ID [1-02-0-001]", "Grundpreis", 0.2, "€/Tag"], ["Artikel-ID [1-02-0-002]", "Arbeitspreis", 0.075, "€/kWh"]]
    r = preisblatt_lesen(_datei(tmp_path, z))
    assert r["ns"] == [18.25, 7.0, 146.0, 2.0]
    assert r["msns"] == [14.6, 6.0, 109.5, 1.5]
    assert r["slp"] == [73.0, 7.5]


def test_zielwert_in_spalte_hat_vorrang(tmp_path):
    z = [["1-01-7-001", "Jahresleistungspreis Niederspannung <2500 h/a (Einheit: €/kW*Tag)", "X", "X", 0.05, "€/kW*Tag", 18.3, "€/kW*a"],
         ["1-01-7-002", "Arbeitspreis (Einheit: €/kWh)", "X", "X", 0.0465, "€/kWh", 4.65, "ct/kWh"],
         ["1-01-7-003", "Leistungspreis >=2500 h/a (Einheit: €/kW*Tag)", "X", "X", 0.3, "€/kW*Tag", 109.5, "€/kW*a"],
         ["1-01-7-004", "Arbeitspreis (Einheit: €/kWh)", "X", "X", 0.0189, "€/kWh", 1.89, "ct/kWh"]]
    assert preisblatt_lesen(_datei(tmp_path, z))["ns"] == [18.3, 4.65, 109.5, 1.89]


def test_unplausibel_oder_unvollstaendig_bleibt_leer(tmp_path):
    z = [["Artikel-ID [1-01-7-001]", "Leistungspreis", 0.05, "€/kW*Tag"], ["Artikel-ID [1-01-7-002]", "Arbeitspreis", 0.07, "€/kWh"]]
    assert "ns" not in preisblatt_lesen(_datei(tmp_path, z))
