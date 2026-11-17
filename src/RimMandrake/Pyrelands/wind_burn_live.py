"""LIVE test of "the wind carries the fire" (RIMMANDRAKE_RESCUE_PYRELANDS_BLACK_RAIN_DOUSES_NEEDED_FIRE). UNRUN as of 2026-11-16.

Game up on the pyrelands tier, a Pyrelands map current, the bridge held:
    python.exe src\\RimMandrake\\Pyrelands\\wind_burn_live.py

What it reads, on two grassed strips of the real map (each 60 x 21 cells of ember grass on deep ash, ringed bare):
  A  wind on:  a 9-cell line lit at the west end with the wind set east. After 10,000 ticks the burn has gone east (the
     easternmost burn stamp at least 4 cells on), the fires at once never passed 3 x the cells lit, and no cell north or
     south of the lit lanes by more than 3 burned. (Bar burn_line_walks: fire that moves; never a flood.)
  B  wind off (windCarriesFireEnabled false): the same line. The burn spreads to both sides (more than 3 lanes beyond the
     lit ones): the control that shows the instrument can see vanilla's even spread.
Then black rain on a third strip under the wind: every fire out within 2,000 ticks (bar three_skies). Row C counts only
when the line actually lit under the rain (firesStarted > 0): an unlit line reads 0 fires from the first sample and
used to pass (first live run, 2026-11-16, RIMMANDRAKE_RUN_PYRELANDS_WEEK_SKY_FREE_NEVER_ONCE_SEEN).
Writes Transient/wind_burn_live.json and prints PASS or FAIL with each reading. Settings, weather and fires are put back.
"""
import json
import sys

sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402

S = "RimMandrake.Pyrelands.RM_PyrelandsSettings"
BURN = "RimMandrake.Pyrelands.MapComponent_BurnLine"
SET = {"burnLineEnabled": "True", "fireHawkSpreadEnabled": "False", "fireClockEnabled": "False", "burrowOnFireEnabled": "False",
       "furnaceThermalEnabled": "False", "scorchFruitEnabled": "False"}
W = "0,0,250,250"
out = {}


def verdict_rows(a, b, c):
    """The five rows from the three readings. C counts only a line that lit: 0 fires from an unlit line is no reading."""
    ser = c["fires_at_0_then_every_250"]
    return [
        ("A the burn moves downwind", a["east_cells"] >= 4, a["east_cells"]),
        ("A never more fires than 3 x the cells lit", a["lit"] > 0 and a["peak_fires"] <= 3 * a["lit"], a["peak_fires"]),
        ("A nothing burns beside the lit lanes", a["fires_in_outer_lanes"] == 0, a["fires_in_outer_lanes"]),
        ("B CONTROL even spread reaches the outer lanes", b["fires_in_outer_lanes"] > 0, b["fires_in_outer_lanes"]),
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
            return rb.call("jawa/list_things", {"defName": "Fire", "limit": 1, "rect": rect}).get("countMatched") or 0

        def strip(x, z):
            """60 x 21 ember grass on deep ash at (x, z), a 4-cell bare ring round it. -> the grass rect."""
            rb.call("jawa/set_plants", {"ops": "CLEAR:%d,%d,68,29" % (x - 4, z - 4)})
            rb.call("jawa/set_terrain", {"x": x - 4, "z": z - 4, "terrainDef": "RM_FE_Ash_Deep", "width": 68, "height": 29, "layer": "top"})
            rect = "%d,%d,60,21" % (x, z)
            rb.call("jawa/set_plants", {"ops": "RM_FE_Plant_EmberGrass:" + rect, "growth": 1.0})
            return rect

        def run(x, z, wind_on, label):
            setf("windCarriesFireEnabled", wind_on)
            rect = strip(x, z)
            rb.call("jawa/map_fire", {"action": "extinguish", "rect": W})
            lit = rb.call("jawa/map_fire", {"action": "start", "rect": "%d,%d,1,9" % (x + 2, z + 6), "fireSize": 0.35}).get("firesStarted") or 0
            peak, east, wide = 0, 0, 0
            for _ in range(20):
                adv(500)
                peak = max(peak, fires(rect))
                for dx in range(59, 2, -1):                       # the easternmost column holding a fire
                    if fires("%d,%d,1,21" % (x + dx, z)):
                        east = max(east, dx - 2)
                        break
                wide = max(wide, fires("%d,%d,60,3" % (x, z)) + fires("%d,%d,60,3" % (x, z + 18)))   # the outer three lanes each side
            out[label] = {"lit": lit, "peak_fires": peak, "east_cells": east, "fires_in_outer_lanes": wide,
                          "probe": rb.call("jawa/static_call", {"type": BURN, "method": "ProbeWind"})}
            print(label, out[label])
            return out[label]

        try:
            for f, v in SET.items():
                setf(f, v)
            rb.call("jawa/weather_set", {"weather": "Clear", "lockWeather": True})
            out["wind_set"] = rb.call("jawa/static_call", {"type": BURN, "method": "SetWindForTest", "args": "90"})
            a = run(60, 40, True, "A_wind_on")
            b = run(60, 90, False, "B_wind_off_control")
            # black rain on a walking line
            setf("windCarriesFireEnabled", True)
            rect = strip(60, 140)
            rb.call("jawa/map_fire", {"action": "extinguish", "rect": W})
            rb.call("jawa/weather_set", {"weather": "RM_FE_BlackRain", "lockWeather": True})
            adv(4500)
            c_lit = rb.call("jawa/map_fire", {"action": "start", "rect": "62,146,1,9", "fireSize": 0.35}).get("firesStarted") or 0
            ser = [fires(rect)]                                   # tick 0: what the rain is given to put out
            for _ in range(8):
                adv(250)
                ser.append(fires(rect))
            out["C_black_rain"] = {"lit": c_lit, "fires_at_0_then_every_250": ser}
            rows = verdict_rows(a, b, out["C_black_rain"])
            out["rows"] = [[n, bool(ok), v] for n, ok, v in rows]
            out["verdict"] = "PASS" if all(ok for _, ok, _ in rows) else "FAIL"
            for n, ok, v in rows:
                print("%-4s %s: %s" % ("ok" if ok else "FAIL", n, v))
            print(out["verdict"])
        finally:
            rb.call("jawa/map_fire", {"action": "extinguish", "rect": W})
            rb.call("jawa/weather_set", {"weather": "Clear", "lockWeather": True})
            adv(60)
            rb.call("jawa/weather_set", {"unlock": True})
            for f, v in prior.items():
                setf(f, v)
    json.dump(out, open(r"Transient\wind_burn_live.json", "w"), indent=1)


if __name__ == "__main__":
    main()
