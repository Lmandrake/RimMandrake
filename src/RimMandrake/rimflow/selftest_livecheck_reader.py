#!/usr/bin/env python3
"""LIVECHECK_FIX_TYPEERROR_BLINDS_EVERY_LINE: the supervisor's live-line reader reads a real verdict.

relentless.py hands `fx.live_check` to relentless_reach.live_reading, which calls `check(line, now=now)`. While
Effects.live_check took (line, not_before) only, that call raised TypeError, so every live line in a Marker's
live.txt read COULD NOT READ (checking audit 2026-11-06). The fix is ab77ccbdd6; rows B, C and D fail on its parent. Rows:
  A the instance: a reader with the old signature, fed through live_reading, is UNREAD with a TypeError (the guard sees it)
  B the supervisor's Effects.live_check takes `now` (and `not_before`, which the close path passes positionally)
  C through the same call the Marker box uses, a live line reads a real verdict: HOLDS for `once:`, DOES NOT HOLD for
    a hook that is not wired and for a malformed line, never COULD NOT READ
  D write_live writes that verdict, not COULD NOT READ
"""
import inspect
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import relentless as R                      # noqa: E402
import relentless_reach as RR               # noqa: E402

FAILS = []


def ok(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


class _Fx(R.Effects):
    """Effects without its constructor: live_check touches no state of the instance."""
    def __init__(self):     # noqa: D401 - deliberately bare
        pass


def main():
    now = 1800000000

    def old_reader(line, not_before=0):      # the signature before the fix
        return None
    got = RR.live_reading("once: anything", old_reader, now)
    ok(got["state"] == RR.UNREAD and "TypeError" in (got["why"] or ""), "A: the old signature is UNREAD by TypeError: %s" % got)

    params = inspect.signature(R.Effects.live_check).parameters
    ok("now" in params and "not_before" in params, "B: Effects.live_check takes now and not_before: %s" % list(params))
    fx = _Fx()
    ok(fx.live_check("once: positional close path", 0) is None, "B: the close path's positional not_before still reads")

    cases = (("once: the build adds a def", RR.HOLDS),
             ("hook=block_no_such_hook_livecheck_probe.py", RR.DOES_NOT_HOLD),
             ("not a live line", RR.DOES_NOT_HOLD))
    for line, want in cases:
        got = RR.live_reading(line, getattr(fx, "live_check", None), now)     # exactly relentless.py's call
        ok(got["state"] == want and got["state"] != RR.UNREAD, "C: %r reads %s: %s" % (line, want, got))

    with tempfile.TemporaryDirectory() as d:
        text = open(RR.write_live(d, RR.live_reading("once: x", fx.live_check, now)), encoding="utf-8").read()
        ok("HOLDS" in text and "COULD NOT READ" not in text, "D: live.txt says HOLDS: %r" % text)
    with tempfile.TemporaryDirectory() as d:
        text = open(RR.write_live(d, RR.live_reading("not a live line", fx.live_check, now)), encoding="utf-8").read()
        ok("DOES NOT HOLD" in text and "COULD NOT READ" not in text, "D: live.txt says DOES NOT HOLD: %r" % text)

    if FAILS:
        print("FAIL selftest_livecheck_reader: %d" % len(FAILS))
        return 1
    print("PASS selftest_livecheck_reader")
    return 0


if __name__ == "__main__":
    sys.exit(main())
