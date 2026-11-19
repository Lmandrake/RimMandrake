#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_ANNOTATE_FOLD_MEMORY_BESIDE_STANDING_WORK_COVER (DESIGN DECISION 2026-11-18 on
RIMMANDRAKE_LET_FOLD_MEMORY_KEEP_THE_WORK_COVER): in findings_fold.latest_decision a `memory` decision made while a
cover decision (findings_fold_rules.json `cover_kinds`: work, merge, route, item) stands on the same signature ANNOTATES it: the standing decision is still the one
returned (same as/into/ts, so `covering` and the outcome clock are unchanged) and carries the note under "memory"
({"into", "ts", "by", "why"}, the newest one). With no cover decision standing (none, retire, or after an undo)
a memory decision is the decision, as today. `undo` right after a memory annotation removes the annotation only;
any other undo clears the decision, as today.
Red on 0dc24342c3 (watched)."""
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import findings_fold as FF  # noqa: E402

FAILS = []
SIG = "sig-1"
RULES = {"cover_kinds": ["work", "merge", "route", "item"], "lane_item": "LANE_ITEM"}


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %s" % (got,)))
    if not ok:
        FAILS.append(name)


def line(as_, ts, into=None, sig=SIG):
    return {"sig": sig, "as": as_, "into": into, "by": "FOUNDRY", "ts": ts, "why": "w-%s-%s" % (as_, ts)}


def spawn(ts, name="ITEM_FROM_SPAWN", frm="finding-a"):
    return {"from": frm, "as": "work", "name": name, "seat": "BENCH", "ts": ts, "why": None}


def ask(lines, spawns=()):
    try:
        return FF.latest_decision(SIG, {"finding-a"}, list(spawns), list(lines))
    except Exception as e:
        return {"as": "CRASH %s: %s" % (type(e).__name__, e)}


def is_(d, as_, into=None, ts=None):
    return isinstance(d, dict) and d.get("as") == as_ and (into is None or d.get("into") == into) and (
        ts is None or d.get("ts") == ts)


def main():
    M1, M2 = "docs/a.md:3", "docs/b.md:9"
    d = ask([line("work", "t1", "ITEM_A"), line("memory", "t2", M1)])
    check("memory after work: the work decision still stands", is_(d, "work", "ITEM_A", "t1"), d)
    check("memory after work: the cover item is unchanged", FF.covering(d, RULES) == "ITEM_A", d)
    check("memory after work: the note rides on it", isinstance(d, dict) and isinstance(d.get("memory"), dict)
          and d["memory"].get("into") == M1 and d["memory"].get("ts") == "t2", d)
    d = ask([line("merge", "t1", "ITEM_A"), line("memory", "t2", M1)])
    check("memory after merge: the merge decision still stands", is_(d, "merge", "ITEM_A", "t1")
          and (d.get("memory") or {}).get("into") == M1, d)
    d = ask([line("memory", "t2", M1)], spawns=[spawn("t1")])
    check("memory after a ledger spawn: the spawn's work decision still stands",
          is_(d, "work", "ITEM_FROM_SPAWN", "t1") and (d.get("memory") or {}).get("into") == M1, d)
    d = ask([line("work", "t1", "ITEM_A"), line("memory", "t2", M1), line("memory", "t3", M2)])
    check("two memories: the newest note rides, the work stands",
          is_(d, "work", "ITEM_A", "t1") and (d.get("memory") or {}).get("into") == M2, d)
    d = ask([line("memory", "t1", M1)])
    check("memory alone is the decision, as today", is_(d, "memory", M1, "t1") and not d.get("memory"), d)
    check("memory alone covers nothing", FF.covering(d, RULES) is None, d)
    d = ask([line("route", "t1", "ITEM_R"), line("memory", "t2", M1)])
    check("memory after route: the route decision still stands", is_(d, "route", "ITEM_R", "t1")
          and (d.get("memory") or {}).get("into") == M1, d)
    d = ask([line("memory", "t2", M1)], spawns=[dict(spawn("t1"), **{"as": "item"})])
    check("memory after a ledger item decision: it still stands", is_(d, "item", "ITEM_FROM_SPAWN", "t1")
          and (d.get("memory") or {}).get("into") == M1, d)
    d = ask([line("retire", "t1"), line("memory", "t2", M1)])
    check("memory after retire (no cover) replaces it, as today", is_(d, "memory", M1, "t2"), d)
    d = ask([line("memory", "t1", M1), line("work", "t2", "ITEM_A")])
    check("work after memory: work is the decision and carries no stale note",
          is_(d, "work", "ITEM_A", "t2") and not d.get("memory"), d)
    d = ask([line("work", "t1", "ITEM_A"), line("memory", "t2", M1), line("work", "t3", "ITEM_B")])
    check("a newer work replaces both the old work and its note", is_(d, "work", "ITEM_B", "t3") and not d.get("memory"), d)
    d = ask([line("work", "t1", "ITEM_A"), line("memory", "t2", M1), line("undo", "t3")])
    check("undo right after the note removes the note only", is_(d, "work", "ITEM_A", "t1") and not d.get("memory"), d)
    d = ask([line("work", "t1", "ITEM_A"), line("memory", "t2", M1), line("undo", "t3"), line("undo", "t4")])
    check("a second undo clears the decision", d is None, d)
    d = ask([line("work", "t1", "ITEM_A"), line("undo", "t2")])
    check("undo after work clears it, as today", d is None, d)
    d = ask([line("work", "t1", "ITEM_A"), line("undo", "t2"), line("memory", "t3", M1)])
    check("memory after an undone work is the decision", is_(d, "memory", M1, "t3"), d)
    d = ask([line("memory", "t1", M1), line("undo", "t2")])
    check("undo after a lone memory clears it, as today", d is None, d)
    d = ask([line("work", "t1", "ITEM_A"), line("memory", "t2", M1, sig="other-sig")])
    check("a memory on another signature annotates nothing", is_(d, "work", "ITEM_A", "t1") and not d.get("memory"), d)
    check("no decision at all is None", ask([]) is None, ask([]))
    d = ask([line("work", "t1", "LANE_ITEM"), line("memory", "t2", M1)])
    check("memory after work into the lane item still annotates (the kind decides, not the item)",
          is_(d, "work", "LANE_ITEM", "t1") and (d.get("memory") or {}).get("into") == M1, d)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
