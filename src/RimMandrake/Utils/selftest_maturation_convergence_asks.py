#!/usr/bin/env python3
"""selftest_maturation_convergence_asks.py: the promises of maturation_convergence.py's Needs Conductor asks.

Page design/specs/2026-11-27-maturation-convergence-asks/boundary.md: one test per promise, of its name. Every fixture
lives in a temp tree; nothing in design/ or src/ is read or written.
"""

import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import maturation_convergence as MC  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  -> %s" % str(detail)[:600]))
    if not ok:
        FAILS.append(name)


def w(root, rel, data):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(data if isinstance(data, str) else json.dumps(data))


def rnd(judge, gaps, tags):
    return {"judge": judge, "at": "2026-11-15T00:00:00Z", "verdict": "not_covered", "gaps": gaps, "tags": tags}


RISING = {"coverage_rounds": [rnd("j1", 3, {"first": 3}), rnd("j2", 5, {"unfixed": 2, "late": 3}),
                              rnd("j3", 8, {"unfixed": 4, "changed": 4})]}
FALLING = {"coverage_rounds": [rnd("j1", 6, {"first": 6}), rnd("j2", 2, {"unfixed": 2})]}
HOLD = os.path.join("src", "RimMandrake", "rimflow", "mod_owner_hold.json")


def tree(mods=("Free", "Held", "Passed"), hold=None, record=None):
    """A temp root: each named mod diverges at Stage 3; Calm converges. hold / record: the hold file's and Passed's
    stage_record.json text or data (None: not written)."""
    root = tempfile.mkdtemp(prefix="maturation_convergence_asks_")
    for m in mods:
        w(root, os.path.join(MC.CONCEPTS, m, "stage.json"), RISING)
    w(root, os.path.join(MC.CONCEPTS, "Calm", "stage.json"), FALLING)
    if hold is not None:
        w(root, HOLD, hold)
    if record is not None:
        w(root, os.path.join(MC.CONCEPTS, "Passed", "version", "stage_record.json"), record)
    return root


def lines_by_mod(root):
    return sorted(x.split(" ", 1)[0] for x in MC.needs_lines(MC.read_all(root)))


def t_a_diverging_stage_asks_the_conductor():
    root = tree(mods=("Free",))
    try:
        lines = MC.needs_lines(MC.read_all(root))
        check("a-diverging-stage-asks-the-conductor: one line, for Free's Stage 3 only",
              len(lines) == 1 and lines[0].startswith("Free Stage 3 (Offline build) DIVERGING"), lines)
        check("a-diverging-stage-asks-the-conductor: the line carries open and new by round",
              lines and "open 3 -> 5 -> 8, new 3 -> 3 -> 4" in lines[0], lines)
        check("a-diverging-stage-asks-the-conductor: it pauses nothing and changes no bar",
              lines and "pauses nothing and changes no bar" in lines[0], lines)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def t_a_passed_or_held_mod_asks_nothing():
    root = tree(hold={"holds": [{"mod": "Held", "date": "2026-11-16", "said": "hold it"}]},
                record={"mod": "Passed", "version": "0.2.0", "stage": "passed"})
    try:
        d = MC.read_all(root)
        check("a-passed-or-held-mod-asks-nothing: only Free asks", lines_by_mod(root) == ["Free"], MC.needs_lines(d))
        check("a-passed-or-held-mod-asks-nothing: quiet names each with its reason",
              d["quiet"] == {"Held": "held by the owner", "Passed": "version 0.2.0 passed"}, d["quiet"])
        check("a-passed-or-held-mod-asks-nothing: their reading is still there",
              all(d["mods"][m]["3"]["verdict"] == MC.DIV for m in ("Held", "Passed"))
              and {r[0] for r in MC.table_rows(d)} >= {"Held", "Passed"}, d["mods"].get("Held"))
        w(root, os.path.join(MC.CONCEPTS, "Passed", "version", "stage_record.json"),
          {"mod": "Passed", "version": "0.3.0", "stage": "offline_build"})
        check("a-passed-or-held-mod-asks-nothing: a next version that runs asks again",
              lines_by_mod(root) == ["Free", "Passed"], MC.needs_lines(MC.read_all(root)))
    finally:
        shutil.rmtree(root, ignore_errors=True)


def t_an_unreadable_record_quiets_nothing():
    everyone = ["Free", "Held", "Passed"]
    for label, hold, record in (("missing", None, None), ("empty", "", ""), ("not JSON", "{holds", "{stage"),
                                ("wrong shape", [{"mod": "Held"}], ["passed"]),
                                ("holds not a list", {"holds": {"mod": "Held"}}, {"stage": ["passed"]})):
        root = tree(hold=hold, record=record)
        try:
            got = lines_by_mod(root)
            check("an-unreadable-record-quiets-nothing: %s hold file and stage record" % label, got == everyone, got)
        finally:
            shutil.rmtree(root, ignore_errors=True)


def t_the_tick_reading_carries_the_asks():
    root = tree(mods=("Free",))
    try:
        rd = MC.annotate_reading(root, {"needs_conductor": ["earlier line"], "other": 1})
        nc = rd.get("needs_conductor") or []
        check("the-tick-reading-carries-the-asks: the line follows the lines already there",
              len(nc) == 2 and nc[0] == "earlier line" and nc[1].startswith("Free Stage 3"), nc)
        check("the-tick-reading-carries-the-asks: convergence per mod and stage",
              rd.get("convergence", {}).get("Free", {}).get("3", {}).get("verdict") == MC.DIV
              and rd["convergence"]["Calm"]["3"]["verdict"] == MC.CONV, rd.get("convergence"))
        real = MC.read_all

        def broken(_root=None):
            raise RuntimeError("planted")
        MC.read_all = broken
        try:
            rd2 = MC.annotate_reading(root, {"needs_conductor": ["kept"], "other": 1})
        finally:
            MC.read_all = real
        check("the-tick-reading-carries-the-asks: a failed reading names itself and keeps the rest",
              rd2.get("convergence_error") == "RuntimeError: planted" and rd2.get("needs_conductor") == ["kept"]
              and rd2.get("other") == 1 and "convergence" not in rd2, rd2)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main():
    t_a_diverging_stage_asks_the_conductor()
    t_a_passed_or_held_mod_asks_nothing()
    t_an_unreadable_record_quiets_nothing()
    t_the_tick_reading_carries_the_asks()
    print("ALL PASS" if not FAILS else "FAILED: %s" % ", ".join(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
