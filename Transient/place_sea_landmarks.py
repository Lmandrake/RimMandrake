import sys, json, csv
from collections import defaultdict, Counter

sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

CSVS = {
    "RUT_GreySea": r"D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\enrichment\grey_sea.csv",
    "RUT_TwilightSea": r"D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\enrichment\twilight_sea.csv",
}
OUTDIR = r"D:\Luke\dev\Rimworld\Transient"
SEA_TILES = json.load(open(OUTDIR + r"\sea_tile_sets.json"))  # {"grey":[...], "twilight":[...]}

by_def = defaultdict(list)   # def -> [tile,...]  (rows to write)
plan_rows = []                # (sea, tile, def)
for sea, path in CSVS.items():
    with open(path) as f:
        for row in csv.reader(f):
            if not row or row[0].startswith("#") or row[0] == "tile":
                continue
            tile, action, defname = row[0], row[1], row[2]
            assert action == "landmark", (sea, row)
            by_def[defname].append(tile)
            plan_rows.append((sea, tile, defname))

all_touched = sorted(set(t for _, t, _ in plan_rows), key=int)
all_defs = sorted(by_def.keys())
print("total rows:", len(plan_rows), "unique tiles:", len(all_touched), "defs:", all_defs)

host, port, token = resolve_endpoint()
print("endpoint:", host, port)


def landmark_tiles_for_defs(rb, defs):
    """def -> set(tile) currently carrying that landmark, planet-wide."""
    out = {}
    for d in defs:
        r = rb.call("jawa/world_landmarks_get", {"def": d, "limit": 5000})
        tiles = set(str(row["tile"]) for row in r.get("landmarks", []))
        out[d] = tiles
        if r.get("returned") != r.get("count"):
            print("  WARNING: %s returned=%s count=%s (possible cap hit)" % (d, r.get("returned"), r.get("count")))
    return out


def read_mutators(rb, tiles):
    out = {}
    for i in range(0, len(tiles), 100):
        chunk = tiles[i:i + 100]
        r = rb.call("jawa/world_mutators_get", {"tiles": ",".join(chunk), "limit": 100})
        for row in r.get("tiles", []):
            out[str(row["tile"])] = set(m["def"] for m in row.get("mutators", []))
    return out


with RimBridge(host, port, token) as rb:
    ui = rb.call("rimworld/get_ui_state", {})
    print("programState:", ui.get("programState"), "hasCurrentGame:", ui.get("hasCurrentGame"))

    # ---- BEFORE ----
    before_landmark_tiles = landmark_tiles_for_defs(rb, all_defs)
    before_touched_hits = [(sea, t, d) for sea, t, d in plan_rows if t in before_landmark_tiles[d]]
    print("BEFORE: planned (tile,def) pairs already present:", len(before_touched_hits), "(expect 0)")

    grey_before_covered = sum(1 for t in SEA_TILES["grey"] if any(t in before_landmark_tiles[d] for d in all_defs))
    twi_before_covered = sum(1 for t in SEA_TILES["twilight"] if any(t in before_landmark_tiles[d] for d in all_defs))
    # note: this only counts the 5 defs in THIS plan; twilight's pre-existing VEE_GravelBeach@5307
    # is counted here since VEE_GravelBeach is one of the 5 planned defs.
    print("BEFORE coverage (of these 5 defs) -- Grey:", grey_before_covered, "/", len(SEA_TILES["grey"]),
          " Twilight:", twi_before_covered, "/", len(SEA_TILES["twilight"]))

    mut_before = read_mutators(rb, all_touched)
    with open(OUTDIR + r"\sea_mutators_before.json", "w") as fo:
        json.dump({k: sorted(v) for k, v in mut_before.items()}, fo, indent=2)

    # ---- APPLY ----
    total_added = 0
    failures = []
    for defname, tiles in by_def.items():
        tiles_csv = ",".join(tiles)
        res = rb.call("jawa/world_landmarks_set", {
            "action": "add",
            "def": defname,
            "tiles": tiles_csv,
        })
        added = res.get("added")
        print(defname, "tiles=%d" % len(tiles), "success=%s added=%s" % (res.get("success"), added))
        if not res.get("success"):
            failures.append((defname, res))
        else:
            total_added += (added if isinstance(added, int) else len(tiles))

    print("TOTAL rows attempted:", sum(len(v) for v in by_def.values()), "reported added:", total_added)
    if failures:
        print("SET-CALL FAILURES:", json.dumps(failures, indent=2)[:3000])

    commit = rb.call("jawa/world_commit", {})
    print("world_commit:", commit.get("success"))

    # ---- AFTER ----
    after_landmark_tiles = landmark_tiles_for_defs(rb, all_defs)
    missing = []
    for sea, tile, defname in plan_rows:
        if tile not in after_landmark_tiles[defname]:
            missing.append((sea, tile, defname))
    print("MISSING landmark placements:", len(missing))
    for m in missing[:40]:
        print("  ", m)
    with open(OUTDIR + r"\sea_landmarks_missing.json", "w") as fo:
        json.dump(missing, fo, indent=2)

    grey_after_covered = sum(1 for t in SEA_TILES["grey"] if any(t in after_landmark_tiles[d] for d in all_defs))
    twi_after_covered = sum(1 for t in SEA_TILES["twilight"] if any(t in after_landmark_tiles[d] for d in all_defs))
    print("AFTER coverage (of these 5 defs) -- Grey:", grey_after_covered, "/", len(SEA_TILES["grey"]),
          " Twilight:", twi_after_covered, "/", len(SEA_TILES["twilight"]))

    mut_after = read_mutators(rb, all_touched)
    with open(OUTDIR + r"\sea_mutators_after.json", "w") as fo:
        json.dump({k: sorted(v) for k, v in mut_after.items()}, fo, indent=2)

    lost = Counter()
    gained = Counter()
    for t in all_touched:
        b = mut_before.get(t, set())
        a = mut_after.get(t, set())
        for d in (b - a):
            lost[d] += 1
        for d in (a - b):
            gained[d] += 1
    print("MUTATOR LOSSES on touched tiles (def: count):", dict(lost))
    print("MUTATOR GAINS on touched tiles (def: count):", dict(gained))
    with open(OUTDIR + r"\sea_mutator_diff.json", "w") as fo:
        json.dump({"lost": dict(lost), "gained": dict(gained)}, fo, indent=2)

    summary = {
        "grey_before": grey_before_covered, "grey_after": grey_after_covered, "grey_total": len(SEA_TILES["grey"]),
        "twilight_before": twi_before_covered, "twilight_after": twi_after_covered, "twilight_total": len(SEA_TILES["twilight"]),
        "rows_attempted": sum(len(v) for v in by_def.values()),
        "rows_added_reported": total_added,
        "missing_count": len(missing),
        "mutator_losses": dict(lost),
        "mutator_gains": dict(gained),
    }
    with open(OUTDIR + r"\sea_landmarks_summary.json", "w") as fo:
        json.dump(summary, fo, indent=2)
    print("SUMMARY:", json.dumps(summary))
