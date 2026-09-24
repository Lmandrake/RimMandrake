import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()

CANDIDATE_TILE = 20000  # far from colony tile 17007; will verify it's empty first

with RimBridge(host, port, token) as rb:
    # 1. confirm candidate tile has no existing world object
    objs = rb.call("jawa/world_objects_get", {"tiles": str(CANDIDATE_TILE)})
    print("OBJECTS_AT_CANDIDATE", json.dumps(objs)[:1500])
