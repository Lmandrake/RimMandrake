#!/usr/bin/env python3
"""Offline selftest for mission_fixture_probe.py's judging (MISSION_PROBE_WIRE_PLAYER_MISSIONS_CHAIN). Reds on: a blind tank
baseline (None) passing; a failed fixture op passing; an UNMEASURED report verdict passing; the MISSION_LIVE rows the
player_missions chain reads not being exactly the rows the probe can write."""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FW = os.path.dirname(HERE)
for _p in (HERE, FW, os.path.join(os.path.dirname(FW), "Utils")):
    sys.path.insert(0, _p)
import mission_fixture_probe as P  # noqa: E402

FAILS = []


def ok(c, m):
    print("%s %s" % ("PASS" if c else "FAIL", m))
    if not c:
        FAILS.append(m)


good = {"fixture": [{"tool": "a", "ok": True}], "tank_baseline": {"T1": 0}}
r = dict((x[0], x) for x in P.judge_start("chain", 0, good))
ok(r["PM_chain_fixture"][1] == "PASS" and r["PM_chain_tank_baseline_read"][1] == "PASS", "a clean chain start passes")
r = dict((x[0], x) for x in P.judge_start("chain", 0, dict(good, tank_baseline=None)))
ok(r["PM_chain_tank_baseline_read"][1] == "FAIL", "a None tank baseline FAILS")
r = dict((x[0], x) for x in P.judge_start("canal", 1, {"fixture": [{"tool": "research_finish_project", "ok": False}]}))
ok(r["PM_canal_fixture"][1] == "FAIL" and "PM_chain_tank_baseline_read" not in r, "a failed fixture op FAILS; canal has no tank row")
ok(P.judge_start("pit", 1, None)[0][1] == "UNMEASURED", "no run.json is UNMEASURED")
ok(P.judge_report("pit", {"verdict": "UNMEASURED"})[1] == "FAIL", "an UNMEASURED report verdict FAILS (blind read)")
ok(P.judge_report("pit", {"verdict": "FAIL"})[1] == "PASS" and P.judge_report("pit", None)[1] == "FAIL",
   "a measured FAIL verdict is a readable game; no report is blind")
spec = importlib.util.spec_from_file_location("fw_validation_probe", os.path.join(FW, "validation.py"))
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
writable = set()
for m in P.MISSIONS:
    writable |= {x[0] for x in P.judge_start(m, 0, good)} | {P.judge_report(m, {"verdict": "PASS"})[0]}
ok({x[0] for x in v.MISSION_LIVE} == writable, "MISSION_LIVE == the rows the probe writes: %s" % sorted(writable ^ {x[0] for x in v.MISSION_LIVE}))
ok("mission_fixture_result_*.json" in v.DRIVER_RESULTS, "the chain reads mission_fixture_result_*.json")
print("RESULT: %s" % ("FAIL" if FAILS else "PASS"))
sys.exit(1 if FAILS else 0)
