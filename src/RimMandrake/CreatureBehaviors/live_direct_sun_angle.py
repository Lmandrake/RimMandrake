#!/usr/bin/env python3
"""Live test of DIRECT_SUN_LIVE_VERIFY_ANGLE_NOT_BIOME L1: on a fixed-sun world, Direct Sun is a function of the sun's
angle over the tile, never of the biome (design/RimMandrake/unified_direct_sun_heat_2026-10-19.md; promises in
design/specs/2026-11-26-direct-sun/boundary.md). Three rows, each Kind A (deterministic: one valid run decides).

  L1a same angle, same numbers
    claim        one world tile regenerated as each biome in turn (default RM_LongShade, RM_Pyrelands, RM_TheForge) has
                 the same sun elevation E, the same Direct Sun offset (zenith x sin E under clear sky), and the same
                 readings at five probes: a cell and a colonist in the open, under a constructed roof, inside a shade
                 tent, a colonist carrying a parasol, and the shadow ('lee') a wall throws down-sun.
    entry point  the current map of a game whose world has a fixed sun (Creature Behaviors + the Weather Suite with
                 Ash'karr's PlanetGeometryDef: tier direct_sun_fixed), through jawa/shadegrid_read, jawa/read_paths and
                 jawa/static_call RM_SunHeatPatches.SunOffsetFor(pawn|current) (a companion that coerces a MapComponent
                 argument; an older one answers 'Unsupported parameter type' = COULD NOT LOOK).
    opportunity  the map reads sunHeatActive true with E > 0, weather is forced Clear, and the staged square is open
                 ground (no shade, no cause) before staging.
    success      every biome's E, offset, cell exposures, colonist offsets and lee length equal the first biome's (to
                 0.01); the open cell's exposure is above the roofed and tented cells'; the lee is as long as the model
                 says for E (RM_SunHeatMath.ShadowLengthPerHeight(E) x the wall's cast height, +-1 cell).
  L1b air heat is a thermometer reading
    claim        on the Forge, the outdoor temperature with RM_ForgeAirHeat on and off differs by the condition's
                 temperatureOffset (+-0.5 C, read two ticks apart across the condition's hourly sync), and turning it
                 off does not change the open cell's Direct Sun exposure.
  L1c the sun stands still
    claim        on a fixed-sun map E reads the same at four points across one in-game day.
  forbidden      a red error in the log naming RM_MapComponent_ShadeGrid, RM_SunHeat or RM_AirHeat during the run.
  end            the Forge's air heat is restored to its value at start; the weather lock is removed.

What this cannot decide: "the lee is long at low E and absent at high E" needs two tiles of different E, and the
regenerate keeps the tile; that half is the C# selftest's case "a shadow is h / tan E long" (selftest_sun_heat.py).
Live here: the lee length matches the model at this tile's E in every biome.

Run on the machine that hosts the game, with that game's environment, a quicktest map loaded on tier direct_sun_fixed:
    python.exe src/RimMandrake/CreatureBehaviors/live_direct_sun_angle.py [--biomes RM_LongShade,RM_Pyrelands,RM_TheForge]
It writes its result to design/specs/2026-11-26-direct-sun/live_angle_result.json (commit it with the run's log).
    python3 src/RimMandrake/CreatureBehaviors/live_direct_sun_angle.py --verdict
reads that file: exit 0 when L1a, L1b and L1c each read PASS, 1 otherwise (the item's outcome check).
Exit codes of a run: 0 PASS, 1 FAIL (MOD FAILURE), 2 COULD NOT LOOK (the cause named).
"""
import argparse
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path[:0] = [os.path.join(ROOT, "src", "RimMandrake", "Utils")]
RESULT = os.path.join(ROOT, "design", "specs", "2026-11-26-direct-sun", "live_angle_result.json")
ROWS = ("L1a", "L1b", "L1c")

HALF = 10              # the staged square is (2 HALF + 1) cells wide
RECOMPUTE = 2001       # the shade grid rebuilds every 2000 ticks
WEATHER_SETTLE = 4200  # a weather transition lerps over about 4000 ticks
SYNC = 2500            # RM_MapComponent_AirHeat syncs at TicksGame % 2500 == 41
TOL = 0.01


class CouldNotLook(Exception):
    pass


def verdict():
    try:
        r = json.load(open(RESULT, encoding="utf-8"))
    except (OSError, ValueError) as e:
        print("NO RESULT: %s (%s): run the live scene first" % (RESULT, e))
        return 1
    rows = r.get("rows") or {}
    bad = [k for k in ROWS if (rows.get(k) or {}).get("verdict") != "PASS"]
    for k in ROWS:
        print("%s %s" % (k, (rows.get(k) or {}).get("verdict", "ABSENT")))
    return 0 if not bad else 1


def call(s, tool, **kw):
    r = s.call(tool, **kw) or {}
    return r


def shade(s, cells):
    r = call(s, "jawa/shadegrid_read", cells=";".join("%d,%d" % c for c in cells))
    return r, {(c["x"], c["z"]): c for c in r.get("cells") or []}


def advance(s, ticks):
    call(s, "jawa/safe_advance", action="start", ticks=int(ticks))


def tick(s):
    r = call(s, "jawa/read_paths", reads=json.dumps([{"of": "game", "path": "tickManager.ticksGameInt"}]))
    v = (r.get("values") or [{}])[0]
    return int(v.get("v")) if v.get("state") == "ok" else None


def static(s, typ, method, args=""):
    r = call(s, "jawa/static_call", type=typ, method=method, args=args)
    if not r.get("success"):
        raise CouldNotLook("static_call %s.%s(%s): %s" % (typ, method, args, r.get("message")))
    return r.get("result")


def fnum(x):
    return float(str(x).replace(",", "."))


def wait_new_map(s, old_id, limit=300):
    t0 = time.time()
    while time.time() - t0 < limit:
        mi = call(s, "jawa/map_info")
        if mi.get("success") and mi.get("mapId") != old_id:
            return mi
        time.sleep(3)
    return None


def regenerate(s, biome):
    mi0 = call(s, "jawa/map_info")
    w = call(s, "jawa/world_tile_set", tiles=str(mi0.get("tile")), biome=biome, hilliness="Flat")
    call(s, "jawa/world_commit")
    g = call(s, "rimworld/execute_debug_action", path=r"Actions\Regenerate Current Map")
    time.sleep(5)
    mi = wait_new_map(s, mi0.get("mapId"))
    if not (w.get("success") and g.get("success") and mi and mi.get("mapBiome") == biome):
        raise CouldNotLook("regenerate as %s: tile_set %s, regen %s, map biome %s" % (
            biome, w.get("success"), g.get("success"), (mi or {}).get("mapBiome")))
    return mi


def find_site(s, size):
    """-> (cx, cz) of a cleared square that reads no shade and no cause, or CouldNotLook."""
    for cx in range(40, size[0] - 40, 25):
        for cz in range(40, size[1] - 40, 25):
            rect = "%d,%d,%d,%d" % (cx - HALF, cz - HALF, 2 * HALF + 1, 2 * HALF + 1)
            call(s, "jawa/set_plants", ops="CLEAR:" + rect)
            ring = [(x, z) for x in range(cx - HALF, cx + HALF + 1, 2) for z in range(cz - HALF, cz + HALF + 1, 2)]
            advance(s, 60)
            _, pre = shade(s, ring)
            if len(pre) == len(ring) and not any(c.get("shade") or c.get("cause") for c in pre.values()):
                return cx, cz
    raise CouldNotLook("no open, unshaded square found on the map")


def stage_and_read(s, site, sdir, e):
    """Builds a wall, a roofed cell, a shade tent; spawns four colonists; returns the readings."""
    cx, cz = site
    dx, dz = sdir
    # the wall stands up-sun of centre so its lee runs across the square; the open probe is up-sun of the wall
    wall = (int(round(cx - 6 * dx)), int(round(cz - 6 * dz)))
    open_c = (int(round(wall[0] - 3 * dx)) + (3 if abs(dz) > abs(dx) else 0),
              int(round(wall[1] - 3 * dz)) + (3 if abs(dx) >= abs(dz) else 0))
    roof_wall = (cx + 7, cz - 7)
    roof_c = (cx + 7, cz - 6)
    tent = (cx - 7, cz + 7)
    parasol_c = (open_c[0] + (2 if abs(dz) > abs(dx) else 0), open_c[1] + (2 if abs(dx) >= abs(dz) else 0))
    b = call(s, "jawa/build_batch", ops="Wall:%d,%d;Wall:%d,%d" % (wall + roof_wall), stuff="Steel", faction="player")
    t = call(s, "jawa/build_batch", ops="RM_ShadeTent:%d,%d" % tent, stuff="Cloth", faction="player")
    r = call(s, "jawa/set_roof_batch", ops="RoofConstructed:%d,%d,1,1" % roof_c)
    if not (b.get("success") and t.get("success") and r.get("success")):
        raise CouldNotLook("staging refused: wall %s, tent %s, roof %s" % (
            b.get("message") or b.get("success"), t.get("message") or t.get("success"), r.get("message") or r.get("success")))
    advance(s, RECOMPUTE)
    lee = [(int(round(wall[0] + k * dx)), int(round(wall[1] + k * dz))) for k in range(1, 16)]
    g, cells = shade(s, [open_c, roof_c, tent, parasol_c] + lee)
    if len(cells) < 4:
        raise CouldNotLook("shadegrid_read returned %d cells" % len(cells))
    lee_len = 0
    for c in lee:
        row = cells.get(c) or {}
        if (row.get("shade") or 0) > 0 and row.get("cause") not in ("roof", "indoors"):
            lee_len += 1
        else:
            break
    pawns = {}
    for name, c in (("open", open_c), ("roof", roof_c), ("tent", tent), ("parasol", parasol_c)):
        p = call(s, "jawa/spawn_pawn", kindDef="Colonist", x=c[0], z=c[1], faction="player")
        pid = ((p.get("pawns") or [{}])[0] or {}).get("id")
        if not pid:
            raise CouldNotLook("spawn_pawn at %s gave no thingId: %s" % (c, json.dumps(p)[:200]))
        pawns[name] = pid
    w = call(s, "jawa/pawn_gear", **{"pawn": pawns["parasol"], "action": "wear", "def": "RM_Parasol", "stuff": "Cloth"})
    if not w.get("success"):
        raise CouldNotLook("the parasol could not be worn: %s" % (w.get("message")))
    offs = {k: fnum(static(s, "RimMandrake.CreatureBehaviors.RM_SunHeatPatches", "SunOffsetFor", "%s|current" % v))
            for k, v in pawns.items()}
    per_h = fnum(static(s, "RimMandrake.CreatureBehaviors.RM_SunHeatMath", "ShadowLengthPerHeight", "%s" % e))
    sg = g.get("shadeGrid") or {}
    return {
        "E": sg.get("sunElevationDegrees"), "offsetC": sg.get("directSunOffsetC"),
        "exposure": {k: (cells.get(c) or {}).get("exposure") for k, c in
                     (("open", open_c), ("roof", roof_c), ("tent", tent))},
        "cause": {k: (cells.get(c) or {}).get("cause") for k, c in
                  (("open", open_c), ("roof", roof_c), ("tent", tent))},
        "pawnOffsetC": offs, "leeCells": lee_len, "shadowLengthPerHeight": per_h,
        "cells": {"wall": wall, "open": open_c, "roof": roof_c, "tent": tent, "parasol": parasol_c},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verdict", action="store_true", help="read the recorded result; exit 0 when every row passed")
    ap.add_argument("--biomes", default="RM_LongShade,RM_Pyrelands,RM_TheForge")
    ap.add_argument("--wall-height", type=float, default=1.0,
                    help="the wall's cast height in cells (vanilla Wall: staticSunShadowHeight 1)")
    a = ap.parse_args()
    if a.verdict:
        return verdict()
    from northstar_driver.session import FastSession
    biomes = [b for b in a.biomes.split(",") if b]
    out = {"when_ticks": None, "biomes": {}, "rows": {}, "notes": []}
    rc = 0
    with FastSession(strict=False, focus=False) as s:
        try:
            geo = call(s, "jawa/read_paths", reads=json.dumps(
                [{"of": "static:RimMandrake.CreatureBehaviors.RM_PlanetSunGeometry", "path": p} for p in ("loaded", "fixedSun", "defName")]))
            gv = {v.get("path"): v.get("v") for v in geo.get("values") or []}
            out["planet"] = gv
            if not (gv.get("loaded") and gv.get("fixedSun")):
                raise CouldNotLook("the world has no fixed sun (RM_PlanetSunGeometry %s): load tier direct_sun_fixed" % gv)
            forge_restore = None
            for b in biomes:
                mi = regenerate(s, b)
                call(s, "jawa/weather_set", weather="Clear", lockWeather=True)
                advance(s, WEATHER_SETTLE)
                g, _ = shade(s, [])
                sg = g.get("shadeGrid") or {}
                if not g.get("sunHeatActive") or not (sg.get("sunElevationDegrees") or 0) > 0:
                    raise CouldNotLook("%s: Direct Sun is not active (sunHeatActive %s, E %s)" % (
                        b, g.get("sunHeatActive"), sg.get("sunElevationDegrees")))
                site = find_site(s, (mi["sizeX"], mi["sizeZ"]))
                rd = stage_and_read(s, site, (sg.get("shadowDirX") or 0.0, sg.get("shadowDirZ") or 0.0), sg["sunElevationDegrees"])
                rd["tile"] = mi.get("tile")
                out["biomes"][b] = rd
                print("READ %s: %s" % (b, json.dumps(rd)), flush=True)
                if b == "RM_TheForge":
                    out["rows"]["L1b"] = air_heat_row(s, rd["cells"]["open"])
                    print("L1b %s" % json.dumps(out["rows"]["L1b"]), flush=True)
                    forge_restore = True
            out["rows"]["L1a"] = same_numbers_row(out["biomes"], a.wall_height)
            out["rows"]["L1c"] = still_sun_row(s)
            if "L1b" not in out["rows"]:
                out["rows"]["L1b"] = {"verdict": "UNMEASURED", "why": "RM_TheForge not in --biomes"}
            call(s, "jawa/weather_set", unlock=True)
            out["when_ticks"] = tick(s)
        except CouldNotLook as e:
            print("COULD NOT LOOK: %s" % e, flush=True)
            out["couldNotLook"] = str(e)
            rc = 2
    for k in ROWS:
        row = out["rows"].get(k) or {"verdict": "UNMEASURED"}
        print("%s %s %s" % (k, row.get("verdict"), "; ".join(row.get("fails") or [])), flush=True)
        if rc == 0 and row.get("verdict") != "PASS":
            rc = 1 if row.get("verdict") == "FAIL" else 2
    out["verdict"] = {0: "PASS", 1: "FAIL", 2: "COULD NOT LOOK"}[rc]
    os.makedirs(os.path.dirname(RESULT), exist_ok=True)
    with open(RESULT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=str)
    print("%s live direct sun angle -> %s" % (out["verdict"], RESULT))
    return rc


def same_numbers_row(biomes, wall_height):
    fails = []
    names = list(biomes)
    if len(names) < 2:
        return {"verdict": "UNMEASURED", "why": "fewer than two biomes read"}
    ref = biomes[names[0]]

    def flat(rd):
        d = {"E": rd["E"], "offsetC": rd["offsetC"], "leeCells": rd["leeCells"]}
        d.update({"exposure." + k: v for k, v in rd["exposure"].items()})
        d.update({"pawnOffsetC." + k: v for k, v in rd["pawnOffsetC"].items()})
        return d
    fr = flat(ref)
    for n in names[1:]:
        fo = flat(biomes[n])
        for k, v in fr.items():
            w = fo.get(k)
            if v is None or w is None or abs(float(v) - float(w)) > TOL:
                fails.append("%s %s = %s, %s = %s" % (k, names[0], v, n, w))
    for n, rd in biomes.items():
        ex = rd["exposure"]
        if not (ex["open"] is not None and ex["roof"] is not None and ex["tent"] is not None
                and ex["open"] > ex["roof"] and ex["open"] > ex["tent"]):
            fails.append("%s: open exposure %s not above roof %s and tent %s" % (n, ex["open"], ex["roof"], ex["tent"]))
        po = rd["pawnOffsetC"]
        if not (po["open"] > po["roof"] and po["open"] > po["tent"] and po["open"] > po["parasol"]):
            fails.append("%s: colonist offsets open %s, roof %s, tent %s, parasol %s (open must be the highest)" % (
                n, po["open"], po["roof"], po["tent"], po["parasol"]))
        if wall_height is not None:
            want = wall_height * rd["shadowLengthPerHeight"]
            if abs(rd["leeCells"] - want) > 1.0:
                fails.append("%s: lee %d cells, the model says %.1f at E %.1f" % (n, rd["leeCells"], want, rd["E"]))
    return {"verdict": "PASS" if not fails else "FAIL", "fails": fails, "biomes": names}


def air_heat_row(s, open_c):
    fs = "RimMandrake.TheForge.RM_TheForgeSettings"
    st = call(s, "jawa/mod_settings_fields", typeName=fs, fields="airHeatEnabled,airHeatC")
    vals = st.get("values") or {}
    if "airHeatEnabled" not in vals:
        return {"verdict": "UNMEASURED", "why": "cannot read the Forge's air-heat settings: %s" % json.dumps(st)[:200]}
    was_on = str(vals["airHeatEnabled"]).lower() == "true"
    offset = fnum(vals["airHeatC"])
    fails = []
    try:
        if not was_on:
            call(s, "jawa/mod_settings_fields", typeName=fs, setField="airHeatEnabled", setValue="true")
            static(s, "RimMandrake.TheForge.RM_TheForgeAirHeatApplier", "Apply")
            advance(s, SYNC)
        t = tick(s)
        if t is None:
            return {"verdict": "UNMEASURED", "why": "cannot read the tick"}
        advance(s, (40 - t % SYNC) % SYNC or SYNC)
        on = call(s, "jawa/cell_temperature", cell="%d,%d" % open_c)
        g_on, c_on = shade(s, [open_c])
        call(s, "jawa/mod_settings_fields", typeName=fs, setField="airHeatEnabled", setValue="false")
        static(s, "RimMandrake.TheForge.RM_TheForgeAirHeatApplier", "Apply")
        advance(s, 2)
        off = call(s, "jawa/cell_temperature", cell="%d,%d" % open_c)
        g_off, c_off = shade(s, [open_c])
        ton, toff = on.get("temperature"), off.get("temperature")
        if ton is None or toff is None:
            return {"verdict": "UNMEASURED", "why": "cell_temperature gave no temperature: %s" % json.dumps(on)[:200]}
        drop = float(ton) - float(toff)
        if abs(drop - offset) > 0.5:
            fails.append("outdoor temperature fell %.2f C when the air heat went off; its offset is %.2f C" % (drop, offset))
        e_on, e_off = (c_on.get(open_c) or {}).get("exposure"), (c_off.get(open_c) or {}).get("exposure")
        if e_on is None or e_off is None or abs(e_on - e_off) > TOL:
            fails.append("the open cell's Direct Sun exposure moved with the air heat: %s -> %s" % (e_on, e_off))
        return {"verdict": "PASS" if not fails else "FAIL", "fails": fails, "on": ton, "off": toff, "offsetC": offset,
                "exposureOn": e_on, "exposureOff": e_off}
    finally:
        call(s, "jawa/mod_settings_fields", typeName=fs, setField="airHeatEnabled", setValue="true" if was_on else "false")
        try:
            static(s, "RimMandrake.TheForge.RM_TheForgeAirHeatApplier", "Apply")
        except CouldNotLook:
            pass


def still_sun_row(s):
    es = []
    for _ in range(4):
        g, _ = shade(s, [])
        es.append((g.get("shadeGrid") or {}).get("sunElevationDegrees"))
        advance(s, 15000)
    if any(e is None for e in es):
        return {"verdict": "UNMEASURED", "why": "an elevation read came back empty: %s" % es}
    spread = max(es) - min(es)
    return {"verdict": "PASS" if spread <= TOL else "FAIL", "elevations": es,
            "fails": [] if spread <= TOL else ["E moved %.3f degrees across a day: %s" % (spread, es)]}


if __name__ == "__main__":
    sys.exit(main())
