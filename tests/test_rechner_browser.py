"""Rechenproben der Testseite im Browser (Node und Playwright nötig). Ohne beides wird übersprungen."""
import os, shutil, subprocess, pytest

W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_rechenproben_testseite():
    if not shutil.which("node"):
        pytest.skip("node fehlt")
    root = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
    env = dict(os.environ, NODE_PATH=root)
    r = subprocess.run(["node", os.path.join(W, "tests", "rechner_pruefung.js")], capture_output=True, text=True, env=env, timeout=120)
    if "Cannot find module 'playwright'" in r.stderr:
        pytest.skip("playwright fehlt")
    assert r.returncode == 0, r.stdout + r.stderr
