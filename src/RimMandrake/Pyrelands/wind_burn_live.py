"""LIVE test of "the wind carries the fire" (RIMMANDRAKE_RESCUE_PYRELANDS_BLACK_RAIN_DOUSES_NEEDED_FIRE). UNRUN as of 2026-11-17.

Game up on the pyrelands tier, a Pyrelands map current, the bridge held:
    python.exe src\\RimMandrake\\Pyrelands\\wind_burn_live.py

What it reads, on four strips of the real map (each 61 x 21 cells of ember grass on deep ash, ringed bare). Every line is a
9-cell line lit across the wind in the MIDDLE of its strip, so 30 cells of grass lie upwind of it and 30 downwind
(RIMMANDRAKE_REVERSE_PYRE_WIND_BEARING_ONE_DIRECTION_STAGED: a line lit at the upwind end has no upwind ground to read, and one
wind cannot show the wind is the cause):
  F  wind set east (SetWindForTest 90), wind on: after 10,000 ticks the burn has run further downwind than upwind.
  R  the same with the wind REVERSED (SetWindForTest 270): the burn turns and runs west. F and R together tell a fire that
     follows the wind from a mod that blocks sideways spread, or walks one way, whatever the wind.
     In F and R the fires at once never pass 3 x the cells lit, and nothing burns in the outer three lanes each side.
  B  wind off (windCarriesFireEnabled false), wind east: the burn reaches the outer lanes and runs both ways along the strip,
     leaning less than either wind run (the control: the instrument sees vanilla's even spread, and has no east bias).
  C  black rain on a fourth strip under the wind: every fire out within 2,000 ticks (bar three_skies). Counts only when the
     line actually lit under the rain (an unlit line reads 0 fires from the first sample and used to pass: first live run,
     2026-11-16, RIMMANDRAKE_RUN_PYRELANDS_WEEK_SKY_FREE_NEVER_ONCE_SEEN).
Before each line is lit it asserts the start: SetWindForTest returned the bearing asked, ProbeWind reads that bearing back
with carries= matching the wind switch, and the strip holds no fire.
Restore (RIMMANDRAKE_SAVE_RELOAD_AROUND_EVERY_TEST_SCENE): the scene runs inside modcheck/scene_snapshot.py, which saves a
unique wind_burn_live_pre_<hex> before anything changes and reloads it after, also when the scene raises; the mod settings
(not in a save) are put back by hand. The JSON's "snapshot" records the save name and the reload's verified.
Writes Transient/wind_burn_live.json and prints each row with its reading, then PASS or FAIL (FAIL too when the reload fails).
Offline: selftest_pyrelands_wind_burn_rows.py drives these rows from pyre_burn_sim.py's model of the shipped carry.
"""
import json
import os
import sys

_UTILS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils")
sys.path.insert(0, _UTILS)
sys.path.insert(0, os.path.join(_UTILS, "modcheck"))
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402
from scene_snapshot import scene_snapshot  # noqa: E402

S = "RimMandrake.Pyrelands.RM_PyrelandsSettings"
BURN = "RimMandrake.Pyrelands.MapComponent_BurnLine"
SET = {"burnLineEnabled": "True", "fireHawkSpreadEnabled": "False", "fireClockEnabled": "False", "burrowOnFireEnabled": "False",
       "furnaceThermalEnabled": "False", "scorchFruitEnabled": "False"}
W = "0,0,250,250"
STRIP_W, STRIP_H = 61, 21
LINE = 30          # the lit column, mid-strip: 30 cells of grass each way
HALF = 30
out = {}


def parse_probe(p):
    """ProbeWind's "wind=90.0;carries=True;carried=0;fires=0" -> (bearing or None, carries or None)."""
    kv = dict(part.split("=", 1) for part in str(p or "").split(";") if "=" in part)
    try:
        wind = float(kv["wind"])
    except (KeyError, ValueError):
        wind = None
    carries = {"true": True, "false": False}.get(str(kv.get("carries", "")).lower())
    return wind, carries


def as_int(v):
    try:
        return int(float(str(v)))
    except (TypeError, ValueError):
        return None


def start_ok(r):
    """The start the run asserts: the wind it asked for is the wind the game holds, and carries= matches its switch."""
    wind, carries = parse_probe(r["probe"])
    return (as_int(r["wind_set"]) == r["asked"] and wind is not None and abs(wind - r["asked"]) < 0.5
            and carries is r["carries_wanted"])


def verdict_rows(f, r, b, c):
    """The rows from the four readings. Each run: asked, wind_set, probe, carries_wanted, fires_before, lit, peak_fires,
    down_cells, up_cells (from the lit column, each way along the wind), fires_in_outer_lanes. C counts only a line that lit."""
    ser = c["fires_at_0_then_every_250"]
    runs = (("F", f), ("R", r), ("B", b))
    lean = min(f["down_cells"] - f["up_cells"], r["down_cells"] - r["up_cells"])
    return [
        ("start the wind reads back as set, carries as its switch", all(start_ok(x) for _, x in runs),
         "; ".join("%s asked %s set %s probe %s" % (n, x["asked"], x["wind_set"], x["probe"]) for n, x in runs)),
        ("start every strip holds no fire before it is lit", all(x["fires_before"] == 0 for x in (f, r, b, c)),
         [x["fires_before"] for x in (f, r, b, c)]),
        ("F wind east: the burn runs further downwind than upwind", f["lit"] > 0 and f["down_cells"] > f["up_cells"],
         "down %d up %d" % (f["down_cells"], f["up_cells"])),
        ("R wind reversed: the burn turns and runs west", r["lit"] > 0 and r["down_cells"] > r["up_cells"],
         "down %d up %d" % (r["down_cells"], r["up_cells"])),
        ("F,R never more fires than 3 x the cells lit", all(x["lit"] > 0 and x["peak_fires"] <= 3 * x["lit"] for x in (f, r)),
         "F %d/%d R %d/%d" % (f["peak_fires"], f["lit"], r["peak_fires"], r["lit"])),
        ("F,R nothing burns beside the lit lanes", f["fires_in_outer_lanes"] == 0 and r["fires_in_outer_lanes"] == 0,
         "F %d R %d" % (f["fires_in_outer_lanes"], r["fires_in_outer_lanes"])),
        ("B CONTROL even spread reaches the outer lanes", b["fires_in_outer_lanes"] > 0, b["fires_in_outer_lanes"]),
        ("B CONTROL runs both ways, leaning less than the wind runs",
         b["lit"] > 0 and b["down_cells"] > 0 and b["up_cells"] > 0 and abs(b["down_cells"] - b["up_cells"]) < lean,
         "down %d up %d, wind lean %d" % (b["down_cells"], b["up_cells"], lean)),
        ("C black rain puts the line out", c["lit"] > 0 and ser[0] > 0 and ser[-1] == 0, "lit %d, %s" % (c["lit"], ser)),
    ]


def main():
    h, p, tk = resolve_endpoint()
    with RimBridge(h, p, tk) as rb:
        prior = {f: rb.call("jawa/mod_settings_field", {"typeName": S, "action": "get", "field": f}).get("value")
                 for f in list(SET) + ["windCarriesFireEnabled"]}

        def setf(f, v):
            rb.call("jawa/mod_settings_field", {"typeName": S, "action": "set", "field": f, "value": str(v)})

        def adv(n):
            while n > 0:
                s = min(2500, n)
                rb.call("jawa/safe_advance", {"ticks": s, "timeException": False})
                n -= s

        def fires(rect):
            n = rb.call("jawa/list_things", {"defName": "Fire", "limit": 1, "rect": rect}).get("countMatched")
            if n is None:                         # could not look: never a zero-fire reading
                raise RuntimeError("list_things unreadable for Fire in %s" % rect)
            return int(n)

        def strip(x, z):
            """61 x 21 ember grass on deep ash at (x, z), a 4-cell bare ring round it. -> the grass rect."""
            rb.call("jawa/set_plants", {"ops": "CLEAR:%d,%d,%d,%d" % (x - 4, z - 4, STRIP_W + 8, STRIP_H + 8)})
            rb.call("jawa/set_terrain", {"x": x - 4, "z": z - 4, "terrainDef": "RM_FE_Ash_Deep", "width": STRIP_W + 8,
                                         "height": STRIP_H + 8, "layer": "top"})
            rect = "%d,%d,%d,%d" % (x, z, STRIP_W, STRIP_H)
            rb.call("jawa/set_plants", {"ops": "RM_FE_Plant_EmberGrass:" + rect, "growth": 1.0})
            return rect

        def side(x, z, sign, beyond):
            """Cells from the lit column to the farthest fire on one side (sign +1 east, -1 west), at least `beyond`."""
            lo, hi = (x + LINE + beyond + 1, x + LINE + HALF) if sign > 0 else (x + LINE - HALF, x + LINE - beyond - 1)
            if hi < lo or not fires("%d,%d,%d,%d" % (lo, z, hi - lo + 1, STRIP_H)):
                return beyond
            for d in range(HALF, beyond, -1):
                if fires("%d,%d,1,%d" % (x + LINE + sign * d, z, STRIP_H)):
                    return d
            return beyond

        def run(x, z, wind_on, asked, wind_set, label):
            """Light the mid-strip line and burn 10,000 ticks. Downwind is east for 90, west for 270."""
            setf("windCarriesFireEnabled", wind_on)
            rect = strip(x, z)
            rb.call("jawa/map_fire", {"action": "extinguish", "rect": W})
            probe = rb.call("jawa/static_call", {"type": BURN, "method": "ProbeWind"}).get("result")
            before = fires(rect)
            lit = rb.call("jawa/map_fire", {"action": "start", "rect": "%d,%d,1,9" % (x + LINE, z + 6), "fireSize": 0.35}
                          ).get("firesStarted") or 0
            sign = 1 if asked == 90 else -1
            peak, down, up, wide = 0, 0, 0, 0
            for _ in range(20):
                adv(500)
                peak = max(peak, fires(rect))
                down = side(x, z, sign, down)
                up = side(x, z, -sign, up)
                wide = max(wide, fires("%d,%d,%d,3" % (x, z, STRIP_W)) + fires("%d,%d,%d,3" % (x, z + STRIP_H - 3, STRIP_W)))
            out[label] = {"asked": asked, "wind_set": wind_set, "probe": probe, "carries_wanted": bool(wind_on),
                          "fires_before": before, "lit": lit, "peak_fires": peak, "down_cells": down, "up_cells": up,
                          "fires_in_outer_lanes": wide}
            print(label, out[label])
            return out[label]

        snap = None
        try:
            # the map (fires, weather, wind bearing, the strips' ground) comes back by reloading the scene-begin save
            with scene_snapshot(lambda tool, **kw: rb.call(tool, kw), "wind_burn_live_pre_") as snap:
                try:
                    for f, v in SET.items():
                        setf(f, v)
                    rb.call("jawa/weather_set", {"weather": "Clear", "lockWeather": True})
                    east = rb.call("jawa/static_call", {"type": BURN, "method": "SetWindForTest", "args": "90"}).get("result")
                    f = run(60, 30, True, 90, east, "F_wind_east")
                    west = rb.call("jawa/static_call", {"type": BURN, "method": "SetWindForTest", "args": "270"}).get("result")
                    r = run(60, 80, True, 270, west, "R_wind_west")
                    east = rb.call("jawa/static_call", {"type": BURN, "method": "SetWindForTest", "args": "90"}).get("result")
                    b = run(60, 130, False, 90, east, "B_wind_off_control")
                    # black rain on a walking line
                    setf("windCarriesFireEnabled", True)
                    rect = strip(60, 180)
                    rb.call("jawa/map_fire", {"action": "extinguish", "rect": W})
                    rb.call("jawa/weather_set", {"weather": "RM_FE_BlackRain", "lockWeather": True})
                    adv(4500)
                    c_before = fires(rect)
                    c_lit = rb.call("jawa/map_fire", {"action": "start", "rect": "%d,186,1,9" % (60 + LINE), "fireSize": 0.35}
                                    ).get("firesStarted") or 0
                    ser = [fires(rect)]                                   # tick 0: what the rain is given to put out
                    for _ in range(8):
                        adv(250)
                        ser.append(fires(rect))
                    out["C_black_rain"] = {"fires_before": c_before, "lit": c_lit, "fires_at_0_then_every_250": ser}
                    rows = verdict_rows(f, r, b, out["C_black_rain"])
                    out["rows"] = [[n, bool(ok), v] for n, ok, v in rows]
                    out["verdict"] = "PASS" if all(ok for _, ok, _ in rows) else "FAIL"
                    for n, ok, v in rows:
                        print("%-4s %s: %s" % ("ok" if ok else "FAIL", n, v))
                    print("%s (%d of %d rows)" % (out["verdict"], sum(1 for _, ok, _ in rows if ok), len(rows)))
                finally:
                    bad = []
                    for f, v in prior.items():           # every field, even after one write fails
                        try:
                            setf(f, v)
                        except Exception as ex:  # noqa: BLE001 - recorded; the scene's own error keeps propagating
                            bad.append("%s: %r" % (f, ex))
                    out["settings_restore_errors"] = bad
        finally:
            if snap is not None:
                out["snapshot"] = snap.evidence
            if out.get("settings_restore_errors") or (snap is not None and snap.evidence.get("restore_errors")):
                out["verdict"] = "FAIL"
                print("FAIL the scene was not put back: settings %s, reload %s" % (
                    out.get("settings_restore_errors"), snap.evidence.get("restore_errors") if snap else None))
            json.dump(out, open(r"Transient\wind_burn_live.json", "w"), indent=1)
    return 0 if out.get("verdict") == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
