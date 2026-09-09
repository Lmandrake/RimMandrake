"""WORLD_BOUNDARY_LAND_AT_SEA_ELEVATION_1 - the fix.

Diagnosis (full evidence in Transient/wble_world_lint_full.json,
Transient/wble_boundary_bleed_test.json, Transient/wble_precheck_*.json):

  171 of 181 flagged tiles sit INSIDE the Twilight Sea (128) or Grey Sea (43)
  region (per region field, 0/181 CSV/live biome mismatches so the field is
  current), already at elevation -350 with marine mutators (AnimalHabitat,
  Fish_Increased, WindyMutator + IceDunes/VEE_DeepSnow/Iceberg) - i.e. these
  ARE sea tiles in every respect except the biome field, which still carries a
  pre-flood land biome name. ashkarr_three_seas.py selected tiles by their OLD
  (region, biome) pair (Lake/Ocean/SeaIce) and never caught tiles whose old
  biome was something else. FIX: repaint biome to match the surrounding sea.

  10 of 181 are the WORLDMAP_LIQUID... "Damp" drained-lake-basin cluster
  authored 2026-09-07 (owner ruling, tiles 957/4924/9784/13026/13027 and
  4161/12269/12271/16042 -> dry land at 2m, orphan 1446 -> 21m, "lowest LAND
  neighbour minus 10m"). Live elevation on ALL 10 has regressed to -50..-94,
  and the frozen CSV (exported from a savegame rebase) carries the SAME
  regression, so this is not a live-session fluke, it is the canonical
  world's current state. Live neighbor elevations confirm the original
  formula (min land neighbour = 12m -> 2m target; matches). FIX: restore
  elevation only, biome and mutators untouched (biome drift on 4 of the
  5-cluster tiles is a later, unrelated pass and out of this item's scope).

Run: python.exe Transient/wble_fix.py
"""
import sys, os, json

sys.path.insert(0, os.path.join("src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402

plan = json.load(open(os.path.join("Transient", "wble_fix_plan.json")))
twilight = plan["twilight"]
grey = plan["grey"]
damp2m = [957, 4924, 9784, 13026, 13027, 4161, 12269, 12271, 16042]
damp21m = [1446]
assert set(damp2m + damp21m) == set(plan["damp"])

host, port, token = resolve_endpoint()
if not token:
    print("NO TOKEN")
    sys.exit(2)

with RimBridge(host, port, token) as rb:
    gi = rb.call("rimworld/get_game_info", {})
    print("status:", gi.get("status"), "ticks:", gi.get("ticksGame"))
    if gi.get("status") != "game_loaded":
        print("Game not loaded, aborting.")
        sys.exit(3)

    results = {}

    r = rb.call("jawa/world_tile_set", {"tiles": ",".join(map(str, twilight)), "biome": "RUT_TwilightSea", "readBack": 5})
    print("twilight biome set:", r.get("success"), "written:", r.get("written"), "errors:", r.get("errors"))
    results["twilight_biome"] = r

    r = rb.call("jawa/world_tile_set", {"tiles": ",".join(map(str, grey)), "biome": "RUT_GreySea", "readBack": 5})
    print("grey biome set:", r.get("success"), "written:", r.get("written"), "errors:", r.get("errors"))
    results["grey_biome"] = r

    r = rb.call("jawa/world_tile_set", {"tiles": ",".join(map(str, damp2m)), "elevation": 2, "readBack": 9})
    print("damp 2m elevation set:", r.get("success"), "written:", r.get("written"), "errors:", r.get("errors"))
    results["damp_2m"] = r

    r = rb.call("jawa/world_tile_set", {"tiles": ",".join(map(str, damp21m)), "elevation": 21, "readBack": 1})
    print("damp 21m elevation set:", r.get("success"), "written:", r.get("written"), "errors:", r.get("errors"))
    results["damp_21m"] = r

    commit = rb.call("jawa/world_commit", {})
    print("world_commit:", commit.get("success"))

    json.dump(results, open(os.path.join("Transient", "wble_fix_results.json"), "w"), indent=2, default=str)

    # Immediate spot-check
    sample = twilight[:3] + grey[:3] + damp2m[:3] + damp21m
    tg = rb.call("jawa/world_tile_get", {"tiles": ",".join(str(t) for t in sample)})
    print("post-fix spot-check:")
    for row in tg.get("tiles", []):
        print(" ", row.get("tile"), row.get("biome"), row.get("elevation"))

    # Re-run lint to confirm the count dropped
    lint2 = rb.call("jawa/world_lint", {"limit": 250})
    json.dump(lint2, open(os.path.join("Transient", "wble_world_lint_after.json"), "w"), indent=2)
    lbs2 = lint2.get("checks", {}).get("landBiomeSubmerged", {})
    print("POST-FIX landBiomeSubmerged count:", lbs2.get("count"), "examples:", lbs2.get("examples"))
