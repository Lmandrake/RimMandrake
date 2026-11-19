#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_CHARGE_SHARED_OUTAGE_ONCE_FORTY_FIVE_DEATHS (DESIGN DECISION 2026-11-18 on
RIMMANDRAKE_DECIDE_GUARDS_OWED_BY_LANDED_OLD_FIXES). One stop of one shared timer was read as the death of every fix whose
promise names that timer (45 deaths in four hours on 2026-11-07), and each then owed its own class guard. The rule:
  deadman  `deadman_check.shared_hosts(rows)` -> {item: host}. rows are the pass's broken rows ({"item", "line", "why"}).
           Two or more items broken in one pass on the same subject (unit=/hook=/role=) with the same reason (digits
           aside) are ONE outage; each maps to the subject's fixed host, `item_id(line)`. The host never maps to itself.
           The sweep writes that host on each such `live broken` event as `sharedWith`.
  model    a `live broken` whose `sharedWith` names ANOTHER item that exists is an outage (it reopens the item and counts
           in live_repeats) but not a death, so it owes no guard. `sharedWith` naming the item itself, or an item the
           ledger does not hold, excuses nothing.
Red on 3e560d2656 (watched)."""
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import model  # noqa: E402
import deadman_check as D  # noqa: E402

FAILS = []
A, B, C = "PROJNOW_FIX_ALPHA_SHARES_A_TIMER", "PROJNOW_FIX_BETA_SHARES_A_TIMER", "PROJNOW_FIX_GAMMA_OWN_TIMER"
HOST = "LIVE_RESTORE_RM_SHARED"
LINE = "unit=rm-shared.timer max_age=1h"
DOWN = "rm-shared.timer: is-active says 'inactive', wanted 'active'"
_n = [1795100000000000000]


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %s" % (got,)))
    if not ok:
        FAILS.append(name)


def ev(seat, event, iid, ts, **k):
    _n[0] += 1
    return dict(seat=seat, event=event, id=iid, ts=ts, tsn=_n[0], **k)


def settled(iid, line=LINE):
    return [ev("BENCH", "file", iid, "2026-11-19T01:00:00Z", title="t", kind="fix", **{"for": "BENCH"}),
            ev("BENCH", "start", iid, "2026-11-19T01:01:00Z"),
            ev("BENCH", "close", iid, "2026-11-19T01:02:00Z", sha="a" * 12, live=line, why="x", noCode=True)]


def broken(iid, ts, **k):
    return ev("RUNNER", "live", iid, ts, result="broken", detail=DOWN, **k)


def kept(iid, ts):
    return ev("RUNNER", "live", iid, ts, result="kept", detail="sweep: running again")


def world(events):
    w = model.replay(events)
    return w.items, w.errors


def main():
    base = settled(A) + settled(B) + settled(C) + settled(HOST)
    items, errs = world(base)
    if errs or any(items[i].state != "done" for i in (A, B, C, HOST)):
        print("UNMEASURED: the fixture's closes did not settle: %s %s" % (errs[:2], {i: items[i].state for i in items}))
        return 2
    T1, T2, T3 = "2026-11-19T02:00:00Z", "2026-11-19T02:15:00Z", "2026-11-19T03:00:00Z"

    items, errs = world(base + [broken(C, T1)])
    check("model: an outage of one settled fix alone is a death and owes a guard",
          items[C].deaths == 1 and model.guard_owed(items[C]) and not errs, (items[C].deaths, errs[:1]))

    items, errs = world(base + [broken(HOST, T1), broken(A, T1, sharedWith=HOST), broken(B, T1, sharedWith=HOST)])
    check("model: a shared outage is no death of the items that share it",
          items[A].deaths == 0 and items[B].deaths == 0 and not errs, (items[A].deaths, items[B].deaths, errs[:1]))
    check("model: a shared outage owes no guard on those items",
          not model.guard_owed(items[A]) and not model.guard_owed(items[B]))
    check("model: a shared outage still reopens the item and counts as an outage",
          items[A].state == "ready" and bool(items[A].live_broken) and items[A].live_repeats == 1,
          (items[A].state, items[A].live_broken, items[A].live_repeats))
    check("model: the host takes the death", items[HOST].deaths == 1 and model.guard_owed(items[HOST]),
          items[HOST].deaths)

    items, errs = world(base + [broken(A, T1, sharedWith=HOST), kept(A, T2)])
    check("model: `kept` after a shared outage puts the item back to done", items[A].state == "done" and not errs,
          (items[A].state, errs[:1]))

    items, errs = world(base + [broken(A, T1, sharedWith=HOST), kept(A, T2), broken(A, T3)])
    check("model: a later outage of its own is a death", items[A].deaths == 1 and model.guard_owed(items[A]),
          items[A].deaths)

    items, errs = world(base + [broken(A, T1, sharedWith=A)])
    check("model: sharedWith naming the item itself excuses nothing", items[A].deaths == 1, items[A].deaths)
    items, errs = world(base + [broken(A, T1, sharedWith="PROJNOW_NO_SUCH_ITEM_WAS_EVER_FILED")])
    check("model: sharedWith naming an item the ledger does not hold excuses nothing", items[A].deaths == 1,
          items[A].deaths)
    for bad in ("", None, 7, ["x"]):
        items, errs = world(base + [broken(A, T1, sharedWith=bad)])
        check("model: sharedWith %r excuses nothing" % (bad,), items[A].deaths == 1, (items[A].deaths, errs[:1]))

    fn = getattr(D, "shared_hosts", None)
    check("deadman: shared_hosts exists", callable(fn))

    def hosts(rows):
        if not callable(fn):
            return "no shared_hosts"
        try:
            return fn(rows)
        except Exception as e:
            return "CRASH %s: %s" % (type(e).__name__, e)

    def row(item, why=DOWN, line=LINE):
        return {"item": item, "line": line, "why": why}
    check("deadman: two items down on one unit for one reason share its host",
          hosts([row(A), row(B)]) == {A: HOST, B: HOST}, hosts([row(A), row(B)]))
    check("deadman: the host's own row never maps to itself",
          hosts([row(A), row(B), row(HOST)]) == {A: HOST, B: HOST}, hosts([row(A), row(B), row(HOST)]))
    check("deadman: one item and the host are one outage too", hosts([row(A), row(HOST)]) == {A: HOST},
          hosts([row(A), row(HOST)]))
    check("deadman: one item broken alone shares nothing", hosts([row(A)]) == {}, hosts([row(A)]))
    check("deadman: no rows, nothing shared", hosts([]) == {}, hosts([]))
    check("deadman: the same unit broken for a different reason is not the shared outage",
          hosts([row(A), row(B), row(C, why="reading /x/own.json is 9000 s old (max 3600)")]) == {A: HOST, B: HOST},
          hosts([row(A), row(B), row(C, why="reading /x/own.json is 9000 s old (max 3600)")]))
    r1, r2 = "last firing of rm-shared.timer is 7201 s old (max 3600)", "last firing of rm-shared.timer is 7203 s old (max 3600)"
    check("deadman: reasons that differ only in their digits are one reason",
          hosts([row(A, why=r1), row(B, why=r2)]) == {A: HOST, B: HOST}, hosts([row(A, why=r1), row(B, why=r2)]))
    check("deadman: different units never share",
          hosts([row(A), row(C, why="rm-own.timer: is-active says 'inactive', wanted 'active'",
                           line="unit=rm-own.timer max_age=1h")]) == {},
          hosts([row(A), row(C, line="unit=rm-own.timer max_age=1h")]))
    check("deadman: rows that are kept (no reason) or have no promise line are ignored",
          hosts([row(A), row(B, why=None), {"item": "LIVE_RESTORE_OPS_WATCH", "line": None, "why": "arm dead"}]) == {},
          hosts([row(A), row(B, why=None), {"item": "LIVE_RESTORE_OPS_WATCH", "line": None, "why": "arm dead"}]))
    hl, hw = "hook=block_x.py", "hook block_x.py is not wired in /a/settings.json"
    check("deadman: two items on one hook share the hook's host",
          hosts([row(A, why=hw, line=hl), row(B, why=hw, line=hl)]) == {A: "LIVE_RESTORE_BLOCK_X", B: "LIVE_RESTORE_BLOCK_X"},
          hosts([row(A, why=hw, line=hl), row(B, why=hw, line=hl)]))
    rl, rw = "role=Operations max_age=1d", "role Operations last launched 90000 s ago (max 86400)"
    check("deadman: two items on one role share the role's host",
          hosts([row(A, why=rw, line=rl), row(B, why=rw, line=rl)]) == {A: "LIVE_RESTORE_OPERATIONS", B: "LIVE_RESTORE_OPERATIONS"},
          hosts([row(A, why=rw, line=rl), row(B, why=rw, line=rl)]))
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
