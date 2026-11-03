#!/usr/bin/env python3
"""selftest_flowworks_tank_shadow.py — TANK_SHADOW_DIAGNOSE_DRIFTS_OFF_THE_SKID.

WHAT WAS SEEN: live round 3b (Transient/live_batch_20261023/r3b/hose_bend_wall_corner.png and
tank_port_met_straight_zoom.png, map R) showed dark cross/T-shaped blocks 1-2 cells west and north of the tanks at
x116, while the wall at x110 had its sun shadow attached. A judge read them as tank shadows drifting off the skid.

WHAT THEY ARE: not shadows. They are vanilla SoilRich terrain lying in GrasslandSoil, cell for cell
(x113-116 z209-211 + 115,208 beside the tall tank; x113-120 z200-203 under the small tank; 105,203 by the reel).
The soft cross outline is vanilla terrain edge blending. Evidence: the fixture Tools/fixtures/tank_shadow_r3b.json
(built by Tools/tank_shadow_fixture.py from save RM_fw_walkthrough_20261023e.rws, map 0, and the r3b capture),
which pairs each cell's terrain from the save's topGridDeflate with its median luminance on screen.

FALSE THEORIES, guarded here:
  - a tank shadow cast by the sun: the tank defs and their styles carry no shadowData, staticSunShadowHeight or
    castEdgeShadows, and BuildingBase sets none; nothing in FlowWorks C# prints a tank shadow. Besides, the wall's
    real sun shadow falls SOUTH-west (it reaches below the wall's lowest cell), while the blob lies NORTH of the
    tall tank's footprint centre, so one sun cannot cast both.
  - a roof darkening the cells: the save's roof grid is empty over the window (fixture roofed_cells_in_window).
A dark patch near a building is a terrain question first: read the terrain grid before chasing a draw bug.

CAN IT FAIL: each check runs on mutated inputs (terrain relabelled all GrasslandSoil, the image flattened so the
wall shadow vanishes, a tank def given a shadowData) and must go red there.

    python3 src/RimMandrake/FlowWorks/selftest_flowworks_tank_shadow.py
"""
from __future__ import annotations

import copy
import json
import re
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "Tools" / "fixtures" / "tank_shadow_r3b.json"
TANK_DEFS = [HERE / "Defs" / "LiquidTypes" / "ThingDefs" / "RM_LiquidTank.xml",
             HERE / "Defs" / "LiquidTypes" / "ThingDefs" / "RM_LiquidTankStyles.xml",
             HERE / "Defs" / "Machinery" / "RM_LiquidLogistics.xml"]
TANK_DEF_RE = re.compile(r"<ThingDef\b.*?</ThingDef>|<ThingStyleDef\b.*?</ThingStyleDef>", re.S)
SHADOW_FIELDS = ("shadowData", "staticSunShadowHeight", "castEdgeShadows")
# the r3b wall (RESULTS_round3a: x110 z206-210; removed before the save); its vanilla sun shadow falls south-west
WALL = [(110, z) for z in range(206, 211)]
WALL_SHADOW = [(x, z) for x in (108, 109) for z in range(205, 211)]   # its core, for the sanity probe
# Vanilla SectionLayer_SunShadows sweeps the wall's cells along the cast vector. Measured on the capture: the shadow's
# west edge at world x 107.5 and its low corner at world z 204.4 (wall spans x 110-111, z 206-211) -> (-2.5, -1.6).
CAST = (-2.5, -1.6)
WALL_SWEEP = sorted({(int(110 + fx_ + t * CAST[0]), int(206 + fz + t * CAST[1]))
                     for fx_ in (0.02, 0.5, 0.98) for fz in [i / 10 for i in range(0, 50)] + [4.98]
                     for t in [i / 40 for i in range(41)]} - set(WALL))
TALL_TANK_FOOTPRINT = [(x, z) for x in (116, 117) for z in (208, 209)]
DARK = 86          # median luminance; open GrasslandSoil reads ~94-101 in this capture
FAILS = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else ": " + detail))
    if not ok:
        FAILS.append(name)
    return ok


def cells_of(fx):
    covered = {tuple(c) for v in fx["covered"].values() for c in v}
    return {(c["x"], c["z"]): c for c in fx["cells"] if (c["x"], c["z"]) not in covered and c["lum"] is not None}


def instrument_sees_shadow(fx):
    """Sanity probe: the instrument must see the wall's real sun shadow, on GrasslandSoil, or it is blind."""
    cells = cells_of(fx)
    shade = [cells[c] for c in WALL_SHADOW if c in cells]
    return (len(shade) >= 10 and all(c["terrain"] == "GrasslandSoil" for c in shade)
            and statistics.median(c["lum"] for c in shade) < DARK - 10), shade


def dark_is_soilrich(fx):
    """Every dark cell outside the wall's swept sun shadow is SoilRich, and SoilRich reads clearly darker than open ground."""
    cells = cells_of(fx)
    rich = {c for c, v in cells.items() if v["terrain"] == "SoilRich"}
    stray = [c for c, v in cells.items() if v["lum"] < DARK and c not in WALL_SWEEP and c not in rich]
    open_ground = [v["lum"] for c, v in cells.items() if v["terrain"] == "GrasslandSoil" and c not in WALL_SWEEP]
    rich_lum = [cells[c]["lum"] for c in rich]
    ok = (not stray and len(rich_lum) >= 8 and all(l < DARK for l in rich_lum)
          and statistics.median(open_ground) - statistics.median(rich_lum) >= 20)
    return ok, {"stray_dark_non_soilrich": stray, "soilrich_cells": len(rich_lum)}


def sun_cannot_cast_blob(fx):
    """The wall's shadow reaches below the wall (sun from the north-east, cast south-west); the blob beside the tall
    tank lies north of the tank's footprint centre. A tank shadow under that sun would land south-west, not there."""
    cells = cells_of(fx)
    shade_z = min(z for (x, z) in WALL_SHADOW if (x, z) in cells and cells[(x, z)]["lum"] < DARK)
    blob = [(x, z) for (x, z), v in cells.items() if v["terrain"] == "SoilRich" and 112 <= x <= 116 and z >= 207]
    tank_cz = statistics.mean(z for _, z in TALL_TANK_FOOTPRINT)
    ok = shade_z < min(z for _, z in WALL) and bool(blob) and statistics.mean(z for _, z in blob) > tank_cz
    return ok, {"wall_shadow_min_z": shade_z, "blob": blob, "tank_centre_z": tank_cz}


def tank_defs_cast_no_shadow(texts):
    hits = []
    for path, text in texts.items():
        for block in TANK_DEF_RE.findall(text):
            name = re.search(r"<defName>([^<]+)</defName>", block)
            if name and re.match(r"RM_(LiquidTank|UniversalCargoTank)", name.group(1)):
                hits += [(name.group(1), f) for f in SHADOW_FIELDS if "<" + f in block]
    found = sum(1 for t in texts.values() for b in TANK_DEF_RE.findall(t)
                if re.search(r"<defName>RM_(LiquidTank|UniversalCargoTank)", b))
    return (not hits and found >= 16), {"shadow_fields": hits, "tank_defs_seen": found}


def main():
    fx = json.loads(FIXTURE.read_text())
    texts = {p.name: p.read_text(encoding="utf-8") for p in TANK_DEFS if p.exists()}

    ok, d = instrument_sees_shadow(fx)
    check("instrument sees the wall's real sun shadow (sanity probe)", ok, str(d))
    ok, d = dark_is_soilrich(fx)
    check("every dark cell off the wall shadow is SoilRich terrain", ok, str(d))
    ok, d = sun_cannot_cast_blob(fx)
    check("the blob lies where this sun cannot cast a tank shadow", ok, str(d))
    check("no roofed cell in the window (roof theory false)", fx.get("roofed_cells_in_window") == 0,
          str(fx.get("roofed_cells_in_window")))
    ok, d = tank_defs_cast_no_shadow(texts)
    check("tank defs and styles carry no shadow fields", ok, str(d))

    # mutants: each must go red
    m = copy.deepcopy(fx)
    for c in m["cells"]:
        c["terrain"] = "GrasslandSoil"
    check("mutant: no SoilRich -> dark_is_soilrich red", not dark_is_soilrich(m)[0])
    m = copy.deepcopy(fx)
    for c in m["cells"]:
        if (c["x"], c["z"]) == (113, 206):      # open GrasslandSoil, far from the wall: a real drifted shadow
            c["lum"] = 65.0
    check("mutant: dark GrasslandSoil cell -> dark_is_soilrich red", not dark_is_soilrich(m)[0])
    m = copy.deepcopy(fx)
    for c in m["cells"]:
        if c["lum"] is not None:
            c["lum"] = 96.0
    check("mutant: flat image -> sanity probe red", not instrument_sees_shadow(m)[0])
    check("mutant: flat image -> sun_cannot_cast_blob red", not _safe(sun_cannot_cast_blob, m))
    m = copy.deepcopy(fx)
    for c in m["cells"]:
        if c["terrain"] == "SoilRich" and c["z"] >= 207:
            c["terrain"] = "GrasslandSoil"
    check("mutant: blob moved off -> sun_cannot_cast_blob red", not _safe(sun_cannot_cast_blob, m))
    mt = dict(texts)
    k = next(iter(mt))
    mt[k] = mt[k].replace("<defName>RM_LiquidTankTall</defName>",
                          "<defName>RM_LiquidTankTall</defName><staticSunShadowHeight>1</staticSunShadowHeight>", 1)
    check("mutant: tank def gains a sun shadow -> red", not tank_defs_cast_no_shadow(mt)[0])

    print("FAILED: " + ", ".join(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


def _safe(fn, arg):
    try:
        return fn(arg)[0]
    except ValueError:
        return False


if __name__ == "__main__":
    sys.exit(main())
