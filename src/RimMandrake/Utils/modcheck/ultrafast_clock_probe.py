#!/usr/bin/env python3
"""MODCHECK_ULTRAFAST_CLOCK_STALL_1 live clause A1: does the validation suites' fast wait move the clock?

On a Playing map, paused, runs helpers.fast_advance for --ticks (default 3000) game ticks -- the exact call the seven
validation _wait helpers now make (rimworld/play_for at Ultrafast, then jawa/set_game_speed Paused) -- and reads
ticksGame before and after. It advances the game clock by about --ticks (that is the clause), touches nothing else.
  exit 0  the fast run reached its goal (why=None), ticksGame moved >= ticks-400 within --wall seconds, every play_for
          asked for speed 4 (Ultrafast), the observed rate is >= --min-rate ticks/s (Normal is 60/s), game paused
  exit 1  the fast run gave up (refused / stalled), moved too little, ran slower than --min-rate or at another speed
  exit 2  no clock to read (no map loaded, bridge down): UNMEASURED
Usage: python3 src/RimMandrake/Utils/modcheck/ultrafast_clock_probe.py [--ticks N] [--wall S] [--min-rate R]
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
        self.c, self.speeds = client, []

    def call(self, tool, **p):
        if tool == "rimworld/play_for":
            self.speeds.append(p.get("speed"))
        return self.c.call(tool, p)


def judge(start, now, why, wall, paused, speeds, ticks, wall_max, min_rate):
    """-> (ok, reasons). The verdict alone, so selftest_fastwait can prove it rejects a slow or non-Ultrafast run."""
    bad = []
    moved = (now or start) - start
    if why is not None:
        bad.append("fast run gave up: %s" % why)
    if moved < ticks - 400:
        bad.append("moved %d < %d" % (moved, ticks - 400))
    if wall > wall_max:
        bad.append("wall %.1fs > %.1fs" % (wall, wall_max))
    if not speeds or any(sp != 4 for sp in speeds):
        bad.append("play_for speeds %s, not all 4 (Ultrafast)" % (speeds,))
    rate = moved / wall if wall > 0 else 0.0
    if rate < min_rate:
        bad.append("rate %.0f ticks/s < %.0f (Normal is 60)" % (rate, min_rate))
    if paused is not True:
        bad.append("game not paused after (paused=%s)" % paused)
    return not bad, bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticks", type=int, default=3000)
    ap.add_argument("--wall", type=float, default=120.0)
    ap.add_argument("--min-rate", type=float, default=150.0)
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
    print("fast_advance %d ticks: start=%d now=%s moved=%d why=%s wall=%.1fs rate=%.0f/s speeds=%s paused=%s"
          % (a.ticks, start, now, moved, why, wall, moved / wall if wall > 0 else 0.0, sorted(set(s.speeds)), paused))
    ok, bad = judge(start, now, why, wall, paused, s.speeds, a.ticks, a.wall, a.min_rate)
    for b in bad:
        print("FAIL  " + b)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
