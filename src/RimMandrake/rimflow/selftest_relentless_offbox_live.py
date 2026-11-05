#!/usr/bin/env python3
"""relentless_live_evidence, the supervisor offbox adapter for a Judge blind on the live round's evidence
(CHECKER_REACH_FIX_WINDOWS_BUILD_STILL_DARK gen 3; instance UNPROVEN_LIVE_LEGS_TRIAGE_1, whose Judge read
'ls -ld /home/mandrake/rm/relentless/live -> Permission denied'). Rows, on a fixture live folder under a temp HOME:
  L1 the adapter is a no-shell python3 -I script whose only slot is {item}; {item} is a supervisor value of id shape,
     and a value of another shape (a path, a lower-case word) refuses the reading, nothing half-filled runs;
  L2 the check launch and the reach probe both pass the item id;
  L3 run as the supervisor runs it, it prints the item's .criteria, its runs.jsonl rows and its logs' tails, exit 0;
  L4 it never prints another item's runs or logs, nor the round lock;
  L5 an absent live folder exits 1, so the reach probe cannot pass on an empty reading."""
import inspect
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import relentless as R                  # noqa: E402
import relentless_reachfix as RF        # noqa: E402
import relentless_wall as W             # noqa: E402

FAILS = []
ITEM = "UNPROVEN_LIVE_LEGS_TRIAGE_1"
OTHER = "ACC_BIOMES_FIXES_LIVE_RERUN_1"
RULES = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "relentless_rules.json")))


def ok(cond, name):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


def adapter():
    return W.adapters(RULES)["relentless_live_evidence"]


def t_slot():
    a = adapter()
    slots = {s for t in a["argv"] for s in W._SLOT.findall(t)}
    ok(a["argv"][:3] == ["python3", "-I", "-c"] and slots == {"item"}, "L1 no-shell script, only slot {item}: %s" % slots)
    argv, why = W.fill_argv(a["argv"], {"item": ITEM})
    ok(argv is not None and argv[-1] == ITEM, "L1 {item} fills with the item id: %s" % why)
    for bad in ("/home/mandrake/rm/relentless/store", "x", "A B", "", None):
        argv, why = W.fill_argv(a["argv"], {"item": bad})
        ok(argv is None and why, "L1 {item}=%r refuses: %s" % (bad, why))


def t_passed():
    src = inspect.getsource(R)
    ok('"item": st["item"]})' in src and "offbox_readings(fx, st[\"contract\"]" in src,
       "L2 the check launch passes the item to the offbox readings")
    ok('"item": owner}' in inspect.getsource(RF.sweep), "L2 the reach probe passes the owner item")


def run(home):
    old = os.environ.get("HOME")
    os.environ["HOME"] = home
    try:
        argv, why = W.fill_argv(adapter()["argv"], {"item": ITEM, "sha": "0" * 40, "repo": "/r"})
        return R.run_bounded("relentless_live_evidence", dict(adapter(), argv=argv), 60)
    finally:
        os.environ["HOME"] = old


def t_reads_fixture():
    with tempfile.TemporaryDirectory() as home:
        d = os.path.join(home, "rm", "relentless", "live")
        os.makedirs(d)
        with open(os.path.join(d, ITEM + ".criteria"), "w") as f:
            f.write("A3 L2: Cauldron bars pass\n")
        with open(os.path.join(d, "runs.jsonl"), "w") as f:
            for it, c, o in ((ITEM, "A3", "FAIL"), (OTHER, "A1", "PASS_SECRET"), (ITEM, "A4", "FAIL")):
                f.write(json.dumps({"at": "2026-11-04T06:12:12Z", "item": it, "criterion": c, "level": "L2", "outcome": o,
                                    "sha": "f3fd31f84506", "proof_exit": 1,
                                    "log": os.path.join(d, "%s-%s-x.log" % (it, c))}) + "\n")
        with open(os.path.join(d, ITEM + "-A3-20261104T061212Z.log"), "w") as f:
            f.write("$ python3 northstar_bar_proof.py --mod Cauldron\n" + "".join("line %d\n" % n for n in range(60))
                    + "BAD water.water_letter_toggle_off -> UNMEASURED\n")
        with open(os.path.join(d, OTHER + "-A1-x.log"), "w") as f:
            f.write("OTHER_ITEM_LOG\n")
        with open(os.path.join(d, "round.lock"), "w") as f:
            f.write("LOCK_TEXT\n")
        got = run(home)
        out = got.get("out") or ""
        ok(got.get("exit") == 0, "L3 exit 0: %s" % got.get("exit"))
        ok("A3 L2: Cauldron bars pass" in out and "criterion=A3" in out and "criterion=A4" in out
           and "water_letter_toggle_off -> UNMEASURED" in out and "northstar_bar_proof.py --mod Cauldron" in out,
           "L3 criteria, both runs, the log's head and tail: %s" % out[-120:])
        ok("line 5\n" not in out and "...\n" in out, "L3 a long log is cut to head and tail")
        ok("PASS_SECRET" not in out and "OTHER_ITEM_LOG" not in out and "LOCK_TEXT" not in out,
           "L4 no other item's runs or logs, no round lock")
    with tempfile.TemporaryDirectory() as home:
        got = run(home)
        ok(got.get("exit") == 1, "L5 an absent live folder exits 1: %s" % got.get("exit"))


def main():
    for t in (t_slot, t_passed, t_reads_fixture):
        t()
    print("%d failed" % len(FAILS) if FAILS else "all ok")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
