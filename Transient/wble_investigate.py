"""WORLD_BOUNDARY_LAND_AT_SEA_ELEVATION_1 - investigation.
Get full landBiomeSubmerged list, spot-check tiles directly, test boundary-bleed
adjacency to the three seas.
Run: python.exe Transient/wble_investigate.py   (from repo root, per repo convention)
"""
import sys, os, json, csv

sys.path.insert(0, os.path.join("src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402

SEAS = {"RUT_TheScald", "RUT_GreySea", "RUT_TwilightSea"}

host, port, token = resolve_endpoint()
if not token:
    print("NO TOKEN - is the game running?")
    sys.exit(2)

with RimBridge(host, port, token) as rb:
    gi = rb.call("rimworld/get_ui_state", {})
    print("ui_state windows:", [w.get("type") for w in gi.get("windows", [])] if isinstance(gi.get("windows"), list) else gi.get("windows"))

    lint = rb.call("jawa/world_lint", {"limit": 250})
    lbs = lint.get("checks", {}).get("landBiomeSubmerged", {})
    count = lbs.get("count")
    examples = lbs.get("examples", [])
    print("landBiomeSubmerged count:", count, "examples returned:", len(examples))

    json.dump(lint, open(os.path.join("Transient", "wble_world_lint_full.json"), "w"), indent=2)
    print("Wrote Transient/wble_world_lint_full.json")

    tiles = [e["tile"] for e in examples]
    biome_by_tile = {e["tile"]: e["biome"] for e in examples}
    elev_by_tile = {e["tile"]: e["elevation"] for e in examples}

    from collections import Counter
    print("biome histogram of flagged tiles:", Counter(biome_by_tile.values()))

    # Spot-check a spread sample directly via world_tile_get: >=15-20 tiles,
    # spread across named biomes.
    by_biome = {}
    for t, b in biome_by_tile.items():
        by_biome.setdefault(b, []).append(t)
    sample = []
    for b, ts in by_biome.items():
        take = ts[:4] if len(ts) >= 4 else ts
        sample.extend(take)
    sample = sample[:30]
    print("sample size:", len(sample), "sample tiles:", sample)

    tg = rb.call("jawa/world_tile_get", {"tiles": ",".join(str(t) for t in sample)})
    json.dump(tg, open(os.path.join("Transient", "wble_spotcheck_tile_get.json"), "w"), indent=2)
    confirmed = 0
    mismatches = []
    for row in tg.get("tiles", []):
        tid = row.get("tile")
        exp_b = biome_by_tile.get(tid)
        exp_e = elev_by_tile.get(tid)
        live_b = row.get("biome")
        live_e = row.get("elevation")
        ok = (live_b == exp_b) and (abs((live_e or 0) - (exp_e or 0)) < 0.01) and (live_e is not None and live_e <= 0)
        if ok:
            confirmed += 1
        else:
            mismatches.append({"tile": tid, "lint": {"biome": exp_b, "elev": exp_e}, "live": {"biome": live_b, "elev": live_e}})
    print(f"CONFIRMED directly via world_tile_get: {confirmed}/{len(sample)}")
    if mismatches:
        print("MISMATCHES:", json.dumps(mismatches, indent=2))

    # Boundary-bleed test done OFFLINE: the grid adjacency
    # (world/world_neighbors_sub7b.csv) is a property of the sphere shape, not of
    # this world's content, and was already dumped. Combine it with the frozen
    # tiles CSV's biome column (re-exported live below via world_tile_get on the
    # neighbor ids of every flagged tile, so biome-adjacency is checked against
    # LIVE state, not a CSV that may have drifted) to test whether flagged tiles
    # cluster next to the three seas.
    all_tiles = tiles
    nbr_csv = os.path.join("world", "world_neighbors_sub7b.csv")
    nbr_of = {}
    with open(nbr_csv, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            tid = int(row["tile"])
            ns = [int(row[f"n{k}"]) for k in range(6) if int(row[f"n{k}"]) >= 0]
            nbr_of[tid] = ns

    all_neighbor_ids = set()
    for t in all_tiles:
        all_neighbor_ids.update(nbr_of.get(t, []))
    all_neighbor_ids -= set(all_tiles)
    print("distinct neighbor tiles to check (live) for sea biome:", len(all_neighbor_ids))

    nb_list = sorted(all_neighbor_ids)
    nbr_biome = {}
    CHUNK = 150
    for i in range(0, len(nb_list), CHUNK):
        chunk = nb_list[i:i + CHUNK]
        r = rb.call("jawa/world_tile_get", {"tiles": ",".join(str(x) for x in chunk)})
        for row in r.get("tiles", []):
            nbr_biome[row["tile"]] = row.get("biome")

    adjacent_to_sea = []
    not_adjacent = []
    for t in all_tiles:
        ns = nbr_of.get(t, [])
        sea_nbrs = [n for n in ns if nbr_biome.get(n) in SEAS]
        if sea_nbrs:
            adjacent_to_sea.append((t, sea_nbrs))
        else:
            not_adjacent.append(t)

    print(f"BOUNDARY-BLEED TEST: {len(adjacent_to_sea)}/{len(all_tiles)} flagged tiles are adjacent to a sea tile.")
    print(f"NOT adjacent to any sea: {len(not_adjacent)} tiles: {not_adjacent[:40]}")

    json.dump({
        "flagged_count": len(all_tiles),
        "adjacent_to_sea_count": len(adjacent_to_sea),
        "adjacent_to_sea_examples": adjacent_to_sea[:20],
        "not_adjacent_count": len(not_adjacent),
        "not_adjacent_tiles": not_adjacent,
    }, open(os.path.join("Transient", "wble_boundary_bleed_test.json"), "w"), indent=2)
    print("Wrote Transient/wble_boundary_bleed_test.json")
    print("done (no writes made this pass - investigation only)")
