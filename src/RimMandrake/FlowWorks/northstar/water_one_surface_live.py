"""WATER ONE SURFACE live check (RIMMANDRAKE_DRILL_FLOWWORKS_WATER_LAYERS_HE_SAW_STACKED_BLUE).

Owner, walk 2026-11-25: "Station 6 still shows odd pit walls under water", the drained side of a sluice "That cannot stand",
and of station 22 "I suspect you're applying multiple layers over each other instead of calculating a single one". This reads
the walk save's stations through jawa/cell_draw_census (every section-layer draw on one square, its colours and their areas)
and decides by count, not by eye:

  ONE_SHEET_PER_WET_SQUARE   every dug square holding liquid draws exactly ONE sheet colour (queue 2449, the rim outline's
                             opaque black excluded) and no triangle of mixed colours: one surface, one alpha.
  NO_SECOND_WATER_LAYER      no dug square draws SectionLayer_RMDeepWaterTint or SectionLayer_RMWetWallBand.
  DRAINED_SQUARE_DRAWS_DRY   a dug square holding no liquid draws no sheet, and where vanilla's terrain layer fades a liquid
                             over it, the walls layer prints the square's floor opaque over the whole square.
  SLUICE_SHEET_ON_WET_HALF   a shut sluice square with one drained side carries its sheet on at most 0.6 of the square.

Kind A (deterministic): one valid run decides. A square the census cannot read is UNMEASURED, never PASS.
Run on the walk save (FLOWWORKS_OWNER_REVIEW_VISIT13_SMALL_20261125_0957 or a copy), on the game you hold:

  python.exe src/RimMandrake/FlowWorks/northstar/water_one_surface_live.py <out.json> [--drain]

--drain first drains, by the dev "Drain liquid... drain ALL" act a player uses (RM_GodLiquid.DrainAll), the east side of
station 7, the west side of station 8, the north side of station 9 and the south side of station 10.
Exit 0 every rule PASS; 1 a FAIL; 2 a rule UNMEASURED.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402

# the walk save's stations (signs read from the save 2026-11-25): 6 wet spikes pit, 22 the 5 m pit, sluices 7 to 10
WET = [(33, 110), (34, 110), (35, 110), (33, 109), (34, 109), (35, 108),       # station 6 (3x3, 2 m deep)
       (55, 136), (56, 136), (57, 136), (55, 135), (56, 135), (57, 134)]      # station 22 (3x3, 5 m)
SLUICE_ROWS = {7: [(x, 119) for x in range(28, 33)], 8: [(x, 119) for x in range(35, 40)],
               9: [(43, z) for z in range(116, 121)], 10: [(50, z) for z in range(116, 121)]}
GATES = {7: (30, 119), 8: (37, 119), 9: (43, 118), 10: (50, 118)}
DRAIN_AT = [(32, 119), (35, 119), (43, 120), (50, 116)]
SECOND_LAYERS = ("SectionLayer_RMDeepWaterTint", "SectionLayer_RMWetWallBand")
WALLS = "SectionLayer_RMExcavationWalls"
SHEET_QUEUE = 2449
OUTLINE = [0, 0, 0, 255]


def sheet_colours(census):
    """The sheet's colours on a square (the walls layer's queue-2449 draws, the rim outline excluded) and their mixed area."""
    cols, mixed = {}, 0.0
    for d in census.get("draws", []):
        if d.get("layer") != WALLS or d.get("renderQueue") != SHEET_QUEUE or not d.get("drawn"):
            continue
        mixed += d.get("mixedArea") or 0.0
        for c in d.get("colours") or []:
            if c["rgba"] != OUTLINE:
                cols[tuple(c["rgba"])] = cols.get(tuple(c["rgba"]), 0.0) + c["area"]
    return cols, mixed


def verdicts(reads, wet_of):
    """reads: (x, z) -> census; wet_of: (x, z) -> True holds liquid / False dry / None unread. -> {rule: (status, detail)}."""
    out = {}
    blind = [k for k, v in reads.items() if not v or not v.get("success") or "colours" not in json.dumps(v)]
    one, second, drained, half = [], [], [], []
    for sq, c in reads.items():
        if sq in blind:
            continue
        cols, mixed = sheet_colours(c)
        wet = wet_of.get(sq)
        if wet:
            one.append((sq, len(cols), round(mixed, 4), [list(k) for k in cols]))
        if wet is False:
            fade = [d for d in c["draws"] if d["layer"] == "SectionLayer_Terrain" and d["drawn"] and "water" in (d["material"] or "").lower()]
            cover = [d for d in c["draws"] if d["layer"] == WALLS and d["drawn"] and d["renderQueue"] >= 2440 and d["renderQueue"] < SHEET_QUEUE
                     and d["area"] >= 0.999 and d["aMin"] == 255 and "Terrain" in (d["shader"] or "")]
            drained.append((sq, len(cols), len(fade), len(cover)))
        second.extend((sq, d["layer"]) for d in c["draws"] if d["layer"] in SECOND_LAYERS and d["drawn"])
    if blind:
        for r in ("ONE_SHEET_PER_WET_SQUARE", "NO_SECOND_WATER_LAYER", "DRAINED_SQUARE_DRAWS_DRY", "SLUICE_SHEET_ON_WET_HALF"):
            out[r] = ("UNMEASURED", {"blind": [list(b) for b in blind]})
        return out
    bad = [o for o in one if o[1] != 1 or o[2] > 1e-4]
    out["ONE_SHEET_PER_WET_SQUARE"] = ("UNMEASURED" if not one else ("FAIL" if bad else "PASS"),
                                       {"squares": len(one), "bad": [[list(o[0]), o[1], o[2], o[3]] for o in bad]})
    out["NO_SECOND_WATER_LAYER"] = ("FAIL" if second else "PASS", {"found": [[list(s[0]), s[1]] for s in second]})
    badd = [d for d in drained if d[1] != 0 or (d[2] > 0 and d[3] == 0)]
    out["DRAINED_SQUARE_DRAWS_DRY"] = ("UNMEASURED" if not drained else ("FAIL" if badd else "PASS"),
                                       {"squares": len(drained), "bad": [[list(d[0]), "sheetColours", d[1], "waterFades", d[2], "floorCovers", d[3]] for d in badd]})
    for st, g in GATES.items():
        row = SLUICE_ROWS[st]
        sides = [wet_of.get(sq) for sq in row if sq != g]
        if g not in reads or wet_of.get(g) is not True or not (True in sides and False in sides):
            continue
        area = sum(sheet_colours(reads[g])[0].values())
        half.append((st, round(area, 4)))
    badh = [h for h in half if h[1] > 0.6]
    out["SLUICE_SHEET_ON_WET_HALF"] = ("UNMEASURED" if not half else ("FAIL" if badh else "PASS"), {"gates": half})
    return out


def main(argv):
    if not argv or argv[0].startswith("-"):
        print(__doc__)
        return 2
    out_path = argv[0]
    h, p, t = resolve_endpoint()
    with RimBridge(h, p, t) as B:
        if "--drain" in argv:
            for x, z in DRAIN_AT:
                r = B.call("jawa/static_call", {"type": "RimMandrake.FlowWorks.RM_GodLiquid", "method": "DrainAll", "args": "%d,%d" % (x, z)},
                           check=False)
                print("drain %d,%d: %s" % (x, z, (r or {}).get("result")))
            B.call("rimworld/set_time_speed", {"speed": "Normal"}, check=False)
            time.sleep(4)
            B.call("rimworld/set_time_speed", {"speed": "Paused"}, check=False)
        squares = list(WET)
        for row in SLUICE_ROWS.values():
            squares += row
        rect = B.call("jawa/flowworks_excavation_rect", {"x": 26, "z": 100, "w": 40, "h": 40, "onlyNonZero": True}, check=False) or {}
        dl = {(r["x"], r["z"]): r["dl"] for r in rect.get("rows", [])}
        wet_of = {sq: (None if sq not in dl else dl[sq] > 0) for sq in squares}
        reads = {}
        for x, z in squares:
            reads[(x, z)] = B.call("jawa/cell_draw_census", {"x": x, "z": z}, check=False)
    v = verdicts(reads, wet_of)
    res = {"item": "RIMMANDRAKE_DRILL_FLOWWORKS_WATER_LAYERS_HE_SAW_STACKED_BLUE", "when": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "rows": [{"id": k, "status": s, "detail": d} for k, (s, d) in v.items()],
           "wet": {"%d,%d" % k: w for k, w in wet_of.items()}}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    for k, (s, d) in v.items():
        print("%-26s %-10s %s" % (k, s, json.dumps(d)[:300]))
    sts = [s for s, _ in v.values()]
    return 1 if "FAIL" in sts else (2 if "UNMEASURED" in sts else 0)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
