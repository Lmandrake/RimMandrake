#!/usr/bin/env python3
"""Acceptance: a wrap-up debt is about one game, and only that game's relaunch voids it. Exit 0 = all pass (6 checks).
Runs wrapup.py's own CLI-level functions in a temp state folder; no game, no bridge. Red on 9e3c73ab1f (3 of 6 pass)."""
import glob
import json
import os
import subprocess
import sys
import tempfile
import time

TOP = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
RF = os.path.join(TOP, "src", "RimMandrake", "rimflow")
OWE = "import sys; sys.path.insert(0, %r); import wrapup; wrapup.owe('setting', 'forced X', undo='x', owner='pid:1')" % RF
VOID = ("import sys, json, glob; sys.path.insert(0, %r); import wrapup; wrapup.sweep(); "
        "print(len(glob.glob(wrapup._p('debts', '*.json'))))" % RF)
bad = 0


def case(what, owed_in, a_log_age, b_log_age, want_open, strip_game=False):
    """A debt owed 2 h ago in game `owed_in`; each game's previous log ended that many seconds ago (None: no log)."""
    global bad
    t = tempfile.mkdtemp(prefix="wrapup_game_")
    env = {**os.environ, "RM_WRAPUP_DIR": os.path.join(t, "state"), "RM_INSTANCES_ROOT": os.path.join(t, "inst"),
           "RM_WRAPUP_PREV_LOG": os.path.join(t, "Player-prev.log"), "RM_WRAPUP_SEAT_CLONES": t}
    env.pop("RM_GAME_INSTANCE", None)
    os.makedirs(os.path.join(t, "inst", "b"))
    for p, age in ((env["RM_WRAPUP_PREV_LOG"], a_log_age), (os.path.join(t, "inst", "b", "Player.log.prev"), b_log_age)):
        if age is not None:
            open(p, "w").close()
            os.utime(p, (time.time() - age,) * 2)
    subprocess.run([sys.executable, "-c", OWE], env={**env, "RM_GAME_INSTANCE": owed_in} if owed_in == "b" else env,
                   check=True, capture_output=True)
    f, = glob.glob(os.path.join(t, "state", "debts", "*.json"))
    d = json.load(open(f))
    d["at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - 7200))
    if strip_game:
        d.pop("game", None)
    json.dump(d, open(f, "w"))
    r = subprocess.run([sys.executable, "-c", VOID], env=env, capture_output=True, text=True)
    got = r.stdout.strip().splitlines()[-1:] or [r.stderr[-200:]]
    ok = got[0] == str(want_open)
    bad += not ok
    print(("PASS " if ok else "FAIL ") + what + ("" if ok else "  (open debts: %s, want %d)" % (got[0], want_open)))


case("ArchSmall's debt stands when only ArchBig relaunched", "b", 60, 9000, 1)
case("ArchSmall's debt is void when ArchSmall relaunched", "b", 9000, 60, 0)
case("ArchBig's debt stands when only ArchSmall relaunched", "a", 9000, 60, 1)
case("ArchBig's debt is void when ArchBig relaunched", "a", 60, 9000, 0)
case("a debt whose game's log cannot be read stands", "b", 60, None, 1)
case("a debt with no game (written before) is ArchBig's", "a", 60, 9000, 0, strip_game=True)
print("acceptance: %s" % ("GREEN" if not bad else "RED, %d of 6" % bad))
sys.exit(1 if bad else 0)
