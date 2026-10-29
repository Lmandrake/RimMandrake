#!/usr/bin/env python3
"""selftest_raise_order.py - raised items come out of `next` in RAISE order, not filing order.

    python3 src/RimMandrake/rimflow/selftest_raise_order.py

RAISE_ORDER_FIX_FILING_DATE_OUTRANKS_PLAN (2026-10-29): items filed A, B, C and raised C, A, B (one
Producer run, so the same `ts` second and distinct `tsn`) are offered C, A, B — for ready items
(`priority.rank`), for proposed ones (`cli._claimable`), and across the two in `cli._choose`. An unraised
item, even one filed first, never beats a raised one. Pure model.replay on in-memory events.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rimflow import cli, model, priority  # noqa: E402

FAILS = []
TS = "2026-10-29T16:00:00Z"


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def ev(**kw):
    kw.setdefault("ts", "2026-10-29T00:00:00Z")
    return kw


def filed(iid, ts):
    d = ev(seat="BENCH", event="file", id=iid, title="t", kind="task", ts=ts)
    d["for"] = "BENCH"
    return d


def raised(iid, n):
    # one run: the same second, ascending nanoseconds, as model.append() stamps them
    return ev(seat="BENCH", event="raise", id=iid, reason="plan", ts=TS, tsn=1793289947000000000 + n)


class Args(object):
    target = "v1"


def world(ready):
    ids = ["ITEM_A", "ITEM_B", "ITEM_C"]
    evs = [filed("ITEM_OLD_UNRAISED", "2026-10-01T00:00:00Z")]
    evs += [filed(i, "2026-10-2%dT00:00:00Z" % n) for n, i in enumerate(ids, 1)]
    if ready:
        evs += [ev(seat="BENCH", event="claim", id=i, ts="2026-10-29T01:00:00Z")
                for i in ["ITEM_OLD_UNRAISED"] + ids]
    evs += [raised("ITEM_C", 1), raised("ITEM_A", 2), raised("ITEM_B", 3)]
    # a second raise of C, later, must not move it: the FIRST raise carries the order
    evs += [ev(seat="BENCH", event="raise", id="ITEM_C", reason="again", ts="2026-10-29T17:00:00Z", tsn=5)]
    return model.replay(evs, strict=True)


def main():
    want = ["ITEM_C", "ITEM_A", "ITEM_B", "ITEM_OLD_UNRAISED"]
    ctx = {"now": model.epoch_now()}

    w = world(ready=True)
    got = [i.id for i in priority.rank(w, "BENCH", "v1", ctx)]
    check(got == want, "ready: rank() offers raise order C, A, B, then the unraised one (%s)" % got)
    ch = cli._choose(w, "BENCH", Args(), ctx, None)
    check(ch["item"] is not None and ch["item"].id == "ITEM_C", "ready: `next` offers C first (%s)"
          % (ch["item"].id if ch["item"] else None))

    w = world(ready=False)
    got = [i.id for i in cli._claimable(w, "BENCH", "v1", ctx["now"])]
    check(got == want, "proposed: _claimable offers raise order C, A, B, then the unraised one (%s)" % got)
    ch = cli._choose(w, "BENCH", Args(), ctx, None)
    check(ch["item"] is not None and ch["item"].id == "ITEM_C", "proposed: `next` offers C first (%s)"
          % (ch["item"].id if ch["item"] else None))
    check(w.items["ITEM_C"].raised == TS, "a re-raise keeps the first stamp")

    # `next` walks C, A, B: each offer, once taken out of the pool, yields the next
    for ready in (True, False):
        w0 = world(ready=ready)
        seen, gone = [], []
        for _ in range(4):
            w = w0
            for g in gone:
                w.items[g].state = "dropped"
            ch = cli._choose(w, "BENCH", Args(), ctx, None)
            if ch["item"] is None:
                break
            seen.append(ch["item"].id)
            gone.append(ch["item"].id)
        check(seen == want, "%s: successive `next` offers %s" % ("ready" if ready else "proposed", seen))

    # mixed: a proposed item raised BEFORE a ready one is offered first; a later-raised proposed one is not
    base = [filed("READY_X", "2026-10-01T00:00:00Z"), ev(seat="BENCH", event="claim", id="READY_X"),
            filed("PROP_Y", "2026-10-02T00:00:00Z")]
    w = model.replay(base + [raised("PROP_Y", 1), raised("READY_X", 2)], strict=True)
    ch = cli._choose(w, "BENCH", Args(), ctx, None)
    check(ch["item"] is not None and ch["item"].id == "PROP_Y", "mixed: earlier-raised proposed beats later-raised "
          "ready (%s)" % (ch["item"].id if ch["item"] else None))
    w = model.replay(base + [raised("READY_X", 1), raised("PROP_Y", 2)], strict=True)
    ch = cli._choose(w, "BENCH", Args(), ctx, None)
    check(ch["item"] is not None and ch["item"].id == "READY_X", "mixed: earlier-raised ready beats later-raised "
          "proposed (%s)" % (ch["item"].id if ch["item"] else None))
    w = model.replay(base + [raised("PROP_Y", 1)], strict=True)
    ch = cli._choose(w, "BENCH", Args(), ctx, None)
    check(ch["item"] is not None and ch["item"].id == "PROP_Y", "mixed: a raised proposed beats an unraised ready")

    print("%d FAIL" % len(FAILS) if FAILS else "ALL OK")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
