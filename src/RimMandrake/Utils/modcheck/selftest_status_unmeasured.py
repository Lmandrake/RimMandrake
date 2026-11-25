#!/usr/bin/env python3
"""selftest_status_unmeasured.py — a modcheck status entry tells a measured failure from a run that measured nothing
(RIMMANDRAKE_SPLIT_RED_FROM_UNMEASURED_STATUS_ENTRY_LIES).

Before: status.verdict_for(False, None) answered RED for a real FAIL, for a suite that recorded no component, and for
a run whose known-good gate skipped a chain, so modcheck_status.json could not tell a defect from an unrun suite.
Now: RED is a measured failure; UNMEASURED (with the cause in the entry's `unmeasured` field) is a run that failed
nothing but could not measure it all; REFUSED stays the visual floor. A4: nothing that read non-GREEN reads GREEN.
Offline: a temp registry, no game.
"""
import itertools
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
FAILS = []


def check(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def old_verdict_for(status, all_green, walk, refused="", reviewed=False):
    """The base commit's verdict_for, verbatim in behaviour: the A4 reference."""
    if refused:
        return "REFUSED"
    if not all_green:
        return "RED"
    present, state = status._checklist_state(walk)
    if present and state != "VALIDATED":
        return "DRAFT-CHECKLIST"
    if present and not reviewed:
        return "PENDING-OWNER-REVIEW"
    return "GREEN"


def comp(name, verdict, execution="ran"):
    return {"name": name, "verdict": verdict, "execution": execution}


def main():
    import status

    # the three causes the runner used to collapse into one RED
    nothing = {"chains": [{"name": "a", "components": []}], "all_green": False}
    not_run = {"chains": [{"name": "a", "components": [comp("x", "NOT_RUN", "not_run")]}], "all_green": False}
    skipped = {"chains": [{"name": "a", "components": [comp("x", "PASS")]}], "all_green": True,
               "gate": {"skipped": ["b", "c"]}}
    failed = {"chains": [{"name": "a", "components": [comp("x", "FAIL")]}], "all_green": False,
              "gate": {"skipped": ["b"]}}
    passed = {"chains": [{"name": "a", "components": [comp("x", "PASS")]}], "all_green": True, "gate": {"skipped": []}}
    c_nothing, c_not_run = status.unmeasured_cause(nothing), status.unmeasured_cause(not_run)
    c_skip, c_fail, c_pass = (status.unmeasured_cause(s) for s in (skipped, failed, passed))
    check("no component" in c_nothing and "no component" in c_not_run,
          "A1 a suite with no measured component has a cause (%r)" % c_nothing)
    check("b" in c_skip and "c" in c_skip and "gate" in c_skip, "A2 a gate skip names the skipped chains (%r)" % c_skip)
    check(c_fail == "", "A3 a measured FAIL has no unmeasured cause, even beside a gate skip: it stays RED")
    check(c_pass == "", "an all-PASS run with nothing skipped has no unmeasured cause")
    got = {k: status.verdict_for(s["all_green"] and not (s.get("gate") or {}).get("skipped"), None, "", False,
                                 status.unmeasured_cause(s))
           for k, s in (("nothing", nothing), ("skipped", skipped), ("failed", failed))}
    check(got == {"nothing": "UNMEASURED", "skipped": "UNMEASURED", "failed": "RED"},
          "A1/A2/A3 nothing measured and a gate skip read UNMEASURED, a FAIL reads RED (%s)" % got)
    check(status.verdict_for(False, None, "the floor", False, "x") == "REFUSED", "A3 the visual floor stays REFUSED")

    # A4 over every combination of the inputs: the new answer is GREEN only where the old one was, and never with a
    # cause; with no cause it is exactly the old answer
    tmp = tempfile.mkdtemp()
    walks = [None]
    for state in ("DRAFT", "VALIDATED"):
        p = os.path.join(tmp, "walk_%s.md" % state)
        with open(p, "w") as f:
            f.write("# walk\n\n## north star\n\nChecklist state: %s\n\n- a bar\n" % state)
        walks.append(p)
    bad = []
    for ag, w, ref, rev, cause in itertools.product((True, False), walks, ("", "floor"), (True, False), ("", "cause")):
        new, old = status.verdict_for(ag, w, ref, rev, cause), old_verdict_for(status, ag, w, ref, rev)
        if (new == "GREEN" and (old != "GREEN" or cause)) or (not cause and new != old):
            bad.append((ag, os.path.basename(w or "-"), ref, rev, cause, old, new))
    check(not bad, "A4 over %d combinations: no new GREEN, and no change without a cause (%s)" % (2 * 3 * 2 * 2 * 2, bad[:3]))
    states = {old_verdict_for(status, True, w, "", r) for w in walks for r in (True, False)}
    check(len(states) >= 2, "the A4 sweep reaches more than one checklist state (%s): the walks parse" % sorted(states))

    # record_run stores the answer and its cause; a measured run stores no cause
    real = status.LOG_PATH
    status.LOG_PATH = os.path.join(tmp, "modcheck_status.json")
    try:
        mod_dir = os.path.join(tmp, "Mod")
        os.makedirs(mod_dir)
        e = status.record_run("Mod", mod_dir, "Mod@1", False, unmeasured=c_nothing)
        check(e["status"] == "UNMEASURED" and e["unmeasured"] == c_nothing, "record_run stores UNMEASURED and its cause")
        e = status.record_run("Mod", mod_dir, "Mod@2", False)
        check(e["status"] == "RED" and e["unmeasured"] is None, "a measured failure stores RED with no cause")
        e = status.record_run("Mod", mod_dir, "Mod@3", False, extra={"unmeasured": "forged", "status": "GREEN"})
        check(e["status"] == "RED" and e["unmeasured"] is None, "extra can never override the verdict or its cause")
        stored = json.load(open(status.LOG_PATH))["Mod"]
        check(stored["run_id"] == "Mod@3", "the registry file holds the last entry")
        status.record_run("Mod", mod_dir, "Mod@4", False, unmeasured=c_skip)
        line = status.check("Mod", mod_dir)
        check(line.startswith("UNMEASURED") and "b, c" in line, "modcheck status names the cause (%s)" % line)
    finally:
        status.LOG_PATH = real

    # env_verify_check: an UNMEASURED run did not prove the environment, and is not a FAIL of it either
    import env_verify_check as EV
    import runner
    saved = (status.load, status.mod_hash, runner.find_mod_dir, EV.env_commit_time)
    try:
        status.mod_hash = lambda d: "h"
        runner.find_mod_dir = lambda m: tmp
        EV.env_commit_time = lambda d: 1
        for st, want in (("UNMEASURED", EV.UNMEASURED), ("RED", EV.PASS), ("REFUSED", EV.FAIL)):
            status.load = lambda st=st: {"M": {"hash": "h", "ts": 10, "status": st, "run_id": "M@1",
                                               "unmeasured": "no component recorded" if st == "UNMEASURED" else None}}
            check(EV.main(["M"]) == want, "env_verify_check: a %s entry exits %d" % (st, want))
    finally:
        status.load, status.mod_hash, runner.find_mod_dir, EV.env_commit_time = saved

    print("%d check(s) failed" % len(FAILS) if FAILS else "all checks passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
