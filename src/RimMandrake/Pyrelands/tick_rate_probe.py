#!/usr/bin/env python3
"""tick_rate_probe.py -- how fast can THIS map's clock go? (PYRE_SITE_REBUILD_ANIMA_STILL_SAVED, 2026-10-12)

The Pyrelands suite spends ~690,000 of its ~730,000 game ticks in two rows (embergrass_regrow 423,000;
scorchfruit_spoils 270,000). Three routes advance the clock, each measured here on the CURRENT map against the
real ticksGame (never a tool's own count):
  stepped   rimworld/step_game_ticks (validation._wait for n <= 5000): 1 tick per frame, ~53-60 ticks/s MEASURED
  ultrafast rimworld/set_time_speed Ultrafast + poll (validation._wait for long waits): ~200 ticks/s MEASURED
            2026-10-12 (272,520 ticks in ~1,354 s on the 250x250 site, 23-mod tier)
  burst     jawa/gss_stage kind=gss_ticks|n=2000: TickManager.DoSingleTick() x n inside ONE main-thread call, so no
            frame renders between ticks. GSS-only and capped at 2000 per call; UNMEASURED as a rate. If it beats
            ultrafast clearly, a general jawa/tick_burst tool is worth building (spec: Transient/pyre_site_2026-10-12.md).

Bridge holder, game up, the site current and PAUSED (it pauses again on exit, whatever happens):
  python.exe src/RimMandrake/Pyrelands/tick_rate_probe.py [--seconds 20] [--out <json>]
"""
import argparse
import json
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_UTILS = os.path.join(os.path.dirname(os.path.dirname(_HERE)), "RimMandrake", "Utils")
for p in (_UTILS, os.path.join(_UTILS, "modcheck")):
    if p not in sys.path:
        sys.path.insert(0, p)


def rate(t0, t1, w0, w1):
    """ticks per wall second, or None when the clock or the wall did not move."""
    if t0 is None or t1 is None or w1 <= w0 or t1 <= t0:
        return None
    return round((t1 - t0) / (w1 - w0), 1)


def _ticks(s):
    r = s.call("jawa/time_clock") or {}
    return r.get("ticksGame")


def probe(s, seconds=20.0, burst_calls=5):
    out = {}
    # stepped: 600 ticks, as t.wait_ticks issues them
    t0, w0 = _ticks(s), time.time()
    s.call("rimworld/step_game_ticks", ticks=600, pauseFirst=True, timeoutMs=60000)
    out["stepped"] = {"ticks": (_ticks(s) or 0) - (t0 or 0), "tps": rate(t0, _ticks(s), w0, time.time())}
    # ultrafast: `seconds` of wall clock
    t0, w0 = _ticks(s), time.time()
    try:
        s.call("rimworld/set_time_speed", speed="Ultrafast")
        time.sleep(seconds)
    finally:
        s.call("rimworld/set_time_speed", speed="Paused")
    t1, w1 = _ticks(s), time.time()
    out["ultrafast"] = {"ticks": (t1 or 0) - (t0 or 0), "tps": rate(t0, t1, w0, w1)}
    # burst: GSS's synchronous DoSingleTick loop
    t0, w0 = _ticks(s), time.time()
    replies = []
    for _ in range(burst_calls):
        r = s.call("jawa/gss_stage", ops="id=burst|kind=gss_ticks|n=2000") or {}
        replies.append(r.get("success"))
        if r.get("success") is False:
            out["burst_refused"] = str(r)[:300]
            break
    t1, w1 = _ticks(s), time.time()
    out["burst"] = {"ticks": (t1 or 0) - (t0 or 0), "tps": rate(t0, t1, w0, w1), "calls": replies}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seconds", type=float, default=20.0)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    from northstar_driver.session import FastSession
    s = FastSession(strict=False)
    with s:
        try:
            res = probe(s, a.seconds)
        finally:
            s.call("rimworld/set_time_speed", speed="Paused")
        res["mapInfo"] = {k: (s.call("jawa/map_info") or {}).get(k) for k in ("mapId", "mapBiome", "sizeX")}
    print(json.dumps(res, indent=1))
    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="\n") as f:
            json.dump(res, f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
