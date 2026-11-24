#!/bin/bash
# Acceptance test (offline part) for RIMMANDRAKE_RERUN_SLACK_ONLY_ROWS_OF_CHANGED_LIST. Exit 0 pass, 1 fail, 2 could not look.
# Usage: bash <this file> [proof_all.py] [test_table.json]   |   bash <this file> --selftest
# Today proof_all.py selects only by BLOCK (--only, "a PARTIAL run, for debugging"): the second mod list reran 110 rows (609 s) to read
# the 4 scenes the table gives it. Pass = proof_all.py takes an option that selects rows or scenes by id (--rows or --scenes: OUR OWN
# naming) AND the table still names the 4 scenes of the changed list. Proxy only: whether the filter selects the right rows is the
# UNRUN live part (python.exe proof_all.py --live --rows <the 4 scenes' rows> must give 6 rows read: the 4 scenes + 2 FlowWorks rows).
cd "$(dirname "$0")/../../.." || exit 2
exec python3 -I - "$@" <<'PY'
import ast, sys, json, tempfile, os
SCENES = ["sc_true_to_grid", "sc_cords_under_items", "sc_shock_reach", "sc_settings"]
def options(path):
    t = ast.parse(open(path, encoding="utf-8").read()); o = []
    for n in ast.walk(t):
        if isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "add_argument":
            o += [a.value for a in n.args if isinstance(a, ast.Constant) and isinstance(a.value, str)]
    return o
def judge(py, tab):
    try: o = options(py); s = open(tab, encoding="utf-8").read()
    except Exception as e: print("could not look: %s" % e); return 2
    if not o: print("could not look: no add_argument found in %s" % py); return 2
    found = [x for x in SCENES if x in s]; flt = [x for x in o if x in ("--rows", "--scenes")]
    print("proof options read %d; row/scene filter %s (needs --rows or --scenes, our own rule); changed-list scenes in the table %d of %d" % (len(o), flt or "none", len(found), len(SCENES)))
    if len(found) < len(SCENES): print("could not look: the table lost a changed-list scene"); return 2
    return 0 if flt else 1
if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
    d = tempfile.mkdtemp(); ok = True
    def w(n, c): p = os.path.join(d, n); open(p, "w").write(c); return p
    base = "import argparse\nap=argparse.ArgumentParser()\nap.add_argument('--only')\n"
    tab = w("t.json", json.dumps(SCENES)); bad = w("bad.json", "[]")
    for name, py, tb, want in [("block-only -> red", w("a.py", base), tab, 1), ("--rows -> green", w("b.py", base + "ap.add_argument('--rows')\n"), tab, 0),
                               ("--scenes -> green", w("c.py", base + "ap.add_argument('--scenes')\n"), tab, 0), ("scene lost -> could not look", w("d.py", base + "ap.add_argument('--rows')\n"), bad, 2),
                               ("no parser -> could not look", w("e.py", "x=1\n"), tab, 2), ("unreadable -> could not look", os.path.join(d, "none.py"), tab, 2)]:
        import io, contextlib
        with contextlib.redirect_stdout(io.StringIO()): got = judge(py, tb)
        if got != want: ok = False; print("SELFTEST FAIL:", name, got, want)
    print("SELFTEST OK" if ok else "SELFTEST FAILED"); sys.exit(0 if ok else 1)
py = sys.argv[1] if len(sys.argv) > 1 else "src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py"
tab = sys.argv[2] if len(sys.argv) > 2 else "design/concepts/GimmeSomeSlack/version/test_table.json"
sys.exit(judge(py, tab))
PY
