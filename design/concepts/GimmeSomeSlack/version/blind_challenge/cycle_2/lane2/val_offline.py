#!/usr/bin/env python3
"""validation.py's offline rows O1, O2, O5-O8 (T_GATE minus O3/O4, which are T_CORE and the Python oracle), one line each.
Exit 0 when every row is PASS. Used by plant_faults.py as the `val` suite (seconds, against T_GATE's ~4 minutes)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
MOD = os.path.join(REPO, "src/RimMandrake/GimmeSomeSlack"); sys.path.insert(0, MOD); os.chdir(MOD)
import validation as V
rows = []
for f in (V.o1_files, V.o2_defaults, V.o5_style_art, V.o6_review_round1, V.o7_gpt_read_fixes, V.o8_lamp_mast_register):
    try: f(rows)
    except Exception as e: rows.append({"id": f.__name__, "status": "FAIL", "detail": "raised %r" % e})
bad = [r for r in rows if r.get("status") != "PASS"]
for r in rows: print(("PASS " if r.get("status") == "PASS" else "FAIL ") + r["id"], str(r.get("detail"))[:300])
print("%d/%d checks passed" % (len(rows) - len(bad), len(rows)))
sys.exit(1 if bad else 0)
