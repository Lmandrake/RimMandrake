import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    # clean up minified corner tanks + rebuild in place
    for mid in ("MinifiedThing482083", "MinifiedThing482084", "MinifiedThing482085"):
        rb.call("rimworld/execute_debug_action", {"path": "Actions\\T: Destroy", "thingId": "Thing_" + mid})
    b = rb.call("jawa/build_batch", {"ops": "ChemfuelTank:149,148,0;ChemfuelTank:149,151,0", "faction": "player", "readBack": 2})
    print("rebuild:", b.get("placed"))
    rb.call("jawa/map_commit", {})
    # try a tiny lua probe first
    lua = 'return "lua-ok"'
    r = rb.call("rimbridge/compile_lua", {"code": lua}) if True else None
    print("lua probe:", str(r)[:200])
