"""fresh.py -- a fresh quick-test map on game A, the clock set to a morning hour, and the story layout's shift.

  python.exe ralph/live/fresh.py [--hour 8] [--keep]     (--keep: no new map, only the clock and the shift)

Prints SHIFT=dx,dz: the offset that puts story1's compound round the colonists (story1 reads FW_SHIFT).
"""
import argparse
import json
import re
import sys
import time

import fwb


def local_hour(B):
    # vanilla GenDate.HourOfDay: (TicksAbs + TimeZoneAt(longitude) * 2500) % 60000 / 2500, TimeZoneAt = round(lon / 15)
    r = B.call("jawa/time_date_at") or {}
    lon, ta = r.get("longitude"), r.get("absTicksUsed")
    if lon is None or ta is None:
        return None, json.dumps(r, default=str)[:300]
    tz = int(round(max(-12.0, min(12.0, lon / 15.0))))
    return ((ta + tz * 2500) % 60000) // 2500, "lon %.1f tz %d abs %d" % (lon, tz, ta)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--hour", type=int, default=8)
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args()
    B = fwb.FW()
    if not a.keep:
        gi = B.call("rimworld/get_game_info") or {}
        if (gi.get("state") or {}).get("programState") == "Playing":
            # the quick test starts only from the main menu
            r = B.call("rimworld/go_to_main_menu") or {}
            print("menu", json.dumps(r, default=str)[:200], flush=True)
            for _ in range(60):
                time.sleep(2)
                st = (B.call("rimworld/get_game_info") or {}).get("state") or {}
                if st.get("programState") == "Entry" and not st.get("hasCurrentGame"):
                    break
        r = B.call("rimworld/start_debug_game_ready", readiness="playable", pauseIfNeeded=True, timeoutMs=180000) or {}
        print("start", json.dumps(r, default=str)[:300])
        time.sleep(3)
    B.call("rimworld/set_time_speed", speed="Paused")
    h, raw = local_hour(B)
    print("hour", h, raw)
    clk = (B.call("jawa/time_clock") or {})
    t = clk.get("ticksGame") or clk.get("TicksGame") or (clk.get("state") or {}).get("ticksGame")
    print("clock", json.dumps(clk, default=str)[:300])
    if h is not None and t is not None and h != a.hour:
        dt = ((a.hour - h) % 24) * 2500
        r = B.call("jawa/time_set_ticks", ticks=int(t) + dt, timeException=True,
                   why="Artisan pass 3: daylight for play-zoom shots of the pit story") or {}
        print("time_set", json.dumps(r, default=str)[:200])
        print("hour now", local_hour(B)[0])
    cen = B.call("jawa/pawn_census", faction="player") or {}
    cols = [p for p in cen.get("pawns") or [] if p.get("isColonist")]
    xs = [p["x"] for p in cols]
    zs = [p["z"] for p in cols]
    if xs:
        mx, mz = sum(xs) // len(xs), sum(zs) // len(zs)
        print("colonists", [(p.get("name"), p["x"], p["z"]) for p in cols])
        print("SHIFT=%d,%d" % (mx - 140, mz - 139))
    gi = B.call("rimworld/get_game_info") or {}
    print("map", json.dumps(gi.get("map") or gi.get("state"), default=str)[:300])


if __name__ == "__main__":
    main()
