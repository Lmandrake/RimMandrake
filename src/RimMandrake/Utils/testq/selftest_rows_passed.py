#!/usr/bin/env python3
"""Selftest for testq/rows_passed.py: each input kind gives its own answer, and a missing queue is UNMEASURED."""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "rows_passed.py")
FAILS = []


def ok(cond, what, got=None):
    print(("PASS  " if cond else "FAIL  ") + what + ("" if cond or got is None else "   got: %r" % (got,)))
    if not cond:
        FAILS.append(what)


def rec(jid, mod, sub, outcome, rows):
    return {"job": {"id": jid, "mod": mod, "submitted": sub},
            "result": {"outcome": outcome, "rows": [{"chain": c, "row": r, "verdict": v} for c, r, v in rows]}}


def run(done, *args):
    env = dict(os.environ, TESTQ_DONE_DIR=done)
    p = subprocess.run([sys.executable, TOOL] + list(args), capture_output=True, text=True, env=env)
    return p.returncode, p.stdout.strip()


def main():
    good = [("phrikite_desert", "phrikite_defs_loaded", "PASS"), ("phrikite_desert", "phrikite_only_in_desert", "PASS")]
    cases = {
        "J1": rec("J1", "UtinniPatches", "2026-11-14T13:00:00Z", "DONE", good),               # before SINCE
        "J2": rec("J2", "UtinniPatches", "2026-11-27T00:00:00Z", "DONE",
                  [("phrikite_desert", "phrikite_defs_loaded", "FAIL")] + good[1:]),
        "J3": rec("J3", "Armoury", "2026-11-27T01:00:00Z", "DONE", good),                     # wrong mod
        "J4": rec("J4", "UtinniPatches", "2026-11-27T02:00:00Z", "INVALID", good),             # did not measure
        "J5": rec("J5", "UtinniPatches", "2026-11-27T03:00:00Z", "DONE",
                  [("phrikite_desert", "phrikite_defs_loaded", "PASS"),
                   ("phrikite_desert", "phrikite_only_in_desert", "UNMEASURED")]),
    }
    since = "2026-11-26T17:00:00Z"
    with tempfile.TemporaryDirectory() as d:
        for jid, r in cases.items():
            with open(os.path.join(d, jid + ".json"), "w") as f:
                json.dump(r, f)
        rc, out = run(d, "UtinniPatches", since, "phrikite_desert")
        ok(rc == 1 and "UNMEASURED" in out, "a FAIL, an INVALID run, an UNMEASURED row, an old run and another mod: no PASS",
           (rc, out))
        rc, out = run(d, "UtinniPatches", since, "phrikite_desert/phrikite_defs_loaded")
        ok(rc == 0 and "J5" in out, "one row selected: the newer run that passed it counts", (rc, out))
        rc, out = run(d, "UtinniPatches", since, "zersium_forge")
        ok(rc == 1 and "no row zersium_forge" in out, "a chain no run carried: FAIL naming it", (rc, out))
        rc, out = run(d, "UtinniPatches", "2026-11-28T00:00:00Z", "phrikite_desert")
        ok(rc == 1 and "no done UtinniPatches job" in out, "nothing since SINCE: FAIL, said so", (rc, out))
        with open(os.path.join(d, "J6.json"), "w") as f:
            json.dump(rec("J6", "UtinniPatches", "2026-11-27T04:00:00Z", "DONE", good), f)
        rc, out = run(d, "UtinniPatches", since, "phrikite_desert")
        ok(rc == 0 and "J6" in out, "a run with every row PASS: PASS naming its job", (rc, out))
        with open(os.path.join(d, "broken.json"), "w") as f:
            f.write("{not json")
        rc, out = run(d, "UtinniPatches", since, "phrikite_desert")
        ok(rc == 0, "a record mid-write is skipped, not fatal", (rc, out))
    rc, out = run("/nonexistent/testq/done", "UtinniPatches", since, "phrikite_desert")
    ok(rc == 2 and out.startswith("UNMEASURED"), "no queue on this host: UNMEASURED, exit 2", (rc, out))
    print("RESULT: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
