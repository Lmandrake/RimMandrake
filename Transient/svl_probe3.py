import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()

TILE = 20000

with RimBridge(host, port, token) as rb:
    # dry run first
    dr = rb.call("jawa/world_tile_map_generate", {"tile": TILE, "dryRun": True})
    print("DRYRUN", json.dumps(dr)[:800])

    gen = rb.call("jawa/world_tile_map_generate", {"tile": TILE, "sizeX": 25, "sizeZ": 25})
    print("GEN", json.dumps(gen)[:1500])

    info1 = rb.call("rimworld/get_game_info", {})
    print("GAME_INFO_AFTER_GEN mapCount=", json.loads(json.dumps(info1)).get("mapCount"))

    objs = rb.call("jawa/world_objects_get", {"tiles": str(TILE)})
    print("OBJECTS_AT_TILE_AFTER_GEN", json.dumps(objs)[:1500])
