import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

with RimBridge(host, port, token) as rb:
    info = rb.call("rimworld/get_game_info", {})
    print("BEFORE mapCount:", info.get("mapCount"))
    colony_tile = info.get("currentMapTile") or info.get("tile")
    print("colony tile (best guess field):", colony_tile, "full keys:", list(info.keys()))

    # pick a candidate tile away from the colony and check it's empty land
    candidate = None
    for offset in [5000, 8000, 12000, 20000, 30000, 45000, 60000]:
        t = offset
        wt = rb.call("jawa/world_tile_get", {"tiles": str(t)})
        rows = wt.get("tiles") or []
        print("tile", t, "->", rows[0] if rows else wt)
        if wt.get("success") and rows and rows[0].get("biome") not in (None, "Ocean", "Lake"):
            candidate = t
            break

    if candidate is None:
        print("NO_CANDIDATE_FOUND")
        sys.exit(1)

    print("=== calling world_tile_map_generate on tile", candidate, "suggestedMapParent=Inhabited_Settlement ===")
    r = rb.call("jawa/world_tile_map_generate", {"tile": candidate, "suggestedMapParent": "Inhabited_Settlement"})
    print(json.dumps(r, indent=2))

    info2 = rb.call("rimworld/get_game_info", {})
    print("AFTER mapCount:", info2.get("mapCount"))
