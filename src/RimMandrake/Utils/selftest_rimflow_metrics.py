#!/usr/bin/env python3
"""Selftest for rimflow_metrics.py — a synthetic ledger with known answers, never the real one.

Each case can fail: the expected numbers are fixed by the event stamps below, and a fold that
re-interpreted a verb (or a timeline that missed a state change) moves them.

    python3 src/RimMandrake/Utils/selftest_rimflow_metrics.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rimflow_metrics as rm  # noqa: E402

model = rm.model
FAIL = []
T0 = model.epoch("2026-10-01T00:00:00Z")


def at(h):
    return model.stamp(T0 + h * 3600)


def file_(iid, h, **kw):
    d = dict(seat="BENCH", event="file", id=iid, title=kw.pop("title", "t"), kind="task", ts=at(h))
    d["for"] = "BUILD"
    d.update(kw)
    return d


def v(seat, verb, iid, h, **kw):
    d = dict(seat=seat, event=verb, id=iid, ts=at(h))
    d.update(kw)
    return d


EVENTS = [
    # A: filed 0h, claimed+started 2h, closed 26h  -> lead 26h, cycle 24h, queue wait 2h
    file_("ALPHA_FIX_ONE", 0),
    v("BUILD", "claim", "ALPHA_FIX_ONE", 2), v("BUILD", "start", "ALPHA_FIX_ONE", 2),
    v("BUILD", "close", "ALPHA_FIX_ONE", 26, sha="abc1234"),
    # B: filed 1h, needs owner at 4h, still open -> one open owner wait of (now - 4h)
    file_("BETA_ASK_OWNER", 1),
    v("BENCH", "needs", "BETA_ASK_OWNER", 4, to="owner"),
    # C: follow-up of the closed A, closed without ever being started, within 5 min of filing
    file_("ALPHA_FIX_AGAIN", 30, caused_by="ALPHA_FIX_ONE"),
    v("BUILD", "close", "ALPHA_FIX_AGAIN", 30.05, sha="def5678"),
    # D: a FlowWorks item by alias, title-mapped item E
    file_("HOSE_LEAK_TWIST", 31),
    file_("ODD_THING_ONE", 31, title="Cauldron soup broken"),
]
NOW = T0 + 48 * 3600


def check(name, got, want):
    if got != want:
        FAIL.append(name)
        print("FAIL  %s: got %r want %r" % (name, got, want))
    else:
        print("ok    %s" % name)


def main():
    evs = model.canonical_order(list(EVENTS))
    world, tl = rm.timelines(evs)
    check("no refusals in the fixture", world.errors, [])
    mods = {"FlowWorks": "RimMandrake", "Cauldron": "RimMandrake"}
    r = rm.compute(evs, now=NOW, window_days=30, mods=mods)
    check("lead n", r["lead"]["n"], 2)
    check("lead max = 26h", r["lead"]["max_d"], round(26 / 24.0, 2))
    check("cycle = 24h", r["cycle"]["max_d"], 1.0)
    check("queue wait = 2h", r["queue_wait"]["max_d"], round(2 / 24.0, 2))
    check("done never started", r["done_never_started"], 1)
    check("receipt within 5 min", r["done_within_5min_of_filing"], 1)
    check("owner wait open n", r["owner_wait_open"]["n"], 1)
    check("owner wait open age = 44h", r["owner_wait_open"]["max_d"], round(44 / 24.0, 2))
    check("rework: cause already done", r["rework"]["cause_already_done"], 1)
    check("flow net (5 filed - 2 done)", r["flow"]["net"], 5 - 2)
    check("mod alias HOSE -> FlowWorks", rm.item_mod("HOSE_LEAK_TWIST", "t", mods), "FlowWorks")
    check("mod by title", rm.item_mod("ODD_THING_ONE", "Cauldron soup broken", mods), "Cauldron")
    check("unmapped stays None", rm.item_mod("ALPHA_FIX_ONE", "t", mods), None)
    check("percentile of empty is None (prints --)", rm.q([], 50), None)
    print("%d failed" % len(FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
