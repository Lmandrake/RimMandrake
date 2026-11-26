"""Offline checks of water_one_surface_live.py's verdicts against planted census readings (no bridge; WSL python3)."""
import copy
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.modules.setdefault("rimbridge_client", types.SimpleNamespace(RimBridge=None, resolve_endpoint=None))
sys.path.insert(0, HERE)
import water_one_surface_live as W  # noqa: E402

fails = []


def check(name, ok):
    print(("ok    " if ok else "FAIL  ") + name)
    if not ok:
        fails.append(name)


def draw(layer, q, colours=(), mixed=0.0, area=1.0, amin=255, shader="Custom/Vertex Color", material="x", drawn=True):
    return {"layer": layer, "renderQueue": q, "drawn": drawn, "colours": [{"rgba": list(c), "area": a} for c, a in colours],
            "mixedArea": mixed, "area": area, "aMin": amin, "shader": shader, "material": material}


def census(*draws):
    return {"success": True, "draws": list(draws), "colours": True}


SHEET = (19, 41, 76, 172)
good_wet = census(draw(W.WALLS, 2449, [(SHEET, 1.0), (tuple(W.OUTLINE), 0.08)]))
good_dry = census(draw("SectionLayer_Terrain", 2392, material="water_RM_WaterThin", shader="Custom/Terrain"),
                  draw(W.WALLS, 2440, shader="Custom/Terrain fade", area=1.0))
gate_half = census(draw(W.WALLS, 2449, [(SHEET, 0.5), (tuple(W.OUTLINE), 0.08)]))
gate_full = census(draw(W.WALLS, 2449, [(SHEET, 1.0)]))


def world(wet_read=good_wet, dry_read=good_dry, gate_read=gate_half, extra=None):
    reads, wet = {}, {}
    for sq in W.WET:
        reads[sq], wet[sq] = copy.deepcopy(wet_read), True
    for st, row in W.SLUICE_ROWS.items():
        g = W.GATES[st]
        for sq in row:
            drained = (sq[0] > g[0]) if st == 7 else (sq[0] < g[0]) if st == 8 else (sq[1] > g[1]) if st == 9 else (sq[1] < g[1])
            if sq == g:
                reads[sq], wet[sq] = copy.deepcopy(gate_read), True
            elif drained:
                reads[sq], wet[sq] = copy.deepcopy(dry_read), False
            else:
                reads[sq], wet[sq] = copy.deepcopy(wet_read), True
    if extra:
        extra(reads, wet)
    return W.verdicts(reads, wet)


v = world()
check("clean: every rule PASS", all(s == "PASS" for s, _ in v.values()))
v = world(wet_read=census(draw(W.WALLS, 2449, [((24, 52, 96, 136), 0.5), ((24, 52, 96, 100), 0.25)])))
check("can-fail: two sheet alphas on a wet square -> ONE_SHEET FAIL", v["ONE_SHEET_PER_WET_SQUARE"][0] == "FAIL")
v = world(wet_read=census(draw(W.WALLS, 2449, [(SHEET, 0.8)], mixed=0.2)))
check("can-fail: a graded (mixed-colour) sheet -> ONE_SHEET FAIL", v["ONE_SHEET_PER_WET_SQUARE"][0] == "FAIL")
v = world(wet_read=census(draw(W.WALLS, 2449, [(SHEET, 1.0)]), draw("SectionLayer_RMDeepWaterTint", 2441, [((21, 30, 49, 144), 1.0)])))
check("can-fail: the deep tint on a dug square -> NO_SECOND FAIL", v["NO_SECOND_WATER_LAYER"][0] == "FAIL")
v = world(wet_read=census(draw(W.WALLS, 2449, [(SHEET, 1.0)]), draw("SectionLayer_RMWetWallBand", 2441, [((48, 34, 24, 191), 0.3)])))
check("can-fail: the wet-wall band -> NO_SECOND FAIL", v["NO_SECOND_WATER_LAYER"][0] == "FAIL")
v = world(dry_read=census(draw("SectionLayer_Terrain", 2392, material="water_RM_WaterThin", shader="Custom/Terrain")))
check("can-fail: a drained square under vanilla's water fade, no reprint -> DRAINED FAIL", v["DRAINED_SQUARE_DRAWS_DRY"][0] == "FAIL")
v = world(dry_read=census(draw(W.WALLS, 2449, [(SHEET, 0.3)])))
check("can-fail: a drained square drawing a sheet -> DRAINED FAIL", v["DRAINED_SQUARE_DRAWS_DRY"][0] == "FAIL")
v = world(gate_read=gate_full)
check("can-fail: the gate's sheet over its drained half -> SLUICE FAIL", v["SLUICE_SHEET_ON_WET_HALF"][0] == "FAIL")
v = world(extra=lambda r, w: r.__setitem__(W.WET[0], {"success": False}))
check("a square the census cannot read: every rule UNMEASURED", all(s == "UNMEASURED" for s, _ in v.values()))
v = world(extra=lambda r, w: [w.__setitem__(k, True) for k in list(w)])
check("no drained square: DRAINED and SLUICE UNMEASURED, never PASS",
      v["DRAINED_SQUARE_DRAWS_DRY"][0] == "UNMEASURED" and v["SLUICE_SHEET_ON_WET_HALF"][0] == "UNMEASURED")
print("%d FAIL" % len(fails))
sys.exit(1 if fails else 0)
