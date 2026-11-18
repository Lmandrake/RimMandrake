#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_BIND_CERTIFICATE_TO_OFFLINE_DECIDERS_NO_OP_PASSED (filed by the GimmeSomeSlack blind
cycle 5 judge, 2026-11-16, from two planted faults the pre-judgement certificate let through: an offline bar with no
decider, and a decider whose command no longer runs its file). Written by the filing seat; the builder does not edit it.

    python3 src/RimMandrake/rimflow/acceptance/guard_certificate_binds_offline_bars_accept.py      # "PASS 8/8" when built

THE CONTRACT IT ADDS to `judge_certificate.certify(root, mod)` (rows as in guard_judge_certificate_accept.py):
  decided     a bar whose proves_at is offline ("2" or "4-5") with offline_decides missing or empty is REFUSED (clause
              "decided": nothing decides it, so it would pass on no run at all); an offline decider a bar names that is
              not in the same bar's `decides` is REFUSED (clause "decided": the table's rule passes a bar on `decides`).
              A bar that proves at stage 6 or later with no offline decider is not refused.
  ran_on_this_build  run_offline records the command it ran in runs_today["command"]; when that is recorded and differs
              from the test's command now, REFUSED (the build hashes files, not the command, so a command swapped for a
              no-op after a green run kept its stamp). A stamp with no recorded command is read as before.
Exit 0 when every check passes.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.dirname(HERE)
sys.path.insert(0, RIMFLOW)
MOD = "FixtureMod"
RESULTS = []


def check(ok, what):
    RESULTS.append(bool(ok))
    print(("ok    " if ok else "FAIL  ") + what)


def tpath(root):
    return os.path.join(root, "design/concepts", MOD, "version/test_table.json")


def fixture(root, bars, command=None):
    os.makedirs(os.path.join(root, "design/concepts", MOD, "version"), exist_ok=True)
    os.makedirs(os.path.join(root, "src/records"), exist_ok=True)
    open(os.path.join(root, "src/records/r.txt"), "w").write("x\n")
    open(os.path.join(root, "src/t_good.py"), "w").write("import sys\nprint('3/3 checks passed')\nsys.exit(0)\n")
    tests = {"T_GOOD": {"id": "T_GOOD", "kind": "offline", "stage": "4-5", "file": "src/t_good.py", "reads": [],
                        "command": "%s src/t_good.py" % sys.executable},
             "REC": {"id": "REC", "kind": "offline", "stage": "4-5", "file": "src/records/", "reads": [],
                     "command": "%s -c 'print(1)'" % sys.executable}}
    table = {"mod": MOD, "version": "0.1.0", "tests": tests, "bars": bars}
    json.dump(table, open(tpath(root), "w"), indent=1)
    import judge_certificate as JC
    JC.run_offline(root, MOD)                       # stamps runs_today with this build (the real path to pass)
    JC.grandfather(root, MOD)                       # red_seen (a later ticket) is not this test's subject: it only warns
    if command is not None:                         # swap the command AFTER the green stamped run: the planted fault
        t = json.load(open(tpath(root)))
        t["tests"]["T_GOOD"]["command"] = command
        json.dump(t, open(tpath(root), "w"), indent=1)
    return JC


def refused(v, clause, bar=None):
    return [r for r in v.get("rows") or [] if r.get("status") == "REFUSED" and r.get("clause") == clause
            and (bar is None or r.get("bar") == bar)]


def run(bars, command=None):
    with tempfile.TemporaryDirectory(prefix="cert_bind_") as root:
        JC = fixture(root, bars, command)
        return JC.certify(root, MOD)


def main():
    good = {"id": "bar_ok", "proves_at": "4-5", "decides": ["T_GOOD"], "offline_decides": ["T_GOOD"]}
    v = run([good])
    check(v["ok"] and not refused(v, "decided"), "control: an offline bar decided by a green, named test is certified")
    v = run([good, {"id": "bar_empty", "proves_at": "4-5", "decides": [], "offline_decides": []}])
    check(not v["ok"] and refused(v, "decided", "bar_empty"), "an offline bar (4-5) with offline_decides [] is REFUSED, clause decided")
    v = run([{"id": "bar_missing", "proves_at": "2", "decides": ["T_GOOD"]}])
    check(not v["ok"] and refused(v, "decided", "bar_missing"), "an offline bar (2) with no offline_decides key is REFUSED")
    v = run([{"id": "bar_split", "proves_at": "4-5", "decides": [], "offline_decides": ["T_GOOD"]}])
    check(not v["ok"] and refused(v, "decided", "bar_split"), "an offline decider missing from the bar's decides is REFUSED")
    v = run([{"id": "bar_late", "proves_at": "6", "decides": ["sc_x"], "offline_decides": []}])
    check(v["ok"] and not refused(v, "decided"), "control: a stage-6 bar with no offline decider is not refused")
    v = run([good], command="true")
    check(not v["ok"] and refused(v, "ran_on_this_build", "bar_ok"), "a decider whose command was swapped for 'true' after its green stamped run is REFUSED, clause ran_on_this_build")
    r = refused(v, "ran_on_this_build", "bar_ok")
    check(bool(r) and all(x.get("smallest_fix") and x.get("would_pass") and x.get("observed") for x in r),
          "the refusal carries observed, would_pass and smallest_fix")
    with tempfile.TemporaryDirectory(prefix="cert_bind_") as root:
        JC = fixture(root, [good])
        rt = json.load(open(tpath(root)))["tests"]["T_GOOD"]["runs_today"]
        check(rt.get("command") == "%s src/t_good.py" % sys.executable, "run_offline records the command it ran in runs_today")
    n = len(RESULTS)
    print("PASS %d/%d" % (sum(RESULTS), n) if all(RESULTS) else "FAIL %d/%d" % (sum(RESULTS), n))
    return 0 if all(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
