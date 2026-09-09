#!/usr/bin/env python3
"""
SEA_ENRICHMENT_LANDMARKS_1 -- apply the already-vetted grey_sea.csv / twilight_sea.csv
landmark plans (design/Jawa/worldbuilding/enrichment/{grey_sea,twilight_sea}.csv) to the
live Ash'karr world via the RimBridge jawa/world_* tools, with full before/after
measurement and a whole-planet mutator-loss diff.

Run under WINDOWS python (python.exe), from the repo root, with a relative path:
    python.exe Transient/seal_apply.py --step measure
    python.exe Transient/seal_apply.py --step apply
    python.exe Transient/seal_apply.py --step verify
"""
import csv
import json
import sys
import argparse
from collections import Counter, defaultdict

sys.path.insert(0, "src/RimMandrake/Utils")
from rimbridge_client import RimBridge, discover_from_log

TILES_CSV = "world/ASHKARR_WORLDMAP_tiles.csv"
GREY_CSV = "design/Jawa/worldbuilding/enrichment/grey_sea.csv"
TWI_CSV = "design/Jawa/worldbuilding/enrichment/twilight_sea.csv"


def load_plan(path):
    rows = []
    with open(path, newline="") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            break
        f.seek(0)
        r = csv.reader(l for l in f if not l.startswith("#") and l.strip())
        header = next(r)
        assert header == ["tile", "action", "def"], header
        for row in r:
            rows.append({"tile": int(row[0]), "action": row[1], "def": row[2]})
    return rows


def load_sea_tiles():
    seas = defaultdict(list)
    with open(TILES_CSV, newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            b = row["biome"]
            if b in ("RUT_GreySea", "RUT_TwilightSea"):
                seas[b].append(int(row["tile"]))
    return seas


def connect():
    host, port, token = discover_from_log()
    if not port or not token:
        print("FATAL: could not discover bridge host/port/token from Player.log", file=sys.stderr)
        sys.exit(2)
    rb = RimBridge(host, port, token)
    rb.connect()
    return rb


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def get_mutators_for_tiles(rb, tile_ids):
    """Return {tile: {'mutators': [...], 'landmark': str|None}} for the given tiles."""
    out = {}
    for group in chunks(tile_ids, 300):
        res = rb.call(
            "jawa/world_mutators_get",
            {"tiles": ",".join(str(t) for t in group), "limit": len(group) + 5},
        )
        for row in res.get("tiles", []):
            out[int(row["tile"])] = {
                "mutators": row.get("mutators", []),
                "landmark": row.get("landmark"),
            }
    return out


def get_all_mutators_full_planet(rb, total_tiles):
    """Harvest the WHOLE planet's mutators via range paging, for the loss diff."""
    out = {}
    step = 2000
    for start in range(0, total_tiles + 1, step):
        end = min(start + step - 1, total_tiles)
        res = rb.call(
            "jawa/world_mutators_get",
            {"range": f"{start}-{end}", "limit": step + 10},
        )
        for row in res.get("tiles", []):
            t = int(row["tile"])
            muts = row.get("mutators", [])
            lm = row.get("landmark")
            if muts or lm:
                out[t] = {"mutators": muts, "landmark": lm}
    return out


def cmd_measure(rb, outpath):
    seas = load_sea_tiles()
    grey_tiles = seas["RUT_GreySea"]
    twi_tiles = seas["RUT_TwilightSea"]
    grey_state = get_mutators_for_tiles(rb, grey_tiles)
    twi_state = get_mutators_for_tiles(rb, twi_tiles)
    grey_landmarked = sum(1 for t in grey_tiles if grey_state.get(t, {}).get("landmark"))
    twi_landmarked = sum(1 for t in twi_tiles if twi_state.get(t, {}).get("landmark"))
    result = {
        "grey_sea_tile_count": len(grey_tiles),
        "grey_sea_landmarked": grey_landmarked,
        "twilight_sea_tile_count": len(twi_tiles),
        "twilight_sea_landmarked": twi_landmarked,
        "grey_sea_tiles": grey_tiles,
        "twilight_sea_tiles": twi_tiles,
    }
    with open(outpath, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps({k: v for k, v in result.items() if not k.endswith("_tiles")}, indent=2))


def cmd_apply(rb, outpath):
    grey_plan = load_plan(GREY_CSV)
    twi_plan = load_plan(TWI_CSV)
    plan = grey_plan + twi_plan
    by_def = defaultdict(list)
    for row in plan:
        by_def[row["def"]].append(row["tile"])

    results = []
    for defname, tiles in by_def.items():
        for group in chunks(tiles, 150):
            res = rb.call(
                "jawa/world_landmarks_set",
                {
                    "action": "add",
                    "def": defname,
                    "tiles": ",".join(str(t) for t in group),
                    "forced": False,
                    "checkValid": True,
                },
            )
            results.append({"def": defname, "tiles": group, "result": res})

    with open(outpath, "w") as f:
        json.dump(results, f, indent=2)

    # summarize
    total_added = 0
    invalid = []
    for r in results:
        res = r["result"]
        total_added += res.get("added", 0)
        for v in res.get("validity", []) or []:
            if not v.get("isValidTile", True):
                invalid.append({"def": r["def"], "tile": v.get("tile")})
    print(json.dumps({"total_added": total_added, "invalid_precheck": invalid[:50], "invalid_count": len(invalid)}, indent=2))


def cmd_commit(rb):
    res = rb.call("jawa/world_commit", {})
    print(json.dumps(res, indent=2))


def cmd_verify(rb, before_path, after_measure_path, full_before_path, full_after_path):
    seas = load_sea_tiles()
    grey_tiles = seas["RUT_GreySea"]
    twi_tiles = seas["RUT_TwilightSea"]
    grey_state = get_mutators_for_tiles(rb, grey_tiles)
    twi_state = get_mutators_for_tiles(rb, twi_tiles)
    grey_landmarked = sum(1 for t in grey_tiles if grey_state.get(t, {}).get("landmark"))
    twi_landmarked = sum(1 for t in twi_tiles if twi_state.get(t, {}).get("landmark"))
    after = {
        "grey_sea_tile_count": len(grey_tiles),
        "grey_sea_landmarked": grey_landmarked,
        "twilight_sea_tile_count": len(twi_tiles),
        "twilight_sea_landmarked": twi_landmarked,
    }
    with open(after_measure_path, "w") as f:
        json.dump(after, f, indent=2)
    print("AFTER:", json.dumps(after, indent=2))

    # whole-planet diff
    stats = rb.call("jawa/world_stats", {})
    # try to find total tile count field
    total_tiles = None
    for k in ("totalTiles", "tileCount", "tiles"):
        if isinstance(stats.get(k), int):
            total_tiles = stats[k]
            break
    if total_tiles is None:
        total_tiles = 21872  # known planet size, fallback
    full_after = get_all_mutators_full_planet(rb, total_tiles)
    with open(full_after_path, "w") as f:
        json.dump(full_after, f, indent=2)

    with open(full_before_path) as f:
        full_before = json.load(f)
    full_before = {int(k): v for k, v in full_before.items()}

    lost = Counter()
    lost_examples = defaultdict(list)
    for t, before_row in full_before.items():
        after_row = full_after.get(t, {"mutators": [], "landmark": None})
        before_muts = set(before_row.get("mutators", []))
        after_muts = set(after_row.get("mutators", []))
        for d in before_muts - after_muts:
            lost[d] += 1
            if len(lost_examples[d]) < 5:
                lost_examples[d].append(t)
    print("WHOLE-PLANET MUTATOR LOSSES:", json.dumps({d: {"count": c, "examples": lost_examples[d]} for d, c in lost.items()}, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", required=True, choices=["measure", "apply", "commit", "verify"])
    ap.add_argument("--out", default="Transient/seal_measure_before.json")
    ap.add_argument("--apply-out", default="Transient/seal_apply_results.json")
    ap.add_argument("--full-before", default="Transient/seal_full_mutators_before.json")
    ap.add_argument("--full-after", default="Transient/seal_full_mutators_after.json")
    ap.add_argument("--after-measure", default="Transient/seal_measure_after.json")
    args = ap.parse_args()

    rb = connect()
    try:
        if args.step == "measure":
            cmd_measure(rb, args.out)
        elif args.step == "apply":
            cmd_apply(rb, args.apply_out)
        elif args.step == "commit":
            cmd_commit(rb)
        elif args.step == "verify":
            cmd_verify(rb, args.out, args.after_measure, args.full_before, args.full_after)
    finally:
        rb.close()
