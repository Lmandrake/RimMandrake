#!/usr/bin/env python3
"""selftest_ops_checker_deaths.py — CHECKER_DEATHS_ALARM_BUILD_29_WENT_UNHEARD: checkers dying across items alarm once.

On 2026-11-03 every walled checker died at launch (EACCES) for 2.5 h, 29 of 29, and each item read only its own
checker_lost; nothing said it was one cause. Each check fails on the code before the change:

1. rl_checks_lost counts the DIFFERENT items with a checker_lost act inside the window, from tick acts and bare rows,
   and leaves out account_lost, rows before the window and rows dated ahead.
2. It is UNMEASURED (never 0) with no journal, and when the tail it reads does not reach back to the window's start.
3. c_relentless carries relentless.checks_lost_items, and an unreadable journal counts in relentless.blind.
4. rules: the target alarms above 2 items under ONE fixed id; it is routed to Operations under its own cause, not
   work_belt; run_alarms files that id at once and a repeat reopens it.

Fixtures only: a temp store, a temp RM_OPS_WATCH_DIR, a fake filer.

    python3 src/RimMandrake/Utils/selftest_ops_checker_deaths.py
"""
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
TMP = Path(tempfile.mkdtemp(prefix="selftest_ops_checker_deaths_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
(TMP / "ops").mkdir()
import ops_watch as OW  # noqa: E402

FAILS = []
NOW = time.time()
NAME = "OPS_CHECKER_DEATHS_DIAGNOSE_SILENT"


def ok(cond, what, got=None):
    print(("PASS " if cond else "FAIL ") + what + ("" if cond else "  got: %r" % (got,)))
    if not cond:
        FAILS.append(what)


def at(dt):
    return OW.iso(NOW - dt)


def journal(store, rows):
    store.mkdir(parents=True, exist_ok=True)
    with open(store / "journal.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def main():
    rules = OW.load_rules()
    cfg = rules["relentless"]
    store = TMP / "store"
    # 1
    journal(store, [
        {"at": at(7200), "do": "tick", "acts": [{"do": "checker_lost", "item": "OLD"}]},       # before the window
        {"at": at(1800), "do": "tick", "acts": [{"do": "check_started", "item": "A"}, {"do": "checker_lost", "item": "A"},
                                                {"do": "checker_lost", "item": "B"}, {"do": "account_lost", "item": "C"}]},
        {"at": at(900), "do": "checker_lost", "item": "A"},
        {"at": at(600), "do": "tick", "acts": [{"do": "checker_lost", "item": "D"}, {"do": "blind_fail", "item": "E"}]},
        {"at": at(-900), "do": "tick", "acts": [{"do": "checker_lost", "item": "FUTURE"}]},
    ])
    p = OW.rl_checks_lost(store, NOW, cfg)
    x = p.get("x") or {}
    ok(p.get("m") == "MEASURED" and p.get("v") == 3 and x.get("lost") == 4 and x.get("items", [])[:1] == ["A"]
       and x.get("started") == 1 and x.get("verdicts") == 1 and "4 checkers lost on 3 items" in x.get("first", ""),
       "1: three different items lost a checker in the hour; account_lost, older and later rows left out", p)
    journal(store, [{"at": at(600), "do": "tick", "acts": [{"do": "check_started", "item": "A"}]}])
    p = OW.rl_checks_lost(store, NOW, cfg)
    ok(p.get("m") == "MEASURED" and p.get("v") == 0 and p["x"]["first"] == "none", "1: a quiet hour reads a measured 0", p)
    # 2
    p = OW.rl_checks_lost(TMP / "nostore", NOW, cfg)
    ok(p.get("m") == "UNMEASURED" and "unreadable" in p.get("why", ""), "2: no journal is UNMEASURED, never 0", p)
    pad = "x" * 400
    journal(store, [{"at": at(300 - i), "do": "wait", "pad": pad} for i in range(100)])
    p = OW.rl_checks_lost(store, NOW, cfg, chunk=4096)
    ok(p.get("m") == "UNMEASURED" and "reach back" in p.get("why", ""),
       "2: a tail that does not reach the window's start is UNMEASURED, not a low count", p)
    # 3
    os.environ["RELENTLESS_ROOT"] = str(TMP / "empty_root")
    pts = OW.c_relentless(NOW, rules, {})
    ok(pts.get("relentless.checks_lost_items", {}).get("m") == "UNMEASURED"
       and "journal.jsonl unreadable" in pts["relentless.checks_lost_items"]["why"]
       and pts["relentless.blind"]["v"] > 0,
       "3: c_relentless carries the point, and an unread journal is blind", pts.get("relentless.checks_lost_items"))
    del os.environ["RELENTLESS_ROOT"]
    # 4
    tg = [t for t in rules["targets"] if t.get("key") == "relentless.checks_lost_items"]
    ok(len(tg) == 1 and tg[0].get("alarm") is True and tg[0].get("op") == ">" and tg[0].get("value") == 2
       and tg[0].get("name") == NAME and len(NAME) + 5 <= 44 and tg[0].get("title_field") == "first",
       "4: one alarming target above 2 items, one fixed id", tg)
    sys.path.insert(0, str(Path(OW.__file__).resolve().parent.parent / "rimflow"))
    import incident as IN
    rt = IN.route_of(IN.load_table(), "relentless.checks_lost_items") or {}
    ok(rt.get("reader") == "Operations" and rt.get("cause") not in (None, "work_belt"),
       "4: routed to Operations under its own cause", rt)
    r4 = {"alarms": {"clear_passes": 1}, "targets": [dict(tg[0], conductor_log=str(TMP / "conductor_log.md"))]}
    pt = {"m": "MEASURED", "v": 15, "x": {"first": "23 checkers lost on 15 items in 1 h, 0 verdicts, 24 checks started (A)"}}
    sent = []

    def filer(todo, conf):
        sent.append([dict(a) for a in todo])
        return {a["name"]: None for a in todo}
    OW.run_alarms({"relentless.checks_lost_items": pt}, r4, NOW, set(), filer)
    first = sent[-1][0] if sent else {}
    name = first.get("name", "")
    ok(name.startswith(NAME) and not first.get("reopen") and "15 items" in first.get("title", ""),
       "4: the first pass over the line files the fixed id", first)
    (TMP / "ops" / "alarms.json").unlink()
    sent.clear()
    OW.run_alarms({"relentless.checks_lost_items": pt}, r4, NOW + 7200, {name}, filer)
    again = sent[-1][0] if sent else {}
    ok(again.get("name") == name and again.get("reopen") is True, "4: a repeat reopens the same id, never refiles", again)
    sent.clear()
    OW.run_alarms({"relentless.checks_lost_items": {"m": "MEASURED", "v": 2, "x": {"first": "x"}}}, r4, NOW + 9000,
                  {name}, filer)
    todo = [a for b in sent for a in b]
    ok(todo and all(a.get("note_only") and "cleared" in a.get("text", "") for a in todo),
       "4: two items is under the line: the alarm clears with a note, nothing new filed", sent)
    shutil.rmtree(TMP, ignore_errors=True)
    print("%d failed" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
