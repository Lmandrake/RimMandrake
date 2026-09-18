"""QUICKTEST_RIVER_WATER_MISSING_1 — repro AND fix-verification for the
missing-water bug.

ROOT CAUSE (measured 2026-09-18): FlowWorks' generated compat patch wrote
`<viscosityClass>water</viscosityClass>` (lowercase) into a modExtension on
nine vanilla/Odyssey water TerrainDefs. RimWorld parses enum fields with a
CASE-SENSITIVE Enum.Parse, the parse throws, and DirectXmlToObjectNew
DISCARDS THE WHOLE TARGET DEF. With WaterShallow/WaterDeep/... absent, every
BiomeDef's water*Terrain field resolves to null, so river/lake/coast tile
mutators paint their channel with a NULL terrain and no map has any water.

Run this against a live bridge. Two independent checks:

  A. DEF CHECK (cheap, no map needed) — do the vanilla water TerrainDefs
     exist? This is the direct read of the bug. Requires only a loaded game.
  B. MAP CHECK (expensive) — generate a map at a land tile carrying a
     river/lake/coast TileMutatorDef and scan EVERY cell for water terrain.
     Pass --generate to run it; it creates a Settlement + map and removes
     both afterwards.

⚠️ Check A is the one that settles it. Check B is what a human notices.
⚠️ A screenshot proves nothing here — a generated map has rendered as a blank
   mesh while holding correct data. Both checks read DATA.
"""
import argparse
import json
import sys

sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb  # noqa: E402

# The exact set RM_LiquidProperties_CompatIndex.xml targets. Every one of
# these read MISSING on 2026-09-18; ToxicWaterOceanDeep and
# ToxicWaterMovingShallow are NOT targeted and survived, which is the
# controlled pair that pinned the patch as the cause.
PATCHED = [
    "WaterShallow", "WaterDeep", "WaterMovingShallow", "WaterMovingChestDeep",
    "WaterOceanShallow", "WaterOceanDeep", "ToxicWaterShallow", "ToxicWaterDeep",
    "Marsh",
]
# Untouched by the patch — these must stay FOUND in every run, or the
# instrument itself is lying rather than the game being broken.
CONTROLS = ["Gravel", "Sand", "MarshyTerrain", "Riverbank",
            "ToxicWaterOceanDeep", "ToxicWaterMovingShallow"]


def connect():
    host, port, token = rb.resolve_endpoint()
    s = rb.RimBridge(host=host, port=port, token=token, timeout=900.0)
    s.connect()
    return s


def make_caller(s):
    def call(tool, **params):
        r = s.call(tool, params) or {}
        if isinstance(r, dict) and r.get("content"):
            try:
                r = json.loads(r["content"][0]["text"])
            except Exception:
                pass
        if isinstance(r, dict):
            r.pop("operation", None)
        return r
    return call


def check_defs(call):
    """A: are the water TerrainDefs actually loaded?"""
    names = PATCHED + CONTROLS
    r = call("jawa/get_defs",
             defs=";".join("TerrainDef/" + n for n in names),
             fields="defName", limit=len(names) + 5)
    found = {d.get("defName"): bool(d.get("found")) for d in r.get("defs", [])}

    bad_controls = [n for n in CONTROLS if not found.get(n)]
    if bad_controls:
        print("INSTRUMENT FAILURE: control defs missing:", bad_controls)
        print("  Do not read anything else in this run as evidence.")
        return None

    missing = [n for n in PATCHED if not found.get(n)]
    print("=== A. water TerrainDef existence ===")
    for n in names:
        print(f"  {'FOUND  ' if found.get(n) else 'MISSING'}  {n}")
    print(f"  controls all present: yes ({len(CONTROLS)})")
    print(f"  patched-set missing: {len(missing)} of {len(PATCHED)}")
    print("  VERDICT:", "BUG PRESENT" if missing else "FIXED — water defs load")
    return missing


def scan_map(call, map_id, size_x, size_z):
    """Full-coverage terrain census. Returns {terrain: cellCount}."""
    cells, read = {}, 0
    for z0 in range(0, size_z, 25):
        h = min(25, size_z - z0)
        r = call("jawa/get_terrain_batch",
                 rects=f"0,{z0},{size_x},{h}", mapId=map_id)
        read += r.get("cellsRead", 0)
        for run in (r.get("ops") or "").split(";"):
            if ":" not in run:
                continue
            name, spec = run.rsplit(":", 1)
            try:
                _x, _z, w, hh = [int(v) for v in spec.split(",")]
            except ValueError:
                continue
            cells[name] = cells.get(name, 0) + w * hh
    expected = size_x * size_z
    if read != expected:
        print(f"  COVERAGE GAP: read {read} of {expected} cells — verdict void.")
        return None
    return cells


def check_map(call, tile):
    """B: generate a map at `tile`, census it, then remove what we made."""
    print(f"\n=== B. map generation at tile {tile} ===")
    mut = call("jawa/world_mutators_get", tiles=str(tile))
    rows = mut.get("tiles") or []
    if not rows:
        print("  no such tile.")
        return
    names = [m["def"] for m in (rows[0].get("mutators") or [])]
    print(f"  biome={rows[0].get('biome')} mutators={names}")

    gen = call("jawa/world_tile_map_generate", tile=tile,
               suggestedMapParent="Settlement")
    if not gen.get("success"):
        print("  generate FAILED:", json.dumps(gen)[:300])
        return
    map_id = gen["mapId"]
    try:
        cells = scan_map(call, map_id, gen["mapSize"]["x"], gen["mapSize"]["z"])
        if cells is None:
            return
        water = {k: v for k, v in cells.items()
                 if any(t in k.lower() for t in ("water", "brine", "ocean"))}
        print(f"  {len(cells)} distinct terrains; water-family = {water}")
        print("  VERDICT:", "WATER PRESENT" if water else "ZERO WATER — BUG PRESENT")
    finally:
        objs = call("jawa/world_objects_get", tiles=str(tile))
        for o in objs.get("objects", []):
            if o.get("isSettlement"):
                call("jawa/settlement_remove", mode="settlement",
                     settlementId=o["id"], force=True)
        left = call("jawa/world_objects_get", tiles=str(tile))
        ids = [str(o["id"]) for o in left.get("objects", [])]
        if ids:
            call("jawa/world_objects_remove", ids=",".join(ids))
        print("  cleaned up:", call("jawa/world_objects_get",
                                    tiles=str(tile)).get("count"), "objects left")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--generate", action="store_true",
                    help="also run check B (creates and removes a map)")
    ap.add_argument("--tile", type=int, default=8500,
                    help="land tile carrying a river/lake/coast mutator")
    args = ap.parse_args()

    call = make_caller(connect())
    check_defs(call)
    if args.generate:
        check_map(call, args.tile)


if __name__ == "__main__":
    sys.exit(main())
