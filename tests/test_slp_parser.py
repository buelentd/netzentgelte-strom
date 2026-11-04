from vnb.slp_parser import slp_parser

def test_netto_brutto():
    z = ["Haushaltsbedarf, gewerblicher Bedarf", "                         Grundpreis                 Arbeitspreis",
         "Netz- oder Umspannebene  netto [€/a]  brutto* [€/a]  netto [ct/kWh]  brutto* [ct/kWh]", "",
         "Niederspannung        41,65     49,56      9,32       11,09"]
    gp, ap, _ = slp_parser(z)
    assert (gp, ap) == (41.65, 9.32)

def test_ohne_leistungsmessung_zeile():
    z = ["Ebene   Grundpreis €/a   Arbeitspreis ct/kWh",
         "Entnahme ohne Leistungsmessung   Niederspannung (NS)   84,00   7,24",
         "Unterbrechbare Versorgungseinrichtungen § 14a EnWG: Speicherheizung   Niederspannung (NS)   0,00   1,91"]
    gp, ap, _ = slp_parser(z)
    assert (gp, ap) == (84.0, 7.24)

def test_speicherheizung_wird_ignoriert():
    z = ["Grundpreis    Arbeitspreis", "Speicherheizung   Niederspannung   0,00   1,91"]
    assert slp_parser(z) is None
