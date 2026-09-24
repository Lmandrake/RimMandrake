import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()

TILE = 20000
WORLD_OBJ_ID = 278

with RimBridge(host, port, token) as rb:
    rem = rb.call("jawa/world_objects_remove", {"ids": str(WORLD_OBJ_ID)})
    print("REMOVE", json.dumps(rem)[:1200])

    info = rb.call("rimworld/get_game_info", {})
    print("GAME_INFO_AFTER_REMOVE mapCount=", json.loads(json.dumps(info)).get("mapCount"))

    objs = rb.call("jawa/world_objects_get", {"tiles": str(TILE)})
    print("OBJECTS_AT_TILE_AFTER_REMOVE", json.dumps(objs)[:800])
