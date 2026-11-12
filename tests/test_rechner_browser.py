"""Rechenproben der Testseite im Browser (Node und Playwright nötig). Ohne beides wird übersprungen.
Die Speicher-Erwartung (Barwert, Summe, Preisgrenze) kommt aus der unabhängigen Nachrechnung tests/audit/speicher_nachrechnung.py
mit den gerade eingebetteten Börsenpreisen. Die Börsenpreise werden täglich aktualisiert, feste Zahlen wären nach wenigen Tagen falsch."""
import ast, os, shutil, subprocess, sys, pytest

W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_rechenproben_testseite():
    if not shutil.which("node"):
        pytest.skip("node fehlt")
    root = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
    env = dict(os.environ, NODE_PATH=root)
    d = subprocess.run(["node", os.path.join(W, "tests", "audit", "speicher_dump.js")], capture_output=True, text=True, env=env, timeout=120)
    if "Cannot find module 'playwright'" in d.stderr:
        pytest.skip("playwright fehlt")
    n = subprocess.run([sys.executable, os.path.join(W, "tests", "audit", "speicher_nachrechnung.py"), "100"], capture_output=True, text=True, timeout=120)
    erg = [l for l in n.stdout.splitlines() if l.startswith("{")]
    if erg:
        werte = ast.literal_eval(erg[-1])
        env.update(EXPECT_BARWERT=str(werte["barwert"]), EXPECT_SUMME=str(werte["summe"]), EXPECT_BREAKEVEN=str(werte["breakEven"]))
    r = subprocess.run(["node", os.path.join(W, "tests", "rechner_pruefung.js")], capture_output=True, text=True, env=env, timeout=120)
    if "Cannot find module 'playwright'" in r.stderr:
        pytest.skip("playwright fehlt")
    assert r.returncode == 0, r.stdout + r.stderr
