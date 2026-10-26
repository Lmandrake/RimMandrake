#!/usr/bin/env python3
"""selftest_runner_seat.py - the RUNNER seat (the test queue's dispatcher) records runs and nothing else.

RUNNER may `verify`, `finding` and `note` on any seat's item, because a measured run is a fact and the queue runs
tests FOR other seats' items; every other verb is refused, and a verify on an item that does not exist is refused.
Pure model.replay on in-memory events: no ledger file is touched.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model  # noqa: E402

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
    print("\n%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
