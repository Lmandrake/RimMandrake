#!/usr/bin/env python3
"""testpilot_reload.py -- may the Test Pilot reload the game now? The burden of proof, as a script.

Owner, 2026-10-29: "there would be a Burden of proof required to trigger a reload." By card the same day: the pilot
decides by a written rule, and each reload logs the rule it met. Design: testpilot_merged_2026-10-29.md M1. Numbers:
testpilot_reload_rule.json. This is the permanent sitting agent's rule (.claude/agents/rm-testpilot.md), not the arena
trio lane's (src/RimMandrake/Utils/arena/testpilot.py), which is a trial arm with its own rule file.

Checked in this order; the first that holds decides:
  R0 no game is up: a cold start.
  LADDER a wedged game walks reconnect, reload a save, restage, hold first. None of those is a reload.
  R1 the process is dead, or the ladder was walked and the game is still wedged.
  R2 no useful valid test remains on what is loaded, and resetting state would not restore one.
  R3 a repair is ready and its drain is spent. Cheap reload: a few more unrelated tests, then go. Expensive reload: keep
     going while a useful test remains. Both end at the maximum acceptance delay, so a repair cannot wait forever.
Anything else is HOLD: keep testing. A useful test is one that can change an acceptance decision or catch a defect
class not yet covered. A test that passes reliably on untouched ground is not useful and is never counted in
--useful-tests, so the rule cannot turn into exhaustive testing. A reload cost nobody measured counts as expensive.

    python3 src/RimMandrake/rimflow/testpilot_reload.py --item <ID> --game live --useful-tests 2 --repair-ready \
        --launch-s 22 --extra-done 3 --waited-s 200 --log
--log stamps `rimflow note <ID> --text "TESTPILOT_RELOAD: ..."` when the verdict is RELOAD. Exit 0 either way, 2 on bad
input. The marker differs from TESTPILOT_SAT on purpose: a reload does not restart the Test Pilot rule's count.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RULE_FILE = os.path.join(HERE, "testpilot_reload_rule.json")
MARKER = "TESTPILOT_RELOAD"


def load_rule(path=RULE_FILE):
    with open(path, "rb") as f:
        raw = f.read()
    rule = json.loads(raw.decode("utf-8"))
    rule["sha256"] = hashlib.sha256(raw).hexdigest()
    return rule


def cost_class(launch_s, rule):
    """The class and its basis. An unmeasured cost is never called cheap by default."""
    if launch_s is None:
        return rule["unmeasured_cost_class"], "UNMEASURED"
    return ("cheap" if launch_s <= rule["cheap_max_launch_to_ready_s"] else "expensive"), "measured"


def decide(f, rule):
    """f: game (cold|dead|wedged|live), ladder_walked, useful_tests, reset_restores, repair_ready, extra_done, waited_s,
    launch_s. -> {verdict: RELOAD|HOLD, rule, why, cost_class, cost_basis}. Pure."""
    cls, basis = cost_class(f.get("launch_s"), rule)

    def out(verdict, name, why):
        return {"verdict": verdict, "rule": name, "why": why, "cost_class": cls, "cost_basis": basis}

    game = f["game"]
    if game == "cold":
        return out("RELOAD", "R0", "no game is up")
    if game == "dead":
        return out("RELOAD", "R1", "the process is dead")
    if game == "wedged":
        if not f.get("ladder_walked"):
            return out("HOLD", "LADDER", "walk reconnect, reload a save, restage, hold; none of those is a reload")
        return out("RELOAD", "R1", "still wedged after the ladder")
    useful = f["useful_tests"]
    if useful <= 0 and not f.get("repair_ready"):
        if f.get("reset_restores"):
            return out("HOLD", "LADDER", "no useful test on this state, but a state reset restores one: reset, no reload")
        return out("RELOAD", "R2", "no useful valid test remains and a state reset would not restore one")
    if f.get("repair_ready"):
        limit = rule["max_acceptance_delay_s"][cls]
        if useful <= 0:
            return out("RELOAD", "R3", "repair ready, no useful test left")
        if f.get("waited_s", 0) >= limit:
            return out("RELOAD", "R3", "repair ready, waited the maximum %ds for a %s reload" % (limit, cls))
        if cls == "cheap" and f.get("extra_done", 0) >= rule["cheap_extra_tests"]:
            return out("RELOAD", "R3", "repair ready, cheap reload, %d extra tests run" % rule["cheap_extra_tests"])
    return out("HOLD", "HOLD", "%d useful test(s) remain on the running game" % useful)


def main(argv=None):
    ap = argparse.ArgumentParser(description="May the Test Pilot reload now? Burden of proof, by written rule.")
    ap.add_argument("--item", required=True)
    ap.add_argument("--game", required=True, choices=("cold", "dead", "wedged", "live"))
    ap.add_argument("--useful-tests", type=int, required=True,
                    help="tests left that can change an acceptance decision or catch an uncovered defect class")
    ap.add_argument("--ladder-walked", action="store_true")
    ap.add_argument("--reset-restores", action="store_true", help="a save reload or restage would restore a useful test")
    ap.add_argument("--repair-ready", action="store_true", help="a fix that needs a reload is built and waiting")
    ap.add_argument("--extra-done", type=int, default=0, help="unrelated tests run since the repair was ready")
    ap.add_argument("--waited-s", type=float, default=0, help="seconds since the repair was ready")
    ap.add_argument("--launch-s", type=float, help="MEASURED launch-to-ready for this list; omit if nobody measured it")
    ap.add_argument("--log", action="store_true", help="on RELOAD, stamp the rule met on the item")
    a = ap.parse_args(argv)
    if a.useful_tests < 0 or a.extra_done < 0 or a.waited_s < 0 or (a.launch_s is not None and a.launch_s <= 0):
        ap.error("counts and times cannot be negative, and a measured launch takes time")
    rule = load_rule()
    d = decide(vars(a), rule)
    line = "%s: rule=%s why=%s cost=%s (%s, %s s) useful=%d rule_sha=%s" % (
        MARKER, d["rule"], d["why"], d["cost_class"], d["cost_basis"], a.launch_s, a.useful_tests, rule["sha256"][:12])
    print("%s %s" % (d["verdict"], line.split(": ", 1)[1]))
    if a.log and d["verdict"] == "RELOAD":
        return subprocess.call([sys.executable, os.path.join(HERE, "cli.py"), "note", a.item, "--text", line,
                                "--why", "Test Pilot reload, written rule met"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
