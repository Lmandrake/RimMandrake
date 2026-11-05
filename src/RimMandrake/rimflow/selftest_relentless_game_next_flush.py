#!/usr/bin/env python3
"""OPS_RELENTLESS_READING_RESTORE_IUUR (outage of 2026-11-05). game_next holds tick.lock through its ledger flush; it
used to take down its game_next.on mark BEFORE the flush, so a tick that arrived in that window saw "lock busy, no mark"
and skipped at once (12:36:04Z and 12:38:19Z, two game_next passes back to back), staffing.json aged 1009 s and the live
promise broke. The mark stands for the whole hold: a tick that arrives at any moment of it waits its turn.

    python3 src/RimMandrake/rimflow/selftest_relentless_game_next_flush.py
"""
import os
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import relentless as R  # noqa: E402
import selftest_relentless as T  # noqa: E402

FAILS = []
SKIP = [{"do": "skip", "why": "a tick is running"}]


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def wake(x):
    with open(x.s.p(R.GAME_WAKE), "w", encoding="utf-8") as f:
        f.write("now")


def t_tick_in_the_flush_waits():
    """The instance: a tick that starts while game_next flushes the ledger waits for the lock and runs."""
    x = T.Rig(n=1, share=1.0)
    x.tick()            # a clean tick on record: game_next leaves the integrity gate to the tick
    wake(x)
    seen, out = {}, {}

    def flushing():
        if "thread" in seen:    # the tick's own flush, later: only game_next's is the instance
            return None
        seen["mark"] = os.path.exists(x.s.p(R.GAME_NEXT_ON))
        th = threading.Thread(target=lambda: out.setdefault("acts", R.tick(x.s, x.w, x.r, x.now + 120)))
        th.start()
        seen["thread"] = th
        time.sleep(0.6)     # the flush is slow (the Windows mount); the tick arrives inside it
        return None
    x.w.flush = flushing
    R.game_next(x.s, x.w, x.r, x.now + 5)
    seen["thread"].join(30)
    ok(seen.get("mark") is True, "the game_next.on mark still stands during the flush: %s" % seen.get("mark"))
    ok(out.get("acts") not in (None, SKIP), "a tick arriving in the flush waits and runs, never skips: %s"
       % (out.get("acts") or [])[:2])
    ok(not os.path.exists(x.s.p(R.GAME_NEXT_ON)), "the mark is gone once the lock is let go")
    x.done()


def t_no_wake_leaves_no_mark():
    x = T.Rig(n=1, share=1.0)
    ok(R.game_next(x.s, x.w, x.r, x.now)[0]["why"] == "no wake", "no wake: the pass leaves")
    ok(not os.path.exists(x.s.p(R.GAME_NEXT_ON)), "and leaves no mark behind")
    x.done()


def main():
    for fn in (t_tick_in_the_flush_waits, t_no_wake_leaves_no_mark):
        fn()
    print("selftest_relentless_game_next_flush: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
