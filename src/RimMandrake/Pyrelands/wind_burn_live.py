"""LIVE test of "the wind carries the fire" (RIMMANDRAKE_RESCUE_PYRELANDS_BLACK_RAIN_DOUSES_NEEDED_FIRE).

Game up on the pyrelands tier, a Pyrelands map current, the bridge held:
    python.exe src\\RimMandrake\\Pyrelands\\wind_burn_live.py

What it reads, on four strips of the real map (each 61 x 21 cells of ember grass on deep ash, ringed bare). Every line is a
9-cell line lit across the wind in the MIDDLE of its strip, so 30 cells of grass lie upwind of it and 30 downwind
(RIMMANDRAKE_REVERSE_PYRE_WIND_BEARING_ONE_DIRECTION_STAGED: a line lit at the upwind end has no upwind ground to read, and one
wind cannot show the wind is the cause). The scene burns at the shipped Fire pace (RM_BurnKernel.FirePacePercentDefault, set
with the other settings, read back, put back after) and reads each strip over the window in which the line walks what 0.1.0's
walked in 10,000 ticks, about 8 cells: 10,000 x 100 / pace ticks, in 20 samples (window_ticks; Conductor ruling 2026-11-27
4:36 AM PST, on the pyre020 fire_pace.md finding: the rows are read in distance walked, not ticks):
  F  wind set east (SetWindForTest 90), wind on: over the window the burn has run further downwind than upwind.
  R  the same with the wind REVERSED (SetWindForTest 270): the burn turns and runs west. F and R together tell a fire that
     follows the wind from a mod that blocks sideways spread, or walks one way, whatever the wind.
     In F and R, at each of the 20 samples, the fires at once stay within a line one fire-life deep across the strip's inner
     lanes (peak_limit: the burning depth, fire life over the carry interval, sets it, not a fixed multiple of the cells lit),
     no one lane (one row of the strip) holds more than that depth burning at once (lane_reading), and nothing burns in the
     outer three lanes each side (a fire that comes and goes between two samples is not seen).
  B  wind off (windCarriesFireEnabled false), wind east: the burn reaches the outer lanes and runs both ways along the strip,
     leaning less than either wind run (the control: the instrument sees vanilla's even spread, and has no east bias). The
     Fire pace does not touch vanilla's spread, so B is read over 0.1.0's own 10,000 ticks at every pace (run_window).
  C  black rain on a fourth strip under the wind: every fire out within 2,000 ticks (bar three_skies). Counts only when the
     line actually lit under the rain (an unlit line reads 0 fires from the first sample and used to pass: first live run,
     2026-11-16, RIMMANDRAKE_RUN_PYRELANDS_WEEK_SKY_FREE_NEVER_ONCE_SEEN).
Before each line is lit it asserts the start: SetWindForTest returned the bearing asked, ProbeWind reads that bearing back
with carries= matching the wind switch, the Fire pace reads back as the shipped default, and the strip holds no fire.
Restore (RIMMANDRAKE_SAVE_RELOAD_AROUND_EVERY_TEST_SCENE): the scene runs inside modcheck/scene_snapshot.py, which saves a
unique wind_burn_live_pre_<hex> before anything changes and reloads it after, also when the scene raises; the mod settings
(not in a save) are put back by hand. The JSON's "snapshot" records the save name and the reload's verified.
Writes Transient/wind_burn_live.json and prints each row with its reading, then PASS or FAIL (FAIL too when the reload fails).
Offline: selftest_pyrelands_wind_burn_rows.py drives these rows from pyre_burn_sim.py's model of the shipped carry.
"""
import json
import os
import re
import sys

_UTILS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils")
sys.path.insert(0, _UTILS)
sys.path.insert(0, os.path.join(_UTILS, "modcheck"))
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402
from scene_snapshot import scene_snapshot  # noqa: E402

S = "RimMandrake.Pyrelands.RM_PyrelandsSettings"
BURN = "RimMandrake.Pyrelands.MapComponent_BurnLine"
STRIP_W, STRIP_H = 61, 21
_KERNEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Source", "Kernel", "RM_BurnKernel.cs")


def kernel_const(name, path=_KERNEL):
    """An int const of RM_BurnKernel, read from the C# (never a copied number)."""
    with open(path, encoding="utf-8") as fh:
        m = re.search(r"const int %s = (\d+);" % name, fh.read())
    if not m:
        raise RuntimeError("RM_BurnKernel.%s not found in %s" % (name, path))
    return int(m.group(1))


PACE_MIN, PACE_DEFAULT, PACE_MAX = (kernel_const(n) for n in ("FirePacePercentMin", "FirePacePercentDefault", "FirePacePercentMax"))
CARRY_TICKS_010 = kernel_const("WindCarryTicks")      # the least ticks before a fire is carried on, at 0.1.0's pace (PACE_MIN)
# The window at 0.1.0's pace: the scene's own 10,000 ticks (a number of the check, sized to 0.1.0's walk), in which the line
# walks about 8 cells (measured in the model at pace 100: 6 to 8 cells downwind over 80 runs). At pace p the line walks as far
# in 10,000 x PACE_MIN / p ticks (CarryTicks and CarryExtraTicks both scale by 100 / pace).
WINDOW_TICKS_010 = 10000
SAMPLES = 20
# The longest an ember-grass fire lit by the carry burns, in ticks: the carry lights at Fire.MinFireSize 0.1; vanilla's
# Fire.DoFireDamage takes (0.0125 + 0.0036 x size) x 150 hit points a 150-tick beat, rounded at random: 1.93 at size 0.1 (so 1
# or 2), at least 2 once the fire has grown one beat (+0.00055 x Flammability 1.6 x 150 = +0.132); ember grass holds 28 hit
# points (Defs/ThingDefs_Plants/EmberGrass.xml, MaxHitPoints): gone by beat 1 + ceil(27 / 2) = 15 at the latest, 2,250 ticks.
# (RM_BurnKernel.WindCarryExtraTicks names the mean, 12 to 13 beats, 1,800.) The selftest reads 28 and 1.6 from the def and
# holds every fire of the model under it.
EMBER_GRASS_HP = 28
EMBER_GRASS_FLAMMABILITY = 1.6
FIRE_LIFE_MAX = 150 * (1 + -(-(EMBER_GRASS_HP - 1) // 2))
OUTER_LANES = 3    # the outer three lanes each side of the 21-lane strip: no fire there with the wind on


def clamp_pace(pace):
    """RM_BurnKernel.ClampPace."""
    return max(PACE_MIN, min(PACE_MAX, int(pace)))


def carry_ticks(pace):
    """RM_BurnKernel.CarryTicks: the least ticks after it is lit that a fire is carried on at this Fire pace."""
    return CARRY_TICKS_010 * 100 // clamp_pace(pace)


def window_ticks(pace):
    """The ticks the scene reads a strip for at this Fire pace: as far walked as 0.1.0's line in WINDOW_TICKS_010; a whole
    number of SAMPLES samples."""
    return WINDOW_TICKS_010 * PACE_MIN // clamp_pace(pace) // SAMPLES * SAMPLES


def run_window(pace, wind_on):
    """The ticks one strip is read for. With the wind on, window_ticks(pace). The wind-off control is vanilla's even spread,
    which the Fire pace does not touch (the only reader of firePacePercent is the carry, FireEcologyHook.cs WindCarriedFire),
    so it walks 0.1.0's distance in 0.1.0's window at every pace."""
    return window_ticks(pace) if wind_on else WINDOW_TICKS_010


def rows_deep(pace):
    """The burning depth: the most cells of one lane a walking line holds burning at once. A lane's next cell is lit no
    sooner than carry_ticks after the last and each burns at most FIRE_LIFE_MAX, so floor(life / interval) + 1 overlap."""
    return FIRE_LIFE_MAX // carry_ticks(pace) + 1


def peak_limit(pace, strip_h=None):
    """The most fires a line can hold at once on a strip: every lane inside the outer lanes, each rows_deep deep. More is a
    burn that is not a line (fire running sideways or back, or living past its fuel)."""
    return ((STRIP_H if strip_h is None else strip_h) - 2 * OUTER_LANES) * rows_deep(pace)


SET = {"burnLineEnabled": "True", "fireHawkSpreadEnabled": "False", "fireClockEnabled": "False", "burrowOnFireEnabled": "False",
       "furnaceThermalEnabled": "False", "scorchFruitEnabled": "False", "firePacePercent": str(PACE_DEFAULT)}
W = "0,0,250,250"
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


def peak_reading(x):
    """(ok, text) for one wind run's peak: the most fires at one sample against peak_limit at the pace the game read back."""
    pace = as_int(x.get("pace"))
    if pace is None or x["lit"] <= 0:
        return False, "pace %r lit %d: no limit to read against" % (x.get("pace"), x["lit"])
    lim = peak_limit(pace)
    return x["peak_fires"] <= lim, "%d of limit %d (%d lanes x %d deep at pace %d; %.1f x the %d lit)" % (
        x["peak_fires"], lim, STRIP_H - 2 * OUTER_LANES, rows_deep(pace), pace, x["peak_fires"] / float(x["lit"]), x["lit"])


def lane_reading(x):
    """(ok, text) for one wind run's deepest lane: the most fires burning at once in one lane along the wind (one row of the
    strip), against rows_deep at the pace the game read back. The direct reading of "a line one fire-life deep": a flood
    is many cells deep in its lanes even where its sum stays under peak_limit (model, flood fault at pace 200: lanes 9 deep
    of 4 while the peak passed on 10 of 40 seeds)."""
    pace = as_int(x.get("pace"))
    deep = as_int(x.get("lane_depth"))
    if pace is None or deep is None or x["lit"] <= 0:
        return False, "pace %r lane depth %r lit %d: no limit to read against" % (x.get("pace"), x.get("lane_depth"), x["lit"])
    return deep <= rows_deep(pace), "%d of limit %d (fire life %d / carry %d ticks at pace %d, + 1)" % (
        deep, rows_deep(pace), FIRE_LIFE_MAX, carry_ticks(pace), pace)


def verdict_rows(f, r, b, c):
    """The rows from the four readings. Each run: asked, wind_set, probe, carries_wanted, pace (read back), window_ticks,
    fires_before, lit, peak_fires, down_cells, up_cells (from the lit column, each way along the wind),
    fires_in_outer_lanes, lane_depth (the most fires at once in one row of the strip). C counts only a line that lit."""
    ser = c["fires_at_0_then_every_250"]
    runs = (("F", f), ("R", r), ("B", b))
    lean = min(f["down_cells"] - f["up_cells"], r["down_cells"] - r["up_cells"])
    pf, pr = peak_reading(f), peak_reading(r)
    lf, lr = lane_reading(f), lane_reading(r)
    return [
        ("start the wind reads back as set, carries as its switch", all(start_ok(x) for _, x in runs),
         "; ".join("%s asked %s set %s probe %s" % (n, x["asked"], x["wind_set"], x["probe"]) for n, x in runs)),
        ("start the Fire pace reads back as the shipped default, the window as that pace's",
         all(as_int(x.get("pace")) == PACE_DEFAULT and x.get("window_ticks") == run_window(PACE_DEFAULT, x["carries_wanted"])
             for _, x in runs),
         "; ".join("%s pace %s window %s" % (n, x.get("pace"), x.get("window_ticks")) for n, x in runs)
         + " (default %d; window %d with the wind, %d without)" % (PACE_DEFAULT, run_window(PACE_DEFAULT, True),
                                                                   run_window(PACE_DEFAULT, False))),
        ("start every strip holds no fire before it is lit", all(x["fires_before"] == 0 for x in (f, r, b, c)),
         [x["fires_before"] for x in (f, r, b, c)]),
        ("F wind east: the burn runs further downwind than upwind", f["lit"] > 0 and f["down_cells"] > f["up_cells"],
         "down %d up %d" % (f["down_cells"], f["up_cells"])),
        ("R wind reversed: the burn turns and runs west", r["lit"] > 0 and r["down_cells"] > r["up_cells"],
         "down %d up %d" % (r["down_cells"], r["up_cells"])),
        ("F,R at each of the %d samples no more fires than a line one fire-life deep" % SAMPLES, pf[0] and pr[0],
         "F %s; R %s" % (pf[1], pr[1])),
        ("F,R at each of the %d samples no lane holds more fires than one fire-life deep" % SAMPLES, lf[0] and lr[0],
         "F %s; R %s" % (lf[1], lr[1])),
        ("F,R at each of the %d samples no fire in the outer %d lanes each side" % (SAMPLES, OUTER_LANES),
         f["fires_in_outer_lanes"] == 0 and r["fires_in_outer_lanes"] == 0,
         "F %d R %d (limit 0)" % (f["fires_in_outer_lanes"], r["fires_in_outer_lanes"])),
        ("B CONTROL even spread reaches the outer lanes", b["fires_in_outer_lanes"] > 0,
         "%d (must be above 0)" % b["fires_in_outer_lanes"]),
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
            """Light the mid-strip line and burn run_window(pace, wind_on) in SAMPLES samples. Downwind is east for 90, west
            for 270."""
            window = run_window(pace, wind_on)
            setf("windCarriesFireEnabled", wind_on)
            rect = strip(x, z)
            rb.call("jawa/map_fire", {"action": "extinguish", "rect": W})
            probe = rb.call("jawa/static_call", {"type": BURN, "method": "ProbeWind"}).get("result")
            before = fires(rect)
            lit = rb.call("jawa/map_fire", {"action": "start", "rect": "%d,%d,1,9" % (x + LINE, z + 6), "fireSize": 0.35}
                          ).get("firesStarted") or 0
            sign = 1 if asked == 90 else -1
            peak, down, up, wide, deep = 0, 0, 0, 0, 0
            for _ in range(SAMPLES):
                adv(window // SAMPLES)
                peak = max(peak, fires(rect))
                down = side(x, z, sign, down)
                up = side(x, z, -sign, up)
                wide = max(wide, fires("%d,%d,%d,3" % (x, z, STRIP_W)) + fires("%d,%d,%d,3" % (x, z + STRIP_H - 3, STRIP_W)))
                if wind_on:                       # each lane (one row of the strip, along the wind) counted on its own
                    deep = max([deep] + [fires("%d,%d,%d,1" % (x, z + k, STRIP_W)) for k in range(STRIP_H)])
            out[label] = {"asked": asked, "wind_set": wind_set, "probe": probe, "carries_wanted": bool(wind_on),
                          "pace": pace, "window_ticks": window,
                          "fires_before": before, "lit": lit, "peak_fires": peak, "down_cells": down, "up_cells": up,
                          "fires_in_outer_lanes": wide, "lane_depth": deep if wind_on else None}
            print(label, out[label])
            return out[label]

        snap = None
        try:
            # the map (fires, weather, wind bearing, the strips' ground) comes back by reloading the scene-begin save
            with scene_snapshot(lambda tool, **kw: rb.call(tool, kw), "wind_burn_live_pre_") as snap:
                try:
                    for f, v in SET.items():
                        setf(f, v)
                    # the pace the game holds, read back: it sets the window (never the asked number taken on trust)
                    pace = as_int(rb.call("jawa/mod_settings_field", {"typeName": S, "action": "get",
                                                                      "field": "firePacePercent"}).get("value"))
                    if pace is None:
                        raise RuntimeError("firePacePercent unreadable after the set")
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
