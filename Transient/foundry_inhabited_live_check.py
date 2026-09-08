import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

def show(label, r):
    print("=== %s ===" % label)
    print(json.dumps(r, indent=1)[:3000])
    print()

with RimBridge(host, port, token) as rb:
    # --- find two empty tiles ---
    r = rb.call("jawa/world_tile_get", {"tiles": "701,702,703,704,705,706,707,708"})
    for t in r["tiles"]:
        print(t["tile"], t["biome"], t["hilliness"], "water=" + str(t["waterCovered"]), "mutators=" + str(t["mutatorCount"]))

    tileA = 701  # wilderness route
    tileB = 702  # settlement route

    # === Test 1: wilderness TileMutatorDef route (INHABITED_TILEMUTATOR_NO_ENTRY_1) ===
    r = rb.call("jawa/world_mutators_set", {"action": "add", "mutators": "RM_InhabitedPlace", "tiles": str(tileA)})
    show("mutators_set tileA", r)

    r = rb.call("jawa/world_commit", {})
    show("world_commit after mutator", r)

    r = rb.call("jawa/world_tile_map_generate", {"tile": tileA, "suggestedMapParent": "Settlement"})
    show("map_generate tileA (wilderness)", r)

    # === Test 2: settlement route (INHABITED_SETTLEMENT_MAPPARENT_GAP_1) ===
    r = rb.call("jawa/world_objects_add", {"def": "Inhabited_Settlement", "tile": tileB, "faction": "OutlanderCivil", "name": "Test Inhabited Settlement"})
    show("world_objects_add InhabitedSettlement", r)

    r = rb.call("jawa/world_commit", {})
    show("world_commit after settlement add", r)

    r = rb.call("jawa/world_tile_map_generate", {"tile": tileB, "suggestedMapParent": "Inhabited_Settlement"})
    show("map_generate tileB (settlement)", r)
