#!/usr/bin/env python3
"""selftest_runner_seat.py - the RUNNER seat (the test queue's dispatcher) records runs and nothing else.

RUNNER may `verify`, `finding` and `note` on any seat's item, because a measured run is a fact and the queue runs
tests FOR other seats' items; every other verb is refused, and a verify on an item that does not exist is refused.
Pure model.replay on in-memory events: no ledger file is touched.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rimflow import model  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def ev(**kw):
    kw.setdefault("ts", "2026-10-26T00:00:00Z")
    return kw


def filed(iid, for_="BENCH"):
    d = ev(seat="BENCH", event="file", id=iid, title="t", kind="task")
    d["for"] = for_
    return d


def refusal(evs):
    try:
        model.replay(evs, strict=True)
    except model.LedgerError as e:
        return str(e)
    return None


def spawn(name, for_, needs, seat="RUNNER", src="SOME_ITEM_FIX_IT"):
    d = ev(seat=seat, event="spawn", name=name, needs=needs, title="t " + name)
    d["for"], d["from"] = for_, src
    return d


def steward_escalation(base, item):
    """2026-10-26 (STEVE_STEWARD_BUILD_NO_LLM_OWNER): the steward files its escalations as RUNNER,
    for BENCH (offline) or OWNER (owner) only, and `raise` puts one at the top of `next`."""
    from rimflow import cli, priority
    esc = "STEVE_LANE_BRAKED_UNOWNED_ABC"
    w = model.replay(base + [spawn(esc, "BENCH", "offline")], strict=True)
    check(w.items.get(esc) is not None and w.items[esc].owner == "BENCH"
          and w.items[esc].state == "proposed", "RUNNER spawns a BENCH escalation (needs offline)")
    w = model.replay(base + [spawn("STEVE_LANE_X_OWNER_A", "OWNER", "owner")], strict=True)
    check(w.items["STEVE_LANE_X_OWNER_A"].needs == "owner", "RUNNER spawns an OWNER ask (needs owner)")
    for bad in (spawn("STEVE_B", "BUILD", "offline"), spawn("STEVE_C", "OWNER", "offline"),
                spawn("STEVE_D", "BENCH", "game-up")):
        msg = refusal(base + [bad])
        check(msg is not None and "RUNNER spawns only" in msg, "RUNNER may not spawn for %s needs %s: %s"
              % (bad["for"], bad["needs"], (msg or "NOT REFUSED")[:70]))
    # raise: an older, row-ranked item and a proposed escalation; raising reorders `next`
    ready = "OTHER_WORK_READY_NOW"
    evs = base + [filed(ready), ev(seat="BENCH", event="claim", id=ready),
                  dict(spawn(esc, "BENCH", "offline"), ts="2026-10-26T01:00:00Z"),
                  dict(spawn("STEVE_LANE_Z_UNOWNED_B", "BENCH", "offline"), ts="2026-10-26T01:00:00Z")]
    w = model.replay(evs, strict=True)
    check(w.items[esc].raised is None, "a spawned escalation starts unraised")

    class A(object):
        target = "v1"
    ctx = {"now": model.epoch_now()}
    before = cli._choose(w, "BENCH", A(), ctx, None)
    check(before["item"] is not None and before["item"].id != esc, "unraised: `next` offers ranked work first (%s)"
          % (before["item"].id if before["item"] else None))
    w = model.replay(evs + [ev(seat="RUNNER", event="raise", id=esc, reason="T+30",
                               ts="2026-10-26T02:00:00Z")], strict=True)
    check(w.items[esc].raised == "2026-10-26T02:00:00Z", "RUNNER may raise; the item carries its stamp")
    after = cli._choose(w, "BENCH", A(), ctx, None)
    check(after["item"] is not None and after["item"].id == esc, "raised: `next --seat BENCH` offers it first (%s)"
          % (after["item"].id if after["item"] else None))
    check([i.id for i in cli._claimable(w, "BENCH", "v1")][:1] == [esc], "raised sorts first among claimables")
    evs2 = evs + [ev(seat="BENCH", event="claim", id=esc), ev(seat="RUNNER", event="raise", id=ready)]
    w = model.replay(evs2, strict=True)
    check([i.id for i in priority.rank(w, "BENCH", "v1", ctx)][:1] == [ready], "raised sorts first in rank()")
    msg = refusal(evs + [ev(seat="BENCH", event="drop", id=esc, reason="r"),
                         ev(seat="RUNNER", event="raise", id=esc)])
    check(msg is not None and "only an open item" in msg, "a closed item cannot be raised")


def main():
    item = "SOME_ITEM_FIX_IT"
    base = [filed(item), ev(seat="BENCH", event="claim", id=item)]
    run = ev(seat="RUNNER", event="verify", id=item, result="fail", config="steve-targeted",
             evidence="D:/x.html", sha="abc1234")
    w = model.replay(base + [run], strict=True)
    check(len(w.items[item].runs) == 1 and w.items[item].runs[0].result == "fail",
          "RUNNER records a run on a BENCH-owned item in flight")
    fnd = ev(seat="RUNNER", event="finding", id=item, type="MOD", severity="medium", name="ROW_R2_FAILS_ON_STEVE",
             **{"from": item + "/run-1@steve-targeted"})
    w = model.replay(base + [run, fnd], strict=True)
    check("ROW_R2_FAILS_ON_STEVE" in w.items[item].findings, "RUNNER files a finding from its run")
    w = model.replay(base + [ev(seat="RUNNER", event="note", id=item, text="run INVALID/HANG")], strict=True)
    check(w is not None, "RUNNER may note an item")
    for bad in (ev(seat="RUNNER", event="close", id=item, sha="abc1234", reason="r"),
                ev(seat="RUNNER", event="claim", id=item),
                dict(filed("RUNNER_FILED_ITEM_X"), seat="RUNNER")):
        msg = refusal(base + [bad])
        check(msg is not None and "RUNNER records test runs only" in msg, "RUNNER may not %s: %s"
              % (bad["event"], (msg or "NOT REFUSED")[:90]))
    msg = refusal(base + [dict(run, id="NO_SUCH_ITEM_HERE")])
    check(msg is not None and "never been filed" in msg, "a RUNNER verify on a missing item is refused")
    other = ev(seat="FOUNDRY", event="verify", id=item, result="pass", config="min-13")
    check(refusal(base + [other]) is not None, "the owning-seat rule still holds for a window seat")
    check(model.shard_path("RUNNER").endswith(os.path.join("events", "RUNNER.jsonl")), "RUNNER has its own shard")
    steward_escalation(base, item)
    print("\n%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
