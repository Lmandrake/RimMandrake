#!/usr/bin/env python3
"""FlowWorks review map — the VISUALS station set (owner principles 1-5, 2026-10-05).

The review-map builder (a separate agent) reads review_map_stations_visuals.json beside this file;
this module is its source of truth and turns a station into bridge calls.

    python3 review_map_visuals.py            # rewrites review_map_stations_visuals.json
    python3 review_map_visuals.py --selftest # checks the grid is complete and the ops are well formed

Grid: depth D1..D4 x ground {dirt, stone} x state {dry, water, tar, scorched} = 32 stations, plus 7
extra liquids at D3 dirt on the two top rows: oil, green slime, white slime, red slime, blood, chemfuel, astrofuel
(owner, 2026-10-06: "Need many more of the fluids online here. Blood. Chemfuel. Astrofuel. White slime. Red Slime."). Every station is the same 6 x 5 plot: ground over the whole plot,
a 4-wide x 3-tall pit at plot offset (1,1), and one colonist standing in the middle of the pit's near
(south) row so the near-lip hiding can be seen. Plots are laid out with a 2-cell gap so nothing overlaps.

Ops vocabulary (all existing tools, plus RM_PitScorchProof added with this pass):
  jawa/set_terrain_batch  ops="Def:x,z,w,h"
  jawa/flowworks_excavation_drive  x,z,deepenLevels,setFill(-1 = leave),fillInLevels
  jawa/static_call  type=RimMandrake.FlowWorks.RM_FluidIdentityProof method=ProofFillWithFluid args="x,z,fill,FluidDef"
  jawa/static_call  type=RimMandrake.FlowWorks.RM_PitScorchProof     method=ProofScorch        args="x0,z0,x1,z1"
  jawa/spawn_pawn   kindDef, x, z, faction
State reads for verification (no screenshot hunt): RM_PitScorchProof.ProofScorchAt "x,z",
RM_NorthstarProofs.ProofWallFaces "x,z", RM_PromotionProofs.ProofPawnSink <pawnId>.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "review_map_stations_visuals.json")

PLOT_W, PLOT_H = 6, 5
PIT_DX, PIT_DZ, PIT_W, PIT_H = 1, 1, 4, 3
GAP = 2

GROUNDS = {
    # dirt: vanilla soil. stone: granite's rough floor — a terrain a natural-rock ThingDef names, which is
    # exactly what RM_FaceMaterial.IsStone reads, so the face comes out granite.
    "dirt": {"terrain": "Soil", "words": "soil"},
    "stone": {"terrain": "Granite_Rough", "words": "granite"},
}
STATES = {
    "dry": {"fluid": None, "words": "dug and empty"},
    "water": {"fluid": "RM_Fluid_Water", "words": "with water standing in it"},
    "tar": {"fluid": "RM_Fluid_Tar", "words": "with tar standing in it"},
    "scorched": {"fluid": None, "scorch": True, "words": "after a fire burned it dry"},
    "oil": {"fluid": "RM_Fluid_Oil", "words": "with oil standing in it"},
    "slime": {"fluid": "RM_Fluid_SlimeGreen", "words": "with green slime standing in it"},
    "slimewhite": {"fluid": "RM_Fluid_SlimeWhite", "words": "with white slime standing in it"},
    "slimered": {"fluid": "RM_Fluid_SlimeRed", "words": "with red slime standing in it"},
    "blood": {"fluid": "RM_Fluid_Blood", "words": "with blood standing in it"},
    "chemfuel": {"fluid": "RM_Fluid_Chemfuel", "words": "with chemfuel standing in it"},
    "astrofuel": {"fluid": "RM_Fluid_Astrofuel", "words": "with astrofuel standing in it"},
}
EXTRAS = ("oil", "slime", "slimewhite", "slimered", "blood", "chemfuel", "astrofuel")
NOTICE = {
    "dry": "The far bank shows a lit face with a dark rim, the way the game draws its own walls; at depth 3 it is "
           "about a wall's height, at depth 4 taller. The side banks show as narrow faces. The person in the near "
           "row is hidden below the near bank, more the deeper the pit.",
    "water": "The water moves like the game's own shallow water. The pit's floor and its drowned far wall show "
             "through it, fainter the deeper the water.",
    "tar": "Tar is dark grey and opaque on soil and granite alike, never blue: a thick liquid that slowly creeps "
           "and shines.",
    "scorched": "Still an empty pit with the same walls, but burned: blast marks (dark starbursts) on the floor and "
                "the ground round the rim, blackened patches, ash, soot climbing the faces.",
    "oil": "Oil: slow dark gloss with a faint rainbow film.",
    "slime": "Green slime: thick, opaque, slowly creeping, a few bubbles rising.",
    "slimewhite": "White slime: thick, opaque, slowly creeping, a few bubbles rising.",
    "slimered": "Red slime: thick, opaque, slowly creeping, a few bubbles rising.",
    "blood": "Blood: thick, opaque dark red, slowly creeping.",
    "chemfuel": "Chemfuel: a thin amber-brown fuel with a faint rainbow film; the pit floor shows faintly through it.",
    "astrofuel": "Astrofuel: a thin pale blue fuel with a faint rainbow film; the pit floor shows faintly through it.",
}


def fill_level(depth, state):
    """A liquid station fills to one level below the brim (so one level of face still shows), at least 1."""
    if STATES[state].get("fluid") is None:
        return 0
    return max(1, depth - 1)


def stations():
    out = []
    order = [(g, s, d) for s in ("dry", "water", "tar", "scorched") for g in ("dirt", "stone") for d in (1, 2, 3, 4)]
    order += [("dirt", e, 3) for e in EXTRAS]
    for i, (g, s, d) in enumerate(order):
        col, row = (d - 1, (i // 4)) if s in ("dry", "water", "tar", "scorched") else ((i - 32) % 4, 8 + (i - 32) // 4)
        st = STATES[s]
        out.append({
            "id": f"vis_{s}_{g}_D{d}",
            "title": f"A depth-{d} pit cut in {GROUNDS[g]['words']}, {st['words']}.",
            "what_to_notice": NOTICE[s],
            "grid": {"col": col, "row": row},
            "setup": {
                "plot": {"w": PLOT_W, "h": PLOT_H},
                "ground_terrain": GROUNDS[g]["terrain"],
                "ground_kind": g,
                "pit": {"dx": PIT_DX, "dz": PIT_DZ, "w": PIT_W, "h": PIT_H, "depth": d},
                "fluid": st.get("fluid"),
                "fill_level": fill_level(d, s),
                "scorched": bool(st.get("scorch")),
                "pawn": {"kindDef": "Colonist", "at": "pit near row, second column", "dx": PIT_DX + 1, "dz": PIT_DZ},
                "roofed": False,
            },
        })
    return out


def origin_of(station, base_x, base_z):
    """Bottom-left cell of a station's plot on the map, given the grid's bottom-left corner."""
    g = station["grid"]
    return base_x + g["col"] * (PLOT_W + GAP), base_z + g["row"] * (PLOT_H + GAP)


def station_ops(station, base_x, base_z):
    """The bridge calls that build one station. Order matters: ground, dig, fill or scorch, then the pawn."""
    s = station["setup"]
    ox, oz = origin_of(station, base_x, base_z)
    p = s["pit"]
    px, pz = ox + p["dx"], oz + p["dz"]
    ops = [("jawa/set_terrain_batch", {"ops": "%s:%d,%d,%d,%d" % (s["ground_terrain"], ox, oz, PLOT_W, PLOT_H)})]
    for x in range(px, px + p["w"]):
        for z in range(pz, pz + p["h"]):
            ops.append(("jawa/flowworks_excavation_drive",
                        {"x": x, "z": z, "deepenLevels": p["depth"], "setFill": -1, "fillInLevels": 0}))
    if s["fluid"]:
        for x in range(px, px + p["w"]):
            for z in range(pz, pz + p["h"]):
                ops.append(("jawa/static_call", {"type": "RimMandrake.FlowWorks.RM_FluidIdentityProof",
                                                 "method": "ProofFillWithFluid",
                                                 "args": "%d,%d,%d,%s" % (x, z, s["fill_level"], s["fluid"])}))
    if s["scorched"]:
        ops.append(("jawa/static_call", {"type": "RimMandrake.FlowWorks.RM_PitScorchProof", "method": "ProofScorch",
                                         "args": "%d,%d,%d,%d" % (px, pz, px + p["w"] - 1, pz + p["h"] - 1)}))
    ops.append(("jawa/spawn_pawn", {"kindDef": s["pawn"]["kindDef"], "x": ox + s["pawn"]["dx"],
                                    "z": oz + s["pawn"]["dz"], "faction": "player"}))
    return ops


def write():
    st = stations()
    doc = {
        "set": "flowworks_visuals",
        "owner_principles": "2026-10-05, five rules: deep cuts look like walls; walls are dirt or stone; water moves; "
                            "tar is a black liquid; a burned pit looks burned",
        "mockups": "src/RimMandrake/FlowWorks/art_source/visual_principles_2026-10-05/",
        "builder": "src/RimMandrake/FlowWorks/review_map_visuals.py (station_ops)",
        "plot": {"w": PLOT_W, "h": PLOT_H, "gap": GAP},
        "notes": [
            "Kill hostiles on the map; keep the plots unroofed and in daylight.",
            "Water/tar/oil/slime: give the pawn a slow walk across the pit so the wake shows.",
            "Fluids flow: fill after every station's dig, and leave a dug-free gap between plots so they never join.",
        ],
        "stations": st,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    return OUT, len(st)


def selftest():
    st = stations()
    ids = [s["id"] for s in st]
    assert len(ids) == len(set(ids)) == 39, len(ids)
    for e in EXTRAS:
        assert f"vis_{e}_dirt_D3" in ids and "_" not in e, e   # review_map reads the state as id.split("_")[1]
    for g in ("dirt", "stone"):
        for s in ("dry", "water", "tar", "scorched"):
            for d in (1, 2, 3, 4):
                assert f"vis_{s}_{g}_D{d}" in ids
    cells = set()
    for s in st:
        ox, oz = origin_of(s, 0, 0)
        for x in range(ox, ox + PLOT_W):
            for z in range(oz, oz + PLOT_H):
                assert (x, z) not in cells, "plots overlap at %s" % ((x, z),)
                cells.add((x, z))
        ops = station_ops(s, 10, 10)
        assert ops[0][0] == "jawa/set_terrain_batch" and ops[-1][0] == "jawa/spawn_pawn"
        if s["setup"]["fluid"]:
            assert 1 <= s["setup"]["fill_level"] < s["setup"]["pit"]["depth"] or s["setup"]["pit"]["depth"] == 1
    print("ok  39 stations, full D1-D4 x dirt/stone x dry/water/tar/scorched grid + 7 liquids, no overlaps")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    path, n = write()
    print("WROTE %s (%d stations)" % (path, n))
