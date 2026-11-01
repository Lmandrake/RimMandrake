#!/usr/bin/env python3
"""Selftest: the Test Pilot's reload rule (testpilot_reload.py). Every rule is checked on both sides of its line.

    python3 src/RimMandrake/rimflow/selftest_testpilot_reload.py
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import testpilot_reload as R                                            # noqa: E402

RULE = R.load_rule()
LIVE = {"game": "live", "useful_tests": 2, "launch_s": 22}
FAIL = []


def check(name, facts, verdict, rule):
    d = R.decide(dict(LIVE, **facts), RULE)
    ok = (d["verdict"], d["rule"]) == (verdict, rule)
    print("%s %s -> %s %s" % ("ok  " if ok else "FAIL", name, d["verdict"], d["rule"]))
    if not ok:
        FAIL.append(name)
    return d


limit_c, limit_e = RULE["max_acceptance_delay_s"]["cheap"], RULE["max_acceptance_delay_s"]["expensive"]
extra, thr = RULE["cheap_extra_tests"], RULE["cheap_max_launch_to_ready_s"]

check("a failure alone is no reload", {}, "HOLD", "HOLD")
check("cold start", {"game": "cold", "useful_tests": 0}, "RELOAD", "R0")
check("dead process", {"game": "dead"}, "RELOAD", "R1")
check("wedged, ladder not walked", {"game": "wedged"}, "HOLD", "LADDER")
check("wedged after the ladder", {"game": "wedged", "ladder_walked": True}, "RELOAD", "R1")
check("no useful test, reset restores", {"useful_tests": 0, "reset_restores": True}, "HOLD", "LADDER")
check("no useful test, no reset", {"useful_tests": 0}, "RELOAD", "R2")
check("cheap: one extra test short", {"repair_ready": True, "extra_done": extra - 1}, "HOLD", "HOLD")
check("cheap: extra tests run", {"repair_ready": True, "extra_done": extra}, "RELOAD", "R3")
check("repair, nothing useful left", {"repair_ready": True, "useful_tests": 0}, "RELOAD", "R3")
check("cheap: maximum delay", {"repair_ready": True, "waited_s": limit_c}, "RELOAD", "R3")
check("cheap: just under the delay", {"repair_ready": True, "waited_s": limit_c - 1}, "HOLD", "HOLD")
big = {"repair_ready": True, "launch_s": thr + 1, "extra_done": extra + 5, "waited_s": limit_c}
check("expensive: keeps going past the cheap drain", big, "HOLD", "HOLD")
check("expensive: maximum delay", dict(big, waited_s=limit_e), "RELOAD", "R3")
check("threshold itself is cheap", {"repair_ready": True, "launch_s": thr, "extra_done": extra}, "RELOAD", "R3")
d = check("unmeasured cost is never cheap", {"repair_ready": True, "launch_s": None, "extra_done": extra + 5},
          "HOLD", "HOLD")
if (d["cost_class"], d["cost_basis"]) != ("expensive", "UNMEASURED"):
    FAIL.append("unmeasured basis")

tool = os.path.join(HERE, "testpilot_reload.py")
base = [sys.executable, tool, "--item", "X_Y_Z", "--game", "live", "--useful-tests", "1"]
got = subprocess.run(base, capture_output=True, text=True)
if got.returncode or not got.stdout.startswith("HOLD rule=HOLD"):
    FAIL.append("cli hold")
if subprocess.run(base + ["--waited-s", "-1"], capture_output=True).returncode != 2:
    FAIL.append("cli accepted a negative time")
# The logged line must say the rule met and which rule file said so, and never carry the marker that restarts the count.
line = subprocess.run(base[:5] + ["dead", "--useful-tests", "1"], capture_output=True, text=True).stdout
if not re.search(r"RELOAD rule=R1 .*rule_sha=[0-9a-f]{12}", line) or "TESTPILOT_SAT" in R.MARKER:
    FAIL.append("cli reload line: %r" % line)
agent = open(os.path.join(HERE, "..", "..", "..", ".claude", "agents", "rm-testpilot.md"), encoding="utf-8").read()
if "testpilot_reload.py" not in agent:
    FAIL.append("rm-testpilot.md does not name the rule")

print("FAIL: %s" % FAIL if FAIL else "selftest_testpilot_reload: all pass")
sys.exit(1 if FAIL else 0)
