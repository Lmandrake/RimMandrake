#!/usr/bin/env python3
"""selftest_scratch_reap_borrow_share.py — the borrower walk spends at most BORROW_WALK_SHARE of a run
(RIMMANDRAKE_UNCLOG_SCRATCH_ARCHIVE_BACKLOG_29_KB_CLONES_EACH). Measured 2026-11-18: Borrows() is a find over every
scan root, 40.6 s alone and 124 s under load; Ctx.refresh rebuilt it whenever it was older than 120 s, so about every
second apply row paid a whole walk (19 rows in 1157 s, 358 deferred).

Proves: a fast walk is still redone after BORROW_REFRESH_S, the old floor; a slow walk waits until its own cost is at
most the share of the time since it began; each walk's seconds are kept for the run record. Live and Borrows are
stubbed and the clock is fake: no /proc, no find."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scratch_reap as s                                    # noqa: E402

FAILS = []


def ok(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


clock = [1000.0]
walk_s = [10.0]
built = []


class FakeBorrows:
    def __init__(self):
        self.taken = clock[0]
        clock[0] += walk_s[0]               # the walk itself takes this long
        built.append(self.taken)


class FakeLive:
    def __init__(self, now):
        pass


real = s.Borrows, s.Live, s.time.time
s.Borrows, s.Live, s.time.time = FakeBorrows, FakeLive, (lambda: clock[0])
try:
    ctx = s.Ctx(clock[0])                   # first walk: 10 s, from 1000 to 1010
    ok(len(built) == 1 and getattr(ctx, "borrow_walks", None) == [10.0], "the first walk's seconds are kept (%r)"
       % getattr(ctx, "borrow_walks", None))
    clock[0] = 1000 + s.BORROW_REFRESH_S - 1
    ctx.refresh()
    ok(len(built) == 1, "a fast walk is not redone inside BORROW_REFRESH_S")
    clock[0] = 1000 + s.BORROW_REFRESH_S + 1
    ctx.refresh()
    ok(len(built) == 2, "a fast walk is redone after BORROW_REFRESH_S, as before (%d walks)" % len(built))

    walk_s[0] = 100.0                       # a slow walk: 100 s, so the next waits until 100 / share s after it began
    start = clock[0] = 5000.0
    ctx.borrows = FakeBorrows()
    ctx.borrow_walks.append(100.0)
    n = len(built)
    gap = 100.0 / s.BORROW_WALK_SHARE
    clock[0] = start + gap - 1
    ctx.refresh()
    ok(len(built) == n, "a slow walk is not redone while it would be more than the share (%.0f s gap)" % gap)
    clock[0] = start + gap + 1
    ctx.refresh()
    ok(len(built) == n + 1, "a slow walk is redone once its share is spent")
    ok(ctx.borrow_walks[-1] == 100.0 and len(ctx.borrow_walks) == 4, "every walk is counted (%r)" % ctx.borrow_walks)
    ok(0 < s.BORROW_WALK_SHARE <= 0.25, "the share stays a minority of the run (%r)" % s.BORROW_WALK_SHARE)
finally:
    s.Borrows, s.Live, s.time.time = real

print("%d failed" % len(FAILS))
sys.exit(1 if FAILS else 0)
