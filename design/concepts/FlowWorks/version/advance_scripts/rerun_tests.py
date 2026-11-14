#!/usr/bin/env python3
"""Throwaway (FlowWorks Stage 3 reconcile, 2026-11-14): re-run named offline tests of version/test_table.json and record
runs_today (rc, seconds, tail, at) the way make_table.py did, so preflight_fw.py's C6 reads today's state.
    python3 design/concepts/FlowWorks/version/advance_scripts/rerun_tests.py PY_LIQUID_LOOKS PY_FLOWWORKS_NORTHSTAR ..."""
import json, os, subprocess, sys, time, datetime
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 5))
os.chdir(ROOT)
P = "design/concepts/FlowWorks/version/test_table.json"
tab = json.load(open(P))
for k in sys.argv[1:]:
    t = tab["tests"][k]
    t0 = time.time()
    r = subprocess.run(t["command"], shell=True, capture_output=True, text=True, timeout=1800)
    out = (r.stdout + r.stderr).strip().splitlines()
    fails = [l for l in out if "FAIL" in l][:3]
    t["runs_today"] = {"ran": True, "rc": r.returncode, "seconds": round(time.time() - t0, 1),
                       "tail": (" | ".join(fails) if r.returncode and fails else (out[-1] if out else ""))[:300],
                       "at": datetime.datetime.now().astimezone().isoformat(timespec="seconds")}
    print(k, r.returncode, t["runs_today"]["seconds"], t["runs_today"]["tail"][:160])
json.dump(tab, open(P, "w"), indent=1)
