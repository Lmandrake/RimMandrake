"""FISH_BESTIARY_BUILD_1 -- live fishing-pass re-verification.

Waves 1-5 of this item deferred a live bridge quicktest five times; the
2026-09-18 live-verification pass finally ran one and found:
  - Scald: FAIL, root-caused to SCALD_MECHANICS_1's own owed cove-painting
    (RUT_ScaldMargin never placed on the live planet). Not this item's own
    defect.
  - Wasteland/Cracked Lands/Weeping Stones/Greentide: UNABLE TO VERIFY --
    every generated map anywhere came back with ZERO water terrain, root
    caused separately to QUICKTEST_RIVER_WATER_MISSING_1 (FlowWorks'
    generated compat patch wrote a lowercase `<viscosityClass>water</...>`
    that a case-sensitive Enum.Parse threw on, discarding 9 vanilla water
    TerrainDefs and nulling every land BiomeDef's water fields).

That bug is now CLOSED (`fe3b2be2c`), live-reverified on the campaign world
(RUT_Greentide tile 8501: check A+B both pass, 9629 water-family cells).
This script re-runs the SAME live fishing/mining pass across the waters that
were UNABLE TO VERIFY, now that the blocker is gone, plus a Twilight spot
check (TWILIGHT_DEEP_WATER_LAYER_1 closed 2026-09-20, hold lifted, deployed,
owed one restart + live check per this item's own 2026-09-20 correction).
Scald is intentionally NOT re-tested here -- its blocker (the cove) is
unchanged and belongs to SCALD_MECHANICS_1, not this item.

Run against a live bridge (python.exe, not python3 -- WSL cannot reach the
bridge's Windows-loopback socket). Creates a Settlement + map per water
tested and removes both afterward -- nothing kept.
"""
_RM_ROOT = __import__("pathlib").Path(__file__).resolve().parents[3]  # repo root, derived (not hardcoded)
import json
import os
import sys

sys.path.insert(0, str(_RM_ROOT / 'src' / 'RimMandrake' / 'Utils'))
import rimbridge_client as rb  # noqa: E402

FISHING_DESIGNATOR = "architect-designator:zone:highlight-designator-zoneadd-fishing"

# (label, biome defName, candidate tiles, mode)
#   mode "fish"  -> look for water, try a Fishing-zone placement
#   mode "brine" -> look for RUT_WastesBrine* terrain + list_things for deposits
WATERS = [
    ("Greentide",     "RUT_Greentide",     [256, 635, 776, 781, 1174], "fish"),
    ("Cracked Lands", "RUT_CrackedLands",  [9225, 14, 20, 107, 110],   "fish"),
    ("Weeping Stones","RUT_WeepingStones", [7344, 10, 83, 142, 144],   "fish"),
    ("Wasteland",     "RUT_Wastes",     [224, 0, 23, 36, 47],       "brine"),
    # The sea tile itself is impassable and canBuildBase false (its generated map is 100% deep brine, where vanilla
    # refuses a fishing zone: Designator_ZoneAdd_Fishing needs a passable cell). Its catch is fished FROM THE SHORE: a land
    # tile beside the sea, whose salt water SeaShores' SetFishTypes postfix stocks from the sea's own table. So Twilight
    # is a "shore" row: tiles are found from the live grid, not listed.
    ("Twilight",      "RUT_TwilightSea",   [],                          "shore"),
]
SHORE_SEAS = {"Twilight": ("RUT_TwilightSea", "RM_TwilightSea")}


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


def scan_map(call, map_id, size_x, size_z):
    """Full-coverage terrain census -> {terrain: [(x,z,w,h), ...]}."""
    runs, read = {}, 0
    for z0 in range(0, size_z, 25):
        h = min(25, size_z - z0)
        r = call("jawa/get_terrain_batch", rects=f"0,{z0},{size_x},{h}", mapId=map_id)
        read += r.get("cellsRead", 0)
        for run in (r.get("ops") or "").split(";"):
            if ":" not in run:
                continue
            name, spec = run.rsplit(":", 1)
            try:
                x, z, w, hh = [int(v) for v in spec.split(",")]
            except ValueError:
                continue
            runs.setdefault(name, []).append((x, z, w, hh))
    expected = size_x * size_z
    if read != expected:
        print(f"    COVERAGE GAP: read {read} of {expected} cells -- result void.")
        return None
    return runs


def cleanup(call, tile):
    objs = call("jawa/world_objects_get", tiles=str(tile))
    for o in objs.get("objects", []):
        if o.get("isSettlement"):
            call("jawa/settlement_remove", mode="settlement",
                 settlementId=o["id"], force=True)
    left = call("jawa/world_objects_get", tiles=str(tile))
    ids = [str(o["id"]) for o in left.get("objects", [])]
    if ids:
        call("jawa/world_objects_remove", ids=",".join(ids))


def try_tile(call, label, biome, tile, mode):
    mut = call("jawa/world_mutators_get", tiles=str(tile))
    rows = mut.get("tiles") or []
    if not rows:
        print(f"  tile {tile}: no such tile, skip")
        return None
    actual_biome = rows[0].get("biome")
    names = [m.get("def") for m in (rows[0].get("mutators") or [])]
    print(f"  tile {tile}: biome={actual_biome} mutators={names}")
    if actual_biome != biome:
        print(f"    biome mismatch (expected {biome}), skip")
        return None

    gen = call("jawa/world_tile_map_generate", tile=tile, suggestedMapParent="Settlement")
    if not gen.get("success"):
        print("    generate FAILED:", json.dumps(gen)[:300])
        return None
    map_id = gen["mapId"]
    try:
        call("jawa/set_current_map", mapId=map_id)
        runs = scan_map(call, map_id, gen["mapSize"]["x"], gen["mapSize"]["z"])
        if runs is None:
            return None
        water = {k: v for k, v in runs.items()
                 if any(t in k.lower() for t in ("water", "brine", "ocean"))}
        total_water_cells = sum(w * h for spans in water.values() for (_, _, w, h) in spans)
        print(f"    {len(runs)} distinct terrains; water-family: "
              f"{ {k: len(v) for k, v in water.items()} }, total water cells={total_water_cells}")
        if not water:
            print("    VERDICT: ZERO WATER on this tile")
            return {"tile": tile, "water": False}

        if mode == "brine":
            things = call("jawa/list_things", limit=100000)
            all_things = things.get("things") or things.get("items") or []
            deposits = [t for t in all_things
                        if isinstance(t, dict) and str(t.get("defName", "")).startswith("RUT_BrineDeposit_")]
            print(f"    scanned {len(all_things)} things; RUT_BrineDeposit_* found: {len(deposits)}")
            for d in deposits[:5]:
                print("      ", d.get("defName"), d.get("position") or d.get("pos"))
            return {"tile": tile, "water": True, "deposits": len(deposits)}

        # mode == "fish": find a shallow water run and try a Fishing zone there
        shallow_runs = []
        for name, spans in water.items():
            if "shallow" in name.lower():
                shallow_runs.extend((name, s) for s in spans)
        target_pool = shallow_runs or [(n, s) for n, spans in water.items() for s in spans]
        placed = False
        attempt_note = ""
        for name, (x, z, w, h) in target_pool[:5]:
            rw, rh = min(w, 3), min(h, 3)
            r = call("rimworld/apply_architect_designator",
                     designatorId=FISHING_DESIGNATOR,
                     x=x, z=z, width=rw, height=rh, keepSelected=False)
            ok = bool(r.get("success"))
            print(f"    Fishing-zone attempt on {name} @({x},{z},{rw}x{rh}): "
                  f"{'OK' if ok else 'REJECTED'} {'' if ok else (r.get('message') or r.get('error') or json.dumps(r)[-300:])}")
            if ok:
                placed = True
                break
            attempt_note = json.dumps(r)[:200]
        print("    VERDICT:", "FISHING ZONE PLACED" if placed else "REJECTED on every water run tried")
        return {"tile": tile, "water": True, "fishing_zone": placed, "note": attempt_note}
    finally:
        cleanup(call, tile)


def sea_catches(label):
    """The sea's catch defNames, read from the shipped RM_ BiomeDef (RUT_TwilightSea's patch names the same species)."""
    import xml.etree.ElementTree as ET
    f = _RM_ROOT / "src" / "RimMandrake" / "TerminalBiomes" / "Defs" / "BiomeDefs" / ("RM_%sSea.xml" % label)
    ft = ET.parse(str(f)).getroot().find("BiomeDef/fishTypes")
    names = set()
    for band in (ft if ft is not None else []):
        names.update(c.tag for c in band)
    names.discard("rareCatchesSetMaker")
    return names


def shore_tiles(call, seas, limit=5):
    """Land tiles with a sea neighbour, from the live grid (world_tile_export + world_neighbors, written under the
    agent data root -- this runs under python.exe, so one path serves the bridge and this reader)."""
    import csv
    from rmpaths import rm_path
    d = rm_path("scratch", "fish_shore")
    os.makedirs(str(d), exist_ok=True)
    tcsv, ncsv = str(d / "tiles.csv"), str(d / "neighbors.csv")
    e = call("jawa/world_tile_export", path=tcsv, format="csv", extended=True)
    n = call("jawa/world_neighbors", path=ncsv)
    if not (e.get("success") and n.get("success")):
        print("    world export FAILED:", json.dumps(e)[:200], json.dumps(n)[:200])
        return []
    biome, water = {}, {}
    with open(e.get("path") or tcsv, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            biome[int(r["tile"])] = r["biome"]
            water[int(r["tile"])] = str(r.get("waterCovered")).strip().lower() == "true"
    out = []
    with open(n.get("path") or ncsv, newline="", encoding="utf-8") as f:
        rd = csv.reader(f)
        next(rd)
        for r in rd:
            if not r or not r[0].strip().isdigit():
                continue
            t = int(r[0])
            if biome.get(t) in seas or water.get(t, True):
                continue
            nb = [int(v) for c in r[1:] for v in c.replace(";", " ").split() if v.lstrip("-").isdigit() and int(v) >= 0]
            if any(biome.get(x) in seas for x in nb):
                out.append(t)
                if len(out) >= limit:
                    break
    print(f"  shore tiles beside {sorted(seas)}: {out}")
    return out


def try_shore(call, label, tile):
    """Generate the shore tile's map, read the salt-water body's fish, and judge it against the sea's own table."""
    want = sea_catches(label)
    gen = call("jawa/world_tile_map_generate", tile=tile, suggestedMapParent="Settlement")
    if not gen.get("success"):
        print("    generate FAILED:", json.dumps(gen)[:300])
        return None
    map_id = gen["mapId"]
    try:
        call("jawa/set_current_map", mapId=map_id)
        runs = scan_map(call, map_id, gen["mapSize"]["x"], gen["mapSize"]["z"])
        if runs is None:
            return None
        sea = [(k, sp) for k, v in runs.items() for sp in v
               if any(t in k.lower() for t in ("ocean", "brine")) and "deep" not in k.lower()]
        sea = sea or [(k, sp) for k, v in runs.items() for sp in v if any(t in k.lower() for t in ("ocean", "brine"))]
        if not sea:
            print("    VERDICT: no sea water on this shore map (SITE)")
            return {"tile": tile, "water": False}
        name, (x, z, w, h) = sea[0]
        fr = call("jawa/fishing", action="read", x=x, z=z)
        body = fr.get("body") if isinstance(fr.get("body"), dict) else {}
        got = set(str(f) for f in (body.get("commonFish") or []) + (body.get("uncommonFish") or []))
        hit = sorted(got & want)
        verdict = "PASS" if hit else ("UNMEASURED" if not body.get("hasBody") or not body.get("hasFish") else "FAIL")
        print(f"    {name} @({x},{z}) body={json.dumps(body)[:300]}")
        print(f"    VERDICT: {verdict} (sea catches on the shore: {hit or 'none'}; want any of {sorted(want)})")
        return {"tile": tile, "water": True, "verdict": verdict, "catches": hit, "body": body}
    finally:
        cleanup(call, tile)


def check_biome_defs(call):
    """Cheap live-def check: does each BiomeDef actually carry maxFishPopulation
    and fishTypes right now, independent of any map generation?"""
    print("=== live BiomeDef fishTypes check ===")
    names = [b for _, b, _, _ in WATERS]
    r = call("jawa/get_defs", defs=";".join("BiomeDef/" + n for n in names),
              fields="defName,maxFishPopulation,fishTypes", limit=len(names) + 5)
    for d in r.get("defs", []):
        f = d.get("fields") or {}
        print(f"  {d.get('defName')}: maxFishPopulation={f.get('maxFishPopulation')} "
              f"fishTypes={'set' if f.get('fishTypes') else 'EMPTY/unset'}")
    return r


def main():
    call = make_caller(connect())
    check_biome_defs(call)
    results = {}
    only = set(sys.argv[1:])  # optional: run just these labels
    for label, biome, tiles, mode in WATERS:
        if only and label not in only:
            continue
        print(f"\n=== {label} ({biome}, mode={mode}) ===")
        result = None
        if mode == "shore":
            tiles = shore_tiles(call, set(SHORE_SEAS[label]))
        for tile in tiles:
            result = try_shore(call, label, tile) if mode == "shore" else try_tile(call, label, biome, tile, mode)
            if result and result.get("water"):
                break
        results[label] = result
    print("\n=== SUMMARY ===")
    for label, r in results.items():
        print(f"  {label}: {r}")
    return results


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
