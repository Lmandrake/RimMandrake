#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_KEEP_IN_FLIGHT_DEBRIS_OPEN_SWEEP_BURIED_IT.

wrapup.row_standing() returns False for a filed clone row while a live process works in the clone (cwd) or a live
cleanse run holds its dot-sibling lock (OPS_WRAPUP_SKIP_CLONES_OF_LIVE_FLEET_RUN, cf4a8a4d02). sweep() then reads
"every filed row cleared" and moves the record to resolved/, so once the run ends with the dirt still there the row
never stands again: "in flight" was turned into "cleared". Measured 2026-11-18 on a907fc6756: sweep (1, 0) while
the lock was live, then standing 0 with the lock freed and the clone still dirty; the cwd case reads the same.

Passes when, for BOTH in-flight kinds, a sweep run while the clone is in flight leaves the record open, and the row
stands again once the run has ended (clone still dirty).

    python3 src/RimMandrake/rimflow/acceptance/wrapup_sweep_keeps_in_flight_accept.py     exit 0 = pass, 1 = fail

Expected on a correct result: `PASS 2 of 2 in-flight kinds stand again after the run`. The builder does not edit this
file.
"""
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
TMP = tempfile.mkdtemp(prefix="accept_wrapup_sweep_")
os.environ["RM_WRAPUP_DIR"] = os.path.join(TMP, "state")
os.environ["RIMFLOW_SHARED_BRIDGE"] = ""
os.environ["RM_WRAPUP_PREV_LOG"] = ""
import wrapup  # noqa: E402


class Fake(wrapup.World):
    def __init__(self, in_use=False, owner=("none", "no lock file")):
        self.in_use, self.owner = in_use, owner

    def shared_bridge(self):
        return None

    def clone_in_use(self, clone):
        return self.in_use

    def clone_owner(self, clone):
        return self.owner


def standing(world, clone):
    """-> how many standing rows name this clone (each case counts only its own record)."""
    return sum(1 for _, _, rs in wrapup.standing(world) for r in rs if r.get("what") == clone)


ok, bad = 0, []
for kind, live in (("cwd", Fake(in_use=True)), ("lock", Fake(owner=("live", "pid 1 holds the lock")))):
    clone = os.path.join(TMP, "cleanse-" + kind)
    os.makedirs(clone)
    subprocess.run(["git", "init", "-q", clone], check=True, timeout=60)
    with open(os.path.join(clone, "stray.md"), "w") as f:
        f.write("left behind\n")
    rec = {"at": wrapup._iso(time.time()), "kind": "unit", "key": kind, "seat": "BENCH", "clones": [clone],
           "rows": [{"kind": "clone", "what": clone, "act": "filed", "why": "1 uncommitted path"}]}
    wrapup._write_json(wrapup._p("open", "unit-%s.json" % kind), rec)
    swept = wrapup.sweep(live)
    after = standing(Fake(owner=("free", "the lock file is there, held by nobody")), clone)
    print("%s: sweep while in flight -> %s; standing once the run ended -> %d" % (kind, swept, after))
    if after == 1:
        ok += 1
    else:
        bad.append(kind)
print(("PASS %d of 2 in-flight kinds stand again after the run" % ok) if not bad else
      ("FAIL in-flight debris resolved for good by a sweep: %s" % ", ".join(bad)))
sys.exit(1 if bad else 0)
