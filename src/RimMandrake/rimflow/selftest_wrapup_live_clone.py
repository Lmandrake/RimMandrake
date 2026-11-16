#!/usr/bin/env python3
"""selftest_wrapup_live_clone.py — RIMMANDRAKE_SPARE_LIVE_CLONE_FROM_DEBRIS_FIFTH_RUN_SAME: a filed clone row stops
standing while a live process works in that clone.

The incident (unrouted-20261102214722) relapsed on wrapup.debris_standing 4: four wrap-ups of earlier detached runs of
one item had filed its .det clone, and the fifth run of that item was working in the same clone. Work in flight is not
debris; once nothing runs there, dirt left behind stands again.

  L1  a dirty filed clone with a live process inside it does not stand
  L2  the same clone with nothing running inside it stands
  L3  clone_in_use unmeasurable (raises): the row stands (never clear on ignorance)
  L4  World.clone_in_use sees a real process whose cwd is inside the clone, and not after it exits
"""
import json
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TMP = tempfile.mkdtemp(prefix="selftest_wrapup_live_")
os.environ["RM_WRAPUP_DIR"] = os.path.join(TMP, "state")
os.environ["RIMFLOW_SHARED_BRIDGE"] = ""
os.environ["RM_WRAPUP_PREV_LOG"] = ""

import wrapup  # noqa: E402

FAILS = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


class Fake(wrapup.World):
    def __init__(self, in_use=False, raises=False):
        self.in_use, self.raises = in_use, raises

    def shared_bridge(self):
        return None

    def clone_in_use(self, clone):
        if self.raises:
            raise OSError("proc unreadable")
        return self.in_use


clone = os.path.join(TMP, "ITEM.det")
os.makedirs(clone)
subprocess.run(["git", "init", "-q", clone], check=True)
with open(os.path.join(clone, "work.txt"), "w") as f:
    f.write("in flight\n")
rec = {"at": wrapup._iso(time.time()), "kind": "unit", "key": "u1", "seat": "BENCH", "clones": [clone],
       "rows": [{"kind": "clone", "what": clone, "act": "filed", "why": "1 uncommitted path"}]}
wrapup._write_json(wrapup._p("open", "unit-u1.json"), rec)


def n_standing(world):
    return sum(len(rs) for _, _, rs in wrapup.standing(world))


check(n_standing(Fake(in_use=True)) == 0, "L1 a dirty clone a live process works in does not stand")
check(n_standing(Fake(in_use=False)) == 1, "L2 the dirty clone with nothing running inside stands")
check(n_standing(Fake(raises=True)) == 1, "L3 an unmeasurable clone_in_use leaves the row standing")

w = wrapup.World()
p = subprocess.Popen(["sleep", "30"], cwd=os.path.join(clone))
try:
    time.sleep(0.2)
    seen = w.clone_in_use(clone)
finally:
    p.kill()
    p.wait()
check(seen is True and w.clone_in_use(clone) is False and w.clone_in_use(os.path.join(TMP, "ITEM")) is False,
      "L4 World.clone_in_use sees a process with its cwd in the clone, not after it exits, not a prefix sibling")

print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
sys.exit(1 if FAILS else 0)
