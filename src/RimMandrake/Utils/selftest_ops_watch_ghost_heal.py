#!/usr/bin/env python3
"""Promise: a started run whose unit systemd reads gone is ended by the ops_watch pass itself, with no hand.

Instance (2026-11-27 16:00Z, incident flow-20261127160122): the 15:50Z account switch stopped the unit of
rm-detached-bench-rimmandrake-autobuild-pyrelands-seven-ba-1795745935; its end receipt never ran, the store held it
`started`, flow.ghost_runs read 1, and only the Conductor's hand-run `pipe doctor` ended it. ops_watch measured the
ghost for 12 min and healed nothing. Guard: the flow.ghost_runs collector ends a gone ghost (control.reconcile) before
it reads, says what it ended, leaves a unit systemd cannot read as it is, and never reads a blind store as 0.
Fixture-only: a temp control store, stand-in systemd readings."""
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))
TMP = tempfile.mkdtemp(prefix="selftest_ops_watch_ghost_heal_")
os.environ["RM_OPS_WATCH_DIR"] = os.path.join(TMP, "ops")
import ops_watch as OW  # noqa: E402
import control as C  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  %s" % (detail,)))
    if not cond:
        FAILS.append(name)


DB = os.path.join(TMP, "c.db")
C.init(DB)
fake = lambda a, **k: subprocess.CompletedProcess(a, 0, "", "")
runs = {}
for u in ("rm-probe-gh-gone", "rm-probe-gh-blind", "rm-probe-gh-live"):
    runs[u] = C.launch_unit(["--user", "--", "true"], {"family": "probe", "unit": u}, runner=fake, p=DB).run
    C.condition(runs[u], p=DB)
seen = {"rm-probe-gh-gone": False, "rm-probe-gh-blind": None, "rm-probe-gh-live": True}
later = time.time() + 3600

r = OW.ghost_runs_reading(p=DB, now=later, unit_loaded=seen.get)
state = {u: C.run_state(x, DB)["state"] for u, x in runs.items()}
check("the gone ghost is ended by the pass", state["rm-probe-gh-gone"] == "ended", state)
check("a live unit and an unreadable unit stay started",
      state["rm-probe-gh-live"] == "started" and state["rm-probe-gh-blind"] == "started", state)
check("the reading is MEASURED 0 after the heal and names what it ended and what it cannot read",
      r.get("m") == "MEASURED" and r.get("v") == 0 and (r.get("x") or {}).get("healed") == ["rm-probe-gh-gone"]
      and (r.get("x") or {}).get("unreadable") == ["rm-probe-gh-blind"], r)

r2 = OW.ghost_runs_reading(p=DB, now=later, unit_loaded=seen.get)
check("a second pass heals nothing and reads 0", r2.get("v") == 0 and not (r2.get("x") or {}).get("healed"), r2)

bad = OW.ghost_runs_reading(p=os.path.join(TMP, "missing", "none.db"), now=later, unit_loaded=seen.get)
check("an unreadable store is UNMEASURED, never 0", bad.get("m") == "UNMEASURED", bad)

print("FAILED: %s" % FAILS if FAILS else "ALL PASS")
sys.exit(1 if FAILS else 0)
