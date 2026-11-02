#!/usr/bin/env python3
"""MODCHECK_ULTRAFAST_CLOCK_STALL_1 live clause A1: does the validation suites' fast wait move the clock?

On a Playing map, paused, runs helpers.fast_advance for --ticks (default 3000) game ticks -- the exact call the seven
validation _wait helpers now make (rimworld/play_for at Ultrafast, then jawa/set_game_speed Paused) -- and reads
ticksGame before and after. It advances the game clock by about --ticks (that is the clause), touches nothing else.
  exit 0  the fast run reached its goal (why=None) and ticksGame moved >= ticks-400 within --wall seconds, game paused
  exit 1  the fast run gave up (refused / stalled) or moved too little: the stall is still there
  exit 2  no clock to read (no map loaded, bridge down): UNMEASURED
Usage: python3 src/RimMandrake/Utils/modcheck/ultrafast_clock_probe.py [--ticks N] [--wall S]
"""
import argparse
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
import clockgate  # noqa: E402
import helpers as H  # noqa: E402
import rimbridge_client as rb  # noqa: E402


class _Session(object):
    def __init__(self, client):
        self.c = client

    def call(self, tool, **p):
        return self.c.call(tool, p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticks", type=int, default=3000)
    ap.add_argument("--wall", type=float, default=120.0)
    a = ap.parse_args()
    h, p, tok = rb.resolve_endpoint()
    c = rb.RimBridge(host=h, port=p, token=tok, timeout=60.0)
    try:
        c.connect()
    except Exception as e:                                      # noqa: BLE001
        print("UNMEASURED bridge unreachable: %s" % e)
        return 2
    s = _Session(c)
    t0 = time.time()
    start, now, why = H.fast_advance(s, a.ticks)
    wall = time.time() - t0
    if start is None:
        print("UNMEASURED clock unreadable (no map loaded?)")
        return 2
    try:
        paused = clockgate._field(clockgate.read_clock(s), "paused")
    except clockgate.ClockLost:
        paused = None
    moved = (now or start) - start
    print("fast_advance %d ticks: start=%d now=%s moved=%d why=%s wall=%.1fs paused=%s"
          % (a.ticks, start, now, moved, why, wall, paused))
    ok = why is None and moved >= a.ticks - 400 and wall <= a.wall and paused is True
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
