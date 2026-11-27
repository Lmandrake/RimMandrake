#!/usr/bin/env python3
"""selftest_ops_watch_fleet_runway.py — the fleet-moved runway and the fleet-stop alarm, replayed from the recorded
account readings of 2026-11-17 (RIMMANDRAKE_READ_FLEET_MOVED_RUNWAY_IDLE_ACCOUNT_READS_TEN).

runway() judges each account by its own burn, so an account not in use read 10 and nothing warned before the fleet
stops of 2026-11-17 03:35 and 05:50 PST. Replays selftest_ops_watch_fleet_runway_20261117.json through the real
ops_watch.fleet_readings, the real slot_allocator.slope (on a series file cut at each replay instant), the real
account plan's week ahead (the plan pinned in the fixture) and the real ops_watch_rules.json targets (andon):
  1. the FLEET_STOP_NEAR alarm stands at least an hour before the 03:35 stop;
  2. it stands before the 05:50 stop;
  3. at 00:10 the idle system account's plain runway reads 10 while its fleet-moved runway reads under 1;
  4. a quiet day (2026-11-12, every 30 min) raises no FLEET_STOP_NEAR, and every fleet_stop_h there is MEASURED.

    python3 src/RimMandrake/Utils/selftest_ops_watch_fleet_runway.py      -> "N of 4"
"""
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
TMP = Path(tempfile.mkdtemp(prefix="selftest_fleet_runway_"))
os.environ["RM_ACCOUNT_USAGE_DIR"] = str(TMP)        # slot_allocator.slope reads the cut series here, never the live one
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
import account_usage as AU  # noqa: E402
import ops_watch as OW  # noqa: E402
import slot_allocator as SA  # noqa: E402

FIX = json.loads((HERE / "selftest_ops_watch_fleet_runway_20261117.json").read_text())
RULES = json.loads((HERE / "ops_watch_rules.json").read_text())
PLAN, LIVE = FIX["plan"], FIX["live"]
ROWS = sorted(({**r, "_t": OW.epoch(r["ts"])} for r in FIX["rows"]), key=lambda r: r["_t"])
STOP1, STOP2 = (OW.epoch(s) for s in FIX["stops"])
Q0, Q1 = (OW.epoch(s) for s in FIX["quiet_day"])
HOUR = 3600.0
RESULTS = []


def case(ok, what, detail=""):
    RESULTS.append(ok)
    print(("PASS " if ok else "FAIL ") + what + ("" if ok else "  " + str(detail)))


def at(t):
    """-> (points, FLEET_STOP_NEAR alarm flags, meter) as ops_watch would read them at t."""
    sub = [r for r in ROWS if r["_t"] <= t]
    (TMP / "series.jsonl").write_text("".join(json.dumps({k: v for k, v in r.items() if k != "_t"}) + "\n"
                                              for r in sub))
    latest = {}
    for r in sub:
        latest[r["account"]] = r
    meter = {n: AU.derive_record({k: v for k, v in r.items() if k != "_t"}, t) for n, r in latest.items()}
    pts = OW.fleet_readings(meter, LIVE, t, RULES, SA.slope, PLAN)
    al = [f for f in OW.andon(pts, {}, {}, RULES, t) if f.get("tag") == "FLEET_STOP_NEAR" and f.get("alarm")]
    return pts, al, meter


def grid(t0, t1, step=1800):
    t = t0
    while t < t1:
        yield t
        t += step


# 1. the alarm stands an hour or more before the 03:35 stop
fired = [t for t in grid(STOP1 - 12 * HOUR, STOP1, 900) if at(t)[1]]
case(bool(fired) and fired[0] <= STOP1 - HOUR,
     "FLEET_STOP_NEAR stands before the 03:35 stop (first at %s, %.1f h ahead)" % (
         OW.iso(fired[0]) if fired else None, (STOP1 - fired[0]) / HOUR if fired else 0), fired[:3])

# 2. it stands before the 05:50 stop (the plan was already stopped: the forecast reads 0, the pool has no room)
pts2, al2, _m = at(STOP2 - 5 * 60)
case(bool(al2) and pts2["accounts.fleet_stop_h"]["v"] == 0.0,
     "FLEET_STOP_NEAR stands 5 min before the 05:50 stop, fleet_stop_h 0", pts2["accounts.fleet_stop_h"])

# 3. the idle system account: plain runway 10, fleet-moved runway under 1 (the fleet's burn empties it first)
t3 = OW.epoch("2026-11-17T00:10:13-08:00")
pts3, _al, m3 = at(t3)
sysr = m3["system"]
own, _n, _span = SA.slope("system", sysr["week_resets_at"], t3, {"fit": RULES["accounts_fit"]})
plain = OW.runway(sysr["week_pct_left"], own, sysr["hours_to_week_reset"])
moved = pts3["accounts.system.moved_runway"]
case(plain == 10.0 and moved["m"] == "MEASURED" and moved["v"] < 1.0,
     "idle system at 00:10: plain runway %s, fleet-moved runway %s" % (plain, moved.get("v")), (plain, moved))

# 4. a quiet day: no alarm, and the instrument saw (every forecast MEASURED, not blind)
quiet = [(t, at(t)) for t in grid(Q0, Q1)]
loud = [OW.iso(t) for t, (p, al, _m) in quiet if al]
blind = [OW.iso(t) for t, (p, al, _m) in quiet if p["accounts.fleet_stop_h"]["m"] != "MEASURED"]
case(len(quiet) == 48 and not loud and not blind,
     "quiet day 2026-11-12: %d readings, %d alarms, %d not MEASURED" % (len(quiet), len(loud), len(blind)),
     (loud[:3], blind[:3]))

print("%d of %d" % (sum(RESULTS), len(RESULTS)))
sys.exit(0 if all(RESULTS) and len(RESULTS) == 4 else 1)
