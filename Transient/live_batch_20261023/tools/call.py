"""call.py TOOL 'JSONARGS' [MAPID] -- one bridge call, printed (truncated 3000)."""
import sys, json, time
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h_, p_, t_ = resolve_endpoint()
with RimBridge(h_, p_, t_) as B:
    if len(sys.argv) > 3:
        B.call("jawa/set_current_map", {"mapId": int(sys.argv[3])}); time.sleep(0.5)
    r = B.call(sys.argv[1], json.loads(sys.argv[2]) if len(sys.argv) > 2 else {})
    print(json.dumps(r, default=str)[:int(__import__("os").environ.get("CALLMAX", "3000"))])
