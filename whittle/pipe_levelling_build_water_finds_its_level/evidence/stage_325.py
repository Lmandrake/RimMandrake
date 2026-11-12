"""Stage the A3 site for pipe_levelling_perf_proof.py on the running game: a player Settlement at TILE, its 325x325 map made
current, one colonist, giant plants cleared twice (skills/live-debugging-proof-harness/references/sites-and-timing.md, "Staging
the 325 pipe-levelling perf site"), and any RM_HugeTrunkBlocker left in the rig gap destroyed.

  python.exe whittle/pipe_levelling_build_water_finds_its_level/evidence/stage_325.py TILE
"""
import json
import os
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
for p in ("src/RimMandrake/FlowWorks/northstar", "src/RimMandrake/Utils"):
    sys.path.insert(0, os.path.join(REPO, p))
import validation_core as V  # noqa: E402
import proof_hose as PH  # noqa: E402

B = V.guard(PH.PB())
tile = int(sys.argv[1])


def show(tag, r):
    r = dict(r or {})
    r.pop("operation", None)
    r.pop("state", None)
    print(tag, json.dumps(r, default=str)[:400], flush=True)
    return r


fs = (B.call("jawa/list_factions") or {})
fs = fs.get("factions") or fs.get("items") or []
pdef = [f.get("def") or f.get("defName") for f in fs if f.get("isPlayer")]
show("ADD", B.call("jawa/world_objects_add", **{"def": "Settlement", "tile": tile, "faction": pdef[0], "name": "RM_PerfSite"}))
t = time.time()
g = show("GEN %.0fs" % 0, B.call("jawa/world_tile_map_generate", tile=tile, sizeX=325, sizeZ=325))
print("generated in %.0f s" % (time.time() - t))
mid = g.get("mapId") if g.get("mapId") is not None else g.get("mapIndex")
show("SET", B.call("jawa/set_current_map", mapId=int(mid)))
mi = B.call("jawa/map_info") or {}
print("MAP", {k: mi.get(k) for k in ("mapId", "sizeX", "sizeZ", "tile", "hilliness")}, (mi.get("biome") or {}) if isinstance(mi.get("biome"), str) else "")
show("PAWN", B.call("jawa/spawn_pawn", kindDef="Colonist", x=320, z=323, faction="player"))
print("CLEAR", str(V.clear_huge_plants(B))[:300])
print("CLEAR2", str(V.clear_huge_plants(B))[:300])
lt = (B.call("jawa/list_things", defName="RM_HugeTrunkBlocker", limit=5000) or {}).get("things") or []
ins = [(t["x"], t["z"]) for t in lt if "x" in t and 135 <= t["x"] <= 190]
print("INSITE", ins)
for x, z in ins:
    show("DESTROY %d,%d" % (x, z), B.call("jawa/destroy_batch", rects="%d,%d,1,1" % (x, z), categories="Building"))
mi = B.call("jawa/map_info") or {}
print("MAPEND", {k: mi.get(k) for k in ("mapId", "sizeX", "sizeZ", "tile")})
