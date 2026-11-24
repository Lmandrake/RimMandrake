#!/usr/bin/env python3
"""Acceptance test of RIMMANDRAKE_RELOAD_SITE_AFTER_A_CHAIN_KILLS_ITS_COLONIST. Offline. Base 2026-11-24: 0/6, exit 1.

Contract: runner.reload_spoiled_site(hold, dead_before, reload) -> (hold, note)
  hold: the site hold's reading {"problems": [...], "dead": [ids]}; dead_before: the colonist ids dead at this run's first hold;
  reload() -> a fresh hold reading, or raises. Called at most once, and only when every problem is a colonist that died in
  an EARLIER chain of this run (in `dead`, not in dead_before). Anything else is returned as it is: a hostile, a fire, an
  unreadable list, a colonist dead at the start. note says what was done; None when nothing was.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
BAD = []
SPOILED = {"bland": False, "problems": ["dead colonists: ['H1']"], "dead": ["H1"]}
CLEAN = {"bland": True, "problems": [], "dead": []}


def R(hold, before=(), fresh=CLEAN):
    import runner
    n = []

    def reload():
        n.append(1)
        if isinstance(fresh, Exception):
            raise fresh
        return fresh
    return runner.reload_spoiled_site(dict(hold), set(before), reload) + (len(n),)


def check(name, fn):
    try:
        ok, why = bool(fn()), ""
    except Exception as e:  # noqa: BLE001
        ok, why = False, " (%s: %s)" % (type(e).__name__, e)
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, why))
    if not ok:
        BAD.append(name)


check("a colonist that an earlier chain killed: one reload, the chain runs", lambda: R(SPOILED)[0] == CLEAN and R(SPOILED)[2] == 1 and R(SPOILED)[1])
check("a clean site is left alone", lambda: R(CLEAN) == (CLEAN, None, 0))
check("a colonist dead at the start of the run is no reload", lambda: R(SPOILED, ["H1"])[2] == 0 and R(SPOILED, ["H1"])[0]["problems"])
check("another problem beside it is no reload", lambda: R(dict(SPOILED, problems=SPOILED["problems"] + ["fires burning: 3"]))[2] == 0)
check("a reload that is still not quiet stays not quiet", lambda: R(SPOILED, (), SPOILED)[0]["problems"] and R(SPOILED, (), SPOILED)[2] == 1)
check("a reload that fails is named, never clean", lambda: "boom" in str(R(SPOILED, (), RuntimeError("boom"))) and R(SPOILED, (), RuntimeError("boom"))[0]["problems"])
print("%d/6" % (6 - len(BAD)))
sys.exit(1 if BAD else 0)
